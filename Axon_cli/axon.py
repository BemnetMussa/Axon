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
    "science": "bright_yellow",
    "code": "bright_cyan", 
    "ai": "bright_magenta",
    "problems": "bright_green",
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
        """Fetch data from backend"""
        try:
            res = httpx.get(f"{BASE_URL}/articles?limit=60", timeout=5.0)
            self.articles = res.json()
            if self.articles and not self.brief_data:
                self.brief_data = self.articles[0]
            self.status_msg = f"ONLINE | {len(self.articles)} SIGNALS"
        except Exception as e:
            self.status_msg = f"ERROR: {str(e)[:30]}"

    # terminal/tui.py

def build_quadrant(self, title, category, color, start_id, visible_list):
    """Build one quadrant with engagement indicators"""
    items = [a for a in self.articles if a.get('category') == category][:12]  # 12 now!
    
    table = Table(box=None, show_header=False, padding=(0, 1), expand=True)
    table.add_column("ID", style=f"bold {color}", width=4)
    table.add_column("Source", width=10)
    table.add_column("Title", ratio=1)
    table.add_column("Views", width=8, justify="right")
    
    for i, item in enumerate(items):
        display_id = start_id + i
        visible_list.append(item)
        
        is_selected = (len(visible_list) - 1) == self.selected_idx
        
        # Get engagement metrics
        views = item.get('views', 0)
        engagement = item.get('engagement_score', 0)
        
        # Color intensity based on engagement
        title_style = self.get_engagement_style(engagement)
        view_text = self.format_views(views)
        
        # Source with brand color
        source_style = self.get_source_color(item['source'])
        source = item['source'].upper()[:8].ljust(8)
        
        if is_selected:
            # Selected row - high contrast
            table.add_row(
                Text(f"{display_id:02}", style="black on white"),
                Text(source, style="black on white"),
                Text(item['title'][:45], style="black on white"),
                Text(view_text, style="black on white")
            )
        else:
            # Normal row with engagement styling
            table.add_row(
                Text(f"{display_id:02}", style=f"bold {color}"),
                Text(source, style=source_style),
                Text(item['title'][:45], style=title_style),
                Text(view_text, style="dim white")
            )
    
        return Panel(table, title=f"[bold {color}]{title}[/]", border_style=color, padding=(0, 1))

    def get_engagement_style(self, score: float) -> str:
        """Return style based on engagement score"""
        if score >= 80:
            return "bold bright_white"  # HOT
        elif score >= 60:
            return "white"              # Warm
        elif score >= 40:
            return "dim white"          # Normal
        else:
            return "dim dim white"      # Cold

    def get_source_color(self, source: str) -> str:
        """Brand colors for sources"""
        source_colors = {
            "OPENAI": "bright_white",
            "ARXIV": "bright_blue",
            "MIT TECH": "bright_red",
            "HACKERNE": "bright_yellow",  # HN
            "NEWS.YCO": "bright_yellow",  # HN
            "REDDIT": "bright_yellow",    # Orange-ish
            "GITHUB": "bright_magenta",
        }
        return source_colors.get(source.upper()[:8], "dim white")

    def format_views(self, count: int) -> str:
        """Format view count nicely"""
        if count >= 1000:
            return f"{count/1000:.1f}k"
        return str(count)

    def refresh_ui(self):
        """Main layout"""
        ui = Layout()
        
        # MORE SPACE FOR ARTICLES
        ui.split_column(
            Layout(name="header", size=1),
            Layout(name="body", size=20),    # BIGGER
            Layout(name="briefing", size=8),
            Layout(name="commands", size=1)  # MERGED WITH INPUT
        )
        
        ui["body"].split_row(Layout(name="left"), Layout(name="right"))
        ui["left"].split_column(Layout(name="q1"), Layout(name="q3"))
        ui["right"].split_column(Layout(name="q2"), Layout(name="q4"))

        # CLEAN HEADER - ONE LINE
        time_str = datetime.now().strftime("%H:%M:%S")
        ui["header"].update(
            Text(f"AXON  |  {self.status_msg}  |  {time_str}", style="bold bright_white")
        )

        # QUADRANTS - SIMPLE NAMES
        visible_list = []
        quads = [
            ("SCIENCE", "Breakthrough", COLORS["science"], 1),
            ("CODE", "Project", COLORS["code"], 11),
            ("AI", "AI", COLORS["ai"], 21),
            ("PROBLEMS", "Problem", COLORS["problems"], 31)
        ]

        for i, (name, cat, color, start) in enumerate(quads):
            ui[f"q{i+1}"].update(self.build_quadrant(name, cat, color, start, visible_list))

        # BRIEFING - CLEAN
        if self.brief_data:
            if 'deep_brief' in self.brief_data:
                content = self.brief_data['deep_brief']
            else:
                insight = self.brief_data.get('insight', 'No insight available')
                content = f"[bold]INSIGHT:[/] {insight}"
            
            ui["briefing"].update(Panel(
                content,
                title=f"[bold bright_blue]BRIEF[/] [{self.brief_data['source'].upper()}] {self.brief_data['title'][:50]}",
                border_style="bright_blue",
                padding=(0, 1)
            ))
        else:
            ui["briefing"].update(Panel("No selection", border_style="dim"))

        # COMMANDS - NO GAP NOW
        ui["commands"].update(
            Text("CMD: 1-40=Select | O=Open | X=Deep | S=Sync | Q=Quit", style="dim white")
        )
        
        return ui, visible_list

    def run(self):
        self.fetch_data()
        
        while True:
            layout, visible_list = self.refresh_ui()
            
            # Clear and render
            os.system('cls' if os.name == 'nt' else 'clear')
            console.print(layout)
            
            # INPUT RIGHT AFTER COMMANDS (NO GAP)
            try:
                cmd = input("AXON> ").lower().strip()
                
                if cmd == 'q':
                    break
                    
                elif cmd == 's':
                    self.status_msg = "SYNCING..."
                    httpx.post(f"{BASE_URL}/ingest", timeout=120)
                    httpx.post(f"{BASE_URL}/analyze", timeout=120)
                    self.fetch_data()
                    
                elif cmd == 'o' and self.brief_data:
                    webbrowser.open(self.brief_data['url'])
                    
                elif cmd == 'x' and self.brief_data:
                    self.status_msg = "GENERATING BRIEF..."
                    res = httpx.get(f"{BASE_URL}/brief/{self.brief_data['id']}", timeout=30).json()
                    self.brief_data['deep_brief'] = res['brief']
                    self.status_msg = "READY"
                    
                elif cmd.isdigit():
                    idx = int(cmd) - 1
                    if 0 <= idx < len(visible_list):
                        self.selected_idx = idx
                        self.brief_data = visible_list[idx]
                        self.status_msg = f"SELECTED #{cmd}"
                        
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.status_msg = f"ERROR: {str(e)[:20]}"

if __name__ == "__main__":
    AxonTerminal().run()       
