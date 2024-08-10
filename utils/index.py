import jwt, os
from datetime import datetime, timedelta

# Generate JWT token
def generate_jwt_token(user: object) -> object:
    expiration_time = datetime.utcnow() + timedelta(days=1)
    payload = {"user": str(user), "exp": expiration_time}
    return jwt.encode(payload, "kalani", algorithm="HS256")

def env(key: str) -> str:
    return os.environ.get(key)

def calculate_impression_rate(investor_count,interests,age,experience):
    # Define the weights for each factor
    weights = {
        'investor_count': 0.4,  # Adjust these weights based on importance
        'interests': 0.3,
        'age': 0.2,
        'experience': 0.1
    }

    # Define normalization functions (example: scale to 0-1 range)
    def normalize_investor_count(count, max_count):
        return min(count / max_count, 1.0)

    def normalize_interests(interests, max_interests):
        return min(interests / max_interests, 1.0)

    def normalize_age(age, min_age, max_age):
        return min((age - min_age) / (max_age - min_age), 1.0)

    def normalize_experience(experience, max_experience):
        return min(experience / max_experience, 1.0)

    max_investor_count = 100
    max_interests = 10
    min_age = 20
    max_age = 60
    max_experience = 20

    # Normalize the values
    norm_investor_count = normalize_investor_count(investor_count, max_investor_count)
    norm_interests = normalize_interests(interests, max_interests)
    norm_age = normalize_age(age, min_age, max_age)
    norm_experience = normalize_experience(experience, max_experience)

    # Calculate the impression rate
    impression_rate = (norm_investor_count * weights['investor_count'] +
                    norm_interests * weights['interests'] +
                    norm_age * weights['age'] +
                    norm_experience * weights['experience'])

    print(f"Impression Rate: {impression_rate:.2f}")
    return format(impression_rate, ".2f")
