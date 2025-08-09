import tkinter as tk
from tkinter import ttk
from typing import Callable, Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class TodoItem:
    text: str
    completed: bool
    created_at: str

@dataclass
class TodoListCallbacks:
    on_toggle_complete: Callable[[int], None]
    on_copy_click: Callable[[int], None]
    on_item_added: Callable[[str], None]

class TodoList(ttk.Frame):
    """A list of todo items with copy functionality"""
    
    def __init__(self, parent, callbacks: TodoListCallbacks, **kwargs):
        super().__init__(parent, **kwargs)
        self.callbacks = callbacks
        self.current_mode = 'todo'  # 'todo' or 'clipboard'
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Initialize the UI components"""
        # Configure grid weights
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        # Entry for new todos
        self.entry = ttk.Entry(self)
        self.entry.grid(row=0, column=0, sticky='ew', padx=2, pady=2)
        self.entry.bind('<Return>', self._on_add_todo)
        
        # Scrollbar for the list
        scrollbar = ttk.Scrollbar(self, orient='vertical')
        scrollbar.grid(row=1, column=1, sticky='ns')
        
        # Treeview for todos
        self.tree = ttk.Treeview(
            self,
            columns=('copy',),
            show='tree',
            selectmode='browse',
            yscrollcommand=scrollbar.set,
            height=15
        )
        self.tree.grid(row=1, column=0, sticky='nsew')
        scrollbar.config(command=self.tree.yview)
        
        # Configure columns
        self.tree.column('#0', stretch=tk.YES, anchor='w')
        self.tree.column('copy', width=30, stretch=False, anchor='center')
        
        # Bind events
        self.tree.bind('<Double-1>', self._on_item_double_click)
        self.tree.bind('<Button-1>', self._on_item_click)
    
    def set_mode(self, mode: str) -> None:
        """Set the display mode (todo or clipboard)"""
        self.current_mode = mode
        self._update_columns()
    
    def _update_columns(self) -> None:
        """Update the treeview columns based on current mode"""
        if self.current_mode == 'clipboard':
            self.tree.heading('copy', text='')
            self.tree.column('copy', width=30, stretch=False, anchor='center')
        else:
            self.tree.heading('copy', text='')
            self.tree.column('copy', width=0, stretch=False, minwidth=0)
    
    def add_item(self, text: str, completed: bool = False, created_at: Optional[str] = None) -> None:
        """Add a new todo item to the list"""
        item_id = self.tree.insert('', 'end', text=text, tags=('completed' if completed else 'active',))
        self.tree.set(item_id, 'copy', '⧉' if self.current_mode == 'clipboard' else '')
        
        if completed:
            self.tree.item(item_id, tags=('completed',))
            self.tree.item(item_id, text=f'✓ {text}')
    
    def update_items(self, items: List[Tuple[str, bool, str]]) -> None:
        """Update the list with new items"""
        self.tree.delete(*self.tree.get_children())
        for text, completed, _ in items:
            self.add_item(text, completed)
    
    def clear(self) -> None:
        """Clear all items from the list"""
        self.tree.delete(*self.tree.get_children())
    
    def _on_add_todo(self, event=None) -> None:
        """Handle adding a new todo"""
        text = self.entry.get().strip()
        if text:
            self.callbacks.on_item_added(text)
            self.entry.delete(0, 'end')
    
    def _on_item_double_click(self, event) -> None:
        """Handle double-click on an item (toggle completion)"""
        if self.current_mode != 'todo':
            return
            
        item = self.tree.identify_row(event.y)
        if not item:
            return
            
        # Toggle completion
        current_tags = self.tree.item(item, 'tags')
        is_completed = 'completed' in current_tags
        
        if is_completed:
            self.tree.item(item, tags=('active',))
            text = self.tree.item(item, 'text')[2:]  # Remove '✓ '
            self.tree.item(item, text=text)
        else:
            self.tree.item(item, tags=('completed',))
            text = self.tree.item(item, 'text')
            self.tree.item(item, text=f'✓ {text}')
        
        # Get the index of the item
        index = self.tree.index(item)
        self.callbacks.on_toggle_complete(index)
    
    def _on_item_click(self, event) -> None:
        """Handle single click on an item (for copy button)"""
        if self.current_mode != 'clipboard':
            return
            
        region = self.tree.identify_region(event.x, event.y)
        if region != 'cell':
            return
            
        column = self.tree.identify_column(event.x)
        item = self.tree.identify_row(event.y)
        
        if column == '#1' and item:  # Clicked on copy column
            # Get the todo text (without the checkmark if present)
            text = self.tree.item(item, 'text')
            if text.startswith('✓ '):
                text = text[2:]
                
            # Show visual feedback
            self.tree.set(item, 'copy', '✓')
            self.after(500, lambda: self.tree.set(item, 'copy', '⧉'))
            
            # Trigger the copy callback
            index = self.tree.index(item)
            self.callbacks.on_copy_click(index)
