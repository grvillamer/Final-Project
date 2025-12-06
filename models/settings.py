"""
Settings Model - Data Transfer Object
"""
from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class UserSettings:
    """User settings data model"""
    user_id: int
    dark_mode: bool = True
    notifications: bool = True
    language: str = "en"
    auto_sync: bool = True
    
    @classmethod
    def from_dict(cls, user_id: int, data: Dict[str, str]) -> "UserSettings":
        """Create UserSettings from dictionary"""
        return cls(
            user_id=user_id,
            dark_mode=data.get('dark_mode', 'true') == 'true',
            notifications=data.get('notifications', 'true') == 'true',
            language=data.get('language', 'en'),
            auto_sync=data.get('auto_sync', 'true') == 'true',
        )
    
    def to_dict(self) -> Dict[str, str]:
        """Convert UserSettings to string dictionary for storage"""
        return {
            'dark_mode': 'true' if self.dark_mode else 'false',
            'notifications': 'true' if self.notifications else 'false',
            'language': self.language,
            'auto_sync': 'true' if self.auto_sync else 'false',
        }







