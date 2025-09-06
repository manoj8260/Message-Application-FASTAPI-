from pydantic import BaseModel,Field,EmailStr


class SignupModel(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    email : EmailStr   = Field(...,min_length=5 ,max_length=50)
    password :str  = Field(...,min_length=8,max_length=128) 

class SignInModel(BaseModel):
    email : EmailStr   = Field(...,min_length=5 ,max_length=50)
    password :str  = Field(...,min_length=8,max_length=128) 
    