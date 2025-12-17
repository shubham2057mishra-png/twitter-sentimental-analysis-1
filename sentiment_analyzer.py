"""
Sentiment Analyzer Module - Handles all sentiment analysis operations
"""

import pickle
import re
from collections import Counter


class SentimentAnalyzer:
    def __init__(self, model_path, vectorizer_path):
        """Initialize sentiment analyzer with trained model"""
        try:
            self.model = pickle.load(open(model_path, 'rb'))
            self.vectorizer = pickle.load(open(vectorizer_path, 'rb'))
            print("✓ Sentiment model loaded successfully")
        except Exception as e:
            print(f"✗ Error loading sentiment model: {e}")
            self.model = None
            self.vectorizer = None
    
    def clean_text(self, text):
        """Clean text for analysis"""
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        text = re.sub(r'@\w+', '', text)
        text = re.sub(r'#', '', text)
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text.lower()
    
    def predict_sentiment(self, text):
        """
        Predict sentiment of text
        Returns: (sentiment, confidence)
        """
        if not self.model or not self.vectorizer:
            return "Unknown", 0.0
        
        try:
            cleaned = self.clean_text(text)
            vectorized = self.vectorizer.transform([cleaned])
            prediction = self.model.predict(vectorized)[0]
            
            # Get confidence
            try:
                proba = self.model.predict_proba(vectorized)[0]
                confidence = float(max(proba))
            except:
                confidence = 1.0
            
            sentiment_map = {0: 'Negative', 1: 'Neutral', 2: 'Positive'}
            return sentiment_map.get(prediction, 'Unknown'), confidence
            
        except Exception as e:
            print(f"Prediction error: {e}")
            return "Error", 0.0
    
    def analyze_tweets(self, tweets):
        """
        Analyze multiple tweets
        Returns: list of tweets with sentiment
        """
        analyzed = []
        
        for tweet in tweets:
            sentiment, confidence = self.predict_sentiment(tweet['text'])
            
            analyzed.append({
                **tweet,
                'sentiment': sentiment,
                'confidence': confidence,
                'cleaned_text': self.clean_text(tweet['text'])
            })
        
        return analyzed
    
    def get_sentiment_stats(self, analyzed_tweets):
        """
        Calculate sentiment statistics
        """
        if not analyzed_tweets:
            return None
        
        total = len(analyzed_tweets)
        sentiment_counts = Counter([t['sentiment'] for t in analyzed_tweets])
        
        return {
            'total': total,
            'positive': sentiment_counts.get('Positive', 0),
            'neutral': sentiment_counts.get('Neutral', 0),
            'negative': sentiment_counts.get('Negative', 0),
            'positive_pct': round((sentiment_counts.get('Positive', 0) / total) * 100, 2),
            'neutral_pct': round((sentiment_counts.get('Neutral', 0) / total) * 100, 2),
            'negative_pct': round((sentiment_counts.get('Negative', 0) / total) * 100, 2),
            'avg_confidence': round(sum([t['confidence'] for t in analyzed_tweets]) / total, 4)
        }
    
    def categorize_tweets(self, analyzed_tweets):
        """
        Categorize tweets into positive, neutral, negative
        """
        categorized = {
            'positive': [],
            'neutral': [],
            'negative': []
        }
        
        for tweet in analyzed_tweets:
            sentiment = tweet['sentiment'].lower()
            if sentiment in categorized:
                categorized[sentiment].append(tweet)
        
        # Sort by engagement (likes + retweets)
        for category in categorized:
            categorized[category].sort(
                key=lambda x: x.get('likes', 0) + x.get('retweets', 0),
                reverse=True
            )
        
        return categorized
    
    def analyze_replies(self, replies):
        """
        Analyze sentiment of replies/comments
        """
        if not replies:
            return {
                'total_replies': 0,
                'sentiment_breakdown': {},
                'analyzed_replies': []
            }
        
        analyzed = self.analyze_tweets(replies)
        stats = self.get_sentiment_stats(analyzed)
        categorized = self.categorize_tweets(analyzed)
        
        return {
            'total_replies': len(replies),
            'sentiment_stats': stats,
            'categorized_replies': categorized,
            'analyzed_replies': analyzed[:50]  # Top 50 replies
        }
    
    def compare_sentiment(self, data1, data2):
        """
        Compare sentiment between two datasets (users, posts, etc.)
        """
        stats1 = self.get_sentiment_stats(data1)
        stats2 = self.get_sentiment_stats(data2)
        
        if not stats1 or not stats2:
            return None
        
        comparison = {
            'dataset1': stats1,
            'dataset2': stats2,
            'differences': {
                'positive_diff': stats1['positive_pct'] - stats2['positive_pct'],
                'neutral_diff': stats1['neutral_pct'] - stats2['neutral_pct'],
                'negative_diff': stats1['negative_pct'] - stats2['negative_pct'],
                'confidence_diff': stats1['avg_confidence'] - stats2['avg_confidence']
            }
        }
        
        return comparison
    
    def get_top_tweets(self, analyzed_tweets, n=10, sort_by='engagement'):
        """
        Get top N tweets based on criteria
        sort_by: 'engagement', 'likes', 'retweets', 'confidence'
        """
        if not analyzed_tweets:
            return []
        
        if sort_by == 'engagement':
            sorted_tweets = sorted(
                analyzed_tweets,
                key=lambda x: x.get('likes', 0) + x.get('retweets', 0),
                reverse=True
            )
        elif sort_by == 'confidence':
            sorted_tweets = sorted(
                analyzed_tweets,
                key=lambda x: x.get('confidence', 0),
                reverse=True
            )
        else:
            sorted_tweets = sorted(
                analyzed_tweets,
                key=lambda x: x.get(sort_by, 0),
                reverse=True
            )
        
        return sorted_tweets[:n]
    
    def generate_word_cloud_data(self, analyzed_tweets, sentiment_filter=None):
        """
        Generate data for word cloud
        sentiment_filter: 'positive', 'neutral', 'negative', or None for all
        """
        filtered_tweets = analyzed_tweets
        
        if sentiment_filter:
            filtered_tweets = [
                t for t in analyzed_tweets 
                if t['sentiment'].lower() == sentiment_filter.lower()
            ]
        
        # Combine all cleaned text
        all_text = ' '.join([t['cleaned_text'] for t in filtered_tweets])
        
        # Count words
        words = all_text.split()
        word_freq = Counter(words)
        
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                     'of', 'is', 'was', 'are', 'were', 'been', 'be', 'have', 'has', 'had',
                     'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
                     'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she',
                     'it', 'we', 'they', 'what', 'which', 'who', 'when', 'where', 'why', 'how'}
        
        filtered_freq = {
            word: count for word, count in word_freq.items() 
            if len(word) > 2 and word not in stop_words
        }
        
        # Get top 50 words
        top_words = dict(sorted(filtered_freq.items(), key=lambda x: x[1], reverse=True)[:50])
        
        return top_words