from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    google_sheets_credentials_path: str = "credentials.json"
    pilot_roster_sheet_id: str
    drone_fleet_sheet_id: str
    mission_sheet_id: str

    google_api_key: str

    environment: str = "development"

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
