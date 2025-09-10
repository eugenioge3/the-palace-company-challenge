from sqlalchemy import Column, Integer, String, ForeignKey, Table, CheckConstraint
from sqlalchemy.orm import relationship
from .database import Base

# Tabla de Unión para la relación Muchos-a-Muchos
contact_department_association = Table(
    'contact_department_association', Base.metadata,
    Column('contact_id', Integer, ForeignKey('contacts.id'), primary_key=True),
    Column('department_id', Integer, ForeignKey('departments.id'), primary_key=True)
)

class Department(Base):
    __tablename__ = "departments"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    # La relación ahora usa la tabla de unión y apunta a la lista de contactos
    contacts = relationship(
        "Contact",
        secondary=contact_department_association,
        back_populates="departments"
    )

class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    company_name = Column(String)
    email = Column(String, unique=True, nullable=False, index=True)
    address = Column(String)
    city = Column(String)
    state = Column(String(2), nullable=False)
    zip = Column(String(10))
    phone1 = Column(String(20))
    phone2 = Column(String(20))
    # La relación ahora usa la tabla de unión y apunta a la lista de departamentos
    departments = relationship(
        "Department",
        secondary=contact_department_association,
        back_populates="contacts"
    )
    # La validación de 'state' - solo 2 letras
    __table_args__ = (CheckConstraint("state ~ '^[A-Z]{2}$'", name='state_check'),)