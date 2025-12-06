"""
App State - Global Application State Management
"""
from typing import Optional, Callable, List, Dict, Any
from models.user import User
from services.auth_service import AuthService
from services.sync_service import SyncService


class AppState:
    """
    Global application state manager.
    
    Implements a simple observer pattern for reactive state updates.
    Components can subscribe to state changes and get notified automatically.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self._current_user: Optional[User] = None
        self._is_loading: bool = False
        self._error_message: Optional[str] = None
        self._theme_mode: str = 'dark'
        self._current_route: str = 'splash'
        self._navigation_stack: List[Dict] = []
        
        # Observers for reactive updates
        self._observers: Dict[str, List[Callable]] = {
            'user': [],
            'loading': [],
            'error': [],
            'theme': [],
            'route': [],
        }
    
    # ==================== OBSERVERS ====================
    
    def subscribe(self, event: str, callback: Callable):
        """Subscribe to state changes"""
        if event in self._observers:
            self._observers[event].append(callback)
    
    def unsubscribe(self, event: str, callback: Callable):
        """Unsubscribe from state changes"""
        if event in self._observers and callback in self._observers[event]:
            self._observers[event].remove(callback)
    
    def _notify(self, event: str, data: Any = None):
        """Notify all observers of a state change"""
        if event in self._observers:
            for callback in self._observers[event]:
                try:
                    callback(data)
                except Exception as e:
                    print(f"Observer error: {e}")
    
    # ==================== USER STATE ====================
    
    @property
    def current_user(self) -> Optional[User]:
        """Get current logged in user"""
        return self._current_user
    
    @current_user.setter
    def current_user(self, user: Optional[User]):
        """Set current user and notify observers"""
        self._current_user = user
        self._notify('user', user)
    
    @property
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return self._current_user is not None
    
    @property
    def is_instructor(self) -> bool:
        """Check if current user is an instructor"""
        return self._current_user.is_instructor if self._current_user else False
    
    @property
    def is_student(self) -> bool:
        """Check if current user is a student"""
        return self._current_user.is_student if self._current_user else False
    
    # ==================== LOADING STATE ====================
    
    @property
    def is_loading(self) -> bool:
        """Get loading state"""
        return self._is_loading
    
    @is_loading.setter
    def is_loading(self, loading: bool):
        """Set loading state and notify observers"""
        self._is_loading = loading
        self._notify('loading', loading)
    
    # ==================== ERROR STATE ====================
    
    @property
    def error_message(self) -> Optional[str]:
        """Get current error message"""
        return self._error_message
    
    @error_message.setter
    def error_message(self, message: Optional[str]):
        """Set error message and notify observers"""
        self._error_message = message
        self._notify('error', message)
    
    def clear_error(self):
        """Clear current error"""
        self.error_message = None
    
    # ==================== THEME STATE ====================
    
    @property
    def theme_mode(self) -> str:
        """Get current theme mode"""
        return self._theme_mode
    
    @theme_mode.setter
    def theme_mode(self, mode: str):
        """Set theme mode and notify observers"""
        self._theme_mode = mode
        self._notify('theme', mode)
    
    def toggle_theme(self):
        """Toggle between dark and light theme"""
        self.theme_mode = 'light' if self._theme_mode == 'dark' else 'dark'
    
    # ==================== NAVIGATION STATE ====================
    
    @property
    def current_route(self) -> str:
        """Get current route"""
        return self._current_route
    
    @current_route.setter
    def current_route(self, route: str):
        """Set current route and notify observers"""
        self._current_route = route
        self._notify('route', route)
    
    @property
    def navigation_stack(self) -> List[Dict]:
        """Get navigation stack"""
        return self._navigation_stack
    
    def push_route(self, route: str, data: Any = None):
        """Push route to navigation stack"""
        self._navigation_stack.append({
            'route': self._current_route,
            'data': data
        })
        self.current_route = route
    
    def pop_route(self) -> Optional[Dict]:
        """Pop route from navigation stack"""
        if self._navigation_stack:
            prev = self._navigation_stack.pop()
            self.current_route = prev['route']
            return prev
        return None
    
    def clear_navigation(self):
        """Clear navigation stack"""
        self._navigation_stack.clear()
    
    # ==================== ACTIONS ====================
    
    def login(self, user: User):
        """Handle user login"""
        self.current_user = user
        self.clear_navigation()
        self.current_route = 'home'
    
    def logout(self):
        """Handle user logout"""
        AuthService.logout()
        self.current_user = None
        self.clear_navigation()
        self.current_route = 'login'
    
    def reset(self):
        """Reset all state to initial values"""
        self._current_user = None
        self._is_loading = False
        self._error_message = None
        self._current_route = 'splash'
        self._navigation_stack.clear()
    
    # ==================== SYNC STATUS ====================
    
    def get_sync_status(self) -> Dict:
        """Get current sync status"""
        return SyncService.get_sync_status()
    
    def sync_data(self) -> tuple:
        """Trigger data sync"""
        return SyncService.process_sync_queue()


# Global app state instance
app_state = AppState()







