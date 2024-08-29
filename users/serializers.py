from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ['email']  # If you don't want email to be editable, for example
    # def update(self, instance, validated_data):
    #     # Handle updates, ensuring you only update fields that should be editable
    #     instance.first_name = validated_data.get('first_name', instance.first_name)
    #     instance.last_name = validated_data.get('last_name', instance.last_name)
    #     instance.phone_number = validated_data.get('phone_number', instance.phone_number)
    #     instance.linkedin_id = validated_data.get('linkedin_id', instance.linkedin_id)
    #     instance.designation = validated_data.get('designation', instance.designation)
    #     instance.company_name = validated_data.get('company_name', instance.company_name)
    #     instance.user_type = validated_data.get('user_type', instance.user_type)
    #     instance.save()
    #     return instance