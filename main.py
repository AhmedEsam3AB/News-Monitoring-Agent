import os
import time
from dotenv import load_dotenv

from rss_fetcher import RSSFetcher
from chains import analyze_news
from memory import NewsMemory
from evaluation import evaluate_analysis

# Load env
load_dotenv()

# Configuration
RSS_URL = "https://feeds.bloomberg.com/markets/news.rss" # Or another specific one
# Note: Google News RSS or Yahoo Finance might be more "open" if Bloomberg blocks bots, 
# but let's try Bloomberg as requested. 
# Fallback: "https://finance.yahoo.com/news/rssindex"

def main():
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found in environment variables.")
        print("Please create a .env file with OPENAI_API_KEY=sk-...")
        return

    print("Initializing News Monitoring Agent...")
    memory = NewsMemory()
    fetcher = RSSFetcher(RSS_URL)
    
    print(f"Fetching news from {RSS_URL}...")
    try:
        news_items = fetcher.fetch()
    except Exception as e:
        print(f"Error fetching RSS: {e}")
        return

    print(f"Found {len(news_items)} items.")
    
    new_items_count = 0
    
    for item in news_items:
        # 1. Deduplication
        if memory.is_duplicate(item['id']):
            continue
            
        new_items_count += 1
        print(f"\nProcessing: {item['title']}")
        
        # 2. Analysis (with Retry logic for Evaluation)
        analysis = None
        max_retries = 2
        for attempt in range(max_retries):
            analysis = analyze_news(item['title'], item['summary'])
            
            # 3. Evaluation
            eval_result = evaluate_analysis(
                original_text=f"{item['title']}\n{item['summary']}",
                analysis=analysis
            )
            
            if eval_result['quality_score'] >= 7:
                break
            else:
                print(f"  - Low quality analysis ({eval_result['quality_score']}/10). Retrying... Feedback: {eval_result['feedback']}")
        
        if not analysis:
            print("  - Failed to generate valid analysis.")
            continue

        # 4. Agent Decision / Output
        score = analysis['score']
        
        # Store in Memory
        memory.add_news(item, analysis)
        
        if score >= 70:
            # ALERT
            print("\n🚨 🚨 🚨 HIGH IMPORTANCE ALERT 🚨 🚨 🚨")
            print(f"HEADLINE: {item['title']}")
            print(f"IMPORTANCE: {score}/100")
            print(f"CATEGORY: {analysis['category']}")
            print(f"SUMMARY: \n{analysis['summary']}")
            print(f"WHY IT MATTERS: {analysis['why_it_matters']}")
            print("--------------------------------------------------")
        else:
            # Normal News
            print("\n📰 Normal News Report")
            print(f"Title: {item['title']}")
            print(f"Category: {analysis['category']}")
            print(f"Importance: {score}/100")
            print(f"Summary: \n{analysis['summary']}")
            print("--------------------------------------------------")
            
    if new_items_count == 0:
        print("No new items found.")
    else:
        print(f"\nProcessed {new_items_count} new items.")

if __name__ == "__main__":
    main()
