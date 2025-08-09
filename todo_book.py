import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
import keyboard
import threading
from datetime import datetime
# Optional modern theme (Windows 11 look)
try:
    import sv_ttk
except ImportError:
    sv_ttk = None
from dataclasses import dataclass, asdict
from typing import Dict, List
from storage import load_state, save_state, get_data_path

@dataclass
class TodoItem:
    text: str
    completed: bool
    created_at: str  # ISO-like timestamp

class TodoBook:
    def __init__(self, root):
        self.root = root
        self.root.title("Todo Book")
        self.root.geometry("400x500")
        self.root.resizable(False, False)
        self.root.attributes('-toolwindow', 1)
        self.root.attributes('-topmost', True)
        
        self.chapters = ["General"]
        self.current_chapter = "General"
        self.todos: Dict[str, List[TodoItem]] = {"General": []}
        # App settings (persisted)
        self.settings = {
            "theme": "light", 
            "hotkey_enabled": True,
            "mode": "todo"  # 'todo' or 'clipboard'
        }
        self.theme_var = tk.StringVar(value=self.settings["theme"])
        self.hotkey_enabled_var = tk.BooleanVar(value=self.settings["hotkey_enabled"])
        self.mode_var = tk.StringVar(value=self.settings["mode"])
        self._hotkey_str = 'ctrl+space'
        self._hotkey_registered = False
        
        self.load_data()
        # Apply theme before building widgets so styles take effect
        self.apply_theme(self.settings.get("theme", "light"))
        self.setup_ui()
        
        # Register global hotkey based on settings (deferred for faster startup)
        self.root.after(300, self.update_hotkey_registration)
        
        self.window_visible = True
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def _setup_hotkey(self):
        """Set up the global hotkey in a separate thread"""
        try:
            keyboard.add_hotkey(self._hotkey_str, self.toggle_window_from_thread)
            self._hotkey_registered = True
        except Exception as e:
            # Could be permissions or OS-level restriction
            self._hotkey_registered = False
    
    def toggle_window_from_thread(self):
        """Wrapper to safely call toggle_window from keyboard thread"""
        self.root.after(0, self.toggle_window)
    
    def on_close(self):
        """Clean up resources when closing the window"""
        try:
            if self._hotkey_registered:
                keyboard.remove_hotkey(self._hotkey_str)
        except Exception:
            pass
        keyboard.unhook_all()
        self.root.destroy()
    
    def toggle_window(self, event=None):
        """Toggle window visibility"""
        if self.window_visible:
            self.root.withdraw()  # Hide window
        else:
            self.root.deiconify()  # Show window
            self.root.lift()
            self.root.focus_force()
        self.window_visible = not self.window_visible
    
    def setup_ui(self):
        # Menu bar
        menubar = tk.Menu(self.root)
        
        # Modes menu
        modes_menu = tk.Menu(menubar, tearoff=0)
        modes_menu.add_radiobutton(label="Todo Mode", value="todo", 
                                 variable=self.mode_var,
                                 command=self.on_mode_change)
        modes_menu.add_radiobutton(label="Clipboard Mode", value="clipboard",
                                 variable=self.mode_var,
                                 command=self.on_mode_change)
        menubar.add_cascade(label="Modes", menu=modes_menu)
        
        # Clear All menu item
        menubar.add_command(label="Clear All", 
                          command=self.clear_all_todos,
                          foreground='red')
        
        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        theme_menu = tk.Menu(settings_menu, tearoff=0)
        theme_menu.add_radiobutton(label="Light", value="light", variable=self.theme_var,
                                 command=lambda: self.set_theme("light"))
        theme_menu.add_radiobutton(label="Dark", value="dark", variable=self.theme_var,
                                 command=lambda: self.set_theme("dark"))
        settings_menu.add_cascade(label="Theme", menu=theme_menu)
        settings_menu.add_separator()
        settings_menu.add_checkbutton(
            label="Global Hotkey (Ctrl+Space)",
            variable=self.hotkey_enabled_var,
            command=self.on_toggle_global_hotkey,
        )
        menubar.add_cascade(label="Settings", menu=settings_menu)
        
        self.root.config(menu=menubar)
        
        # Configure style
        style = ttk.Style()
        if not sv_ttk:
            style.configure('TFrame', background='white')
            style.configure('Sidebar.TFrame', background='#f5f5f5')
        style.configure('TButton', padding=2)
        style.configure('TEntry', padding=2)
        
        # Main container with less padding
        self.main_frame = ttk.Frame(self.root, padding="5")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Header with smaller font and compact layout
        header = ttk.Frame(self.main_frame)
        header.grid(row=0, column=0, columnspan=2, pady=(0, 5), sticky="ew")
        
        ttk.Label(header, text="Todo Book", font=('Segoe UI', 9, 'bold')).pack(side=tk.LEFT)
        ttk.Button(header, text="×", command=self.toggle_window, width=2).pack(side=tk.RIGHT)
        
        # Sidebar with smaller font and compact layout
        sidebar = ttk.Frame(self.main_frame, width=120, style='Sidebar.TFrame')
        sidebar.grid(row=1, column=0, sticky="ns", padx=(0, 5), pady=5)
        
        ttk.Label(sidebar, text="Chapters", font=('Segoe UI', 8, 'bold')).pack(pady=(0, 3), anchor='w')
        
        # Chapter list with smaller font
        self.chapter_list = ttk.Treeview(sidebar, show='tree', selectmode='browse', height=10)
        self.chapter_list.pack(fill=tk.X, pady=(0, 5))
        self.update_chapter_list()
        
        ttk.Button(sidebar, text="+ New", command=self.add_chapter, 
                  style='TButton').pack(fill=tk.X, pady=(0, 5))
        
        # Main content
        content = ttk.Frame(self.main_frame)
        content.grid(row=1, column=1, sticky="nsew")
        
        # Current chapter label with smaller font
        self.current_chapter_label = ttk.Label(content, text=f"{self.current_chapter}", 
                                            font=('Segoe UI', 8, 'bold'))
        self.current_chapter_label.pack(anchor='w', pady=(0, 5))
        
        # Add todo frame with compact layout
        add_frame = ttk.Frame(content)
        add_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.todo_entry = ttk.Entry(add_frame, font=('Segoe UI', 8))
        self.todo_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 3))
        self.todo_entry.bind("<Return>", lambda e: self.add_todo())
        
        ttk.Button(add_frame, text="+", command=self.add_todo, width=3).pack(side=tk.LEFT)
        
        # Todo list as themed treeview with a clickable Copy column
        self.todo_list = ttk.Treeview(content, columns=("copy",), show='tree', selectmode='browse', height=15)
        
        # Configure columns - use #0 for the task and 'copy' for the copy button
        self.todo_list.heading("#0", text="Task", anchor='w')
        self.todo_list.column("#0", stretch=tk.YES, anchor='w')
        self.todo_list.heading("copy", text="")
        self.todo_list.column("copy", width=0, stretch=False, anchor='center')
        
        # Hide the tree column header since we're using #0 for the task
        self.todo_list['show'] = 'tree headings'
        
        self.todo_list.pack(fill=tk.BOTH, expand=True)
        
        # Bind events
        self.todo_list.bind("<Button-1>", self.on_todo_click)
        self.chapter_list.bind('<<TreeviewSelect>>', self.on_chapter_select)
        
        # Footer with Clear All button
        footer = ttk.Frame(content)
        footer.pack(fill=tk.X, pady=(5, 0), padx=5)  # Add some padding on the sides
        
        # Add a separator for better visual separation
        ttk.Separator(footer, orient='horizontal').pack(fill=tk.X, pady=5)
        
        # Clear All button (will be shown/hidden based on mode)
        # Using standard tkinter Button for better styling
        self.clear_btn = tk.Button(
            footer, 
            text="Clear All",
            command=self.clear_all_todos,
            bg='#e74c3c',
            fg='white',
            bd=0,
            padx=15,
            pady=3,
            font=('Segoe UI', 8, 'bold'),
            relief=tk.FLAT,
            activebackground='#c0392b',
            activeforeground='white'
        )
        # Make the button more visible by default for testing
        self.clear_btn.pack(side=tk.RIGHT, padx=5, pady=2)
        
        # Add a label to the left to balance the layout
        ttk.Label(footer, text=f"Mode: {self.mode_var.get().title()}").pack(side=tk.LEFT, padx=5)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
        
        # Apply initial mode
        self.on_mode_change()
    
    def on_mode_change(self):
        """Handle mode change between todo and clipboard modes"""
        mode = self.mode_var.get()
        if mode == "clipboard":
            # Show copy column with copy icon
            self.todo_list.column("copy", width=30, anchor='center', stretch=False)
            self.todo_list.heading("copy", text="")
        else:
            # Hide copy column in todo mode
            self.todo_list.column("copy", width=0, stretch=False)
        
        # Update the display
        self.update_todo_list()
        
        # Save mode preference
        self.settings["mode"] = mode
        self.save_data()
    
    def update_todo_list(self):
        """Update the todo list display based on current mode"""
        for child in self.todo_list.get_children():
            self.todo_list.delete(child)
            
        for i, todo in enumerate(self.todos.get(self.current_chapter, [])):
            if self.mode_var.get() == "todo":
                prefix = "✓ " if todo.completed else "  "
                self.todo_list.insert('', 'end', iid=str(i), 
                                    text=f"{prefix}{todo.text}",
                                    values=("",))
            else:  # clipboard mode
                # Show copy icon (⧉) in the copy column
                self.todo_list.insert('', 'end', iid=str(i),
                                    text=todo.text,
                                    values=("⧉",))
    
    def on_todo_click(self, event):
        """Handle clicks in the todo list"""
        # Get the item that was clicked
        item_id = self.todo_list.identify_row(event.y)
        if not item_id:
            return
            
        # Get the column that was clicked
        column = self.todo_list.identify_column(event.x)
        
        if self.mode_var.get() == "clipboard" and column == "#1":
            # Handle copy icon click in clipboard mode
            try:
                # Get the todo item text
                todo_text = self.todos[self.current_chapter][int(item_id)].text
                # Copy to clipboard
                self.root.clipboard_clear()
                self.root.clipboard_append(todo_text)
                # Show feedback
                self.todo_list.set(item_id, "copy", "✓")
                # Reset icon after 1 second
                self.root.after(1000, lambda iid=item_id: self.todo_list.set(iid, "copy", "⧉"))
            except Exception as e:
                print(f"Copy failed: {e}")
        elif self.mode_var.get() == "todo" and event.num == 3:  # Double click in todo mode
            # Toggle todo completion on double-click in todo mode
            self.toggle_todo(int(item_id))
    
    def clear_all_todos(self):
        """Clear all todos in the current chapter with confirmation"""
        if not self.todos.get(self.current_chapter):
            return
            
        if messagebox.askyesno(
            "Clear All", 
            f"Are you sure you want to delete all tasks in '{self.current_chapter}'?",
            icon='warning'
        ):
            # Clear the todos for current chapter
            self.todos[self.current_chapter] = []
            self.update_todo_list()
            self.save_data()
    
    def add_chapter(self):
        chapter = simpledialog.askstring("New Chapter", "Enter chapter name:")
        if chapter and chapter.strip() and chapter not in self.chapters:
            self.chapters.append(chapter)
            self.todos[chapter] = []
            self.update_chapter_list()
            self.save_data()
    
    def update_chapter_list(self):
        for child in self.chapter_list.get_children():
            self.chapter_list.delete(child)
        for i, chapter in enumerate(self.chapters):
            self.chapter_list.insert('', 'end', iid=str(i), text=chapter)
        if self.current_chapter in self.chapters:
            idx = self.chapters.index(self.current_chapter)
            self.chapter_list.selection_set(str(idx))
            self.chapter_list.see(str(idx))
    
    def on_chapter_select(self, event):
        selection = self.chapter_list.selection()
        if selection:
            idx = int(selection[0])
            self.current_chapter = self.chapters[idx]
            self.current_chapter_label.config(text=f"{self.current_chapter}")
            self.update_todo_list()
    
    def add_todo(self, event=None):
        text = self.todo_entry.get().strip()
        if text:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            self.todos[self.current_chapter].append(
                TodoItem(text=text, completed=False, created_at=timestamp)
            )
            self.todo_entry.delete(0, tk.END)
            self.update_todo_list()
            self.save_data()
    
    def toggle_todo(self, index):
        if 0 <= index < len(self.todos[self.current_chapter]):
            item = self.todos[self.current_chapter][index]
            item.completed = not item.completed
            self.update_todo_list()
            self.save_data()
    
    def save_data(self):
        # Convert dataclass instances to plain dicts for JSON
        serializable_todos: Dict[str, List[dict]] = {
            chapter: [asdict(item) for item in items]
            for chapter, items in self.todos.items()
        }
        data = {
            "chapters": self.chapters,
            "current_chapter": self.current_chapter,
            "todos": serializable_todos,
            "settings": self.settings,
        }
        save_state(data)
    
    def load_data(self):
        try:
            data = load_state() or {}
            self.chapters = data.get("chapters", ["General"])
            self.current_chapter = data.get("current_chapter", "General")
            raw_todos = data.get("todos", {"General": []})
            # Convert lists of dicts to TodoItem instances; tolerate legacy shapes
            converted: Dict[str, List[TodoItem]] = {}
            for chapter, items in raw_todos.items():
                converted[chapter] = []
                for it in items:
                    if isinstance(it, dict):
                        # Legacy keys: text/completed/created_at
                        text = it.get("text", "")
                        completed = bool(it.get("completed", False))
                        created_at = it.get("created_at", "")
                        converted[chapter].append(TodoItem(text=text, completed=completed, created_at=created_at))
                    elif isinstance(it, TodoItem):
                        converted[chapter].append(it)
            self.todos = converted or {"General": []}
            
            # Load settings
            loaded_settings = data.get("settings", {})
            self.settings.update(loaded_settings)
            
            # Update UI state
            self.theme_var.set(self.settings.get("theme", "light"))
            self.hotkey_enabled_var.set(bool(self.settings.get("hotkey_enabled", True)))
            self.mode_var.set(self.settings.get("mode", "todo"))
            
        except ValueError as e:
            messagebox.showerror("Error", f"Failed to load data from {get_data_path()}\n{e}")
    
    def apply_theme(self, mode: str):
        """Apply theme using sv-ttk if available; otherwise minimal fallback."""
        if sv_ttk:
            try:
                sv_ttk.set_theme(mode)
            except Exception as e:
                # Fallback: ignore and continue
                print(f"Theme apply failed: {e}")
        else:
            # Minimal fallback: adjust a couple styles for light/dark
            style = ttk.Style()
            if mode == "dark":
                style.configure('TFrame', background='#1e1e1e')
                style.configure('Sidebar.TFrame', background='#2b2b2b')
            else:
                style.configure('TFrame', background='white')
                style.configure('Sidebar.TFrame', background='#f5f5f5')
    
    def set_theme(self, mode: str):
        """Menu action: update theme and persist."""
        self.apply_theme(mode)
        self.settings["theme"] = mode
        self.save_data()

    def update_hotkey_registration(self):
        """Ensure global hotkey registration matches current setting."""
        enabled = bool(self.hotkey_enabled_var.get())
        if enabled and not self._hotkey_registered:
            # Use thread to mirror original behavior; prevents blocking
            try:
                self.hotkey_thread = threading.Thread(target=self._setup_hotkey, daemon=True) 
                self.hotkey_thread.start()
            except Exception:
                self._hotkey_registered = False
        elif not enabled and self._hotkey_registered:
            try:
                keyboard.remove_hotkey(self._hotkey_str)
            except Exception:
                pass
            self._hotkey_registered = False

    def on_toggle_global_hotkey(self):
        """Menu handler for toggling global hotkey."""
        self.settings["hotkey_enabled"] = bool(self.hotkey_enabled_var.get())
        self.update_hotkey_registration()
        self.save_data()

def main():
    root = tk.Tk()
    app = TodoBook(root)
    root.mainloop()

if __name__ == "__main__":
    main()