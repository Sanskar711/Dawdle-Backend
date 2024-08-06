# views.py
from django.contrib.auth import login, logout
from .models import User, OTP
from django.contrib.auth.decorators import login_required
from django.utils.crypto import get_random_string
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.middleware.csrf import get_token
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from clients.models import Meeting
from backend.settings import EMAIL_HOST_PASSWORD, EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_USE_TLS
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
from django.http import HttpResponseServerError
from rest_framework import generics
from .models import User
from .serializers import UserSerializer
from rest_framework.permissions import IsAuthenticated
import jwt
import datetime
from clients.models import Product
from clients.serializers import ProductSerializer

logger = logging.getLogger(__name__)

def send_otp(user):
    code = get_random_string(6, allowed_chars='0123456789')
    OTP.objects.create(user=user, code=code)

    subject = f'{user.first_name} Your OTP Code'
    message = f'Your OTP code is {code}'
    from_email = EMAIL_HOST_USER
    recipient_list = [user.email]

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = ', '.join(recipient_list)
    msg['Subject'] = subject

    msg.attach(MIMEText(message, 'plain'))

    try:
        logger.info(f"Connecting to SMTP server at {EMAIL_HOST}:{EMAIL_PORT}")
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            if EMAIL_USE_TLS:
                logger.info("Starting TLS")
                server.starttls()
            logger.info("Logging in")
            server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
            logger.info("Sending email")
            server.sendmail(from_email, recipient_list, msg.as_string())
            logger.info(f"Email sent: {subject} - {message} to {recipient_list}")
    except Exception as e:
        logger.error(f"Error sending OTP: {e}")

@csrf_exempt
def register(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            email = data.get('email')
            phone_number = data.get('phone_number')
            user_type = data.get('user_type')
            linkedin_id = data.get('linkedin_id')
            designation = data.get('designation')
            company_name = data.get('company_name')
            if not (first_name and last_name and email and phone_number and user_type):
                return JsonResponse({"error": "All fields are required."}, status=400)
            if User.objects.filter(email=email).exists():
                return JsonResponse({"error": "Email already exists."}, status=400)
            if User.objects.filter(phone_number=phone_number).exists():
                return JsonResponse({"error": "Phone number already exists."}, status=400)

            user = User(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone_number=phone_number,
                user_type=user_type,
                linkedin_id=linkedin_id,
                designation=designation,
                company_name=company_name
            )
            user.save()
            return JsonResponse({"message": "User registered successfully", "user_id": user.id}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
    return JsonResponse({"message": "Invalid request method"}, status=405)


@csrf_exempt
def signin(request):
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            email = data.get('email')
            if not email:
                return JsonResponse({"error": "Email is required."}, status=400)
            
            user = User.objects.filter(email=email).first()
            if user:
                send_otp(user)
                response = JsonResponse({"message": "OTP sent successfully", "user_id": user.id}, status=200)
            else:
                response = JsonResponse({"error": "User not found"}, status=404)
            
            # response['Access-Control-Allow-Origin'] = 'http://localhost:3000'
            # response['Access-Control-Allow-Credentials'] = 'true'
            return response
        
        return JsonResponse({"message": "Invalid request method"}, status=405)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        logger.error(f"Error during login process: {e}")
        return HttpResponseServerError('An error occurred during login. Please try again later.')

class UserProductsView(APIView):
   

    def get(self, request):
        user = request.user
        products = Product.objects.filter(assigned_users=user)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

@csrf_exempt
def verify_otp_login(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "User does not exist"}, status=404)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            code = data.get('code')
        except (json.JSONDecodeError, KeyError):
            return JsonResponse({"error": "Invalid request payload"}, status=400)

        otp = OTP.objects.filter(user=user, code=code, is_used=False).first()
        if otp and otp.is_valid():
            otp.is_used = True
            otp.delete()
            login(request, user)  # Log the user in
            request.session['user_id'] = user.id  # Set user ID in the session
            request.session.save()  # Ensure session is saved
            token = jwt.encode({'user_id': user.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)}, SECRET_KEY, algorithm='HS256')
            return JsonResponse({"message": "User verified successfully", "token": token}, status=200)
        else:
            return JsonResponse({"error": "Invalid or expired OTP"}, status=400)

    return JsonResponse({"message": "Invalid request method"}, status=405)

@login_required
def home(request):
    user = request.user
    if user.isverified:
        status = "Verification Pending"
        products = []
    else:
        status = "Verified"
        products = user.assigned_products.all()
    # return render(request, 'users/home.html', {'status': status, 'products': products})

class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        scheduled_meetings = Meeting.objects.filter(user=user).count()
        completed_meetings = Meeting.objects.filter(user=user, completed=True).count()
        successful_meetings = Meeting.objects.filter(user=user, is_successful=True).count()
        return Response({
            'scheduled_meetings': scheduled_meetings,
            'completed_meetings': completed_meetings,
            'successful_meetings': successful_meetings,
        })

def logout_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({"detail":"You are not logged in"},status=400)
    logout(request)
    return JsonResponse({"detail":"You are now logged out"},status=200)

@login_required
def session_view(request):
    user_id = request.session.get('user_id')
    return JsonResponse({"authenticated": True, "user_id": user_id})


def debug_session_view(request):
    session_data = request.session.items()
    session_info = {key: value for key, value in session_data}
    return JsonResponse({"session": session_info})

def logout_view(request):
    logout(request)
    response = JsonResponse({"message": "User logged out successfully"})
    response['Access-Control-Allow-Origin'] = 'http://localhost:3000'
    response['Access-Control-Allow-Credentials'] = 'true'
    return response

class UserProfileDetail(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user