import trafilatura
import requests
from datetime import datetime, timedelta
import re

def clean_html(raw_html):
    """Remove HTML tags from a string"""
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

def get_yahoo_finance_news(symbol):
    """Fetch news from Yahoo Finance"""
    try:
        url = f"https://finance.yahoo.com/quote/{symbol}/news"
        downloaded = trafilatura.fetch_url(url)
        news_items = []

        if downloaded:
            text_content = trafilatura.extract(downloaded)
            if text_content:
                # Split content into potential news items
                sections = text_content.split('\n\n')
                for section in sections:
                    if len(section.strip()) > 50:  # Filter out short sections
                        # Look for timestamp patterns
                        timestamp_match = re.search(r'\d{1,2}:\d{2}|\d{1,2} hours ago|yesterday|\d{1,2} days ago', section.lower())
                        if timestamp_match:
                            news_items.append({
                                'title': section.split('\n')[0],
                                'summary': section,
                                'timestamp': timestamp_match.group()
                            })
                            if len(news_items) >= 5:  # Limit to 5 most recent news
                                break

        return news_items
    except Exception as e:
        print(f"Error fetching news: {str(e)}")
        return []

def analyze_sentiment(text):
    """Simple sentiment analysis based on keyword matching"""
    positive_words = set(['surge', 'gain', 'up', 'rise', 'positive', 'profit', 'growth', 'strong',
                         'bullish', 'outperform', 'beat', 'exceeded', 'higher', 'increase'])
    negative_words = set(['drop', 'down', 'fall', 'negative', 'loss', 'weak', 'bearish',
                         'underperform', 'miss', 'lower', 'decrease', 'concern'])

    text = text.lower()
    words = set(text.split())

    positive_count = len(words.intersection(positive_words))
    negative_count = len(words.intersection(negative_words))

    if positive_count > negative_count:
        return 'Positive'
    elif negative_count > positive_count:
        return 'Negative'
    else:
        return 'Neutral'

def get_news_with_sentiment(symbol):
    """Get news articles with sentiment analysis"""
    news_items = get_yahoo_finance_news(symbol) or []  # Ensure we always have a list

    for item in news_items:
        item['sentiment'] = analyze_sentiment(item['summary'])

    return news_items