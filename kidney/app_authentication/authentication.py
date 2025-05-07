from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken

class CustomJWTAuthentication(JWTAuthentication):
    def get_validated_token(self, raw_token):
        validated_token = super().get_validated_token(raw_token)

        # Check if token is blacklisted
        jti = validated_token.get('jti')
        if jti is not None:
            try:
                if BlacklistedToken.objects.filter(token__jti=jti).exists():
                    raise InvalidToken('Token is blacklisted')
            except BlacklistedToken.DoesNotExist:
                pass

        return validated_token
