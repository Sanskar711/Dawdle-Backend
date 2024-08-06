import jwt
from django.conf import settings
from django.http import JsonResponse
from .models import User
from rest_framework_simplejwt.exceptions import InvalidToken

class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/'):
            return self.get_response(request)
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                # Decode the token
                # print(token)
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                print(payload)
                user_id = payload.get('user_id')
                print(user_id)
                if user_id:
                    try:
                        user = User.objects.get(id=user_id)
                        request.user = user
                    except User.DoesNotExist:
                        return JsonResponse({'error': 'User does not exist'}, status=404)
                else:
                    return JsonResponse({'error': 'Invalid token payload'}, status=401)
            except (jwt.ExpiredSignatureError, jwt.DecodeError, InvalidToken) as e:
                return JsonResponse({'error': str(e)}, status=401)
        else:
            request.user = None

        response = self.get_response(request)
        return response
