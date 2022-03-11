from fastapi import Depends, HTTPException, Security
import threading, string, random
from sqlalchemy.orm import Session
from fastapi.security.api_key import APIKeyHeader

from . import config, crud, schemas
from .database import get_db

class BackgroundService():
    def update_status(db : Session, id : int, software : schemas.Software):
        timer = threading.Timer(config.UPDATE_TIME, crud.update_software, [db, id, software])
        timer.start()
        # print("Running Update")


class VersionService():
    def is_version_valid(curr_version : str, new_version : str):
        try:
            curr_version = curr_version.split(".")
            new_version = new_version.split(".")
            for index in range(3):
                curr_version[index] = int(curr_version[index])
                new_version[index] = int(new_version[index])
                
            if (curr_version[0] < new_version[0]) \
                or (curr_version[0] == new_version[0] \
                    and curr_version[1] < new_version[1]) \
                or (curr_version[0] == new_version[0] \
                    and curr_version[1] == new_version[1] \
                    and curr_version[2] < new_version[2]):
                return True
            else:
                return False
        except Exception as err:
            print(err)
            raise HTTPException(status_code=422, detail="Invalid Version Format")

class AuthService():
    def get_api_key(db: Session):
        api_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(config.API_KEY_SIZE))
        return crud.create_api_key(db, schemas.ApiKey(key=api_key))

    def authenticate(db: Session, api_key: str):
        if crud.get_activated_api_key(db, schemas.ApiKey(key=api_key)) is not None:
            return True
        else:
            return False

    def validate_api_key(db: Session = Depends(get_db), api_key_header: str = Security(APIKeyHeader(name='X-API-Key'))):
        if AuthService.authenticate(db, api_key_header):
            return api_key_header
        else:
            raise HTTPException(status_code=403, detail="Invalid API Key")
