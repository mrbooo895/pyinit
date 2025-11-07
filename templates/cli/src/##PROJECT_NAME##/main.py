import argparse
from rich.console import Console

def main():
    console = Console()
    parser = argparse.ArgumentParser(description=f"Description for ##PROJECT_NAME##.")
    parser.add_argument("--name", default="World", help="The name to greet.")
    args = parser.parse_args()
    
    console.print(f"Hello, [bold magenta]{args.name}[/bold magenta]!")
    console.print("This is the entry point for your new CLI tool.")

if __name__ == "__main__":
    main()
