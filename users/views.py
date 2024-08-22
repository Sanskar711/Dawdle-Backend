# views.py
from django.contrib.auth import login, logout
from .models import User, OTP
from django.contrib.auth.decorators import login_required
from django.utils.crypto import get_random_string
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from clients.models import Meeting, QualifyingQuestionResponse
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
from datetime import datetime, timezone
from django.conf import settings
from clients.models import Product
from clients.serializers import ProductSerializer
from datetime import timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from clients.models import Product, Prospect, UseCase
from clients.serializers import ProductSerializer, ProspectSerializer, UseCaseSerializer, QualifyingQuestionSerializer, AssignProspectsSerializer, MeetingSerializer
from rest_framework.decorators import action
from rest_framework import viewsets
from django.core.mail import send_mail
from django.middleware.csrf import get_token
from clients.models import EmailRequest
from clients.serializers import EmailRequestSerializer


class CSRFTokenView(APIView):
    """
    This view provides a CSRF token for the frontend to use.
    """
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        csrf_token = get_token(request)
        return Response({'csrfToken': csrf_token})


logger = logging.getLogger(__name__)


@csrf_exempt
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
            logger.info(
                f"Email sent: {subject} - {message} to {recipient_list}")
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
                response = JsonResponse(
                    {"message": "OTP sent successfully", "user_id": user.id}, status=200)
            else:
                response = JsonResponse(
                    {"error": "User not found"}, status=404)

            # response['Access-Control-Allow-Origin'] = 'http://localhost:3000'
            # response['Access-Control-Allow-Credentials'] = 'true'
            return response

        return JsonResponse({"message": "Invalid request method"}, status=405)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        logger.error(f"Error during login process: {e}")
        return HttpResponseServerError('An error occurred during login. Please try again later.')


def generate_jwt_token(user):
    now = datetime.now(timezone.utc)
    payload = {
        'user_id': user.id,
        'exp': now + timedelta(hours=1),  # Set expiration time
        'iat': now,  # Issued at time
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token


class UserProductsView(APIView):

    def get(self, request):
        user = request.user
        products = Product.objects.filter(assigned_users=user)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def get_assigned_questions(self, request, pk=None):
        user_id = request.user.id
        assigned_questions = Product.objects.filter(assigned_users=user_id)
        serializer = QualifyingQuestionSerializer(
            assigned_questions, many=True)
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
            login(request, user)
            token = generate_jwt_token(user)
            return JsonResponse({"message": "User verified successfully", "token": token}, status=200)
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
        completed_meetings = Meeting.objects.filter(
            user=user, completed=True).count()
        successful_meetings = Meeting.objects.filter(
            user=user, is_successful=True).count()
        return Response({
            'scheduled_meetings': scheduled_meetings,
            'completed_meetings': completed_meetings,
            'successful_meetings': successful_meetings,
        })

# @login_required
# def session_view(request):
#     user_id = request.session.get('user_id')
#     return JsonResponse({"authenticated": True, "user_id": user_id})


# def debug_session_view(request):
#     session_data = request.session.items()
#     session_info = {key: value for key, value in session_data}
#     return JsonResponse({"session": session_info})

# def logout_view(request):
#     logout(request)
#     response = JsonResponse({"message": "User logged out successfully"})
#     response['Access-Control-Allow-Origin'] = 'http://localhost:3000'
#     response['Access-Control-Allow-Credentials'] = 'true'
#     return response
class UserLogoutView(APIView):
    def get(self, request):
        user = request.user
        if user is None or user.is_anonymous:
            return JsonResponse({'error': 'Unauthorized'}, status=401)

        logout(request)  # Assuming you have this field in your User model
        return JsonResponse({"User logged Out"})


class UserProfileDetail(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_object(self):
        #print(self.request.user)
        return self.request.user
    
from django.shortcuts import get_object_or_404
@csrf_exempt
def update_user_profile(request, user_id):
    if request.method == 'PUT':
        # Fetch user profile using user_id
        user_profile = get_object_or_404(User, id=user_id)
        
        # Assume the request body contains JSON data for profile update
        data = json.loads(request.body.decode('utf-8'))
        
        # Update user profile fields
        user_profile.first_name = data.get('first_name', user_profile.first_name)
        user_profile.last_name = data.get('last_name', user_profile.last_name)
        user_profile.email = data.get('email', user_profile.email)
        user_profile.phone_number = data.get('phone_number', user_profile.phone_number)
        user_profile.linkedin_id = data.get('linkedin_id', user_profile.linkedin_id)
        user_profile.designation = data.get('designation', user_profile.designation)
        user_profile.company_name = data.get('company_name', user_profile.company_name)
        # user_profile.user_type = data.get('user_type', user_profile.user_type)
        
        # Save the updated profile
        user_profile.save()
        
        return JsonResponse({'message': 'Profile updated successfully!'}, status=200)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)
class UserVerificationStatusView(APIView):
    def get(self, request):
        user = request.user
        if user is None or user.is_anonymous:
            return JsonResponse({'error': 'Unauthorized'}, status=401)

        is_verified = user.isverified  # Assuming you have this field in your User model
        return JsonResponse({"is_verified": is_verified})


class ProductInfoView(APIView):
    def get(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductProspectsView(APIView):
    def get(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        prospects = Prospect.objects.filter(product=product, is_approved=True)
        serializer = ProspectSerializer(prospects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductUseCasesView(APIView):
    def get(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        use_cases = product.use_cases
        serializer = UseCaseSerializer(use_cases, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductQuestions(APIView):
    def get(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        questions = product.qualifying_questions
        serializer = QualifyingQuestionSerializer(questions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UseCaseDetailView(APIView):
    def get(self, request, product_id, usecase_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        use_case = product.use_cases.filter(id=usecase_id).first()
        if not use_case:
            return Response({"error": "Use case not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = UseCaseSerializer(use_case)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UseCaseViewSet(viewsets.ModelViewSet):
    queryset = UseCase.objects.all()
    serializer_class = UseCaseSerializer

    @action(detail=True, methods=['get'])
    def details(self, request, pk=None):
        """
        Get detailed information about a specific use case.
        """
        use_case = self.get_object(request.id)
        serializer = UseCaseSerializer(use_case)
        return Response(serializer.data)
    

def add_prospect_to_product(request, product_id, prospect_id):
    # Fetch the product and prospect using the provided IDs
    product = get_object_or_404(Product, id=product_id)
    prospect = get_object_or_404(Prospect, id=prospect_id)
    
    # Add the prospect to the product's list of prospects
    product.product_prospects.add(prospect)
    
    # Optionally, you could return some useful response, like the updated list of prospects
    return JsonResponse({
        "message": "Prospect added to product successfully.",
        "product_id": product_id,
        "prospect_id": prospect_id,
        "total_prospects": product.product_prospects.count(),
    })

@csrf_exempt
def create_prospect(request):
    if request.method == 'POST':
        # Parse the JSON data from the request body
        data = json.loads(request.body)
        
        # Initialize the serializer with the parsed data
        serializer = ProspectSerializer(data=data)
        
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    return JsonResponse({'detail': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@csrf_exempt
def create_meeting(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            prospect_id = data.get('prospect_id')
            responses = data.get('qualifying_responses', [])
            poc_first_name = data.get('poc_first_name')
            poc_last_name = data.get('poc_last_name')
            poc_email = data.get('poc_email')
            poc_phone_number = data.get('poc_phone_number')
            poc_designation = data.get('poc_designation')
            scheduled_at = data.get('scheduled_at')
            other_relevant_details = data.get('other_relevant_details')
            use_case_titles = data.get('use_cases', [])
            product_id = data.get('product_id')

            # Check for required fields
            if not (user_id and prospect_id and poc_first_name and poc_last_name and poc_email and poc_phone_number and scheduled_at and product_id):
                return JsonResponse({"error": "All required fields must be provided."}, status=400)

            # Fetch the related objects
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return JsonResponse({"error": "User not found."}, status=404)
            try:
                prod = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return JsonResponse({"error": "Product not found."}, status=404)
            try:
                prospect = Prospect.objects.get(id=prospect_id)
            except Prospect.DoesNotExist:
                return JsonResponse({"error": "Prospect not found."}, status=404)

            # Create the Meeting object
            try:
                meeting = Meeting.objects.create(
                    user=user,
                    prospect=prospect,
                    scheduled_at=scheduled_at,
                    poc_first_name=poc_first_name,
                    poc_last_name=poc_last_name,
                    poc_email=poc_email,
                    poc_phone_number=poc_phone_number,
                    poc_designation=poc_designation,
                    other_relevant_details=other_relevant_details,
                    status='scheduled',
                    product=prod,
                )

                # Update prospect status to 'scheduled'
                prospect.status = 'scheduled'
                prospect.save()

            except Exception as e:
                print("Error creating Meeting:", str(e))
                return JsonResponse({"error": "Failed to create Meeting object", "details": str(e)}, status=500)

            # Process qualifying question responses
            for id, answer in responses.items():
                try:
                    if not (id and answer):
                        continue  # Skip invalid responses

                    qualifying_question_response = QualifyingQuestionResponse.objects.create(
                        qualifying_question_id=id,
                        response=answer
                    )

                    meeting.qualifying_question_responses.add(qualifying_question_response)
                except Exception as e:
                    print(f"Error processing qualifying question response: {str(e)}")
                    return JsonResponse({"error": f"Failed to associate qualifying question response: {str(e)}"}, status=500)

            # Associate UseCase objects
            for use_case_title in use_case_titles:
                try:
                    use_case = UseCase.objects.get(title=use_case_title)
                    meeting.use_cases.add(use_case)
                except UseCase.DoesNotExist:
                    print("ERROR in usecase adding")
                    continue  # Skip if the use case does not exist

            # Save the meeting with the associated ManyToMany fields
            meeting.save()

            # Send email to admin
            admin_email = settings.ADMIN_EMAIL
            send_mail(
                subject=f"New Meeting Scheduled with {prospect.company_name}",
                message=f"A new meeting has been scheduled.\n\nProspect: {prospect.company_name}\nScheduled At: {meeting.scheduled_at}\nPOC: {poc_first_name} {poc_last_name}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[admin_email],
            )

            return JsonResponse({"message": "Meeting created successfully", "meeting_id": meeting.id}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"message": "Invalid request method"}, status=405)

class UserMeetingsAPI(APIView):

    def get(self,request):
        # Return meetings for the logged-in user
        user = request.user
        meetings=Meeting.objects.filter(user=user.id)
        serializer = MeetingSerializer(meetings, many=True)
        return Response(serializer.data)
class ProspectInfoView(APIView):
    def get(self, request, prospect_id):
        try:
            prospect = Prospect.objects.get(id=prospect_id)
        except Prospect.DoesNotExist:
            return Response({"error": "Prospect not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProspectSerializer(prospect)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
def meeting_detail(request, meeting_id):
    meeting = get_object_or_404(Meeting, pk=meeting_id)
    data = {
        "id": meeting.id,
        "scheduled_at": meeting.scheduled_at,
        "status": meeting.status,
        "prospect": {
            "id": meeting.prospect.id,
            "company_name": meeting.prospect.company_name,
            "is_approved": meeting.prospect.is_approved,
            "geography": meeting.prospect.geography,
            "status": meeting.prospect.status,
        },
        # Add other fields as necessary
    }
    return JsonResponse(data)



@csrf_exempt
def send_email_request(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            prospect_id = data.get('prospect_id')
            product_id = data.get('product_id')
            poc_first_name = data.get('poc_first_name')
            poc_last_name = data.get('poc_last_name')
            poc_email = data.get('poc_email')
            poc_designation = data.get('poc_designation')
            email_subject = data.get('email_subject')
            email_body = data.get('email_body')

            # Validate required fields
            if not (user_id and prospect_id and poc_first_name and poc_last_name and poc_email and poc_designation and email_subject and email_body):
                return JsonResponse({"error": "All fields are required."}, status=400)

            # Create EmailRequest object
            email_request = EmailRequest.objects.create(
                user_id=user_id,
                prospect_id=prospect_id,
                product_id=product_id,
                poc_first_name=poc_first_name,
                poc_last_name=poc_last_name,
                poc_email=poc_email,
                poc_designation=poc_designation,
                email_subject=email_subject,
                email_body=email_body,
            )

            # Send email to admin
            try:
                send_mail(
                    subject=f"New Email Request: {email_subject}",
                    message=f"POC Name: {poc_first_name} {poc_last_name}\n"
                            f"Designation: {poc_designation}\n"
                            f"Email: {poc_email}\n\n"
                            f"Product ID: {product_id}\n\n"
                            f"Message:\n{email_body}",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[settings.ADMIN_EMAIL],
                )
                email_request.status = 'pending'
                email_request.save()
            except Exception as e:
                email_request.status = 'failed'
                email_request.save()
                return JsonResponse({"error": "Failed to send email.", "details": str(e)}, status=500)

            return JsonResponse({"message": "Email request sent successfully."}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"message": "Invalid request method"}, status=405)
