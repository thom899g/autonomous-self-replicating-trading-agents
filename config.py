"""
Configuration management for the Autonomous Trading Agents system.
Centralizes all configuration with validation and environment variable support.
"""
import os
from typing import Optional
from pydantic import BaseSettings, Field
from dotenv import load_dotenv

load_dotenv()

class FirebaseConfig(BaseSettings):
    """Firebase configuration with validation"""
    type: str = Field(..., env="FIREBASE_TYPE")
    project_id: str = Field(..., env="FIREBASE_PROJECT_ID")
    private_key_id: str = Field(..., env="FIREBASE_PRIVATE_KEY_ID")
    private_key: str = Field(..., env="FIREBASE_PRIVATE_KEY").replace('\\n', '\n')
    client_email: str = Field(..., env="FIREBASE_CLIENT_EMAIL")
    client_id: str = Field(..., env="FIREBASE_CLIENT_ID")
    auth_uri: str = Field("https://accounts.google.com/o/oauth2/auth", env="FIREBASE_AUTH_URI")
    token_uri: str = Field("https://oauth2.googleapis.com/token", env="FIREBASE_TOKEN_URI")
    auth_provider_x509_cert_url: str = Field(
        "https://www.googleapis.com/oauth2/v1/certs", 
        env="FIREBASE_AUTH_PROVIDER_CERT_URL"
    )
    client_x509_cert_url: str = Field(..., env="FIREBASE_CLIENT_CERT_URL")

class AgentConfig(BaseSettings):
    """Agent system configuration"""
    replication_threshold: float = Field(0.8, ge=0.0, le=1.0)
    max_agents_per_generation: int = Field(100, gt=0)
    evaluation_period_hours: int = Field(24, gt=0)
    min_performance_for_replication: float = Field(0.15, ge=0.0)
    
class TradingConfig(BaseSettings):
    """Trading-specific configuration"""
    paper_trading: bool = Field(True)
    default_exchange: str = Field("binance")
    max_position_size_usd: float = Field(1000.0, gt=0)
    risk_per_trade: float = Field(0.02, gt=0.0, le=0.05)
    
class Config(BaseSettings):
    """Main configuration container"""
    firebase: FirebaseConfig = FirebaseConfig()
    agent: AgentConfig = AgentConfig()
    trading: TradingConfig = TradingConfig()
    log_level: str = Field("INFO", env="LOG_LEVEL")
    
    class Config:
        env_nested_delimiter = '__'

config = Config()