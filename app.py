"""
Main Flask Application - Imports all modules
Advanced Twitter Sentiment Analysis Dashboard
"""

from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv

# Import custom modules
from twitter_api import TwitterAPI, TwitterStreamer
from sentiment_analyzer import SentimentAnalyzer
from data_visualizer import DataVisualizer

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration
BEARER_TOKEN = os.getenv('BEARER_TOKEN')
MODEL_PATH = os.getenv('MODEL_PATH', 'trained_model.sav')
VECTORIZER_PATH = os.getenv('VECTORIZER_PATH', 'vectorizer.pkl')

# Initialize modules
twitter_api = TwitterAPI(BEARER_TOKEN) if BEARER_TOKEN else None
sentiment_analyzer = SentimentAnalyzer(MODEL_PATH, VECTORIZER_PATH)
visualizer = DataVisualizer()

print("\n" + "="*60)
print("ADVANCED TWITTER SENTIMENT ANALYSIS SYSTEM")
print("="*60)
print(f"✓ Twitter API: {'Connected' if twitter_api else 'Not Connected'}")
print(f"✓ Sentiment Model: {'Loaded' if sentiment_analyzer.model else 'Not Loaded'}")
print("="*60 + "\n")


@app.route('/')
def index():
    """Main dashboard"""
    return render_template('dashboard.html')


@app.route('/api/user-info', methods=['POST'])
def get_user_info():
    """Get detailed user information including post count"""
    try:
        data = request.get_json()
        username = data.get('username', '')
        
        if not username or not twitter_api:
            return jsonify({'error': 'Invalid request'}), 400
        
        user_info = twitter_api.get_user_info(username)
        
        if not user_info:
            return jsonify({'error': f'User @{username} not found'}), 404
        
        return jsonify({
            'success': True,
            'user_info': user_info
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/user-tweets', methods=['POST'])
def get_user_tweets():
    """Get user's tweets with sentiment analysis"""
    try:
        data = request.get_json()
        username = data.get('username', '')
        max_results = int(data.get('max_results', 50))
        
        if not username or not twitter_api:
            return jsonify({'error': 'Invalid request'}), 400
        
        # Get tweets
        tweets = twitter_api.get_user_tweets(username, max_results)
        
        if tweets is None:
            return jsonify({'error': 'Failed to fetch tweets'}), 500
        
        if not tweets:
            return jsonify({'error': 'No tweets found'}), 404
        
        # Analyze sentiment
        analyzed_tweets = sentiment_analyzer.analyze_tweets(tweets)
        stats = sentiment_analyzer.get_sentiment_stats(analyzed_tweets)
        categorized = sentiment_analyzer.categorize_tweets(analyzed_tweets)
        
        # Prepare charts
        charts = {
            'pie_chart': visualizer.prepare_sentiment_pie_chart(stats),
            'bar_chart': visualizer.prepare_sentiment_bar_chart(stats),
            'timeline': visualizer.prepare_timeline_chart(analyzed_tweets),
            'engagement': visualizer.prepare_engagement_chart(analyzed_tweets)
        }
        
        return jsonify({
            'success': True,
            'stats': stats,
            'categorized': categorized,
            'tweets': analyzed_tweets,
            'charts': charts
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/tweet-replies', methods=['POST'])
def get_tweet_replies():
    """Analyze sentiment of replies/comments on a specific tweet"""
    try:
        data = request.get_json()
        tweet_id = data.get('tweet_id', '')
        
        if not tweet_id or not twitter_api:
            return jsonify({'error': 'Invalid request'}), 400
        
        # Get tweet details
        tweet = twitter_api.get_single_tweet(tweet_id)
        if not tweet:
            return jsonify({'error': 'Tweet not found'}), 404
        
        # Get replies
        replies = twitter_api.get_tweet_replies(tweet_id)
        
        # Analyze replies
        reply_analysis = sentiment_analyzer.analyze_replies(replies)
        
        # Prepare charts if replies exist
        charts = None
        if reply_analysis['analyzed_replies']:
            charts = {
                'sentiment_distribution': visualizer.prepare_sentiment_pie_chart(
                    reply_analysis['sentiment_stats']
                )
            }
        
        return jsonify({
            'success': True,
            'tweet': tweet,
            'reply_analysis': reply_analysis,
            'charts': charts
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/compare-users', methods=['POST'])
def compare_users():
    """Compare two users' profiles and sentiment"""
    try:
        data = request.get_json()
        username1 = data.get('username1', '')
        username2 = data.get('username2', '')
        max_tweets = int(data.get('max_tweets', 50))
        
        if not username1 or not username2 or not twitter_api:
            return jsonify({'error': 'Invalid request'}), 400
        
        # Get comparison data
        comparison = twitter_api.compare_users(username1, username2, max_tweets)
        
        if not comparison:
            return jsonify({'error': 'Failed to compare users'}), 500
        
        # Analyze sentiment for both users
        user1_analyzed = sentiment_analyzer.analyze_tweets(comparison['user1']['tweets'])
        user2_analyzed = sentiment_analyzer.analyze_tweets(comparison['user2']['tweets'])
        
        # Get sentiment comparison
        sentiment_comparison = sentiment_analyzer.compare_sentiment(
            user1_analyzed, user2_analyzed
        )
        
        # Prepare charts
        charts = {
            'profile_comparison': visualizer.prepare_user_comparison_chart(
                comparison['user1'], comparison['user2']
            ),
            'sentiment_comparison': visualizer.prepare_comparison_chart(
                sentiment_comparison, username1, username2
            )
        }
        
        return jsonify({
            'success': True,
            'user1': {
                'info': comparison['user1']['info'],
                'tweets': user1_analyzed,
                'stats': sentiment_analyzer.get_sentiment_stats(user1_analyzed)
            },
            'user2': {
                'info': comparison['user2']['info'],
                'tweets': user2_analyzed,
                'stats': sentiment_analyzer.get_sentiment_stats(user2_analyzed)
            },
            'comparison': sentiment_comparison,
            'charts': charts
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/compare-tweets', methods=['POST'])
def compare_tweets():
    """Compare sentiment of replies on two different tweets"""
    try:
        data = request.get_json()
        tweet_id1 = data.get('tweet_id1', '')
        tweet_id2 = data.get('tweet_id2', '')
        
        if not tweet_id1 or not tweet_id2 or not twitter_api:
            return jsonify({'error': 'Invalid request'}), 400
        
        # Get both tweets
        tweet1 = twitter_api.get_single_tweet(tweet_id1)
        tweet2 = twitter_api.get_single_tweet(tweet_id2)
        
        if not tweet1 or not tweet2:
            return jsonify({'error': 'One or both tweets not found'}), 404
        
        # Get replies for both
        replies1 = twitter_api.get_tweet_replies(tweet_id1)
        replies2 = twitter_api.get_tweet_replies(tweet_id2)
        
        # Analyze both
        analyzed1 = sentiment_analyzer.analyze_tweets(replies1)
        analyzed2 = sentiment_analyzer.analyze_tweets(replies2)
        
        stats1 = sentiment_analyzer.get_sentiment_stats(analyzed1)
        stats2 = sentiment_analyzer.get_sentiment_stats(analyzed2)
        
        # Compare
        comparison = sentiment_analyzer.compare_sentiment(analyzed1, analyzed2)
        
        # Prepare charts
        charts = {
            'comparison': visualizer.prepare_comparison_chart(
                comparison, f"Tweet 1 Replies", f"Tweet 2 Replies"
            )
        }
        
        return jsonify({
            'success': True,
            'tweet1': {
                'details': tweet1,
                'stats': stats1,
                'replies': analyzed1
            },
            'tweet2': {
                'details': tweet2,
                'stats': stats2,
                'replies': analyzed2
            },
            'comparison': comparison,
            'charts': charts
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/search-analyze', methods=['POST'])
def search_and_analyze():
    """Search tweets and analyze sentiment with charts"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        max_results = int(data.get('max_results', 100))
        
        if not query or not twitter_api:
            return jsonify({'error': 'Invalid request'}), 400
        
        # Search tweets
        tweets = twitter_api.search_tweets(query, max_results)
        
        if not tweets:
            return jsonify({'error': 'No tweets found'}), 404
        
        # Analyze
        analyzed = sentiment_analyzer.analyze_tweets(tweets)
        stats = sentiment_analyzer.get_sentiment_stats(analyzed)
        categorized = sentiment_analyzer.categorize_tweets(analyzed)
        
        # Prepare all charts
        charts = {
            'pie_chart': visualizer.prepare_sentiment_pie_chart(stats),
            'bar_chart': visualizer.prepare_sentiment_bar_chart(stats),
            'timeline': visualizer.prepare_timeline_chart(analyzed),
            'engagement': visualizer.prepare_engagement_chart(analyzed),
            'hashtags': visualizer.prepare_hashtag_chart(analyzed),
            'hourly': visualizer.prepare_sentiment_by_hour(analyzed),
            'confidence': visualizer.prepare_confidence_distribution(analyzed)
        }
        
        return jsonify({
            'success': True,
            'query': query,
            'stats': stats,
            'categorized': categorized,
            'tweets': analyzed[:50],
            'charts': charts
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/test-sentiment', methods=['POST'])
def test_sentiment():
    """Test sentiment on single text"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'Text required'}), 400
        
        sentiment, confidence = sentiment_analyzer.predict_sentiment(text)
        
        return jsonify({
            'success': True,
            'text': text,
            'cleaned_text': sentiment_analyzer.clean_text(text),
            'sentiment': sentiment,
            'confidence': round(confidence * 100, 2)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health')
def health():
    """System health check"""
    return jsonify({
        'status': 'running',
        'twitter_api': twitter_api is not None,
        'sentiment_model': sentiment_analyzer.model is not None,
        'bearer_token': BEARER_TOKEN is not None
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)