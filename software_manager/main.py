from typing import List
from urllib import response

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from software_manager import services

from .enums import Status

from . import crud, models, schemas
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/software", response_model= List[schemas.Software])
async def get_all_software_details(db: Session = Depends(get_db), api_key: str = Depends(services.AuthService.validate_api_key)):
    softwares = crud.get_softwares(db)
    return softwares

@app.get("/software/{id}", response_model= schemas.Software)
async def get_software_details(id: int, db: Session = Depends(get_db), api_key: str = Depends(services.AuthService.validate_api_key)):
    software = crud.get_software(db, id)
    if software is None:
        raise HTTPException(status_code=404, detail="Software with id = " + str(id) + " doesn't exist")
    return software

@app.post("/software", response_model= schemas.Software, status_code=201)
async def add_software_details(software: schemas.SoftwareCreate, db: Session = Depends(get_db), api_key: str = Depends(services.AuthService.validate_api_key)):
    if software.name is not None:
        db_software = crud.add_software(db, software)
    else:
        raise HTTPException(status_code=422, detail="Bad payload")
    return db_software

@app.delete("/software/{id}", response_model= schemas.Software)
async def delete_software_details(id : str, db: Session = Depends(get_db), api_key: str = Depends(services.AuthService.validate_api_key)):
    try:
        software = crud.delete_software(db, id)
        return software
    except:
        raise HTTPException(status_code=404, detail="Software with id = " + str(id) + " doesn't exist")


# @app.patch("/software/{id}", response_model= schemas.Software)
# async def update_software_details(id : str, software: schemas.Software, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
#     db_software = crud.get_software(db, id)
#     if db_software is None:
#         raise HTTPException(status_code=404, detail="Software with id = " + str(id) + " doesn't exist")
#     if(software.status != None and software.status != Status.CREATED and software.status != db_software.status):
#         background_tasks.add_task(services.BackgroundService.update_status, db, id, software)
#         return db_software
#     else:
#         updated_software = crud.update_software(db, id, software)
#         return updated_software

@app.patch("/software/{id}/activate", response_model= schemas.Software)
async def activate_software(id : str, background_tasks: BackgroundTasks, db: Session = Depends(get_db), api_key: str = Depends(services.AuthService.validate_api_key)):
    db_software = crud.get_software(db, id)
    if db_software is None:
        raise HTTPException(status_code=404, detail="Software with id = " + str(id) + " doesn't exist")
    if(db_software.status != Status.ACTIVE):
        background_tasks.add_task(services.BackgroundService.update_status, db, id, schemas.Software(status=Status.ACTIVE, name = db_software.name))
        return db_software
    else:
        return db_software

@app.patch("/software/{id}/download", response_model= schemas.Software)
async def download_software(id : str, background_tasks: BackgroundTasks, db: Session = Depends(get_db), api_key: str = Depends(services.AuthService.validate_api_key)):
    db_software = crud.get_software(db, id)
    if db_software is None:
        raise HTTPException(status_code=404, detail="Software with id = " + str(id) + " doesn't exist")
    if(db_software.status != Status.DOWNLOADED):
        background_tasks.add_task(services.BackgroundService.update_status, db, id, schemas.Software(status=Status.DOWNLOADED, name=db_software.name))
        return db_software
    else:
        return db_software

@app.patch("/software/{id}/version", response_model= schemas.Software)
async def update_software_version(id : str, software: schemas.Software, db: Session = Depends(get_db), api_key: str = Depends(services.AuthService.validate_api_key)):
    db_software = crud.get_software(db, id)
    if db_software is None:
        raise HTTPException(status_code=404, detail="Software with id = " + str(id) + " doesn't exist")
    # Call service to update version
    if(services.VersionService.is_version_valid(db_software.version, software.version)):
        software.name, software.status = None, Status.CREATED
        return crud.update_software(db, id, software)
    else:
        raise HTTPException(status_code=409, detail="Version Conflict")


@app.get("/create-api-key", response_model= schemas.ApiKey)
async def create_api_key(db: Session = Depends(get_db)):
    return services.AuthService.get_api_key(db=db)

@app.get("/get-all-api-keys", response_model= List[schemas.ApiKeyStatus])
async def get_all_api_keys(db: Session = Depends(get_db)):
    return crud.get_api_keys(db=db)

@app.patch("/change-api-key-status", response_model= schemas.ApiKeyStatus)
async def update_api_key(api_key: schemas.ApiKeyStatus, db: Session = Depends(get_db)):
    try:
        return crud.update_api_key(db, api_key.activated, schemas.ApiKey(key = api_key.key))
    except:
        raise HTTPException(status_code=404, detail="Api key doesn't exist")


@app.delete("/delete-api-key", response_model= schemas.ApiKey)
async def delete_api_key(api_key: schemas.ApiKey, db: Session = Depends(get_db)):
    try:
        return crud.delete_api_key(db, schemas.ApiKey(key = api_key.key))
    except:
        raise HTTPException(status_code=404, detail="Api key doesn't exist")
