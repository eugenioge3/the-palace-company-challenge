def test_create_contact(client):
    """Prueba la creación de un nuevo contacto."""
    response = client.post(
        "/contacts/",
        json={
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
            "state": "CA",
            "departments": ["Finances"]
        },
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["id"] is not None
    assert len(data["departments"]) == 1
    assert data["departments"][0]["name"] == "Finances"

def test_read_contacts(client):
    """Prueba leer una lista de contactos."""
    # creamos un contacto para que la lista no esté vacía
    client.post(
        "/contacts/",
        json={"first_name": "Jane", "last_name": "Doe", "email": "jane@example.com", "state": "NY"}
    )
    
    response = client.get("/contacts/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["email"] == "jane@example.com"

def test_create_duplicate_email_error(client):
    """Prueba que no se pueda crear un contacto con un email duplicado."""
    client.post(
        "/contacts/",
        json={"first_name": "John", "last_name": "Smith", "email": "john@example.com", "state": "TX"}
    )
    
    # Intentamos crear otro contacto con el mismo email
    response = client.post(
        "/contacts/",
        json={"first_name": "Johnathan", "last_name": "Smithy", "email": "john@example.com", "state": "FL"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

def test_read_contact_not_found(client):
    """Prueba que se devuelva un 404 para un contacto que no existe."""
    response = client.get("/contacts/999")
    assert response.status_code == 404

def test_update_contact(client):
    """Prueba la actualización de un contacto existente."""
    # Crear el contacto inicial
    response = client.post(
        "/contacts/",
        json={"first_name": "Update", "last_name": "Me", "email": "update@example.com", "state": "WA"}
    )
    contact_id = response.json()["id"]

    # Actualizar el contacto
    response_update = client.put(
        f"/contacts/{contact_id}",
        json={
            "first_name": "Updated",
            "last_name": "Successfully",
            "email": "update@example.com",
            "state": "WA",
            "departments": ["Sales", "Marketing"]
        }
    )
    assert response_update.status_code == 200
    data = response_update.json()
    assert data["first_name"] == "Updated"
    assert data["last_name"] == "Successfully"
    assert len(data["departments"]) == 2

def test_create_contact_invalid_state(client):
    """Prueba que la API rechace un 'state' con una longitud incorrecta."""
    response = client.post(
        "/contacts/",
        json={
            "first_name": "Invalid",
            "last_name": "State",
            "email": "badstate@example.com",
            "state": "CAL", # <-- DATO INVÁLIDO
            "departments": []
        },
    )
    assert response.status_code == 422
    data = response.json()
    assert "state" in data["detail"][0]["loc"]
    assert "String should have at most 2 characters" in data["detail"][0]["msg"]

def test_create_contact_invalid_email(client):
    """Prueba que la API rechace un email con formato incorrecto."""
    response = client.post(
        "/contacts/",
        json={
            "first_name": "Invalid",
            "last_name": "Email",
            "email": "bademail-example.com", # <-- DATO INVÁLIDO
            "state": "FL",
            "departments": []
        },
    )
    assert response.status_code == 422
    data = response.json()
    assert "email" in data["detail"][0]["loc"]
    assert "value is not a valid email address" in data["detail"][0]["msg"]

def test_create_contact_empty_first_name(client):
    """Prueba que la API rechace un 'first_name' vacío."""
    response = client.post(
        "/contacts/",
        json={
            "first_name": "", # <-- DATO INVÁLIDO
            "last_name": "User",
            "email": "empty@example.com",
            "state": "TX",
            "departments": []
        },
    )
    assert response.status_code == 422
    data = response.json()
    assert "first_name" in data["detail"][0]["loc"]
    assert "String should have at least 1 character" in data["detail"][0]["msg"]