import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app, get_db
from app.database import Base

# --- Configuración de la Base de Datos de Prueba ---
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Fixtures de Pytest ---

@pytest.fixture(scope="function")
def db_session():
    """
    Fixture para crear una base de datos limpia para cada prueba.
    """
    # Crea todas las tablas antes de que se ejecute la prueba
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Destruye todas las tablas después de que la prueba termine
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """
    Fixture para crear un cliente de API que usa la base de datos de prueba.
    """
    # Función para sobreescribir la dependencia get_db
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    # Aplicamos la sobreescritura
    app.dependency_overrides[get_db] = override_get_db
    
    # Creamos y devolvemos el cliente de prueba
    yield TestClient(app)

    # Limpiamos la sobreescritura después de la prueba
    app.dependency_overrides.clear()