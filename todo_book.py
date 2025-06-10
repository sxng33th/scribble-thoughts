import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
import keyboard
import threading
from datetime import datetime

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
        self.todos = {"General": []}
        
        self.load_data()
        self.setup_ui()
        
        # Set up global hotkey in a separate thread
        self.hotkey_thread = threading.Thread(target=self._setup_hotkey, daemon=True)
        self.hotkey_thread.start()
        
        self.window_visible = True
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def _setup_hotkey(self):
        """Set up the global hotkey in a separate thread"""
        keyboard.add_hotkey('ctrl+space', self.toggle_window_from_thread)
        
    def toggle_window_from_thread(self):
        """Wrapper to safely call toggle_window from keyboard thread"""
        self.root.after(0, self.toggle_window)
    
    def on_close(self):
        """Clean up resources when closing the window"""
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
        # Configure style
        style = ttk.Style()
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
        self.chapter_list = tk.Listbox(sidebar, selectmode=tk.SINGLE, height=10, 
                                     font=('Segoe UI', 8), borderwidth=1, 
                                     relief='solid', highlightthickness=0)
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
        
        # Todo list with smaller font
        self.todo_list = tk.Listbox(content, selectmode=tk.SINGLE, height=15, 
                                  font=('Segoe UI', 8), borderwidth=1, 
                                  relief='solid', highlightthickness=0)
        self.todo_list.pack(fill=tk.BOTH, expand=True)
        self.update_todo_list()
        
        # Bind double click to toggle todo
        self.todo_list.bind("<Double-Button-1>", self.on_todo_double_click)
        
        # Bind events
        self.chapter_list.bind('<<ListboxSelect>>', self.on_chapter_select)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
    
    def add_chapter(self):
        chapter = simpledialog.askstring("New Chapter", "Enter chapter name:")
        if chapter and chapter.strip() and chapter not in self.chapters:
            self.chapters.append(chapter)
            self.todos[chapter] = []
            self.update_chapter_list()
            self.save_data()
    
    def update_chapter_list(self):
        self.chapter_list.delete(0, tk.END)
        for chapter in self.chapters:
            self.chapter_list.insert(tk.END, chapter)
        
        if self.current_chapter in self.chapters:
            idx = self.chapters.index(self.current_chapter)
            self.chapter_list.selection_set(idx)
            self.chapter_list.see(idx)
    
    def on_chapter_select(self, event):
        selection = self.chapter_list.curselection()
        if selection:
            self.current_chapter = self.chapters[selection[0]]
            self.current_chapter_label.config(text=f"{self.current_chapter}")
            self.update_todo_list()
    
    def add_todo(self, event=None):
        text = self.todo_entry.get().strip()
        if text:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            self.todos[self.current_chapter].append({
                "text": text,
                "completed": False,
                "created_at": timestamp
            })
            self.todo_entry.delete(0, tk.END)
            self.update_todo_list()
            self.save_data()
    
    def update_todo_list(self):
        self.todo_list.delete(0, tk.END)
        for todo in self.todos.get(self.current_chapter, []):
            prefix = "[✓] " if todo["completed"] else "[ ] "
            self.todo_list.insert(tk.END, prefix + todo["text"])
    
    def on_todo_double_click(self, event):
        selection = self.todo_list.curselection()
        if selection:
            self.toggle_todo(selection[0])
    
    def toggle_todo(self, index):
        if 0 <= index < len(self.todos[self.current_chapter]):
            self.todos[self.current_chapter][index]["completed"] = not self.todos[self.current_chapter][index]["completed"]
            self.update_todo_list()
            self.save_data()
    
    def save_data(self):
        data = {
            "chapters": self.chapters,
            "current_chapter": self.current_chapter,
            "todos": self.todos
        }
        with open("todo_book_data.json", "w") as f:
            json.dump(data, f, indent=2)
    
    def load_data(self):
        if os.path.exists("todo_book_data.json"):
            try:
                with open("todo_book_data.json", "r") as f:
                    data = json.load(f)
                self.chapters = data.get("chapters", ["General"])
                self.current_chapter = data.get("current_chapter", "General")
                self.todos = data.get("todos", {"General": []})
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load data: {e}")

def main():
    root = tk.Tk()
    style = ttk.Style()
    style.configure('TFrame', background='white')
    style.configure('Sidebar.TFrame', background='#f5f5f5')
    
    app = TodoBook(root)
    root.mainloop()

if __name__ == "__main__":
    main()