# 🧠 AXON Intelligence Platform

> **Track the world's emerging technologies, breakthroughs, and unsolved problems in real-time through a tactical terminal interface.**

Axon continuously scans global data sources, analyzes signals with AI, and presents actionable intelligence through a high-contrast command-line dashboard. Instead of browsing 50+ websites daily, open Axon and see the future forming.

---

## 📸 Screenshot



```
┌─ SCIENCE ──────────────────────────────┬─ CODE ─────────────────────────────┐
│ 01  OPENAI   Scaling social science   │ 11  GITHUB  Bolt-Inference Rust    │
│ 02  ARXIV    In-Context Autonomous    │ 12  GITHUB  Open-Source MCP        │
│ 03  ARXIV    Verified Semantic Cache  │ 13  NPM     NPMX Modern Registry   │
├─ AI ───────────────────────────────────┼─ PROBLEMS ─────────────────────────┤
│ 21  OPENAI   Introducing GPT-5.3      │ 31  REDDIT  Junior Dev Talent Gap  │
│ 22  MIT      Moltbook Social Graph    │ 32  REDDIT  Cloud Logging Costs    │
│ 23  ANTHR    Claude Computer Use v2   │ 33  HN      Vector DB Consistency  │
└─────────────────────────────────────────┴────────────────────────────────────┘
┌─ BRIEF ─────────────────────────────────────────────────────────────────────┐
│ INSIGHT: Shift from passive inference to active OS-level agency.           │
│ Opportunity for specialized 'Air-gap' agent containers.                    │
└─────────────────────────────────────────────────────────────────────────────┘
CMD: 1-40=Select | O=Open | X=Deep | S=Sync | Q=Quit
AXON>

```

---

## 🎯 What This Does

### The Problem
The future is being built across:
- Research papers (ArXiv, academic journals)
- Developer activity (GitHub, tech forums)
- AI breakthroughs (company announcements)
- Community discussions (Hacker News, Reddit)

But it's **fragmented, noisy, and overwhelming**.

### The Solution
Axon is your **intelligence layer** that:

1. **Ingests** data from multiple sources every 6 hours
2. **Processes** and categorizes signals automatically
3. **Synthesizes** insights using AI (Groq LLM)
4. **Presents** everything in a clean, scannable terminal UI
5. **Tracks** trends and momentum over time

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    DATA SOURCES                             │
├─────────────────────────────────────────────────────────────┤
│  • Hacker News     → Technologies, Problems                 │
│  • ArXiv           → Research Papers, Breakthroughs         │
│  • GitHub Trending → Open Source Projects                   │
│  • Reddit          → Community Problems & Discussions       │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│         DATA INGESTION SERVICE (Python Scrapers)            │
├─────────────────────────────────────────────────────────────┤
│  1. Fetch raw data from APIs and web pages                  │
│  2. Extract clean text (bypass paywalls, ads)              │
│  3. Categorize by type: Science, Code, AI, Problems        │
│  4. Calculate importance scores                             │
│  5. Store structured data                                   │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                DATABASE (PostgreSQL)                        │
├─────────────────────────────────────────────────────────────┤
│  articles                                                   │
│  ├─ id, title, url, content                                │
│  ├─ source, category                                       │
│  ├─ view_count, created_at                                 │
│  └─ insight (AI-generated summary)                         │
│                                                             │
│  trends                                                     │
│  └─ keyword, count, momentum, date                         │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│              BACKEND API (FastAPI)                          │
├─────────────────────────────────────────────────────────────┤
│  GET  /articles?limit=60&category=AI                        │
│  POST /ingest          → Trigger all scrapers               │
│  POST /analyze         → Generate AI insights               │
│  GET  /brief/{id}      → Deep analysis via Groq             │
│  GET  /trends          → Keyword momentum tracking          │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│           FRONTEND (Rich Terminal Interface)                │
├─────────────────────────────────────────────────────────────┤
│  • 4-quadrant layout (Science, Code, AI, Problems)         │
│  • Live selection with keyboard navigation                  │
│  • AI-powered briefings on demand                          │
│  • One-command sync and analysis                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL (Docker recommended)
- Groq API key (for AI insights)

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/axon-intelligence.git
cd axon-intelligence
```

### 2. Set Up PostgreSQL

**Option A: Docker (Recommended)**
```bash
docker run -d \
  --name axon-postgres \
  -e POSTGRES_USER=axon \
  -e POSTGRES_PASSWORD=axon123 \
  -e POSTGRES_DB=axon_db \
  -p 5432:5432 \
  postgres:15-alpine
```

**Option B: Local Installation**
```bash
# Mac
brew install postgresql
createdb axon_db

# Ubuntu
sudo apt install postgresql
sudo -u postgres createdb axon_db
```

### 3. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add:
DATABASE_URL=postgresql://axon:axon123@localhost:5432/axon_db
GROQ_API_KEY=your_groq_api_key_here
```

Get a free Groq API key: https://console.groq.com

### 5. Initialize Database

```bash
# Run migrations
python -c "from database.connection import init_db; init_db()"
```

### 6. Run First Data Sync

```bash
# Start the backend API
python backend/main.py

# In another terminal, trigger data ingestion
curl -X POST http://127.0.0.1:8000/ingest
curl -X POST http://127.0.0.1:8000/analyze
```

This will:
- Scrape Hacker News, ArXiv, GitHub
- Store articles in database
- Generate AI insights

### 7. Launch Terminal Interface

```bash
python terminal/axon_terminal.py
```

---

## 🎮 Usage

### Terminal Commands

| Command | Action |
|---------|--------|
| `1-40` | Select an article by number |
| `O` | Open selected article in browser |
| `X` | Generate deep AI analysis (3-point breakdown) |
| `S` | Sync - fetch new data from all sources |
| `Q` | Quit |

### Workflow Example

```bash
AXON> 11              # Select article #11
AXON> X               # Get deep AI analysis
AXON> O               # Open in browser to read full article
AXON> S               # Sync to get latest data
```

---

## 📂 Project Structure

```
axon-intelligence/
├── backend/
│   ├── main.py                  # FastAPI server
│   ├── scrapers/
│   │   ├── hackernews.py        # Hacker News scraper
│   │   ├── arxiv.py             # ArXiv research papers
│   │   ├── github.py            # GitHub trending repos
│   │   └── reddit.py            # Reddit discussions
│   ├── models/
│   │   └── models.py            # Database models (SQLAlchemy)
│   ├── database/
│   │   └── connection.py        # PostgreSQL connection
│   └── ai/
│       └── groq_client.py       # AI insight generation
├── terminal/
│   └── axon_terminal.py         # Rich-based TUI
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment template
└── README.md                    # This file
```

---

## 🗃️ Data Sources

### 1. **Hacker News** (Category: Science, AI, Problems)
- **What**: Tech news, startup discussions, Show HN projects
- **API**: Official HN API (https://github.com/HackerNews/API)
- **Update Frequency**: Every 6 hours
- **Signal Quality**: High - community-filtered content

### 2. **ArXiv** (Category: Science)
- **What**: Research papers in CS, AI, Physics, Math
- **API**: ArXiv API (https://arxiv.org/help/api)
- **Update Frequency**: Daily
- **Signal Quality**: Very High - peer-reviewed research

### 3. **GitHub Trending** (Category: Code)
- **What**: Trending repositories, new frameworks, dev tools
- **Method**: Web scraping (https://github.com/trending)
- **Update Frequency**: Every 6 hours
- **Signal Quality**: High - developer activity indicator

### 4. **Reddit** (Category: Problems)
- **What**: Community discussions from r/programming, r/MachineLearning
- **API**: Reddit API (requires OAuth)
- **Update Frequency**: Every 12 hours
- **Signal Quality**: Medium - user-generated content

---

## 🤖 AI Integration (Groq)

Axon uses **Groq's LLaMA models** to:

1. **Generate Quick Insights** (automatic on ingestion)
   - One-sentence strategic summary
   - "Why does this matter?"
   
2. **Deep Briefings** (on-demand via `X` command)
   - Technical Primitive: What is the core innovation?
   - Market Impact: How does this change the game?
   - Opportunity: What can be built with this?

3. **Cross-Signal Synthesis** (coming soon)
   - Connect two signals: "How could [Science Paper #3] solve [Problem #17]?"

### Why Groq?
- **Fast**: Sub-second inference (perfect for terminal UX)
- **Free tier**: 14,400 requests/day
- **Quality**: LLaMA 3.1 70B performs well on technical analysis

---

## 🔧 Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/axon_db

# AI
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxx

# Scraping
SCRAPE_INTERVAL_HOURS=6
USER_AGENT=AxonBot/1.0

# API
API_HOST=0.0.0.0
API_PORT=8000
```

### Customization

**Add New Data Sources:**
1. Create scraper in `backend/scrapers/your_source.py`
2. Inherit from `BaseScraper` class
3. Register in `backend/main.py`

**Change Categories:**
Edit `CATEGORY_KEYWORDS` in `backend/scrapers/categorizer.py`

**Adjust Terminal Colors:**
Modify `COLORS` dict in `terminal/axon_terminal.py`

---

## 📊 Database Schema

### `articles` table
```sql
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    url VARCHAR(1000),
    content TEXT,
    source VARCHAR(100),        -- 'hackernews', 'arxiv', 'github'
    category VARCHAR(100),      -- 'Breakthrough', 'Project', 'AI', 'Problem'
    insight TEXT,               -- AI-generated summary
    view_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### `trends` table
```sql
CREATE TABLE trends (
    id SERIAL PRIMARY KEY,
    keyword VARCHAR(200) UNIQUE,
    count INTEGER DEFAULT 1,
    trend_date DATE DEFAULT NOW()
);
```

---

## 🛠️ Development

### Running in Dev Mode

```bash
# Backend with auto-reload
uvicorn backend.main:app --reload --port 8000

# Terminal in debug mode
python terminal/axon_terminal.py --debug
```

### Adding a New Scraper

```python
# backend/scrapers/your_source.py
from .base import BaseScraper

class YourSourceScraper(BaseScraper):
    def fetch(self):
        # Fetch data from API/website
        pass
    
    def parse(self, data):
        # Extract articles
        pass
    
    def categorize(self, article):
        # Assign category
        return "AI"  # or "Science", "Code", "Problem"
```

Register in `backend/main.py`:
```python
from scrapers.your_source import YourSourceScraper

@app.post("/ingest")
async def ingest():
    scrapers = [
        HackerNewsScraper(),
        ArxivScraper(),
        YourSourceScraper(),  # Add here
    ]
    # ...
```

---

## 🚢 Deployment

### Deploy Backend (Render.com)

```yaml
# render.yaml
services:
  - type: web
    name: axon-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: axon-postgres
          property: connectionString
      - key: GROQ_API_KEY
        sync: false
```

Push to GitHub, connect to Render, and deploy!

### Use Terminal Anywhere

The terminal connects to your deployed backend:
```bash
# Update terminal/axon_terminal.py
BASE_URL = "https://your-axon-backend.onrender.com"
```

---

## 🤝 Contributing

We welcome contributions! Here's how:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/new-scraper`
3. **Make your changes**
4. **Test thoroughly**: `pytest tests/`
5. **Submit a pull request**

### Contribution Ideas
- [ ] Add new data sources (Product Hunt, TechCrunch RSS)
- [ ] Improve AI prompts for better insights
- [ ] Add search/filter functionality
- [ ] Create web dashboard (Next.js)
- [ ] Add bookmarking system
- [ ] Trend prediction algorithm
- [ ] Multi-language support

---

## 📜 License

MIT License - See [LICENSE](LICENSE) file

---

## 🙏 Credits

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Rich](https://rich.readthedocs.io/) - Terminal UI framework
- [SQLAlchemy](https://www.sqlalchemy.org/) - Database ORM
- [Groq](https://groq.com/) - Fast AI inference
- [PostgreSQL](https://www.postgresql.org/) - Database

Inspired by the need to stay ahead in a rapidly evolving tech landscape.

---

## 📧 Contact

Questions? Open an issue or reach out:
- GitHub Issues: https://github.com/bemnetmussa/axon/issues
- Twitter: @https://x.com/BemnetMussa

---

**Built for curious builders who want to see the future forming. 🚀**
