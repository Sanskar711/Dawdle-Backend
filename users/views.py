from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import CustomUserCreationForm, OTPForm
from .models import User,OTP
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.utils.crypto import get_random_string
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from clients.models import  Meeting
from django.views.decorators.csrf import csrf_exempt
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from backend.settings import EMAIL_HOST_PASSWORD, EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_USE_TLS
import logging

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


@login_required
def home(request):
    print(request.user)
    if not request.user.is_verified:
        status = "Verification Pending"
        products = []
    else:
        status = "Verified"
        products = request.user.assigned_products.all()
    return render(request, 'users/home.html', {'status': status, 'products': products})

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

def verify_otp(request, user_id):
    user = User.objects.get(id=user_id)
    if request.method == 'POST':
        form = OTPForm(request.POST)
        if form.is_valid():
            otp = OTP.objects.filter(user=user, code=form.cleaned_data['code'], is_used=False).first()
            if otp and otp.is_valid():
                otp.is_used = True
                otp.delete()
                # login(request, user)
                return redirect('home')
    else:
        form = OTPForm()
    return render(request, 'users/verify_otp.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        email_or_phone = request.POST.get('email_or_phone')
        user = User.objects.filter(email=email_or_phone).first() or User.objects.filter(phone_number=email_or_phone).first()
        if user:
            send_otp(user)
            return redirect('verify_otp_login', user_id=user.id)
    return render(request, 'users/login.html')
@csrf_exempt
def verify_otp_login(request, user_id):
    user = User.objects.get(id=user_id)
    if request.method == 'POST':
        form = OTPForm(request.POST)
        if form.is_valid():
            otp = OTP.objects.filter(user=user, code=form.cleaned_data['code'], is_used=False).first()
            if otp and otp.is_valid():
                otp.is_used = True
                otp.save()
                # login(request, user)
                return redirect('home')
    else:
        form = OTPForm()
    return render(request, 'users/verify_otp.html', {'form': form})

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
