import uuid
import logging
from passlib.context import CryptContext
from datetime import datetime ,timedelta
from config import Config
from errors import InvalidOrExpireToken
# jwt 
from jose import jwt ,JWTError ,ExpiredSignatureError

password_context = CryptContext(schemes=["bcrypt"],deprecated="auto")

def generate_password_hash(password :str)-> str:
    """Hash a password using bcrypt."""
    return password_context.hash(password)

def verify_password(password:str,hash_password:str)->bool:
    return password_context.verify(password,hash_password)
    
def create_token(user_data: dict ,expire_delta : timedelta | None =None ,refresh : bool =False )  :
    payload = {}
    
    payload['user'] = user_data
    payload['exp'] = datetime.utcnow() + (expire_delta or timedelta(seconds=Config.ACCESS_TOKEN_EXPIRE)) 
    payload['refresh'] = refresh
    payload['jti']  =  str(uuid.uuid4())
    payload['iat'] =  datetime.utcnow()
    
    token = jwt.encode(
        claims=payload,
        key=Config.JWT_SECRETKEY,
        algorithm=Config.JWT_ALGORITHM
    )
    return token


def token_decode(token: str) -> dict | None:
    try:
        user_data = jwt.decode(
            token=token,
            key=Config.JWT_SECRETKEY,
            algorithms=[Config.JWT_ALGORITHM]
        )
        return user_data
    except ExpiredSignatureError:
        logging.exception("Token expired")
        raise InvalidOrExpireToken()
    except JWTError:
        logging.exception("Invalid token")
        raise InvalidOrExpireToken()

    