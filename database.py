from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, scoped_session

# Define the database URI
DATABASE_URI = 'sqlite:///patients.db'

# Create an engine
engine = create_engine(DATABASE_URI, connect_args={"check_same_thread": False})

# Create a scoped session
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

# Base class for declarative models
Base = declarative_base()
Base.query = db_session.query_property()

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

def init_db():
    Base.metadata.create_all(bind=engine)

def insert_patient(name, age, diagnosis, treatment_plan, medication, follow_up_schedule, comments):
    """Insert a new patient into the database."""
    new_patient = Patient(
        name=name,
        age=age,
        diagnosis=diagnosis,
        treatment_plan=treatment_plan,
        medication=medication,
        follow_up_schedule=follow_up_schedule,
        comments=comments
    )
    db_session.add(new_patient)
    db_session.commit()

def get_all_patients():
    """Return all patients."""
    return Patient.query.all()

def get_patient_by_id(patient_id):
    """Return a patient by their ID."""
    return Patient.query.get(patient_id)

def update_patient(patient_id, **kwargs):
    """Update patient information."""
    patient = get_patient_by_id(patient_id)
    for key, value in kwargs.items():
        setattr(patient, key, value)
    db_session.commit()

def delete_patient(patient_id):
    """Delete a patient from the database."""
    patient = get_patient_by_id(patient_id)
    db_session.delete(patient)
    db_session.commit()

# Make sure to call init_db() at the right place in your actual app to initialize the DB
# For example, call init_db() when your application starts

# Don't forget to close the session after the app stops or at the end of a request
# For example, in Streamlit you might use st.on_session_end(db_session.remove)
