import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
from datetime import datetime

class TodoBook:
    def __init__(self, root):
        self.root = root
        self.root.title("Todo Book")
        self.root.geometry("800x600")
        
        # Initialize data
        self.chapters = ["General"]
        self.current_chapter = "General"
        self.todos = {"General": []}
        
        # Load saved data
        self.load_data()
        
        # Create UI
        self.setup_ui()
        
        # Bind global hotkey (Ctrl+Space)
        self.root.bind("<Control-space>", self.toggle_window)
        
        # Keep track of window state
        self.window_visible = True
        
    def setup_ui(self):
        # Main container
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Header
        header = ttk.Frame(self.main_frame)
        header.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky="ew")
        
        ttk.Label(header, text="My Todo Book", font=('Arial', 16, 'bold')).pack(side=tk.LEFT)
        ttk.Button(header, text="×", command=self.toggle_window, width=3).pack(side=tk.RIGHT)
        
        # Sidebar
        sidebar = ttk.Frame(self.main_frame, width=200, style='Sidebar.TFrame')
        sidebar.grid(row=1, column=0, sticky="ns", padx=(0, 10))
        
        ttk.Label(sidebar, text="Chapters", font=('Arial', 10, 'bold')).pack(pady=(0, 5), anchor='w')
        
        # Chapter list
        self.chapter_list = tk.Listbox(sidebar, selectmode=tk.SINGLE, height=15)
        self.chapter_list.pack(fill=tk.X, pady=(0, 10))
        self.update_chapter_list()
        
        ttk.Button(sidebar, text="+ New Chapter", command=self.add_chapter).pack(fill=tk.X)
        
        # Main content
        content = ttk.Frame(self.main_frame)
        content.grid(row=1, column=1, sticky="nsew")
        
        # Current chapter label
        self.current_chapter_label = ttk.Label(content, text=f"Chapter: {self.current_chapter}", 
                                            font=('Arial', 12, 'bold'))
        self.current_chapter_label.pack(anchor='w', pady=(0, 10))
        
        # Add todo frame
        add_frame = ttk.Frame(content)
        add_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.todo_entry = ttk.Entry(add_frame)
        self.todo_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.todo_entry.bind("<Return>", lambda e: self.add_todo())
        
        ttk.Button(add_frame, text="Add", command=self.add_todo).pack(side=tk.LEFT)
        
        # Todo list
        self.todo_list = tk.Listbox(content, selectmode=tk.SINGLE, height=20)
        self.todo_list.pack(fill=tk.BOTH, expand=True)
        self.update_todo_list()
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
        
        # Bind events
        self.chapter_list.bind('<<ListboxSelect>>', self.on_chapter_select)
        
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
        
        # Select current chapter
        if self.current_chapter in self.chapters:
            idx = self.chapters.index(self.current_chapter)
            self.chapter_list.selection_set(idx)
    
    def on_chapter_select(self, event):
        selection = self.chapter_list.curselection()
        if selection:
            self.current_chapter = self.chapters[selection[0]]
            self.current_chapter_label.config(text=f"Chapter: {self.current_chapter}")
            self.update_todo_list()
    
    def add_todo(self, event=None):
        text = self.todo_entry.get().strip()
        if text:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            self.todos[self.current_chapter].append({"text": text, "completed": False, "created_at": timestamp})
            self.todo_entry.delete(0, tk.END)
            self.update_todo_list()
            self.save_data()
    
    def update_todo_list(self):
        self.todo_list.delete(0, tk.END)
        for todo in self.todos.get(self.current_chapter, []):
            prefix = "[✓] " if todo["completed"] else "[ ] "
            self.todo_list.insert(tk.END, prefix + todo["text"])
    
    def toggle_todo(self, index):
        if 0 <= index < len(self.todos[self.current_chapter]):
            self.todos[self.current_chapter][index]["completed"] = \
                not self.todos[self.current_chapter][index]["completed"]
            self.update_todo_list()
            self.save_data()
    
    def toggle_window(self, event=None):
        if self.window_visible:
            self.root.withdraw()  # Hide window
        else:
            self.root.deiconify()  # Show window
            self.root.lift()
            self.root.focus_force()
        self.window_visible = not self.window_visible
    
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
    
    # Set style
    style = ttk.Style()
    style.configure('TFrame', background='white')
    style.configure('Sidebar.TFrame', background='#f0f0f0')
    
    app = TodoBook(root)
    root.mainloop()

if __name__ == "__main__":
    main()
