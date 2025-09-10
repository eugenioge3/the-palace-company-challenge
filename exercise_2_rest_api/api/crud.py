from sqlalchemy.orm import Session, joinedload
from . import models, schemas

# === Funciones de Lectura (GET) ===
def get_contact(db: Session, contact_id: int):
    return db.query(models.Contact).options(joinedload(models.Contact.departments)).filter(models.Contact.id == contact_id).first()

def get_contacts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Contact).options(joinedload(models.Contact.departments)).offset(skip).limit(limit).all()

# === Funciones de Creación/Actualización (POST/PUT) ===
def create_contact(db: Session, contact: schemas.ContactCreate):
    # 1. Crear el objeto Contacto sin los departamentos
    db_contact = models.Contact(
        email=contact.email, first_name=contact.first_name, last_name=contact.last_name,
        company_name=contact.company_name, address=contact.address, city=contact.city,
        state=contact.state, zip=contact.zip, phone1=contact.phone1, phone2=contact.phone2
    )

    # 2. Manejar los departamentos
    for dept_name in contact.departments:
        # Buscar si el departamento ya existe
        db_dept = db.query(models.Department).filter(models.Department.name == dept_name).first()
        if not db_dept:
            # Si no existe, lo creamos
            db_dept = models.Department(name=dept_name)
            db.add(db_dept)
        # Añadimos el departamento a la lista del contacto
        db_contact.departments.append(db_dept)

    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

def update_contact(db: Session, contact_id: int, contact_update: schemas.ContactCreate):
    db_contact = get_contact(db, contact_id)
    if not db_contact:
        return None

    # Actualizar campos simples
    for var, value in vars(contact_update).items():
        if var != 'departments':
            setattr(db_contact, var, value)

    # Actualizar departamentos
    db_contact.departments.clear() # Limpiamos los departamentos existentes
    for dept_name in contact_update.departments:
        db_dept = db.query(models.Department).filter(models.Department.name == dept_name).first()
        if not db_dept:
            db_dept = models.Department(name=dept_name)
            db.add(db_dept)
        db_contact.departments.append(db_dept)
    
    db.commit()
    db.refresh(db_contact)
    return db_contact