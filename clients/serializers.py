from rest_framework import serializers
from .models import Client, Product, UseCase, Prospect, Meeting

class UseCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = UseCase
        fields = '__all__'

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    use_cases = UseCaseSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = '__all__'

class ProspectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prospect
        fields = '__all__'

class MeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = '__all__'
