# backend/app/services/analyzer.py
import re
import spacy
from collections import Counter
from datetime import date, timedelta
from sqlmodel import Session, select
from app.models import Article, Trend

nlp = spacy.load("en_core_web_sm")

def clean_text(raw_html: str) -> str:
    if not raw_html: return ""
    clean_r = re.compile('<.*?>')
    return re.sub(clean_r, '', raw_html).replace('\n', ' ').strip()

def analyze_articles(session: Session):
    # 1. Get Unprocessed Articles
    articles = session.exec(select(Article).where(Article.is_processed == False)).all()
    if not articles: return 0

    keyword_counts = Counter()
    
    for article in articles:
        full_text = f"{clean_text(article.title)} {clean_text(article.content_snippet)}" # type: ignore
        doc = nlp(full_text)
        
        # A. Extract Single Nouns (Unigrams)
        for token in doc:
            if (token.pos_ in ["NOUN", "PROPN"] and not token.is_stop and 
                token.is_alpha and 3 <= len(token.text) <= 20):
                keyword_counts.update([token.lemma_.lower()])
        
        # B. Extract Phrases (Bi-grams/Noun Chunks)
        # This catches things like "Social Media" or "Artificial Intelligence"
        for chunk in doc.noun_chunks:
            clean_chunk = chunk.text.lower().strip()
            if len(clean_chunk.split()) > 1 and not any(t.is_stop for t in chunk):
                keyword_counts.update([clean_chunk])

        article.is_processed = True
        session.add(article)

    # 2. Update Trends
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    for word, count in keyword_counts.most_common(40):
        # Get/Update Today's Record
        statement = select(Trend).where(Trend.keyword == word, Trend.trend_date == today)
        trend = session.exec(statement).first()
        
        if trend:
            trend.count += count
        else:
            trend = Trend(keyword=word, count=count, trend_date=today)
        session.add(trend)
    
    session.commit()
    return len(articles)

def get_enriched_trends(session: Session):
    """
    Calculates Velocity and groups data for the Frontend.
    """
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    # Get all trends for today and yesterday
    today_trends = session.exec(select(Trend).where(Trend.trend_date == today)).all()
    yesterday_trends = session.exec(select(Trend).where(Trend.trend_date == yesterday)).all()
    
    y_map = {t.keyword: t.count for t in yesterday_trends}
    
    results = []
    for t in today_trends:
        prev_count = y_map.get(t.keyword, 0)
        
        # Velocity Logic
        if prev_count == 0:
            velocity = "NEW"
        else:
            change = ((t.count - prev_count) / prev_count) * 100
            velocity = f"{'+' if change >= 0 else ''}{int(change)}%"
            
        results.append({
            "keyword": t.keyword,
            "count": t.count,
            "velocity": velocity,
            "is_new": prev_count == 0
        })
    
    # Sort by count (highest first)
    return sorted(results, key=lambda x: x['count'], reverse=True)