import tkinter as tk
from tkinter import ttk
from typing import Literal, Optional

# Try to import sv_ttk for modern theming
try:
    import sv_ttk
except ImportError:
    sv_ttk = None

class ThemeManager:
    """Manages application theming and styling"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.style = ttk.Style()
        self.current_theme: Literal['light', 'dark'] = 'light'
        self._setup_styles()
    
    def set_theme(self, theme_name: Literal['light', 'dark']) -> None:
        """Set the application theme"""
        self.current_theme = theme_name
        
        # Use sv_ttk if available, otherwise fall back to basic theming
        if sv_ttk:
            try:
                sv_ttk.set_theme(theme_name)
                return
            except Exception:
                pass
        
        # Fallback theming
        bg_color = '#f0f0f0' if theme_name == 'light' else '#1e1e1e'
        fg_color = '#000000' if theme_name == 'light' else '#ffffff'
        
        self.style.configure('.', background=bg_color, foreground=fg_color)
        self.style.configure('TFrame', background=bg_color)
        self.style.configure('TLabel', background=bg_color, foreground=fg_color)
        self.style.configure('TButton', padding=5)
        self.style.configure('TEntry', fieldbackground=bg_color, foreground=fg_color)
        
        # Configure Treeview
        self.style.configure('Treeview', 
                           background=bg_color,
                           fieldbackground=bg_color,
                           foreground=fg_color)
        self.style.map('Treeview',
                      background=[('selected', '#0078d7' if theme_name == 'light' else '#1a73e8')],
                      foreground=[('selected', '#ffffff')])
    
    def _setup_styles(self) -> None:
        """Set up initial styles"""
        # Configure button styles
        self.style.configure('TButton', padding=2)
        self.style.configure('TEntry', padding=2)
        
        # Configure Treeview style
        self.style.configure('Treeview', rowheight=25)
        self.style.layout('Treeview', [('Treeview.treearea', {'sticky': 'nswe'})])
        
        # Configure scrollbar
        self.style.configure('Vertical.TScrollbar', arrowsize=12)
        
        # Configure notebook style
        self.style.configure('TNotebook', tabposition='n')
        self.style.configure('TNotebook.Tab', padding=[10, 2])
    
    def get_theme(self) -> str:
        """Get the current theme name"""
        return self.current_theme
