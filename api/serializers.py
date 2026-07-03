from rest_framework import serializers 
from api.models import Austin 
from django.contrib.auth.hashers import check_password

class Registrationserializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = Austin 
        fields = ['name', 'email', 'password', 'confirm_password']
        extra_kwargs = {
            'password': {'write_only': True}
        } 
    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({'confirm_password': 'Password do not match'})
        return data
    def create(self, validate_data):
        validate_data.pop('confirm_password')
        return Austin.objects.create(**validate_data) 
    
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        try:
            user = Austin.objects.get(email=email)
            if not check_password(password, user.password):
                raise serializers.ValidationError({"password": "Incorrect password"})
        except Austin.DoesNotExist:
            raise serializers.ValidationError({"email": "User does not exist"})
        return data
