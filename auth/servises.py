from  sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import select
from schema import SignupModel
from database.models import User
from utils import generate_password_hash


class  AuthServices:
    
    @staticmethod
    async def get_user_by_email(email:str,session:AsyncSession):
       """Fetch a user by email (or return None if not found)."""
       statement =  select(User).where(User.email==email)
       
       result = await session.execute(statement)
       
       user = result.scalars().first()
       return user
   
    
    async def user_exists(self,email:str,session:AsyncSession):
       """Check if a user with this email exists.""" 
       get_user=  await  self.get_user_byemail(email,session)
       return  get_user is not None
        
   
       
    
    async def create_user(self,user_data:SignupModel,session:AsyncSession):
        """Create a new user with hashed password."""
        user_data_dict = user_data.model_dump()
        username = user_data_dict['email'].split('@')[0]
        
        
        new_user = User(**user_data_dict,username=username)
        new_user.password = generate_password_hash(user_data_dict['password'])
        
        session.add(new_user)
        await  session.commit()
        
        return new_user
        