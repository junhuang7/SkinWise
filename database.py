import os
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
import logging

# Environment Configuration
DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///patients.db')

# Logging Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Engine and Session Setup
engine = create_engine(DATABASE_URI, connect_args={"check_same_thread": False}, echo=True, pool_size=20, max_overflow=0)
db_session = scoped_session(sessionmaker(bind=engine))

# Declarative Base
Base = declarative_base()

class Patient(Base):
    __tablename__ = 'patients'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    age = Column(Integer)
    diagnosis = Column(String(250))
    treatment_plan = Column(Text)
    medication = Column(Text)
    follow_up_schedule = Column(String(250))
    comments = Column(Text)

# Database Initialization
def init_db():
    Base.metadata.create_all(engine)

# CRUD Operations with Error Handling
def insert_patient(**kwargs):
    try:
        new_patient = Patient(**kwargs)
        db_session.add(new_patient)
        db_session.commit()
        logger.info("New patient added.")
    except Exception as e:
        db_session.rollback()
        logger.error(f"Error adding patient: {e}")
        raise

def get_all_patients():
    try:
        return Patient.query.all()
    except Exception as e:
        logger.error(f"Error fetching patients: {e}")
        raise

# Additional CRUD operations (update, delete) should follow similar structure

# Session Cleanup
def cleanup():
    db_session.remove()

# Make sure to call init_db() at the appropriate place in your application
if __name__ == "__main__":
    init_db()
