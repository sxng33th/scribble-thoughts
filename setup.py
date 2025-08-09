from setuptools import setup, find_packages

setup(
    name="ScribbleThoughts",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'keyboard>=0.13.5',
        'sv-ttk>=2.5.0',
        'pyinstaller>=5.0',
    ],
    entry_points={
        'console_scripts': [
            'scribble-thoughts=app.__main__:main',
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A simple todo and clipboard manager",
    keywords="todo clipboard manager",
    url="https://github.com/yourusername/scribble-thoughts",
    python_requires='>=3.8',
)
