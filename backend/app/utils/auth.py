from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import os

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT配置
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def hash_password(password: str) -> str:
    """
    对密码进行哈希加密
    
    Args:
        password: 原始密码
    
    Returns:
        加密后的密码哈希
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    
    Args:
        plain_password: 原始密码
        hashed_password: 哈希密码
    
    Returns:
        验证结果
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建访问令牌
    
    Args:
        data: 要编码的数据
        expires_delta: 过期时间增量
    
    Returns:
        JWT令牌
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """
    验证JWT令牌
    
    Args:
        token: JWT令牌
    
    Returns:
        解码后的数据，如果验证失败返回None
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def create_judge_token(judge_id: int, username: str) -> str:
    """
    为评委创建访问令牌
    
    Args:
        judge_id: 评委ID
        username: 用户名
    
    Returns:
        JWT令牌
    """
    data = {
        "sub": str(judge_id),
        "username": username,
        "type": "judge"
    }
    return create_access_token(data)

def create_admin_token(admin_id: str = "admin") -> str:
    """
    为管理员创建访问令牌
    
    Args:
        admin_id: 管理员ID
    
    Returns:
        JWT令牌
    """
    data = {
        "sub": admin_id,
        "type": "admin"
    }
    return create_access_token(data)

def get_current_user_from_token(token: str) -> Optional[dict]:
    """
    从令牌中获取当前用户信息
    
    Args:
        token: JWT令牌
    
    Returns:
        用户信息字典
    """
    payload = verify_token(token)
    if payload is None:
        return None
    
    user_id = payload.get("sub")
    user_type = payload.get("type")
    username = payload.get("username")
    
    if user_id is None:
        return None
    
    return {
        "id": user_id,
        "type": user_type,
        "username": username
    }

def generate_default_password(name: str, phone_last4: str = "") -> str:
    """
    生成默认密码
    
    Args:
        name: 姓名
        phone_last4: 手机后四位
    
    Returns:
        默认密码
    """
    if phone_last4:
        return f"{name}{phone_last4}"
    else:
        return f"{name}123456"