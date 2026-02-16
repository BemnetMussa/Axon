import httpx
import os
import webbrowser
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.markdown import Markdown

console = Console()
BASE_URL = "http://127.0.0.1:8000"

def build_silo_panel(title, color, articles, start_idx, limit=2):
    table = Table(box=None, show_header=False, padding=(0, 1))
    table.add_column("ID", style="dim", width=4)
    table.add_column("Data")


    current_idx = start_idx
    for a in articles[:limit]:
        # Tag next to title!
        title_line = f"[bold white]{a['title']}[/] [bold {color}][{a['source']}][/]"
        table.add_row(f"[{current_idx}]", title_line)
        insight = a.get('insight') or "No insight available."
        table.add_row("", f"[dim italic gray70]💡 {insight}[/]\n")
        current_idx += 1
        
    return Panel(table, title=f"[bold {color}] {title} [/]", border_style=color, width=70), current_idx

def deep_brief(article_id):
    with console.status("[bold yellow]Generating AI Deep Brief...[/]"):
        try:
            res = httpx.get(f"{BASE_URL}/brief/{article_id}", timeout=30.0).json()
            console.print(Panel(Markdown(res['brief']), title=f"[bold cyan]DEEP BRIEF: {res['title']}[/]", border_style="cyan"))
        except Exception as e:
            console.print(f"[red]Failed to generate brief:[/] {e}")
    input("\nPress Enter to return...")

def main():
    focus_category = None
    
    while True:
        try:
            os.system('cls' if os.name == 'nt' else 'clear')
            console.print(Panel("[bold yellow]AXON STRATEGIC RADAR[/] | [bold green]SYSTEM: ACTIVE[/] | [cyan]LLM: GROQ[/]", border_style="yellow"))
            
            articles = httpx.get(f"{BASE_URL}/articles?limit=100").json()
            
            silo_defs = [
                ("BREAKTHROUGHS", "Breakthrough", "yellow"),
                ("RISING TECH", "Project", "cyan"),
                ("AI & MODELS", "AI", "magenta"),
                ("  OPPORTUNITY GAPS", "Problem", "green")
            ]

            flat_list = []
            next_id = 1
            panels = []

            # Filter logic (Grid vs Bucket view)
            for title, cat, color in silo_defs:
                items = [a for a in articles if a['category'] == cat]
                if focus_category and focus_category != cat:
                    continue # Skip if we are focusing on another bucket
                
                limit = 15 if focus_category else 2 # Show more if focused
                for item in items[:limit]: flat_list.append(item)
                
                p, next_id = build_silo_panel(title, color, items, next_id, limit)
                panels.append(p)

            # Draw UI
            if focus_category:
                console.print(panels[0]) # Print single bucket
            else:
                # Print 2x2 Grid
                console.print(Columns([panels[0], panels[1]]))
                console.print(Columns([panels[2], panels[3]]))

            console.print(f"\n[bold yellow]CMDS:[/] [white]1-{len(flat_list)}[/] (Open) | [white]x1-x{len(flat_list)}[/] (Deep Brief) | [white]b1-b4[/] (Focus Bucket) | [white]0[/] (Home Grid) | [white]s[/] (Sync) | [white]q[/] (Quit)")
            
            choice = input("\nAXON > ").lower().strip()
            
            if choice == 'q': break
            elif choice == 's':
                with console.status("[bold yellow]Scraping & Synthesizing AI Insights...[/]"):
                    httpx.post(f"{BASE_URL}/ingest", timeout=120)
                    httpx.post(f"{BASE_URL}/analyze", timeout=120)
            elif choice == '0':
                focus_category = None
            elif choice.startswith('b') and len(choice) == 2 and choice[1].isdigit():
                idx = int(choice[1]) - 1
                if 0 <= idx < 4: focus_category = silo_defs[idx][1]
            elif choice.startswith('x') and len(choice) > 1 and choice[1:].isdigit():
                idx = int(choice[1:]) - 1
                if 0 <= idx < len(flat_list): deep_brief(flat_list[idx]['id'])
            elif choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(flat_list): webbrowser.open(flat_list[idx]['url'])
                
        except Exception as e:
            console.print(f"[red]System Error:[/] {e}")
            input("Press Enter to retry...")

if __name__ == "__main__":
    main()
