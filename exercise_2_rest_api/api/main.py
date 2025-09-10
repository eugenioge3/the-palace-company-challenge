from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import event, DDL
from typing import List

from . import crud, models, schemas
from .database import SessionLocal, engine

# Esto crea las tablas en la base de datos la primera vez que arranca la API
models.Base.metadata.create_all(bind=engine)

# 1. Definimos el DDL (Data Definition Language) como un string.
#    Este es el comando SQL exacto para AÑADIR la constraint a una tabla existente.
add_constraint_ddl = DDL(
    "ALTER TABLE contacts ADD CONSTRAINT state_check_postgres CHECK (state ~ '^[A-Z]{2}$')"
)

# 2. Adjuntamos el evento para que se ejecute DESPUÉS de crear la tabla contacts,
#    y SOLAMENTE si el dialecto es postgresql.
event.listen(
    models.Contact.__table__,
    'after_create',
    add_constraint_ddl.execute_if(dialect='postgresql')
)


app = FastAPI(title="Tech Test API", description="API for managing contacts")

# Dependencia para obtener la sesión de la base de datos en cada request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/contacts/", response_model=schemas.Contact, status_code=status.HTTP_201_CREATED)
def create_contact(contact: schemas.ContactCreate, db: Session = Depends(get_db)):
    db_contact = db.query(models.Contact).filter(models.Contact.email == contact.email).first()
    if db_contact:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_contact(db=db, contact=contact)

@app.put("/contacts/{contact_id}", response_model=schemas.Contact)
def update_contact(contact_id: int, contact: schemas.ContactCreate, db: Session = Depends(get_db)):
    db_contact = crud.update_contact(db, contact_id=contact_id, contact_update=contact)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact

@app.get("/contacts/", response_model=List[schemas.Contact])
def read_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    contacts = crud.get_contacts(db, skip=skip, limit=limit)
    return contacts

@app.get("/contacts/{contact_id}", response_model=schemas.Contact)
def read_contact(contact_id: int, db: Session = Depends(get_db)):
    db_contact = crud.get_contact(db, contact_id=contact_id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact
