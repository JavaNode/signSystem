from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# 数据库文件路径
DATABASE_URL = "sqlite:///./data/database.db"

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False},
    echo=False  # 设置为True可以看到SQL语句
)

# 创建SessionLocal类
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建Base类
Base = declarative_base()

# 依赖项：获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 创建所有表
def create_tables():
    Base.metadata.create_all(bind=engine)

# 初始化数据库
def init_database():
    """初始化数据库，创建必要的目录和表"""
    # 确保data目录存在
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/photos", exist_ok=True)
    os.makedirs("data/exports", exist_ok=True)
    
    # 创建所有表
    create_tables()
    print("数据库初始化完成！")