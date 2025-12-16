# News Monitoring Agent

A LangChain-powered AI agent designed to monitor financial RSS feeds, analyze market news using GPT-4o, and prioritize high-impact stories. The agent includes a self-evaluation loop to ensure quality analysis and uses vector memory to retain context.

## 🚀 Features

- **Automated RSS Monitoring**: Fetches real-time news from financial feeds (default: Bloomberg).
- **Intelligent Analysis**: Uses GPT-4o to summarize, categorize, and score news based on market impact (0-100).
- **Self-Correction Loop**: Validates its own analysis using an evaluation chain. If the quality score is low (< 7/10), it automatically retries with feedback.
- **Smart Deduplication**: Tracks processed news IDs to prevent duplicate alerts.
- **Vector Memory**: Persists important news (score ≥ 50) using FAISS for historical context.
- **Alert System**: Triggers high-priority alerts for major market-moving news (score ≥ 70).

## 🛠️ Technology Stack

- **Python 3**
- **LangChain** (Chains, Agents, Output Parsers)
- **OpenAI GPT-4o** (LLM)
- **FAISS** (Vector Store for Memory)
- **Feedparser** (RSS Ingestion)

## 📦 Installation

1. **Clone the repository**:
   ```bash
   git clone <repository_url>
   cd "News Agent"
   ```

2. **Create a virtual environment** (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment**:
   Copy the example environment file and add your OpenAI API key:
   ```bash
   cp .env.example .env
   # Edit .env and set OPENAI_API_KEY=sk-your-api-key-here
   ```

## ▶️ Usage

Run the agent using the provided shell script or directly via Python:

```bash
# Using the run script
./run.sh

# OR directly with Python
python main.py
```

## 📂 Project Structure

- `main.py`: Entry point. Handles the main loop, deduplication checks, and alert logic.
- `chains.py`: Contains LangChain definitions for **Summarization** and **Scoring** chains.
- `evaluation.py`: Logic for the "Quality Assurance" agent that grades the analysis.
- `memory.py`: Manages the local FAISS index and processed ID tracking.
- `rss_fetcher.py`: Helper class to parse RSS feeds safely.

## ⚙️ Configuration

You can customize the RSS feed URL in `main.py`:

```python
RSS_URL = "https://feeds.bloomberg.com/markets/news.rss"
```

*Note: Some RSS feeds may block automated requests. If this happens, try alternative feeds like Yahoo Finance or Google News.*
