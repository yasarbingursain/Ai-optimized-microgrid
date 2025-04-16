from sqlalchemy import create_engine
from app.db import Base, User, System, PowerQuality, GridStability, LoadBalancing
from app.config import settings
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def init_db():
    # Create database engine
    engine = create_engine(settings.DATABASE_URL)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    print("Database tables created successfully!")

def create_admin_user():
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=create_engine(settings.DATABASE_URL))
    session = Session()
    
    # Check if admin user already exists
    admin = session.query(User).filter(User.username == "admin").first()
    if not admin:
        # Create admin user
        admin = User(
            username="admin",
            email="admin@example.com",
            hashed_password=pwd_context.hash("admin123"),
            is_active=True,
            is_admin=True
        )
        session.add(admin)
        session.commit()
        print("Admin user created successfully!")
    else:
        print("Admin user already exists!")
    
    session.close()

if __name__ == "__main__":
    init_db()
    create_admin_user() 