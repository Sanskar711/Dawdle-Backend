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
from clients.models import Product, Prospect, UseCase,Client
from clients.serializers import ProductSerializer, ProspectSerializer,Prospect2Serializer, UseCaseSerializer, QualifyingQuestionSerializer, AssignProspectsSerializer, MeetingSerializer
from rest_framework.decorators import action
from rest_framework import viewsets
from django.core.mail import send_mail
from django.middleware.csrf import get_token
from clients.models import EmailRequest
from clients.serializers import EmailRequestSerializer

logger = logging.getLogger(__name__)
@csrf_exempt
def send_client_otp(client):
    code = get_random_string(6, allowed_chars='0123456789')
    OTP.objects.create(client=client, code=code)  # Assuming OTP model has a foreign key to Client

    subject = f'{client.name}, Your OTP Code'
    message = f'Your OTP code is {code}'
    from_email = EMAIL_HOST_USER
    recipient_list = [client.email]

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
def signin_client(request):
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            email = data.get('email')
            if not email:
                return JsonResponse({"error": "Email is required."}, status=400)

            client = Client.objects.filter(email=email).first()
            if client:
                send_client_otp(client)
                response = JsonResponse(
                    {"message": "OTP sent successfully", "client_id": client.id}, status=200)
            else:
                response = JsonResponse(
                    {"error": "Client not found"}, status=404)

            return response

        return JsonResponse({"message": "Invalid request method"}, status=405)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        logger.error(f"Error during client login process: {e}")
        return HttpResponseServerError('An error occurred during login. Please try again later.')


def generate_client_jwt_token(client):
    now = datetime.now(timezone.utc)
    payload = {
        'client_id': client.id,
        'exp': now + timedelta(hours=1),  # Set expiration time
        'iat': now,  # Issued at time
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token
@csrf_exempt
def verify_client_otp_login(request, client_id):
    try:
        client = Client.objects.get(id=client_id)
    except Client.DoesNotExist:
        return JsonResponse({"error": "Client does not exist"}, status=404)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            code = data.get('code')
        except (json.JSONDecodeError, KeyError):
            return JsonResponse({"error": "Invalid request payload"}, status=400)

        otp = OTP.objects.filter(client=client, code=code, is_used=False).first()  # Assuming OTP has a foreign key to Client
        if otp and otp.is_valid():
            otp.is_used = True
            otp.delete()
            # login(request, client)
            request.session['client_id'] = client.id
            token = generate_client_jwt_token(client)
            return JsonResponse({"message": "Client verified successfully", "token": token}, status=200)
        return JsonResponse({"error": "Invalid or expired OTP"}, status=400)

    return JsonResponse({"message": "Invalid request method"}, status=405)


# class ClientDashboardView(APIView):
#     # permission_classes = [IsAuthenticated]

#     # def get(self, request):
#     #     client = request.client  # Assuming you're using a middleware to set request.client
#     #     scheduled_meetings = Meeting.objects.filter(client=client).count()  # Assuming Meeting model has a foreign key to Client
#     #     completed_meetings = Meeting.objects.filter(client=client, completed=True).count()
#     #     successful_meetings = Meeting.objects.filter(client=client, is_successful=True).count()

#     #     return Response({
#     #         'scheduled_meetings': scheduled_meetings,
#     #         'completed_meetings': completed_meetings,
#     #         'successful_meetings': successful_meetings,
#     #     })
        

from django.views.decorators.http import require_GET
from .serializers import ClientSerializer 
@require_GET
def client_info(request):
    client = getattr(request, 'client', None)  # Assuming your middleware sets request.client
    if client is None:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    # is_verified = client.is_verified  # Assuming you have this field in your Client model
    serializer = ClientSerializer(client)
    return JsonResponse(serializer.data, safe=False)
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
@method_decorator(csrf_exempt, name='dispatch')
@require_http_methods(["PUT"])
def update_client_info(request):
    client = getattr(request, 'client', None)  # Assuming your middleware sets request.client
    if client is None:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    try:
        data = JSONParser().parse(request)
    except ValueError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    serializer = ClientSerializer(client, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse(serializer.data, safe=False)
    else:
        return JsonResponse(serializer.errors, status=400)












from django.shortcuts import get_object_or_404


from django.http import JsonResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from .models import (
    Product, UseCase, Prospect, Resource, QualifyingQuestion, IdealCustomerProfile, Meeting
)
from .serializers import (
    ProductSerializer, UseCaseSerializer, ProspectSerializer, ResourceSerializer,
    QualifyingQuestionSerializer, IdealCustomerProfileSerializer, MeetingSerializer
)
from rest_framework.parsers import JSONParser
from django.core.exceptions import ObjectDoesNotExist
@csrf_exempt
def client_product_list(request):
    client = request.client
    if client is None:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    if request.method == 'GET':
        products = Product.objects.filter(client=client)
        serializer = ProductSerializer(products, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = ProductSerializer(data=data)
        if serializer.is_valid():
            serializer.save(client=client)
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        data = JSONParser().parse(request)
        product_id = data.get('id')
        try:
            product = Product.objects.get(id=product_id, client=client)
            product.delete()
            return JsonResponse({'message': 'Product deleted successfully'}, status=200)
        except ObjectDoesNotExist:
            return JsonResponse({'error': 'Product not found'}, status=404)

    return HttpResponseNotAllowed(['GET', 'POST', 'DELETE'])


@csrf_exempt
def client_product_detail(request, pk):
    client = request.client
    if client is None:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    product = get_object_or_404(Product, pk=pk, client=client)
    if not product.client==client:
        return JsonResponse({'error': 'Forbidden'}, status=403)

    if request.method == 'GET':
        serializer = ProductSerializer(product)
        return JsonResponse(serializer.data)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = ProductSerializer(product, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        product.delete()
        return JsonResponse(status=204)

    return HttpResponseNotAllowed(['GET', 'PUT', 'DELETE'])


@csrf_exempt
def client_usecase_list(request, product_id):
    client = request.client
    if client is None:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    

    product = get_object_or_404(Product, id=product_id, client=client)

    if request.method == 'GET':
        use_cases = UseCase.objects.filter(products=product).distinct()
        serializer = UseCaseSerializer(use_cases, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = UseCaseSerializer(data=data)
        if serializer.is_valid():
            serializer.save(products=[product])
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)

    return HttpResponseNotAllowed(['GET', 'POST'])


@csrf_exempt
def client_usecase_detail(request, product_id, pk):
    client = request.client
    if client is None:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    product = get_object_or_404(Product, id=product_id, client=client)
    use_case = get_object_or_404(UseCase, pk=pk, products=product)

    if request.method == 'GET':
        serializer = UseCaseSerializer(use_case)
        return JsonResponse(serializer.data)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = UseCaseSerializer(use_case, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        use_case.delete()
        return HttpResponse(status=204)

    return HttpResponseNotAllowed(['GET', 'PUT', 'DELETE'])


@csrf_exempt
def client_prospect_list(request, product_id):
    client = request.client
    if client is None:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    product = get_object_or_404(Product, id=product_id, client=client)

    if request.method == 'GET':
        prospects = Prospect.objects.filter(product=product).distinct()
        serializer = ProspectSerializer(prospects, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = ProspectSerializer(data=data)
        if serializer.is_valid():
            serializer.save(product=[product])
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)

    return HttpResponseNotAllowed(['GET', 'POST'])


@csrf_exempt
def client_prospect_detail(request, product_id, pk):
    client = request.client
    if client is None:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    product = get_object_or_404(Product, id=product_id, client=client)
    prospect = get_object_or_404(Prospect, pk=pk, product=product)

    if request.method == 'GET':
        serializer = ProspectSerializer(prospect)
        return JsonResponse(serializer.data)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = ProspectSerializer(prospect, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)
    
    
    

    elif request.method == 'DELETE':
        prospect.delete()
        return HttpResponse(status=204)

    return HttpResponseNotAllowed(['GET', 'PUT', 'DELETE'])


@csrf_exempt
def client_resource_list(request, product_id):
    client = request.client
    if client is None:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    product = get_object_or_404(Product, id=product_id, client=client)

    if request.method == 'GET':
        resources = Resource.objects.filter(products=product).distinct()
        serializer = ResourceSerializer(resources, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = ResourceSerializer(data=data)
        if serializer.is_valid():
            serializer.save(products=[product])
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)

    return HttpResponseNotAllowed(['GET', 'POST'])

from django.http import JsonResponse, HttpResponse, HttpResponseNotAllowed
@csrf_exempt
def client_resource_detail(request, product_id, pk):
    client = request.client
    if client is None:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    product = get_object_or_404(Product, id=product_id, client=client)
    resource = get_object_or_404(Resource, pk=pk, products=product)

    if request.method == 'GET':
        serializer = ResourceSerializer(resource)
        return JsonResponse(serializer.data)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = ResourceSerializer(resource, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        resource.delete()
        return HttpResponse(status=204)

    return HttpResponseNotAllowed(['GET', 'PUT', 'DELETE'])


@csrf_exempt
def client_qualifying_question_list(request, product_id):
    client = request.client
    if client is None:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    product = get_object_or_404(Product, id=product_id, client=client)

    if request.method == 'GET':
        qualifying_questions = QualifyingQuestion.objects.filter(products=product).distinct()
        serializer = QualifyingQuestionSerializer(qualifying_questions, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = QualifyingQuestionSerializer(data=data)
        if serializer.is_valid():
            serializer.save(products=[product])
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)

    return HttpResponseNotAllowed(['GET', 'POST'])


@csrf_exempt
def client_qualifying_question_detail(request, product_id, pk):
    client = request.client
    if client is None:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    product = get_object_or_404(Product, id=product_id, client=client)
    qualifying_question = get_object_or_404(QualifyingQuestion, pk=pk, products=product)

    if request.method == 'GET':
        serializer = QualifyingQuestionSerializer(qualifying_question)
        return JsonResponse(serializer.data)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = QualifyingQuestionSerializer(qualifying_question, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        qualifying_question.delete()
        return JsonResponse(status=204)

    return HttpResponseNotAllowed(['GET', 'PUT', 'DELETE'])


@csrf_exempt
def client_ideal_customer_profile_list(request, product_id):
    client = request.client
    if client is None:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    product = get_object_or_404(Product, id=product_id, client=client)

    if request.method == 'GET':
        ideal_customer_profiles = IdealCustomerProfile.objects.filter(products=product).distinct()
        serializer = IdealCustomerProfileSerializer(ideal_customer_profiles, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = IdealCustomerProfileSerializer(data=data)
        if serializer.is_valid():
            serializer.save(products=[product])
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)

    return HttpResponseNotAllowed(['GET', 'POST'])


@csrf_exempt
def client_ideal_customer_profile_detail(request, product_id, pk):
    client = request.client
    if client is None:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    product = get_object_or_404(Product, id=product_id, client=client)
    ideal_customer_profile = get_object_or_404(IdealCustomerProfile, pk=pk, products=product)

    if request.method == 'GET':
        serializer = IdealCustomerProfileSerializer(ideal_customer_profile)
        return JsonResponse(serializer.data)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = IdealCustomerProfileSerializer(ideal_customer_profile, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        ideal_customer_profile.delete()
        return HttpResponse(status=204)

    return HttpResponseNotAllowed(['GET', 'PUT', 'DELETE'])


@csrf_exempt
def client_meeting_list(request, product_id):
    client = request.client
    if client is None:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    product = get_object_or_404(Product, id=product_id, client=client)

    if request.method == 'GET':
        meetings = Meeting.objects.filter(prospect__product=product).distinct()
        serializer = MeetingSerializer(meetings, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = MeetingSerializer(data=data)
        if serializer.is_valid():
            serializer.save(prospect__product=product)
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)

    return HttpResponseNotAllowed(['GET', 'POST'])


@csrf_exempt
def client_meeting_detail(request, product_id, pk):
    client = request.client
    if client is None:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    product = get_object_or_404(Product, id=product_id, client=client)
    meeting = get_object_or_404(Meeting, pk=pk, prospect__product=product)

    if request.method == 'GET':
        serializer = MeetingSerializer(meeting)
        return JsonResponse(serializer.data)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = MeetingSerializer(meeting, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        meeting.delete()
        return JsonResponse(status=204)

    return HttpResponseNotAllowed(['GET', 'PUT', 'DELETE'])



@csrf_exempt
def entire_client_meeting_list(request):
    client = request.client  # Assuming `request.client` is set by your middleware or view logic
    if client is None:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    if request.method == 'GET':
        # Fetch all products associated with the given client
        products = Product.objects.filter(client=client)

        # Fetch all meetings associated with these products
        meetings = Meeting.objects.filter(product__in=products).distinct()

        # Serialize the meetings data
        serializer = MeetingSerializer(meetings, many=True)
        return JsonResponse(serializer.data, safe=False)

    return HttpResponseNotAllowed(['GET'])

@csrf_exempt
def meeting_detail(request, meeting_id):
    client = request.client  # Assuming `request.client` is set by your middleware or view logic
    if client is None:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    meeting = get_object_or_404(Meeting, pk=meeting_id)

    # Ensure the meeting is associated with the client
    if meeting.product.client != client:
        return JsonResponse({'error': 'Forbidden'}, status=403)

    serializer = MeetingSerializer(meeting)
    return JsonResponse(serializer.data, safe=False)

@csrf_exempt
def prospect_detail(request, prospect_id):
    client = request.client  # Assuming `request.client` is set by your middleware or view logic
    if client is None:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    prospect = get_object_or_404(Prospect, pk=prospect_id)
    print(prospect)

    # Ensure the prospect is associated with the client
    if not prospect.product.filter(client=client).exists():
        return JsonResponse({'error': 'Forbidden'}, status=403)

    serializer = ProspectSerializer(prospect)
    return JsonResponse(serializer.data, safe=False)

@csrf_exempt
def usecase_detail(request, usecase_id):
    client = request.client  # Assuming `request.client` is set by your middleware or view logic
    if client is None:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    use_case = get_object_or_404(UseCase, pk=usecase_id)

    # Ensure the use case is associated with a product that belongs to the client
    if not use_case.products.filter(client=client).exists():
        return JsonResponse({'error': 'Forbidden'}, status=403)

    serializer = UseCaseSerializer(use_case)
    return JsonResponse(serializer.data, safe=False)

@csrf_exempt
def qualifying_question_detail(request, question_id):
    client = request.client  # Assuming `request.client` is set by your middleware or view logic
    if client is None:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    question = get_object_or_404(QualifyingQuestion, pk=question_id)

    # Ensure the qualifying question is associated with a product that belongs to the client
    if not question.products.filter(client=client).exists():
        return JsonResponse({'error': 'Forbidden'}, status=403)

    serializer = QualifyingQuestionSerializer(question)
    return JsonResponse(serializer.data, safe=False)