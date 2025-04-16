from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from .config import settings
import bcrypt

# PostgreSQL Connection
SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def set_password(self, password: str):
        salt = bcrypt.gensalt()
        self.hashed_password = bcrypt.hashpw(password.encode(), salt)
    
    def verify_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode(), self.hashed_password.encode())

class System(Base):
    __tablename__ = "systems"
    
    id = Column(Integer, primary_key=True, index=True)
    location = Column(String, index=True)
    status = Column(String)  # online, offline, maintenance
    last_update = Column(DateTime, default=datetime.utcnow)
    solar_capacity = Column(Float)
    wind_capacity = Column(Float)
    battery_capacity = Column(Float)
    is_active = Column(Boolean, default=True)
    
    # Additional metrics
    power_quality = relationship("PowerQuality", back_populates="system")
    grid_stability = relationship("GridStability", back_populates="system")
    load_balancing = relationship("LoadBalancing", back_populates="system")

class PowerQuality(Base):
    __tablename__ = "power_quality"
    
    id = Column(Integer, primary_key=True, index=True)
    system_id = Column(Integer, ForeignKey("systems.id"))
    voltage = Column(Float)  # in volts
    frequency = Column(Float)  # in Hz
    harmonic_distortion = Column(Float)  # in percentage
    power_factor = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    system = relationship("System", back_populates="power_quality")

class GridStability(Base):
    __tablename__ = "grid_stability"
    
    id = Column(Integer, primary_key=True, index=True)
    system_id = Column(Integer, ForeignKey("systems.id"))
    voltage_stability = Column(Float)  # in percentage
    frequency_stability = Column(Float)  # in percentage
    phase_balance = Column(Float)  # in percentage
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    system = relationship("System", back_populates="grid_stability")

class LoadBalancing(Base):
    __tablename__ = "load_balancing"
    
    id = Column(Integer, primary_key=True, index=True)
    system_id = Column(Integer, ForeignKey("systems.id"))
    load_imbalance = Column(Float)  # in percentage
    generation_imbalance = Column(Float)  # in percentage
    battery_utilization = Column(Float)  # in percentage
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    system = relationship("System", back_populates="load_balancing")

# Create tables
def init_db():
    Base.metadata.create_all(bind=engine)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 