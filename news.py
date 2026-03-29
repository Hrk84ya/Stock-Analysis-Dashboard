import trafilatura
import re


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
                        timestamp_match = re.search(
                            r'\d{1,2}:\d{2}|\d{1,2} hours ago|yesterday|\d{1,2} days ago',
                            section.lower()
                        )
                        if timestamp_match:
                            news_items.append({
                                'title': section.split('\n')[0],
                                'summary': section,
                                'timestamp': timestamp_match.group()
                            })
                            if len(news_items) >= 5:
                                break

        return news_items
    except Exception as e:
        print(f"Error fetching news: {str(e)}")
        return []


def analyze_sentiment(text):
    """Simple sentiment analysis based on keyword matching with basic negation handling"""
    positive_words = {
        'surge', 'gain', 'up', 'rise', 'positive', 'profit', 'growth', 'strong',
        'bullish', 'outperform', 'beat', 'exceeded', 'higher', 'increase',
        'rally', 'upgrade', 'record', 'boom', 'soar',
    }
    negative_words = {
        'drop', 'down', 'fall', 'negative', 'loss', 'weak', 'bearish',
        'underperform', 'miss', 'lower', 'decrease', 'concern',
        'decline', 'crash', 'plunge', 'downgrade', 'slump',
    }
    negation_words = {'not', "n't", 'no', 'never', 'neither', 'nor', 'hardly', 'barely'}

    words = text.lower().split()
    positive_count = 0
    negative_count = 0

    for i, word in enumerate(words):
        # Check if the previous word is a negation
        negated = i > 0 and any(words[i - 1].endswith(n) for n in negation_words)

        if word in positive_words:
            if negated:
                negative_count += 1
            else:
                positive_count += 1
        elif word in negative_words:
            if negated:
                positive_count += 1
            else:
                negative_count += 1

    if positive_count > negative_count:
        return 'Positive'
    elif negative_count > positive_count:
        return 'Negative'
    return 'Neutral'


def get_news_with_sentiment(symbol):
    """Get news articles with sentiment analysis"""
    news_items = get_yahoo_finance_news(symbol) or []

    for item in news_items:
        item['sentiment'] = analyze_sentiment(item['summary'])

    return news_items
