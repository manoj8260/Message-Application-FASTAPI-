from fastapi import Depends,status
from fastapi.security import HTTPBearer ,HTTPAuthorizationCredentials
from fastapi.requests import Request
from utils import token_decode
from fastapi.exceptions import HTTPException
from database.redis import is_token_blacklisted
from servises import AuthServices
from database.connection import get_session
from sqlalchemy.ext.asyncio.session import AsyncSession
from errors import InvalidOrExpireToken

user_servises = AuthServices()





class TokenBearer(HTTPBearer):
    def __init__(self,  auto_error :bool = True):
        super().__init__(auto_error=auto_error)
    
    async def __call__(self, request:Request):
        credentials : HTTPAuthorizationCredentials=  await super().__call__(request)  
        
        token = credentials.credentials
        token_data = token_decode(token)
        if not token_data :
            raise InvalidOrExpireToken()
        print(token_data)    
        jti = token_data['jti']  
        if await is_token_blacklisted(jti) :
             raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has been revoked",
                    headers={"WWW-Authenticate": "Bearer"}
                )     
            
        self.verify_token_type(token_data)
        return token_data
    def verify_token_type(self,token_data:dict):
        raise NotImplementedError('please overide the method in child class')

class AccessTokenBearer(TokenBearer):
    def verify_token_type(self,token_data:dict):
        if token_data  and token_data['refresh']:
            raise HTTPException(
                detail={
                    'message' : 'Access toekn is Requird',
                    'Hint' : 'You Pass Refresh token'
                },
                status_code=status.HTTP_400_BAD_REQUEST
            )
class RefreshTokenBearer(TokenBearer):
    def verify_token_type(self,token_data:dict):
        if token_data  and not  token_data['refresh']:
            raise HTTPException(
                detail={
                    'message' : 'Refresh toekn is Requird',
                    'Hint' : 'You Pass Access token'
                },status_code=status.HTTP_400_BAD_REQUEST
            )
  
async  def get_current_user(token_data : dict  = Depends(AccessTokenBearer()) , session :AsyncSession =Depends(get_session) )  :
    email = token_data['user']['email']
    user =  await user_servises.get_user_by_email(email,session)  
    # print(user)
    if user : 
       return user
    else :
        raise HTTPException(
                detail={
                    'message' : 'User not found',
                },status_code=status.HTTP_400_BAD_REQUEST
            )  