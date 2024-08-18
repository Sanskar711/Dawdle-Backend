from rest_framework import serializers
from .models import (
    Client, Product, UseCase, Prospect, Meeting,
    Resource, QualifyingQuestion, IdealCustomerProfile,
    QualifyingQuestionResponse
)


class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = '__all__'


class QualifyingQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QualifyingQuestion
        fields = '__all__'


class IdealCustomerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = IdealCustomerProfile
        fields = '__all__'


class UseCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = UseCase
        fields = '__all__'


class QualifyingQuestionResponseSerializer(serializers.ModelSerializer):
    qualifying_question = QualifyingQuestionSerializer()

    class Meta:
        model = QualifyingQuestionResponse
        fields = '__all__'


class ClientSerializer(serializers.ModelSerializer):
    products = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Client
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    use_cases = UseCaseSerializer(many=True, read_only=True)
    assigned_users = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    product_prospects = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    qualifying_questions = QualifyingQuestionSerializer(many=True, read_only=True)
    resources = ResourceSerializer(many=True, read_only=True)
    ideal_customer_profiles = IdealCustomerProfileSerializer(many=True, read_only=True)
    client_logo = serializers.ImageField(source='client.company_logo', read_only=True)  # Existing field for client logo
    client_name = serializers.SerializerMethodField()  # New field for client name

    class Meta:
        model = Product
        fields = '__all__'

    def get_client_name(self, obj):
        return obj.client.name if obj.client else None


class ProspectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prospect
        fields = '__all__'


class MeetingSerializer(serializers.ModelSerializer):
    qualifying_question_responses = QualifyingQuestionResponseSerializer(many=True, read_only=True)
    use_cases = UseCaseSerializer(many=True, read_only=True)

    class Meta:
        model = Meeting
        fields = '__all__'

class AssignProspectsSerializer(serializers.Serializer):
    prospect_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True
    )

    def validate_prospect_ids(self, value):
        if not all(Prospect.objects.filter(id=prospect_id).exists() for prospect_id in value):
            raise serializers.ValidationError("One or more prospects do not exist.")
        return value

    def update(self, instance, validated_data):
        prospects = Prospect.objects.filter(id__in=validated_data['prospect_ids'])
        instance.product_prospects.add(*prospects)
        return instance
