"""
Navigation Controller - Handles app navigation and routing
"""
from typing import Callable, Dict, Any, Optional, List
import flet as ft


class NavigationController:
    """
    Controller for managing application navigation.
    Handles page routing, navigation stack, and bottom navigation state.
    """
    
    def __init__(self, page: ft.Page):
        self.page = page
        self._current_index: int = 0
        self._routes: Dict[str, Callable] = {}
        self._navigation_stack: List[Dict] = []
        self._current_route: str = 'splash'
        self._route_data: Any = None
    
    # Main navigation tabs
    TABS = ['home', 'classes', 'attendance', 'analytics', 'settings']
    
    # Routes that show bottom navigation
    NAV_ROUTES = ['home', 'classes', 'attendance', 'analytics', 'settings']
    
    # Routes that don't show bottom navigation (sub-pages)
    SUB_ROUTES = [
        'splash', 'login', 'register', 'forgot_password',
        'create_class', 'edit_class', 'class_detail',
        'take_attendance', 'profile', 'change_password'
    ]
    
    @property
    def current_index(self) -> int:
        """Get current navigation tab index"""
        return self._current_index
    
    @current_index.setter
    def current_index(self, index: int):
        """Set current navigation tab index"""
        self._current_index = index
    
    @property
    def current_route(self) -> str:
        """Get current route name"""
        return self._current_route
    
    @property
    def route_data(self) -> Any:
        """Get current route data"""
        return self._route_data
    
    def register_route(self, route: str, builder: Callable):
        """Register a route with its page builder"""
        self._routes[route] = builder
    
    def navigate_to(self, route: str, data: Any = None) -> bool:
        """
        Navigate to a specific route.
        Returns True if navigation was successful.
        """
        if route not in self._routes:
            print(f"Route not found: {route}")
            return False
        
        # Clear navigation stack when navigating to main tabs
        if route in self.TABS:
            self._navigation_stack.clear()
            self._current_index = self.TABS.index(route)
        
        self._current_route = route
        self._route_data = data
        
        return True
    
    def push(self, route: str, data: Any = None) -> bool:
        """
        Push a new route onto the navigation stack.
        Preserves current route for back navigation.
        """
        if route not in self._routes:
            return False
        
        # Save current route to stack
        self._navigation_stack.append({
            'route': self._current_route,
            'data': self._route_data,
            'index': self._current_index
        })
        
        self._current_route = route
        self._route_data = data
        
        return True
    
    def pop(self) -> bool:
        """
        Pop the current route and return to previous.
        Returns True if there was a route to pop to.
        """
        if not self._navigation_stack:
            # If no stack, go to home
            self._current_route = 'home'
            self._route_data = None
            self._current_index = 0
            return False
        
        prev = self._navigation_stack.pop()
        self._current_route = prev['route']
        self._route_data = prev.get('data')
        self._current_index = prev.get('index', 0)
        
        return True
    
    def can_pop(self) -> bool:
        """Check if there's a route to pop to"""
        return len(self._navigation_stack) > 0
    
    def get_page_builder(self, route: str = None) -> Optional[Callable]:
        """Get the page builder for a route"""
        route = route or self._current_route
        return self._routes.get(route)
    
    def should_show_nav(self) -> bool:
        """Check if bottom navigation should be shown"""
        return self._current_route in self.NAV_ROUTES
    
    def handle_tab_change(self, index: int):
        """Handle bottom navigation tab change"""
        if 0 <= index < len(self.TABS):
            route = self.TABS[index]
            self.navigate_to(route)
    
    def reset(self):
        """Reset navigation state"""
        self._current_index = 0
        self._navigation_stack.clear()
        self._current_route = 'splash'
        self._route_data = None







