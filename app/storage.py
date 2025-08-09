import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
from .models import AppState, TodoItem, Settings

class Storage:
    """Handles saving and loading application state"""
    
    def __init__(self, app_name: str = "ScribbleThoughts", file_name: str = "todo_data.json"):
        self.app_name = app_name
        self.file_name = file_name
        self._data_path = self._get_data_path()
        
    def _get_data_path(self) -> Path:
        """Get the path to the data file"""
        if os.name == 'nt':  # Windows
            base_dir = Path(os.getenv('APPDATA', Path.home() / 'AppData' / 'Roaming'))
        else:  # macOS/Linux
            base_dir = Path.home() / '.config'
            
        app_dir = base_dir / self.app_name
        app_dir.mkdir(parents=True, exist_ok=True)
        return app_dir / self.file_name
    
    def load(self) -> AppState:
        """Load application state from disk"""
        if not self._data_path.exists():
            return self._get_default_state()
            
        try:
            with open(self._data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return self._deserialize_state(data)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading data: {e}")
            return self._get_default_state()
    
    def save(self, state: AppState) -> None:
        """Save application state to disk"""
        try:
            with open(self._data_path, 'w', encoding='utf-8') as f:
                json.dump(self._serialize_state(state), f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving data: {e}")
    
    def _get_default_state(self) -> AppState:
        """Return default application state"""
        return {
            'chapters': ['General'],
            'current_chapter': 'General',
            'todos': {'General': []},
            'settings': {
                'theme': 'light',
                'hotkey_enabled': True,
                'mode': 'todo'
            }
        }
    
    def _serialize_state(self, state: AppState) -> Dict[str, Any]:
        """Convert state to serializable format"""
        serialized = state.copy()
        # Convert TodoItem objects to dictionaries
        serialized['todos'] = {
            chapter: [item.to_dict() for item in items]
            for chapter, items in state['todos'].items()
        }
        return serialized
    
    def _deserialize_state(self, data: Dict[str, Any]) -> AppState:
        """Convert serialized data back to application state"""
        # Ensure all required fields exist
        state = self._get_default_state()
        state.update(data)
        
        # Convert todo dictionaries back to TodoItem objects
        state['todos'] = {
            chapter: [TodoItem.from_dict(item) for item in items]
            for chapter, items in state.get('todos', {}).items()
        }
        
        return state
