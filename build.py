import os
import sys
import shutil
import PyInstaller.__main__

def clean_build():
    """Clean up previous build artifacts"""
    for folder in ['build', 'dist']:
        if os.path.exists(folder):
            shutil.rmtree(folder)

def build():
    """Build the application using PyInstaller"""
    # Clean previous builds
    clean_build()
    
    # Get the current directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    app_dir = os.path.join(base_dir, 'app')
    
    # PyInstaller configuration
    pyi_args = [
        '--name=ScribbleThoughts',
        '--onefile',
        '--windowed',
        '--clean',
        '--noconfirm',
        f'--add-data={app_dir}{os.pathsep}app',
    ]
    
    # Add icon if exists
    icon_path = os.path.join(base_dir, 'app.ico')
    if os.path.exists(icon_path):
        pyi_args.append(f'--icon={icon_path}')
    
    # Add the main script
    pyi_args.append('run.py')
    
    print("Building executable...")
    PyInstaller.__main__.run(pyi_args)
    
    print("\nBuild complete! The executable is in the 'dist' folder.")
    
    # On Windows, open the dist folder
    if sys.platform == 'win32':
        dist_path = os.path.abspath('dist')
        os.startfile(dist_path)

if __name__ == '__main__':
    build()
