from sqlalchemy.orm import Session
from src.models.user import User
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher()

class AuthService:
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str):
        user = db.query(User).filter(User.username == username, User.is_active == True).first()
        if not user:
            return None, 'AUTH_USER_NOT_FOUND'
        
        try:
            ph.verify(user.hashed_password, password)
            return user, None
        except VerifyMismatchError:
            return None, 'AUTH_INVALID_CREDENTIALS'
        except Exception as e:
            return None, f'AUTH_ERROR: {str(e)}'
