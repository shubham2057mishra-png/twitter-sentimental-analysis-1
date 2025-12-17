"""
Twitter API Module - Handles all Twitter API interactions
"""

import tweepy
from datetime import datetime, timedelta
import time


class TwitterAPI:
    def __init__(self, bearer_token):
        """Initialize Twitter API client"""
        self.client = tweepy.Client(bearer_token=bearer_token, wait_on_rate_limit=True)
        
    def get_user_info(self, username):
        """
        Get detailed user information
        Returns: user data with followers, following, tweet count
        """
        try:
            username = username.replace('@', '')
            user = self.client.get_user(
                username=username,
                user_fields=['created_at', 'description', 'public_metrics', 'verified']
            )
            
            if not user.data:
                return None
                
            data = user.data
            return {
                'id': data.id,
                'username': data.username,
                'name': data.name,
                'description': data.description,
                'created_at': data.created_at,
                'verified': data.verified,
                'followers_count': data.public_metrics['followers_count'],
                'following_count': data.public_metrics['following_count'],
                'tweet_count': data.public_metrics['tweet_count'],
                'listed_count': data.public_metrics['listed_count']
            }
        except Exception as e:
            print(f"Error getting user info: {e}")
            return None
    
    def get_user_tweets(self, username, max_results=100):
        """
        Get user's recent tweets
        Returns: list of tweets with metadata
        """
        try:
            user_info = self.get_user_info(username)
            if not user_info:
                return None
                
            tweets = self.client.get_users_tweets(
                id=user_info['id'],
                max_results=min(max_results, 100),
                tweet_fields=['created_at', 'public_metrics', 'referenced_tweets'],
                exclude=['retweets']
            )
            
            if not tweets.data:
                return []
                
            tweet_list = []
            for tweet in tweets.data:
                tweet_list.append({
                    'id': tweet.id,
                    'text': tweet.text,
                    'created_at': tweet.created_at,
                    'likes': tweet.public_metrics['like_count'],
                    'retweets': tweet.public_metrics['retweet_count'],
                    'replies': tweet.public_metrics['reply_count'],
                    'impressions': tweet.public_metrics.get('impression_count', 0)
                })
            
            return tweet_list
            
        except Exception as e:
            print(f"Error getting user tweets: {e}")
            return None
    
    def get_tweet_replies(self, tweet_id, max_results=100):
        """
        Get replies/comments on a specific tweet
        Returns: list of reply tweets
        """
        try:
            # Search for tweets that are replies to this tweet
            query = f"conversation_id:{tweet_id}"
            
            tweets = self.client.search_recent_tweets(
                query=query,
                max_results=min(max_results, 100),
                tweet_fields=['created_at', 'public_metrics', 'author_id', 'referenced_tweets']
            )
            
            if not tweets.data:
                return []
            
            replies = []
            for tweet in tweets.data:
                # Check if it's actually a reply
                if hasattr(tweet, 'referenced_tweets') and tweet.referenced_tweets:
                    for ref in tweet.referenced_tweets:
                        if ref.type == 'replied_to':
                            replies.append({
                                'id': tweet.id,
                                'text': tweet.text,
                                'created_at': tweet.created_at,
                                'author_id': tweet.author_id,
                                'likes': tweet.public_metrics['like_count'],
                                'retweets': tweet.public_metrics['retweet_count'],
                                'replies': tweet.public_metrics['reply_count']
                            })
                            break
            
            return replies
            
        except Exception as e:
            print(f"Error getting tweet replies: {e}")
            return []
    
    def search_tweets(self, query, max_results=100, start_time=None):
        """
        Search tweets by query
        """
        try:
            if start_time is None:
                start_time = datetime.utcnow() - timedelta(days=7)
            
            tweets = self.client.search_recent_tweets(
                query=query,
                max_results=min(max_results, 100),
                start_time=start_time,
                tweet_fields=['created_at', 'public_metrics', 'author_id', 'entities']
            )
            
            if not tweets.data:
                return []
            
            tweet_list = []
            for tweet in tweets.data:
                hashtags = []
                if hasattr(tweet, 'entities') and tweet.entities and 'hashtags' in tweet.entities:
                    hashtags = [tag['tag'] for tag in tweet.entities['hashtags']]
                
                tweet_list.append({
                    'id': tweet.id,
                    'text': tweet.text,
                    'created_at': tweet.created_at,
                    'author_id': tweet.author_id,
                    'likes': tweet.public_metrics['like_count'],
                    'retweets': tweet.public_metrics['retweet_count'],
                    'replies': tweet.public_metrics['reply_count'],
                    'hashtags': hashtags
                })
            
            return tweet_list
            
        except Exception as e:
            print(f"Error searching tweets: {e}")
            return []
    
    def compare_users(self, username1, username2, max_tweets=50):
        """
        Compare two users' profiles and tweets
        """
        try:
            user1_info = self.get_user_info(username1)
            user2_info = self.get_user_info(username2)
            
            if not user1_info or not user2_info:
                return None
            
            user1_tweets = self.get_user_tweets(username1, max_tweets)
            user2_tweets = self.get_user_tweets(username2, max_tweets)
            
            return {
                'user1': {
                    'info': user1_info,
                    'tweets': user1_tweets
                },
                'user2': {
                    'info': user2_info,
                    'tweets': user2_tweets
                }
            }
            
        except Exception as e:
            print(f"Error comparing users: {e}")
            return None
    
    def get_single_tweet(self, tweet_id):
        """
        Get details of a single tweet
        """
        try:
            tweet = self.client.get_tweet(
                id=tweet_id,
                tweet_fields=['created_at', 'public_metrics', 'author_id']
            )
            
            if not tweet.data:
                return None
            
            t = tweet.data
            return {
                'id': t.id,
                'text': t.text,
                'created_at': t.created_at,
                'author_id': t.author_id,
                'likes': t.public_metrics['like_count'],
                'retweets': t.public_metrics['retweet_count'],
                'replies': t.public_metrics['reply_count']
            }
            
        except Exception as e:
            print(f"Error getting single tweet: {e}")
            return None


class TwitterStreamer:
    """
    Real-time Twitter streaming (requires elevated access)
    Note: Free tier doesn't support streaming
    """
    def __init__(self, bearer_token):
        self.client = tweepy.Client(bearer_token=bearer_token)
        self.stream = None
    
    def create_stream_rules(self, keywords):
        """
        Create rules for streaming
        keywords: list of keywords to track
        """
        try:
            # Delete existing rules
            rules = self.client.get_rules()
            if rules.data:
                rule_ids = [rule.id for rule in rules.data]
                self.client.delete_rules(rule_ids)
            
            # Add new rules
            rules_to_add = []
            for keyword in keywords:
                rules_to_add.append(tweepy.StreamRule(value=keyword))
            
            self.client.add_rules(rules_to_add)
            return True
            
        except Exception as e:
            print(f"Error creating stream rules: {e}")
            return False
    
    def start_stream(self, callback_function):
        """
        Start streaming tweets
        callback_function: function to process each tweet
        """
        try:
            # Note: This requires elevated access
            # Free tier users won't be able to use this
            print("Note: Streaming requires elevated Twitter API access")
            return False
        except Exception as e:
            print(f"Error starting stream: {e}")
            return False