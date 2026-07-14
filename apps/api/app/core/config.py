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
    db_pool_size: int = 3
    db_max_overflow: int = 2
    db_pool_timeout: int = 30
    db_pool_recycle: int = 1800
    class Config:
        env_file = ".env"
settings = Settings()
