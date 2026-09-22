import jwt
from django.contrib.auth import get_user_model
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse
from django.middleware.security import SecurityMiddleware
from django.middleware.csrf import CSRFCheck
from django.middleware.locale import LocaleMiddleware

User_renamed = get_user_model()

class JWTAuthenticationMiddleware(AuthenticationMiddleware):
    def process_request(self, request):
        try:
            authorization_header = request.META.get('HTTP_AUTHORIZATION')
            if authorization_header:
                token = authorization_header.split()[1]
                try:
                    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                    user_id = payload.get('user_id')
                    request.user = User_renamed.objects.get(id=user_id)
                except jwt.ExpiredSignatureError:
                    return HttpResponse("Token has expired", status=401)
                except jwt.InvalidTokenError:
                    return HttpResponse("Invalid token", status=401)

            else:
                return super().process_request(request)

        except User_renamed.DoesNotExist:
            return HttpResponse("User not found", status=401)
        except jwt.DecodeError:
            return HttpResponse("Invalid token", status=401)

    def process_response(self, request, response):
        return response
