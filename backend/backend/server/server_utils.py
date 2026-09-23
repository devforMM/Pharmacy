from passlib.context import CryptContext
from jose import jwt
from fastapi import Request
from datetime import datetime,timedelta,timezone
from fastapi import Depends,HTTPException
from sqlalchemy.orm import Session
from  models.DataBase import Supplier,Pharmacist
from models.Bridge import get_session

SECRET_KEY="secret_key"
CRYPT_SCHEMES="bcrypt"
ALGO="HS256"


context=CryptContext(schemes=[CRYPT_SCHEMES],deprecated="auto")
def hash_password(password):
    return context.hash(password)
def verify_password(password,hashed_password):
    return context.verify(password,hashed_password)


def expire_time():
    return datetime.now(timezone.utc)+timedelta(minutes=300)



def create_token(data:dict):
    try:
        to_encode=data.copy()
        to_encode.update({
            "exp":expire_time()
        })
        return jwt.encode(to_encode,key=SECRET_KEY,algorithm=ALGO)
    except Exception:
     raise(HTTPException(status_code=401,detail="erreur lors de la creation du token"))
        

def get_current_Supplier(request:Request,db:Session=Depends(get_session)):
    try:
        access_token=request.cookies.get("access_token")
        if access_token:
            user_data=jwt.decode(access_token,key=SECRET_KEY,algorithms=ALGO)
            if user_data:
                user=db.query(Supplier).filter(Supplier.email==user_data["email"]).first()
                if user:
                    return user
                else:
                    raise HTTPException(status_code=401,
                                        detail="invalid token")

        else: 
            raise HTTPException(status_code=404,detail="Token not found")
            
    except Exception as e:
        raise HTTPException(status_code=400,detail=f"server error : {e}")



def get_current_Pharmacist(request:Request,db:Session=Depends(get_session)):
    try:
        access_token=request.cookies.get("access_token")
        if access_token:
            user_data=jwt.decode(access_token,key=SECRET_KEY,algorithms=ALGO)
            if user_data:
                user=db.query(Pharmacist).filter(Pharmacist.email==user_data["email"]).first()
                if user:
                    return user
                else:
                    raise HTTPException(status_code=401,
                                        detail="invalid token")

        else: 
            raise HTTPException(status_code=404,detail="Token not found")
            
    except Exception as e:
        raise HTTPException(status_code=400,detail=f"server error : {e}")

