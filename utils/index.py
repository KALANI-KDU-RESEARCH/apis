import jwt
from datetime import datetime, timedelta

# Generate JWT token
def generate_jwt_token(user: object) -> object:
    expiration_time = datetime.utcnow() + timedelta(days=1)
    payload = {"user": str(user), "exp": expiration_time}
    return jwt.encode(payload, "kalani", algorithm="HS256")