from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Client, Product, UseCase, Prospect, Meeting
from .serializers import ClientSerializer, ProductSerializer, UseCaseSerializer, ProspectSerializer, MeetingSerializer
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class UseCaseViewSet(viewsets.ModelViewSet):
    queryset = UseCase.objects.all()
    serializer_class = UseCaseSerializer

class ProspectViewSet(viewsets.ModelViewSet):
    queryset = Prospect.objects.all()
    serializer_class = ProspectSerializer

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def book_meeting(self, request, pk=None):
        prospect = self.get_object()
        if prospect.is_locked:
            return Response({"error": "Prospect is already locked"}, status=400)
        
        data = request.data
        data['user'] = request.user.id
        data['prospect'] = prospect.id
        data['scheduled_at'] = timezone.now()  # Replace with actual scheduled time

        serializer = MeetingSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            prospect.is_locked = True
            prospect.save()
            return Response({"calendly_link": prospect.product.client.calendly_link}, status=201)
        return Response(serializer.errors, status=400)

class MeetingViewSet(viewsets.ModelViewSet):
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def update_status(self, request, pk=None):
        meeting = self.get_object()
        status = request.data.get('status')

        if status == 'completed':
            meeting.completed = True
            meeting.is_successful = request.data.get('is_successful', False)
            if meeting.is_successful:
                meeting.prospect.is_locked = False  # Unlock if successful
            else:
                meeting.prospect.is_locked = False  # Unlock if not successful
        elif status == 'no_show':
            meeting.prospect.is_locked = False  # Unlock if no show

        meeting.save()
        meeting.prospect.save()
        return Response({"status": "updated"}, status=200)
