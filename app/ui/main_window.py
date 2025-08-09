import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List, Optional, Callable, Any
import threading
import keyboard as kb
from pathlib import Path
import os

from ..models import TodoItem, AppState, Settings
from .menu_bar import MenuBar, MenuActions
from .todo_list import TodoList, TodoListCallbacks
from .theme import ThemeManager

class MainWindow:
    """Main application window"""
    
    def __init__(self, root, storage):
        self.root = root
        self.storage = storage
        self.state = self.storage.load()
        
        # Initialize UI
        self._setup_window()
        self.theme_manager = ThemeManager(root)
        self._setup_ui()
        
        # Set initial state
        self._update_from_state()
        
        # Register hotkey if enabled
        self._hotkey_registered = False
        self._register_hotkey()
        
        # Bind close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def _setup_window(self) -> None:
        """Configure main window properties"""
        self.root.title("Todo Book")
        self.root.geometry("400x500")
        self.root.resizable(False, False)
        self.root.attributes('-toolwindow', 1)
        self.root.attributes('-topmost', True)
    
    def _setup_ui(self) -> None:
        """Initialize all UI components"""
        # Main container
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Menu bar
        self._setup_menu()
        
        # Todo list
        self._setup_todo_list()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(
            self.main_frame,
            textvariable=self.status_var,
            relief='sunken',
            anchor='w'
        )
        self.status_bar.pack(side='bottom', fill='x')
    
    def _setup_menu(self) -> None:
        """Set up the menu bar"""
        menu_actions = MenuActions(
            on_mode_change=self.on_mode_change,
            on_clear_all=self.on_clear_all,
            on_theme_change=self.on_theme_change,
            on_toggle_hotkey=self.on_toggle_hotkey
        )
        
        self.menu_bar = MenuBar(
            self.root,
            actions=menu_actions,
            initial_state={
                'theme': self.state.get('settings', {}).get('theme', 'light'),
                'hotkey_enabled': self.state.get('settings', {}).get('hotkey_enabled', True),
                'mode': self.state.get('settings', {}).get('mode', 'todo')
            }
        )
    
    def _setup_todo_list(self) -> None:
        """Set up the todo list component"""
        callbacks = TodoListCallbacks(
            on_toggle_complete=self.on_toggle_complete,
            on_copy_click=self.on_copy_click,
            on_item_added=self.on_item_added
        )
        
        self.todo_list = TodoList(self.main_frame, callbacks=callbacks)
        self.todo_list.pack(fill='both', expand=True, pady=(5, 0))
        
        # Set initial mode
        self.todo_list.set_mode(self.state.get('settings', {}).get('mode', 'todo'))
        
        # Load initial todos
        current_chapter = self.state.get('current_chapter', 'General')
        todos = self.state.get('todos', {}).get(current_chapter, [])
        self.todo_list.update_items([(t.text, t.completed, t.created_at) for t in todos])
    
    def _update_from_state(self) -> None:
        """Update UI from current state"""
        # Apply theme
        theme = self.state.get('settings', {}).get('theme', 'light')
        self.theme_manager.set_theme(theme)
        
        # Update status
        current_chapter = self.state.get('current_chapter', 'General')
        todo_count = len(self.state.get('todos', {}).get(current_chapter, []))
        self.status_var.set(f"{current_chapter}: {todo_count} items")
    
    def _register_hotkey(self) -> None:
        """Register global hotkey if enabled"""
        if self._hotkey_registered:
            return
            
        if self.state.get('settings', {}).get('hotkey_enabled', True):
            try:
                kb.add_hotkey('ctrl+space', self.toggle_visibility)
                self._hotkey_registered = True
            except Exception as e:
                print(f"Failed to register hotkey: {e}")
    
    def _unregister_hotkey(self) -> None:
        """Unregister global hotkey"""
        if self._hotkey_registered:
            try:
                kb.remove_hotkey('ctrl+space')
                self._hotkey_registered = False
            except Exception as e:
                print(f"Failed to unregister hotkey: {e}")
    
    def toggle_visibility(self) -> None:
        """Toggle window visibility"""
        if self.root.state() == 'withdrawn':
            self.root.deiconify()
            self.root.lift()
            self.root.focus_force()
        else:
            self.root.withdraw()
    
    def save_state(self) -> None:
        """Save current state to storage"""
        # Update settings from menu
        menu_state = self.menu_bar.get_state()
        if 'settings' not in self.state:
            self.state['settings'] = {}
        self.state['settings'].update(menu_state)
        
        # Save to storage
        self.storage.save(self.state)
    
    # Event handlers
    def on_mode_change(self, mode: str) -> None:
        """Handle mode change (todo/clipboard)"""
        self.todo_list.set_mode(mode)
        self.save_state()
    
    def on_theme_change(self, theme: str) -> None:
        """Handle theme change"""
        self.theme_manager.set_theme(theme)
        self.save_state()
    
    def on_toggle_hotkey(self, enabled: bool) -> None:
        """Handle hotkey toggle"""
        if enabled:
            self._register_hotkey()
        else:
            self._unregister_hotkey()
        self.save_state()
    
    def on_clear_all(self) -> None:
        """Handle clear all action"""
        if messagebox.askyesno("Clear All", "Are you sure you want to clear all tasks?"):
            current_chapter = self.state.get('current_chapter', 'General')
            if current_chapter in self.state.get('todos', {}):
                self.state['todos'][current_chapter] = []
                self.todo_list.clear()
                self.save_state()
                self.status_var.set(f"{current_chapter}: 0 items")
    
    def on_toggle_complete(self, index: int) -> None:
        """Handle todo completion toggle"""
        current_chapter = self.state.get('current_chapter', 'General')
        if current_chapter in self.state.get('todos', {}):
            todos = self.state['todos'][current_chapter]
            if 0 <= index < len(todos):
                todos[index].completed = not todos[index].completed
                self.save_state()
    
    def on_copy_click(self, index: int) -> None:
        """Handle copy button click"""
        current_chapter = self.state.get('current_chapter', 'General')
        if current_chapter in self.state.get('todos', {}):
            todos = self.state['todos'][current_chapter]
            if 0 <= index < len(todos):
                text = todos[index].text
                self.root.clipboard_clear()
                self.root.clipboard_append(text)
                self.status_var.set(f"Copied to clipboard: {text[:30]}...")
    
    def on_item_added(self, text: str) -> None:
        """Handle new todo item added"""
        import datetime
        
        current_chapter = self.state.get('current_chapter', 'General')
        if current_chapter not in self.state.get('todos', {}):
            self.state['todos'][current_chapter] = []
        
        todo = TodoItem(
            text=text,
            completed=False,
            created_at=datetime.datetime.now().isoformat()
        )
        
        self.state['todos'][current_chapter].append(todo)
        self.todo_list.add_item(text, False, todo.created_at)
        
        # Update status
        todo_count = len(self.state['todos'][current_chapter])
        self.status_var.set(f"{current_chapter}: {todo_count} items")
        
        self.save_state()
    
    def on_close(self) -> None:
        """Handle window close event"""
        self._unregister_hotkey()
        self.save_state()
        self.root.quit()
        self.root.destroy()
    
    def run(self) -> None:
        """Start the main event loop"""
        self.root.mainloop()
