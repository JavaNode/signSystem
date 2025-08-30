import os
import shutil
from typing import Optional
from fastapi import UploadFile
import uuid
from PIL import Image
import io

# 允许的图片格式
ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
# 最大文件大小 (2MB)
MAX_FILE_SIZE = 2 * 1024 * 1024

def get_file_extension(filename: str) -> str:
    """获取文件扩展名"""
    return os.path.splitext(filename)[1].lower()

def is_allowed_image(filename: str) -> bool:
    """检查是否为允许的图片格式"""
    return get_file_extension(filename) in ALLOWED_IMAGE_EXTENSIONS

def generate_unique_filename(original_filename: str) -> str:
    """生成唯一的文件名"""
    ext = get_file_extension(original_filename)
    unique_id = str(uuid.uuid4())
    return f"{unique_id}{ext}"

async def save_uploaded_file(file: UploadFile, upload_dir: str = "data/photos") -> str:
    """
    保存上传的文件
    
    Args:
        file: 上传的文件
        upload_dir: 上传目录
    
    Returns:
        保存的文件路径
    
    Raises:
        ValueError: 文件格式不支持或文件过大
    """
    # 检查文件格式
    if not is_allowed_image(file.filename):
        raise ValueError(f"不支持的文件格式。支持的格式: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}")
    
    # 读取文件内容
    content = await file.read()
    
    # 检查文件大小
    if len(content) > MAX_FILE_SIZE:
        raise ValueError(f"文件过大。最大允许大小: {MAX_FILE_SIZE // (1024*1024)}MB")
    
    # 确保上传目录存在
    os.makedirs(upload_dir, exist_ok=True)
    
    # 生成唯一文件名
    filename = generate_unique_filename(file.filename)
    file_path = os.path.join(upload_dir, filename)
    
    # 保存文件
    with open(file_path, "wb") as f:
        f.write(content)
    
    return file_path

def save_participant_photo(file: UploadFile, participant_id: int, 
                          upload_dir: str = "data/photos") -> str:
    """
    保存参赛者照片
    
    Args:
        file: 上传的文件
        participant_id: 参赛者ID
        upload_dir: 上传目录
    
    Returns:
        保存的文件路径
    """
    # 检查文件格式
    if not is_allowed_image(file.filename):
        raise ValueError(f"不支持的文件格式。支持的格式: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}")
    
    # 确保上传目录存在
    os.makedirs(upload_dir, exist_ok=True)
    
    # 使用参赛者ID作为文件名
    ext = get_file_extension(file.filename)
    filename = f"participant_{participant_id}{ext}"
    file_path = os.path.join(upload_dir, filename)
    
    # 如果已存在同名文件，先删除
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # 保存文件
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    return file_path

def resize_image(image_path: str, max_width: int = 400, max_height: int = 600) -> str:
    """
    调整图片尺寸
    
    Args:
        image_path: 图片路径
        max_width: 最大宽度
        max_height: 最大高度
    
    Returns:
        处理后的图片路径
    """
    try:
        with Image.open(image_path) as img:
            # 计算新尺寸
            width, height = img.size
            ratio = min(max_width / width, max_height / height)
            
            if ratio < 1:
                new_width = int(width * ratio)
                new_height = int(height * ratio)
                
                # 调整尺寸
                img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # 保存调整后的图片
                img_resized.save(image_path, optimize=True, quality=85)
        
        return image_path
    except Exception as e:
        print(f"调整图片尺寸失败: {e}")
        return image_path

def delete_file(file_path: str) -> bool:
    """
    删除文件
    
    Args:
        file_path: 文件路径
    
    Returns:
        删除是否成功
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        print(f"删除文件失败: {e}")
        return False

def get_file_url(file_path: str, base_url: str = "/static") -> str:
    """
    获取文件的URL
    
    Args:
        file_path: 文件路径
        base_url: 基础URL
    
    Returns:
        文件URL
    """
    if not file_path:
        return ""
    
    # 将Windows路径分隔符转换为URL分隔符
    url_path = file_path.replace("\\", "/")
    
    # 移除data/前缀（如果存在）
    if url_path.startswith("data/"):
        url_path = url_path[5:]
    
    return f"{base_url}/{url_path}"

def create_directory(dir_path: str) -> bool:
    """
    创建目录
    
    Args:
        dir_path: 目录路径
    
    Returns:
        创建是否成功
    """
    try:
        os.makedirs(dir_path, exist_ok=True)
        return True
    except Exception as e:
        print(f"创建目录失败: {e}")
        return False

def get_file_size(file_path: str) -> int:
    """
    获取文件大小
    
    Args:
        file_path: 文件路径
    
    Returns:
        文件大小（字节）
    """
    try:
        return os.path.getsize(file_path)
    except Exception:
        return 0

def validate_image_file(file_content: bytes) -> bool:
    """
    验证图片文件
    
    Args:
        file_content: 文件内容
    
    Returns:
        是否为有效图片
    """
    try:
        with Image.open(io.BytesIO(file_content)) as img:
            img.verify()
        return True
    except Exception:
        return False