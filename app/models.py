from dataclasses import dataclass, asdict
from typing import Dict, List, TypedDict, Optional

class Settings(TypedDict, total=False):
    """Application settings structure"""
    theme: str
    hotkey_enabled: bool
    mode: str  # 'todo' or 'clipboard'

@dataclass
class TodoItem:
    """Represents a single todo item"""
    text: str
    completed: bool
    created_at: str  # ISO-like timestamp

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'TodoItem':
        """Create from dictionary"""
        return cls(
            text=data.get('text', ''),
            completed=bool(data.get('completed', False)),
            created_at=data.get('created_at', '')
        )

class AppState(TypedDict, total=False):
    """Complete application state structure"""
    chapters: List[str]
    current_chapter: str
    todos: Dict[str, List[TodoItem]]
    settings: Settings
