from sqlite3 import Time
from time import sleep
from urllib import response
from fastapi import HTTPException, Security
from fastapi.testclient import TestClient
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.security.api_key import APIKeyHeader

from ..main import app
from ..database import Base, get_db
from ..enums import Status
from ..services import AuthService

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread":False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

TEST_API_KEY = "ABCDXYZ123"

def override_validate_api_key(api_key_header: str = Security(APIKeyHeader(name='X-API-Key'))):
        if api_key_header == TEST_API_KEY:
            return api_key_header
        else:
            raise HTTPException(status_code=403, detail="Invalid API Key")

def override_get_db():
    try:
        db = TestSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[AuthService.validate_api_key] = override_validate_api_key

client = TestClient(app)

def test_add_software_details():
    data = {
        "name" : "test"
    }
    response = client.post("/software", json.dumps(data), headers = {"X-API-Key" : TEST_API_KEY})
    assert response.status_code == 201
    assert response.json()["status"] == Status.CREATED
    assert response.json()["name"] == data["name"]
    assert response.json()["version"] == "1.0.0"
    return response.json()["id"], data

def test_add_software_details_wrong_contract():
    data = {
        "names" : "test"
    }
    response = client.post("/software", json.dumps(data), headers = {"X-API-Key" : TEST_API_KEY})
    assert response.status_code == 422

def test_add_software_details_unauth():
    data = {
        "names" : "test"
    }
    response = client.post("/software", json.dumps(data), headers = {"X-API-Key" : "TEST_API_KEY"})
    assert response.status_code == 403

def test_get_all_software_details(key = TEST_API_KEY):
    response = client.get("/software", headers = {"X-API-Key" : key})
    assert response.status_code == 200

def test_get_software_details():
    id, data = test_add_software_details()
    response = client.get("/software/{}".format(id), headers = {"X-API-Key" : TEST_API_KEY})
    assert response.status_code == 200
    assert response.json()["id"] == id
    assert response.json()["status"] == Status.CREATED
    assert response.json()["name"] == data["name"]
    assert response.json()["version"] == "1.0.0"

def test_delete_software_details():
    id, data = test_add_software_details()
    response = client.delete("/software/{}".format(id), headers = {"X-API-Key" : TEST_API_KEY})
    assert response.status_code == 200
    assert response.json()["id"] == id
    assert response.json()["status"] == Status.CREATED
    assert response.json()["name"] == data["name"]
    assert response.json()["version"] == "1.0.0"
    response = client.get("/software/{}".format(id), headers = {"X-API-Key" : TEST_API_KEY})
    assert response.status_code == 404

def test_update_software_version_invalid_version():
    id, data = test_add_software_details()
    updated_version = {
        "version" : "0.0.0"
    }
    response = client.patch("/software/{}/version".format(id), json.dumps(updated_version), headers = {"X-API-Key" : TEST_API_KEY})
    assert response.status_code == 409

def test_update_software_version():
    id, data = test_add_software_details()
    updated_version = {
        "version" : "2.0.0"
    }
    response = client.patch("/software/{}/version".format(id), json.dumps(updated_version), headers = {"X-API-Key" : TEST_API_KEY})
    assert response.status_code == 200
    response = client.get("/software/{}".format(id), headers = {"X-API-Key" : TEST_API_KEY})
    assert response.status_code == 200
    assert response.json()["id"] == id
    assert response.json()["status"] == Status.CREATED
    assert response.json()["name"] == data["name"]
    assert response.json()["version"] == "2.0.0"

def test_update_software_version_bad_format():
    id, data = test_add_software_details()
    updated_version = {
        "version" : "2.0."
    }
    response = client.patch("/software/{}/version".format(id), json.dumps(updated_version), headers = {"X-API-Key" : TEST_API_KEY})
    assert response.status_code == 422

def test_activate_software_invalid_id():
    id = 0
    response = client.patch("/software/{}/activate".format(id), headers = {"X-API-Key" : TEST_API_KEY})
    assert response.status_code == 404

def test_download_software_invalid_id():
    id = 0
    response = client.patch("/software/{}/download".format(id), headers = {"X-API-Key" : TEST_API_KEY})
    assert response.status_code == 404

def test_activate_software():
    id, data = test_add_software_details()
    response = client.patch("/software/{}/activate".format(id), headers = {"X-API-Key" : TEST_API_KEY})
    assert response.status_code == 200
    sleep(15)
    response = client.get("/software/{}".format(id), headers = {"X-API-Key" : TEST_API_KEY})
    assert response.status_code == 200
    assert response.json()["id"] == id
    assert response.json()["status"] == Status.ACTIVE
    assert response.json()["name"] == data["name"]
    assert response.json()["version"] == "1.0.0"

def test_download_software():
    id, data = test_add_software_details()
    response = client.patch("/software/{}/download".format(id), headers = {"X-API-Key" : TEST_API_KEY})
    assert response.status_code == 200
    sleep(15)
    response = client.get("/software/{}".format(id), headers = {"X-API-Key" : TEST_API_KEY})
    assert response.status_code == 200
    assert response.json()["id"] == id
    assert response.json()["status"] == Status.DOWNLOADED
    assert response.json()["name"] == data["name"]
    assert response.json()["version"] == "1.0.0"

def test_create_api_key():
    app.dependency_overrides = {}
    app.dependency_overrides[get_db] = override_get_db

    response = client.get("/create-api-key")
    assert response.status_code == 200
    key = response.json()["key"]
    test_get_all_software_details(key=key)
    app.dependency_overrides[AuthService.validate_api_key] = override_validate_api_key
    return key
    
def test_get_all_api_keys():
    response = client.get("/get-all-api-keys")
    assert response.status_code == 200

def test_update_api_key():
    key = test_create_api_key()
    response = client.patch("/change-api-key-status", json.dumps({ "key" : key, "activated" : False}))
    assert response.status_code == 200
    assert response.json()["activated"] == False
    assert response.json()["key"] == key

    app.dependency_overrides = {}
    app.dependency_overrides[get_db] = override_get_db

    response = client.get("/software", headers = {"X-API-Key" : key})
    assert response.status_code == 403

    app.dependency_overrides[AuthService.validate_api_key] = override_validate_api_key

def test_delete_api_key():
    key = test_create_api_key()
    response = client.delete("/delete-api-key", data = json.dumps({ "key" : key}))
    assert response.status_code == 200

    response = client.get("/get-all-api-keys")
    for res_key in response.json():
        if res_key["key"] == key:
            assert False
    assert True



