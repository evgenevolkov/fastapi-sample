from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated='auto')


def hash(string: str):
    return pwd_context.hash(string)


def verify(password_plain, password_hashed):
    return pwd_context.verify(secret=password_plain, hash=password_hashed)