"""
Data Visualizer Module - Generates chart data for frontend
"""

from datetime import datetime
from collections import Counter


class DataVisualizer:
    @staticmethod
    def prepare_sentiment_pie_chart(sentiment_stats):
        """
        Prepare data for sentiment pie chart
        """
        return {
            'labels': ['Positive', 'Neutral', 'Negative'],
            'data': [
                sentiment_stats['positive'],
                sentiment_stats['neutral'],
                sentiment_stats['negative']
            ],
            'colors': ['#48bb78', '#4299e1', '#f56565'],
            'percentages': [
                sentiment_stats['positive_pct'],
                sentiment_stats['neutral_pct'],
                sentiment_stats['negative_pct']
            ]
        }
    
    @staticmethod
    def prepare_sentiment_bar_chart(sentiment_stats):
        """
        Prepare data for sentiment bar chart
        """
        return {
            'labels': ['Positive', 'Neutral', 'Negative'],
            'datasets': [{
                'label': 'Tweet Count',
                'data': [
                    sentiment_stats['positive'],
                    sentiment_stats['neutral'],
                    sentiment_stats['negative']
                ],
                'backgroundColor': ['#48bb78', '#4299e1', '#f56565']
            }]
        }
    
    @staticmethod
    def prepare_comparison_chart(comparison_data, label1, label2):
        """
        Prepare data for comparing two datasets
        """
        return {
            'labels': ['Positive', 'Neutral', 'Negative'],
            'datasets': [
                {
                    'label': label1,
                    'data': [
                        comparison_data['dataset1']['positive_pct'],
                        comparison_data['dataset1']['neutral_pct'],
                        comparison_data['dataset1']['negative_pct']
                    ],
                    'backgroundColor': 'rgba(102, 126, 234, 0.7)',
                    'borderColor': 'rgba(102, 126, 234, 1)',
                    'borderWidth': 2
                },
                {
                    'label': label2,
                    'data': [
                        comparison_data['dataset2']['positive_pct'],
                        comparison_data['dataset2']['neutral_pct'],
                        comparison_data['dataset2']['negative_pct']
                    ],
                    'backgroundColor': 'rgba(237, 100, 166, 0.7)',
                    'borderColor': 'rgba(237, 100, 166, 1)',
                    'borderWidth': 2
                }
            ]
        }
    
    @staticmethod
    def prepare_timeline_chart(analyzed_tweets):
        """
        Prepare data for sentiment over time
        """
        if not analyzed_tweets:
            return None
        
        # Group by date
        daily_data = {}
        for tweet in analyzed_tweets:
            date = tweet['created_at'].strftime('%Y-%m-%d')
            if date not in daily_data:
                daily_data[date] = {'positive': 0, 'neutral': 0, 'negative': 0, 'total': 0}
            
            sentiment = tweet['sentiment'].lower()
            daily_data[date][sentiment] = daily_data[date].get(sentiment, 0) + 1
            daily_data[date]['total'] += 1
        
        # Sort by date
        sorted_dates = sorted(daily_data.keys())
        
        return {
            'labels': sorted_dates,
            'datasets': [
                {
                    'label': 'Positive',
                    'data': [daily_data[d]['positive'] for d in sorted_dates],
                    'borderColor': '#48bb78',
                    'backgroundColor': 'rgba(72, 187, 120, 0.2)',
                    'fill': True
                },
                {
                    'label': 'Neutral',
                    'data': [daily_data[d]['neutral'] for d in sorted_dates],
                    'borderColor': '#4299e1',
                    'backgroundColor': 'rgba(66, 153, 225, 0.2)',
                    'fill': True
                },
                {
                    'label': 'Negative',
                    'data': [daily_data[d]['negative'] for d in sorted_dates],
                    'borderColor': '#f56565',
                    'backgroundColor': 'rgba(245, 101, 101, 0.2)',
                    'fill': True
                }
            ]
        }
    
    @staticmethod
    def prepare_engagement_chart(analyzed_tweets, top_n=10):
        """
        Prepare data for engagement metrics
        """
        if not analyzed_tweets:
            return None
        
        # Sort by engagement
        sorted_tweets = sorted(
            analyzed_tweets,
            key=lambda x: x.get('likes', 0) + x.get('retweets', 0),
            reverse=True
        )[:top_n]
        
        labels = [f"Tweet {i+1}" for i in range(len(sorted_tweets))]
        
        return {
            'labels': labels,
            'datasets': [
                {
                    'label': 'Likes',
                    'data': [t['likes'] for t in sorted_tweets],
                    'backgroundColor': '#f56565'
                },
                {
                    'label': 'Retweets',
                    'data': [t['retweets'] for t in sorted_tweets],
                    'backgroundColor': '#48bb78'
                },
                {
                    'label': 'Replies',
                    'data': [t.get('replies', 0) for t in sorted_tweets],
                    'backgroundColor': '#4299e1'
                }
            ],
            'tweet_texts': [t['text'][:50] + '...' for t in sorted_tweets]
        }
    
    @staticmethod
    def prepare_confidence_distribution(analyzed_tweets):
        """
        Prepare data for confidence score distribution
        """
        if not analyzed_tweets:
            return None
        
        # Create bins
        bins = {
            '0-20%': 0,
            '20-40%': 0,
            '40-60%': 0,
            '60-80%': 0,
            '80-100%': 0
        }
        
        for tweet in analyzed_tweets:
            confidence = tweet['confidence'] * 100
            if confidence <= 20:
                bins['0-20%'] += 1
            elif confidence <= 40:
                bins['20-40%'] += 1
            elif confidence <= 60:
                bins['40-60%'] += 1
            elif confidence <= 80:
                bins['60-80%'] += 1
            else:
                bins['80-100%'] += 1
        
        return {
            'labels': list(bins.keys()),
            'data': list(bins.values()),
            'backgroundColor': ['#f56565', '#ed8936', '#ecc94b', '#48bb78', '#38a169']
        }
    
    @staticmethod
    def prepare_hashtag_chart(analyzed_tweets, top_n=10):
        """
        Prepare data for top hashtags
        """
        if not analyzed_tweets:
            return None
        
        all_hashtags = []
        for tweet in analyzed_tweets:
            if 'hashtags' in tweet and tweet['hashtags']:
                if isinstance(tweet['hashtags'], list):
                    all_hashtags.extend(tweet['hashtags'])
                else:
                    all_hashtags.extend(tweet['hashtags'].split(', '))
        
        if not all_hashtags:
            return None
        
        hashtag_counts = Counter(all_hashtags).most_common(top_n)
        
        return {
            'labels': [f"#{tag}" for tag, _ in hashtag_counts],
            'data': [count for _, count in hashtag_counts],
            'backgroundColor': '#667eea'
        }
    
    @staticmethod
    def prepare_user_comparison_chart(user1_data, user2_data):
        """
        Prepare data for comparing two users
        """
        return {
            'labels': ['Followers', 'Following', 'Total Tweets'],
            'datasets': [
                {
                    'label': user1_data['info']['username'],
                    'data': [
                        user1_data['info']['followers_count'],
                        user1_data['info']['following_count'],
                        user1_data['info']['tweet_count']
                    ],
                    'backgroundColor': 'rgba(102, 126, 234, 0.7)'
                },
                {
                    'label': user2_data['info']['username'],
                    'data': [
                        user2_data['info']['followers_count'],
                        user2_data['info']['following_count'],
                        user2_data['info']['tweet_count']
                    ],
                    'backgroundColor': 'rgba(237, 100, 166, 0.7)'
                }
            ]
        }
    
    @staticmethod
    def prepare_sentiment_by_hour(analyzed_tweets):
        """
        Prepare data for sentiment distribution by hour of day
        """
        if not analyzed_tweets:
            return None
        
        hourly_data = {}
        for i in range(24):
            hourly_data[i] = {'positive': 0, 'neutral': 0, 'negative': 0}
        
        for tweet in analyzed_tweets:
            hour = tweet['created_at'].hour
            sentiment = tweet['sentiment'].lower()
            hourly_data[hour][sentiment] += 1
        
        return {
            'labels': [f"{h:02d}:00" for h in range(24)],
            'datasets': [
                {
                    'label': 'Positive',
                    'data': [hourly_data[h]['positive'] for h in range(24)],
                    'borderColor': '#48bb78',
                    'fill': False
                },
                {
                    'label': 'Neutral',
                    'data': [hourly_data[h]['neutral'] for h in range(24)],
                    'borderColor': '#4299e1',
                    'fill': False
                },
                {
                    'label': 'Negative',
                    'data': [hourly_data[h]['negative'] for h in range(24)],
                    'borderColor': '#f56565',
                    'fill': False
                }
            ]
        }