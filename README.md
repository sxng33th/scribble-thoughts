# Todo Book

A simple desktop application for managing todos in a book-like format with chapters.

## Features

-   Create multiple chapters for organizing todos
-   Quick show/hide with `Ctrl+Space`
-   Data is automatically saved to `todo_book_data.json`
-   Simple and clean interface

## Requirements

-   Python 3.6+
-   Tkinter (usually comes with Python)

## Installation

1. Clone this repository:

    ```bash
    git clone <repository-url>
    cd stuffTodo
    ```

2. Run the application:
    ```bash
    python todo_book.py
    ```

## Usage

-   Click "+ New Chapter" to create a new chapter
-   Type a task and press Enter or click "Add" to add it to the current chapter
-   Click on a chapter in the sidebar to switch between chapters
-   Press `Ctrl+Space` to hide/show the application

## Data

Your todos are automatically saved in `todo_book_data.json` in the same directory as the script.

## Updating

To update the application:

1. Pull the latest changes:
    ```bash
    git pull
    ```
2. Restart the application

## Building an Executable

To create a standalone executable:

1. Install PyInstaller:

    ```bash
    pip install pyinstaller
    ```

2. Build the executable:

    ```bash
    pyinstaller --onefile --windowed todo_book.py
    ```

3. The executable will be in the `dist` folder
