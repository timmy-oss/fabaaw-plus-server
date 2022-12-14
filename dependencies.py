from fastapi.security import  OAuth2PasswordBearer
from fastapi import Depends, HTTPException, Path
from jose import jwt, JWTError
from config import app_settings as settings
from db import db
from models.users import TokenData
from models.users import UserModel



oauth2_scheme =  OAuth2PasswordBearer(tokenUrl= '/api/v1/login')


async def get_user_by_share_id( share_id : str =  Path(min_length= 4)):
    print(share_id)
    user = await db.users.find_one({ 'share_id' : share_id})
    if user is None:
        raise HTTPException(detail= "Share ID does not exist!", status_code= 404)

    if user['disabled']:
         raise HTTPException(detail= "Share ID does not exist!", status_code= 404)

    return user

async def get_authenticated_user( token : str  = Depends(oauth2_scheme)):
    
    credentials_exception = HTTPException(
        status_code= 401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ settings.hash_algorithm])
        user_id  : str = payload.get('sub')
        
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id = user_id)
        
    except JWTError:
        raise credentials_exception

    user = await db.users.find_one({ 'user_id' : str(token_data.user_id) })

    if user is None:
        raise credentials_exception

    return UserModel(**user)