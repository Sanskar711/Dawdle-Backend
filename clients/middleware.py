import jwt
from django.conf import settings
from django.http import JsonResponse
from .models import Client

from users.models import User
from rest_framework_simplejwt.exceptions import InvalidToken
import logging

logger = logging.getLogger(__name__)

class PathBasedJWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Determine which authentication logic to apply based on the request path
        if request.path.startswith('/admin/'):
            # Bypass JWT authentication for admin paths
            return self.get_response(request)
        elif request.path.startswith('/users/'):
            # Apply User JWT authentication
            return self._authenticate_user(request)
        elif request.path.startswith('/clients/'):
            # Apply Client JWT authentication
            print("hello")
            return self._authenticate_client(request)
        
        else:
            # Default action if path does not match known patterns
            request.user = None
            request.client = None
            return self.get_response(request)

    def _authenticate_user(self, request):
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                # Decode the JWT token for users
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                user_id = payload.get('user_id')
                if user_id:
                    try:
                        user = User.objects.get(id=user_id)
                        request.user = user
                    except User.DoesNotExist:
                        logger.warning(f"User with ID {user_id} does not exist.")
                        return JsonResponse({'error': 'User does not exist'}, status=404)
                else:
                    logger.warning("Invalid token payload: missing user_id.")
                    return JsonResponse({'error': 'Invalid token payload'}, status=401)
            except (jwt.ExpiredSignatureError, jwt.DecodeError, InvalidToken) as e:
                logger.error(f"JWT error: {str(e)}")
                return JsonResponse({'error': 'Token is invalid or expired'}, status=401)
        else:
            request.user = None

        return self.get_response(request)
    

    def _authenticate_client(self, request):
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                # Decode the JWT token for clients
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                client_id = payload.get('client_id')
                print("hello",client_id)
                if client_id:
                    try:
                        client = Client.objects.get(id=client_id)
                        request.client = client
                        print(client)
                    except Client.DoesNotExist:
                        logger.warning(f"Client with ID {client_id} does not exist.")
                        return JsonResponse({'error': 'Client does not exist'}, status=404)
                else:
                    logger.warning("Invalid token payload: missing client_id.")
                    return JsonResponse({'error': 'Invalid token payload'}, status=401)
            except (jwt.ExpiredSignatureError, jwt.DecodeError, InvalidToken) as e:
                logger.error(f"JWT error: {str(e)}")
                return JsonResponse({'error': 'Token is invalid or expired'}, status=401)
        else:
            request.client = None

        return self.get_response(request)
