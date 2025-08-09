import tkinter as tk
from tkinter import ttk
from typing import Callable, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class MenuActions:
    """Actions that can be triggered from the menu"""
    on_mode_change: Callable[[str], None]
    on_clear_all: Callable[[], None]
    on_theme_change: Callable[[str], None]
    on_toggle_hotkey: Callable[[bool], None]

class MenuBar:
    """Application menu bar with all menu items"""
    
    def __init__(self, root: tk.Tk, actions: MenuActions, initial_state: Dict[str, Any]):
        self.root = root
        self.actions = actions
        self.menubar = tk.Menu(root)
        
        # Menu variables
        self.theme_var = tk.StringVar(value=initial_state.get('theme', 'light'))
        self.hotkey_var = tk.BooleanVar(value=initial_state.get('hotkey_enabled', True))
        self.mode_var = tk.StringVar(value=initial_state.get('mode', 'todo'))
        
        self._setup_menus()
    
    def _setup_menus(self) -> None:
        """Set up all menu items"""
        # Modes menu
        modes_menu = tk.Menu(self.menubar, tearoff=0)
        modes_menu.add_radiobutton(
            label="Todo Mode", 
            value="todo",
            variable=self.mode_var,
            command=lambda: self.actions.on_mode_change("todo")
        )
        modes_menu.add_radiobutton(
            label="Clipboard Mode", 
            value="clipboard",
            variable=self.mode_var,
            command=lambda: self.actions.on_mode_change("clipboard")
        )
        self.menubar.add_cascade(label="Modes", menu=modes_menu)
        
        # Clear All menu item
        self.menubar.add_command(
            label="Clear All",
            command=self.actions.on_clear_all,
            foreground='red'
        )
        
        # Settings menu
        settings_menu = tk.Menu(self.menubar, tearoff=0)
        
        # Theme submenu
        theme_menu = tk.Menu(settings_menu, tearoff=0)
        theme_menu.add_radiobutton(
            label="Light", 
            value="light", 
            variable=self.theme_var,
            command=lambda: self.actions.on_theme_change("light")
        )
        theme_menu.add_radiobutton(
            label="Dark", 
            value="dark", 
            variable=self.theme_var,
            command=lambda: self.actions.on_theme_change("dark")
        )
        settings_menu.add_cascade(label="Theme", menu=theme_menu)
        settings_menu.add_separator()
        
        # Hotkey toggle
        settings_menu.add_checkbutton(
            label="Global Hotkey (Ctrl+Space)",
            variable=self.hotkey_var,
            command=lambda: self.actions.on_toggle_hotkey(self.hotkey_var.get())
        )
        
        self.menubar.add_cascade(label="Settings", menu=settings_menu)
        
        # Apply the menu to the root window
        self.root.config(menu=self.menubar)
    
    def get_state(self) -> Dict[str, Any]:
        """Get the current state of menu settings"""
        return {
            'theme': self.theme_var.get(),
            'hotkey_enabled': self.hotkey_var.get(),
            'mode': self.mode_var.get()
        }
