from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Client, Product, UseCase, Prospect, Meeting
from .serializers import ClientSerializer, ProductSerializer, UseCaseSerializer, ProspectSerializer, MeetingSerializer,QualifyingQuestionSerializer
from rest_framework.views import APIView
from django.contrib.auth.models import User

class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def company_info(self, request, pk=None):
        client = self.get_object()
        serializer = ClientSerializer(client)
        return Response(serializer.data)

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def get_assigned_products(self, request, pk=None):
        user_id = request.user.id
        assigned_products = Product.objects.filter(assigned_users=user_id)
        serializer = ProductSerializer(assigned_products, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def get_assigned_questions(self, request, pk=None):
        user_id = request.user.id
        assigned_questions = Product.objects.filter(assigned_users=user_id)
        serializer = QualifyingQuestionSerializer(assigned_questions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def details(self, request, pk=None):
        product = self.get_object()
        prospects = Prospect.objects.filter(product=product)
        client = product.client

        product_serializer = ProductSerializer(product)
        prospects_serializer = ProspectSerializer(prospects, many=True)
        client_serializer = ClientSerializer(client)

        data = {
            'product': product_serializer.data,
            'prospects': prospects_serializer.data,
            'client': client_serializer.data
        }

        return Response(data)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def usecases(self, request, pk=None):
        product = self.get_object()
        use_cases = UseCase.objects.filter(product=product)
        serializer = UseCaseSerializer(use_cases, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def add_usecase(self, request, pk=None):
        product = self.get_object()
        data = request.data
        data['product'] = product.id

        serializer = UseCaseSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def prospects(self, request, pk=None):
        product = self.get_object()
        prospects = Prospect.objects.filter(product=product)
        serializer = ProspectSerializer(prospects, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def add_prospect(self, request, pk=None):
        product = self.get_object()
        data = request.data
        data['product'] = product.id

        serializer = ProspectSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class UserProductsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        products = Product.objects.filter(assigned_users=user)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)



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


class AssignedProductsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        print(request.user)
        user = request.user
        products = Product.objects.filter(assigned_users=user)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
