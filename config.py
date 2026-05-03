"""
Smart Classroom - Secure Configuration Module
Loads settings from environment variables with secure defaults
"""
import os
from typing import Any
from pathlib import Path

# Try to load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    base = Path(__file__).parent
    for fname in ('.env', '.env.local'):
        p = base / fname
        if p.exists():
            load_dotenv(p, override=(fname == '.env.local'))
except ImportError:
    pass


class Config:
    """
    Secure configuration management.
    All secrets are loaded from environment variables, never hardcoded.
    """
    
    # Application Settings
    APP_NAME: str = os.getenv('APP_NAME', 'Smart Classroom Access Control System')
    APP_ENV: str = os.getenv('APP_ENV', 'development')
    DEBUG: bool = os.getenv('DEBUG', 'false').lower() == 'true'
    
    # Security Settings - MUST be set via environment in production
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'dev-only-change-in-production')
    SESSION_TIMEOUT_MINUTES: int = int(os.getenv('SESSION_TIMEOUT_MINUTES', '30'))
    MAX_LOGIN_ATTEMPTS: int = int(os.getenv('MAX_LOGIN_ATTEMPTS', '5'))
    LOCKOUT_DURATION_MINUTES: int = int(os.getenv('LOCKOUT_DURATION_MINUTES', '15'))
    
    # Password Policy
    PASSWORD_MIN_LENGTH: int = int(os.getenv('PASSWORD_MIN_LENGTH', '8'))
    PASSWORD_REQUIRE_UPPERCASE: bool = os.getenv('PASSWORD_REQUIRE_UPPERCASE', 'true').lower() == 'true'
    PASSWORD_REQUIRE_LOWERCASE: bool = os.getenv('PASSWORD_REQUIRE_LOWERCASE', 'true').lower() == 'true'
    PASSWORD_REQUIRE_DIGIT: bool = os.getenv('PASSWORD_REQUIRE_DIGIT', 'true').lower() == 'true'
    PASSWORD_REQUIRE_SPECIAL: bool = os.getenv('PASSWORD_REQUIRE_SPECIAL', 'true').lower() == 'true'
    PASSWORD_HISTORY_COUNT: int = int(os.getenv('PASSWORD_HISTORY_COUNT', '5'))
    
    # Database
    DATABASE_PATH: str = os.getenv('DATABASE_PATH', 'spotted.db')

    # Google OAuth (Sign in with Google) — Desktop / localhost redirect flow
    GOOGLE_CLIENT_ID: str = os.getenv('GOOGLE_CLIENT_ID', '')
    GOOGLE_CLIENT_SECRET: str = os.getenv('GOOGLE_CLIENT_SECRET', '')
    # Port for Google's redirect to http://localhost:{PORT}/ ... must match your OAuth client authorized redirect URIs
    GOOGLE_OAUTH_REDIRECT_PORT: int = int(os.getenv('GOOGLE_OAUTH_REDIRECT_PORT', '9353'))
    
    # Outbound email (optional, used for password reset codes)
    SMTP_ENABLED: bool = os.getenv('SMTP_ENABLED', 'false').lower() == 'true'
    SMTP_HOST: str = os.getenv('SMTP_HOST', '')
    SMTP_PORT: int = int(os.getenv('SMTP_PORT', '587'))
    SMTP_USE_TLS: bool = os.getenv('SMTP_USE_TLS', 'true').lower() == 'true'
    SMTP_USERNAME: str = os.getenv('SMTP_USERNAME', '')
    SMTP_PASSWORD: str = os.getenv('SMTP_PASSWORD', '')
    SMTP_FROM_EMAIL: str = os.getenv('SMTP_FROM_EMAIL', SMTP_USERNAME or 'no-reply@example.com')
    SMTP_FROM_NAME: str = os.getenv('SMTP_FROM_NAME', APP_NAME)
    
    # Logging
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE: str = os.getenv('LOG_FILE', 'app.log')
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production mode"""
        return cls.APP_ENV.lower() == 'production'
    
    @classmethod
    def validate(cls) -> list:
        """
        Validate configuration for production readiness.
        Returns list of warnings/errors.
        """
        issues = []
        
        if cls.is_production():
            if cls.SECRET_KEY == 'dev-only-change-in-production':
                issues.append("CRITICAL: SECRET_KEY must be changed in production!")
            if cls.DEBUG:
                issues.append("WARNING: DEBUG mode is enabled in production!")
            if len(cls.SECRET_KEY) < 32:
                issues.append("WARNING: SECRET_KEY should be at least 32 characters")
        
        return issues


# Create global config instance
config = Config()

# Validate on import and print warnings
_issues = config.validate()
if _issues:
    for issue in _issues:
        print(f"[CONFIG] {issue}")

