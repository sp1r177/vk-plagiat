from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database.database import get_db
from models.user import User
from schemas.auth import UserCreate, UserResponse, Token
from services.vk_auth import VKAuthService
from services.jwt_service import JWTService
from config.settings import settings

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/vk-login", response_model=Token)
async def vk_login(code: str, db: Session = Depends(get_db)):
    """Аутентификация через VK"""
    try:
        vk_auth = VKAuthService()
        user_data = await vk_auth.get_user_data(code)
        
        # Проверяем, существует ли пользователь
        user = db.query(User).filter(User.vk_id == user_data["vk_id"]).first()
        
        if not user:
            # Создаем нового пользователя
            user = User(
                vk_id=user_data["vk_id"],
                username=user_data.get("username"),
                first_name=user_data.get("first_name"),
                last_name=user_data.get("last_name"),
                photo_url=user_data.get("photo_url")
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # Создаем JWT токен
        jwt_service = JWTService()
        access_token = jwt_service.create_access_token(data={"sub": str(user.id)})
        
        return {"access_token": access_token, "token_type": "bearer"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ошибка аутентификации через VK"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Получение информации о текущем пользователе"""
    jwt_service = JWTService()
    user_id = jwt_service.verify_token(token)
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    return user


@router.post("/logout")
async def logout():
    """Выход из системы"""
    return {"message": "Успешный выход из системы"} 