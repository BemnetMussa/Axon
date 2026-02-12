# backend/app/services/analyzer.py
import re
import spacy
from collections import Counter
from datetime import date
from sqlmodel import Session, select
from app.models import Article, Trend

nlp = spacy.load("en_core_web_sm")

def clean_text(raw_html: str) -> str:
    """
    Strips HTML tags and removes weird encoded junk.
    """
    if not raw_html:
        return ""
    # 1. Remove HTML tags like <img...>, <div...>, etc.
    clean_r = re.compile('<.*?>')
    text = re.sub(clean_r, '', raw_html)
    
    # 2. Basic cleanup of weird whitespace
    text = text.replace('\n', ' ').strip()
    return text

def analyze_articles(session: Session):
    print("🧠 Starting Smart Analysis...")
    
    statement = select(Article).where(Article.is_processed == False)
    articles = session.exec(statement).all()
    
    if not articles:
        print("zzz No new articles.")
        return 0

    keyword_counts = Counter()
    
    for article in articles:
        # CLEAN THE TEXT before it hits the Brain
        cleaned_title = clean_text(article.title)
        cleaned_snippet = clean_text(article.content_snippet)
        full_text = f"{cleaned_title} {cleaned_snippet}"
        
        doc = nlp(full_text)
        
        tokens = []
        for token in doc:
            # THE JUNIOR GENIUS FILTER:
            # 1. Must be a Noun or Proper Noun
            # 2. No stop words or punctuation
            # 3. MUST be alphabetic (removes height="360" and Base64 junk)
            # 4. Length between 3 and 20 chars (skips "ai" or "supercalifragilistic...")
            if (token.pos_ in ["NOUN", "PROPN"] and 
                not token.is_stop and 
                not token.is_punct and 
                token.is_alpha and 
                3 <= len(token.text) <= 20):
                
                tokens.append(token.lemma_.lower())
        
        keyword_counts.update(tokens)
        article.is_processed = True
        session.add(article)

    # Save Trends
    today = date.today()
    for word, count in keyword_counts.most_common(20):
        statement = select(Trend).where(Trend.keyword == word, Trend.trend_date == today)
        trend = session.exec(statement).first()
        
        if trend:
            trend.count += count
        else:
            trend = Trend(keyword=word, count=count, trend_date=today)
        session.add(trend)
    
    session.commit()
    print("✅ Clean analysis complete.")
    return len(articles)