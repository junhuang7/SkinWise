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
def insert_period_data(form_data):
    try:
        # Assuming form_data is a dictionary that contains all necessary patient fields
        new_patient = Patient(
            name=form_data.get("Name"),
            age=form_data.get("Age"),
            diagnosis=form_data.get("Diagnosis"),
            treatment_plan=form_data.get("Treatment Plan"),
            medication=form_data.get("Medication"),
            follow_up_schedule=form_data.get("Follow-up Schedule"),
            comments=form_data.get("Comment")
        )
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

def fetch_all_periods():
    try:
        # Assuming 'follow_up_schedule' is stored in a way that allows this query to work
        # Modify the query as necessary to fit your actual data storage format
        periods = db_session.query(Patient.follow_up_schedule).distinct().all()
        # Flatten the list of tuples into a list of strings
        periods = [period[0] for period in periods if period[0] is not None]
        return periods
    except Exception as e:
        logger.error(f"Error fetching periods: {e}")
        raise


# Additional CRUD operations (update, delete) should follow similar structure

# Session Cleanup
def cleanup():
    db_session.remove()

# Make sure to call init_db() at the appropriate place in your application
if __name__ == "__main__":
    init_db()
