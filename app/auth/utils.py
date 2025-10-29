# password hashing
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str):
    return pwd_context.hash(password)

BLACKLISTED_TOKENS = set()

def add_to_blacklist(token: str):
    BLACKLISTED_TOKENS.add(token)

def is_blacklisted(token: str) -> bool:
    return token in BLACKLISTED_TOKENS