import httpx
import os
import webbrowser
import sys
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from datetime import datetime

# Global Config
BASE_URL = "http://127.0.0.1:8000"
console = Console()

# CLEAN COLOR PALETTE - High Contrast
COLORS = {
    "research": "bright_yellow",
    "alpha": "bright_cyan", 
    "pulse": "bright_magenta",
    "discourse": "bright_green",
    "selected": "black on white",
    "header": "bright_white",
    "dim": "dim white",
}

class AxonTerminal:
    def __init__(self):
        self.articles = []
        self.selected_idx = 0
        self.brief_data = None
        self.status_msg = "ONLINE"

    def fetch_data(self):
        try:
            res = httpx.get(f"{BASE_URL}/articles?limit=60", timeout=5.0)
            self.articles = res.json()
            if self.articles and not self.brief_data:
                self.brief_data = self.articles[0]
            self.status_msg = f"ONLINE | {len(self.articles)} SIGNALS"
        except Exception as e:
            self.status_msg = f"ERROR: {str(e)[:30]}"

    def build_quadrant(self, title, category, color, start_id, visible_list):
        items = [a for a in self.articles if a.get('category') == category][:15]
        table = Table(box=None, show_header=False, padding=(0, 1), expand=True)
        table.add_column("ID", style=f"bold {color}", width=4)
        table.add_column("Source", width=10)
        table.add_column("Title", ratio=1, overflow="ellipsis")
        table.add_column("Views", width=8, justify="right")
        
        for i, item in enumerate(items):
            display_id = start_id + i
            visible_list.append(item)
            is_selected = (len(visible_list) - 1) == self.selected_idx
            title_style = self.get_engagement_style(item.get('engagement_score', 0))
            view_text = self.format_views(item.get('views', 0))
            source_style = self.get_source_color(item['source'])
            source_name = item['source'].upper()[:8].ljust(8)
            
            clean_title = item['title'].replace("\n", " ")
            for p in ["[GOOGLE]", "[DEEPMIND]", "[OPENAI]", "[NVIDIA]", "[MODAL]"]:
                clean_title = clean_title.replace(p, "").replace(p.lower(), "")
            clean_title = clean_title.strip()[:85]
            
            if is_selected:
                table.add_row(Text(f"{display_id:02}", style="black on white"), Text(source_name, style="black on white"), Text(clean_title, style="black on white"), Text(view_text, style="black on white"))
            else:
                table.add_row(Text(f"{display_id:02}", style=f"bold {color}"), Text(source_name, style=source_style), Text(clean_title, style=title_style), Text(view_text, style="dim white"))
        return Panel(table, title=f"[bold {color}]{title}[/]", border_style=color, padding=(0, 1))

    def get_engagement_style(self, score: float) -> str:
        if score >= 80: return "bold bright_white"
        elif score >= 60: return "white"
        elif score >= 40: return "dim white"
        else: return "dim dim white"

    def get_source_color(self, source: str) -> str:
        source_colors = {
            "OPENAI": "bright_green", "DEEPMIND": "bright_blue", "GOOGLE": "bright_blue", "NVIDIA": "bright_green",
            "PINECONE": "bright_cyan", "MODAL": "bright_magenta", "ANTHROPI": "bright_yellow", "ARXIV": "bright_white",
            "HACKERNE": "bright_yellow", "GITHUB": "bright_magenta", "LOBSTERS": "bright_cyan", "KARPATHY": "bright_white",
            "SIMONW": "bright_white", "REDDIT": "orange3"
        }
        return source_colors.get(source.upper()[:8], "dim white")

    def format_views(self, count: int) -> str:
        if count >= 1000: return f"{count/1000:.1f}k"
        return str(count)

    def refresh_ui(self):
        ui = Layout()
        ui.split_column(Layout(name="header", size=1), Layout(name="body", ratio=3), Layout(name="briefing", ratio=1), Layout(name="commands", size=1))
        ui["body"].split_row(Layout(name="left"), Layout(name="right"))
        ui["left"].split_column(Layout(name="q1"), Layout(name="q3"))
        ui["right"].split_column(Layout(name="q2"), Layout(name="q4"))
        time_str = datetime.now().strftime("%H:%M:%S")
        ui["header"].update(Text(f"AXON  |  {self.status_msg}  |  {time_str}", style="bold bright_white"))
        visible_list = []
        quads = [("RESEARCH", "Breakthrough", COLORS["research"], 1), ("ALPHA", "Project", COLORS["alpha"], 16), ("AI PULSE", "AI", COLORS["pulse"], 31), ("DISCOURSE", "Problem", COLORS["discourse"], 46)]
        for i, (name, cat, color, start) in enumerate(quads):
            ui[f"q{i+1}"].update(self.build_quadrant(name, cat, color, start, visible_list))
        if self.brief_data:
            content = self.brief_data.get('deep_brief', f"[bold bright_cyan]INSIGHT:[/] {self.brief_data.get('insight', 'None')}")
            content = content.replace("▶ THE SIGNAL:", "[bold bright_green]▶ THE SIGNAL:[/]").replace("◈ THE CONTEXT:", "[bold bright_yellow]◈ THE CONTEXT:[/]").replace("↳ THE PLAY:", "[bold bright_magenta]↳ THE PLAY:[/]")
            ui["briefing"].update(Panel(content, title=f"[bold bright_blue]BRIEF[/] [{self.brief_data['source'].upper()}] {self.brief_data['title'][:60]}", border_style="bright_blue", padding=(1, 2)))
        else: ui["briefing"].update(Panel("No selection", border_style="dim"))
        ui["commands"].update(Text("CMD: 1-40=Select | O=Open | X=Deep | S=Sync | Q=Quit", style="dim white"))
        return ui, visible_list

    def run(self):
        self.fetch_data()
        while True:
            layout, visible_list = self.refresh_ui()
            os.system('cls' if os.name == 'nt' else 'clear')
            console.print(layout)
            try:
                cmd = input("AXON> ").lower().strip()
                if cmd == 'q': break
                elif cmd == 's':
                    self.status_msg = "SYNCING INTELLIGENCE..."
                    with console.status("[bold green]AXON: Hunting for signals...", spinner="dots"):
                        try:
                            httpx.post(f"{BASE_URL}/ingest", timeout=120)
                            httpx.post(f"{BASE_URL}/analyze", timeout=120); self.fetch_data()
                            self.status_msg = "SYNC COMPLETE"
                        except Exception as e: self.status_msg = f"SYNC ERROR"
                elif cmd == 'o' and self.brief_data:
                    try: httpx.post(f"{BASE_URL}/articles/{self.brief_data['id']}/view")
                    except: pass
                    webbrowser.open(self.brief_data['url'])
                    import time; time.sleep(0.1); self.fetch_data() 
                elif cmd == 'x' and self.brief_data:
                    self.status_msg = "GENERATING REPORT..."
                    with console.status(f"[bold blue]AXON: Decrypting signals...", spinner="bouncingBar"):
                        try:
                            res = httpx.get(f"{BASE_URL}/brief/{self.brief_data['id']}", timeout=30).json()
                            self.brief_data['deep_brief'] = res['brief']; self.status_msg = "REPORT READY"
                        except Exception as e: self.status_msg = "BRIEFING FAILED"
                elif cmd.isdigit():
                    idx = int(cmd) - 1
                    if 0 <= idx < len(visible_list):
                        self.selected_idx = idx; self.brief_data = visible_list[idx]; self.status_msg = f"SELECTED #{cmd}"
                        try:
                            httpx.post(f"{BASE_URL}/articles/{self.brief_data['id']}/view")
                            self.brief_data['views'] = self.brief_data.get('views', 0) + 1
                        except: pass
            except KeyboardInterrupt: break
            except Exception as e: self.status_msg = f"ERROR"

if __name__ == "__main__":
    AxonTerminal().run()
