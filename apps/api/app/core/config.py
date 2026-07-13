from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "sqlite:///./tameike.db"
    api_prefix: str = ""
    risk_model_version: str = "baseline-screening-v0.1"
    hazard_weight: float = 0.30
    vulnerability_weight: float = 0.25
    exposure_weight: float = 0.20
    anomaly_weight: float = 0.15
    uncertainty_weight: float = 0.10
    cors_allowed_origins: str = "http://localhost:3000"
    class Config:
        env_file = ".env"
settings = Settings()
