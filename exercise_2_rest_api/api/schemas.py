from pydantic import BaseModel, EmailStr, constr
from typing import Optional, List

# Schema para la respuesta del Departamento
class Department(BaseModel):
    id: int
    name: str
    class Config:
        from_attributes = True # Renombrado de orm_mode en Pydantic V2

# Schema base para Contacto
class ContactBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    company_name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    # Usamos constr para validar el formato de 'state' a nivel de API
    state: constr(strip_whitespace=True, to_upper=True, min_length=2, max_length=2, pattern=r'^[A-Z]{2}$')
    zip: Optional[str] = None
    phone1: Optional[str] = None
    phone2: Optional[str] = None

# Schema para crear un Contacto (puede recibir una lista de departamentos)
class ContactCreate(ContactBase):
    # El departamento ahora es una lista de strings
    departments: List[str] = []

# Schema para la respuesta de la API
class Contact(ContactBase):
    id: int
    # La respuesta incluye una lista de objetos Department
    departments: List[Department] = []
    class Config:
        from_attributes = True