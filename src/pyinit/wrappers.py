import sys
from rich.console import Console

console = Console()

def error_handling(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except (KeyboardInterrupt, EOFError):
            console.print(f"[red]\n-> [ERROR]: Interrupted By The User")
            sys.exit(1)
    return wrapper
