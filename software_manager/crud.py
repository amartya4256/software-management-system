from xmlrpc.client import Boolean
from importlib_metadata import version
from sqlalchemy.orm import Session

from .enums import Status

from . import models, schemas


def get_software(db: Session, id: int):
    return db.query(models.Software).filter(models.Software.id == id).first()


def get_softwares(db: Session):
    return db.query(models.Software).all()


def add_software(db: Session, software: schemas.SoftwareCreate):
    db_software = models.Software(name=software.name, version = "1.0.0", status = Status.CREATED)
    db.add(db_software)
    db.commit()
    db.refresh(db_software)
    return db_software

def delete_software(db: Session, id: int):
    software = get_software(db, id)
    db.delete(software)
    db.commit()
    return software

def update_software(db: Session, id: int, software: schemas.Software):
    db_software = get_software(db, id)
    if software.name:
        db_software.name = software.name
    if software.version:
        db_software.version = software.version
    if software.status:
        db_software.status = software.status
    db.commit()
    return db_software

def create_api_key(db: Session, key: schemas.ApiKey):
    api_key = models.ApiKey(key= key.key, activated=True)
    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    return api_key

def get_api_key(db: Session, key: schemas.ApiKey):
    return db.query(models.ApiKey).filter(models.ApiKey.key == key.key).first()

def get_api_keys(db: Session):
    return db.query(models.ApiKey).all()

def get_activated_api_key(db: Session, key: schemas.ApiKey):
    return db.query(models.ApiKey).filter(models.ApiKey.key == key.key, models.ApiKey.activated == True).first()

def update_api_key(db: Session, activated: Boolean, api_key: schemas.ApiKey):
    api_key = get_api_key(db, api_key)
    api_key.activated = activated
    db.commit()
    return api_key

def delete_api_key(db: Session, api_key: schemas.ApiKey):
    api_key = get_api_key(db, api_key)
    db.delete(api_key)
    db.commit()
    return api_key

