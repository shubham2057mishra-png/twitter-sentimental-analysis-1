// Dashboard JavaScript Functions

let chartInstances = {};

function switchTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    document.getElementById(tabName + '-tab').classList.add('active');
    event.target.classList.add('active');
}

function showLoading(id) {
    document.getElementById(id).classList.add('active');
}

function hideLoading(id) {
    document.getElementById(id).classList.remove('active');
}

function showError(id, message) {
    const errorDiv = document.getElementById(id);
    errorDiv.textContent = message;
    errorDiv.classList.add('active');
}

function hideError(id) {
    document.getElementById(id).classList.remove('active');
}

function showResults(id) {
    document.getElementById(id).classList.add('active');
}

function hideResults(id) {
    document.getElementById(id).classList.remove('active');
}

function extractTweetId(input) {
    // Extract tweet ID from URL or return as is
    const match = input.match(/status\/(\d+)/);
    return match ? match[1] : input;
}

// User Profile
async function getUserProfile() {
    const username = document.getElementById('profileUsername').value;
    
    if (!username) {
        showError('profileError', 'Please enter a username');
        return;
    }
    
    showLoading('profileLoading');
    hideError('profileError');
    hideResults('profileResults');
    
    try {
        const response = await fetch('/api/user-info', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username})
        });
        
        const data = await response.json();
        hideLoading('profileLoading');
        
        if (data.success) {
            displayUserProfile(data.user_info);
        } else {
            showError('profileError', data.error);
        }
    } catch (error) {
        hideLoading('profileLoading');
        showError('profileError', 'Error: ' + error.message);
    }
}

function displayUserProfile(user) {
    const html = `
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Username</h3>
                <div class="value" style="font-size: 1.5em;">@${user.username}</div>
            </div>
            <div class="stat-card">
                <h3>Total Posts</h3>
                <div class="value">${user.tweet_count.toLocaleString()}</div>
            </div>
            <div class="stat-card">
                <h3>Followers</h3>
                <div class="value">${user.followers_count.toLocaleString()}</div>
            </div>
            <div class="stat-card">
                <h3>Following</h3>
                <div class="value">${user.following_count.toLocaleString()}</div>
            </div>
        </div>
        <div class="chart-container">
            <h3>${user.name} ${user.verified ? '✓' : ''}</h3>
            <p style="color: #666; margin-top: 10px;">${user.description || 'No description'}</p>
            <p style="color: #999; margin-top: 10px; font-size: 0.9em;">
                Joined: ${new Date(user.created_at).toLocaleDateString()}
            </p>
        </div>
    `;
    
    document.getElementById('profileResults').innerHTML = html;
    showResults('profileResults');
}

// User Tweets Analysis
async function getUserTweets() {
    const username = document.getElementById('tweetsUsername').value;
    const maxResults = document.getElementById('tweetsMax').value;
    
    if (!username) {
        showError('tweetsError', 'Please enter a username');
        return;
    }
    
    showLoading('tweetsLoading');
    hideError('tweetsError');
    hideResults('tweetsResults');
    
    try {
        const response = await fetch('/api/user-tweets', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username, max_results: maxResults})
        });
        
        const data = await response.json();
        hideLoading('tweetsLoading');
        
        if (data.success) {
            displayUserTweets(data, username);
        } else {
            showError('tweetsError', data.error);
        }
    } catch (error) {
        hideLoading('tweetsLoading');
        showError('tweetsError', 'Error: ' + error.message);
    }
}

function displayUserTweets(data, username) {
    let html = `
        <h2 style="margin-bottom: 20px;">@${username}'s Tweet Analysis</h2>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Total Analyzed</h3>
                <div class="value">${data.stats.total}</div>
            </div>
            <div class="stat-card">
                <h3>Positive</h3>
                <div class="value">${data.stats.positive_pct}%</div>
            </div>
            <div class="stat-card">
                <h3>Neutral</h3>
                <div class="value">${data.stats.neutral_pct}%</div>
            </div>
            <div class="stat-card">
                <h3>Negative</h3>
                <div class="value">${data.stats.negative_pct}%</div>
            </div>
        </div>
        
        <div class="chart-grid">
            <div class="chart-container">
                <canvas id="tweetsChart"></canvas>
            </div>
            <div class="chart-container">
                <canvas id="engagementChart"></canvas>
            </div>
        </div>
        
        <h3 style="margin: 20px 0;">Recent Tweets by Sentiment</h3>
        <div class="tweets-list">
    `;
    
    // Display categorized tweets
    ['positive', 'neutral', 'negative'].forEach(sentiment => {
        const tweets = data.categorized[sentiment].slice(0, 5);
        if (tweets.length > 0) {
            html += `<h4 style="margin: 15px 0; text-transform: capitalize;">${sentiment} Tweets:</h4>`;
            tweets.forEach(tweet => {
                html += `
                    <div class="tweet-card">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                            <span class="sentiment-badge ${sentiment}">${sentiment} (${(tweet.confidence * 100).toFixed(1)}%)</span>
                            <span style="color: #666; font-size: 0.9em;">${new Date(tweet.created_at).toLocaleDateString()}</span>
                        </div>
                        <p style="margin-bottom: 10px;">${tweet.text}</p>
                        <div style="color: #999; font-size: 0.9em;">
                            ❤️ ${tweet.likes} | 🔄 ${tweet.retweets} | 💬 ${tweet.replies}
                            <button class="btn" style="float: right; padding: 5px 15px; font-size: 0.8em;" 
                                    onclick="analyzeSpecificTweet('${tweet.id}')">
                                Analyze Replies
                            </button>
                        </div>
                    </div>
                `;
            });
        }
    });
    
    html += '</div>';
    document.getElementById('tweetsResults').innerHTML = html;
    showResults('tweetsResults');
    
    // Create charts
    createChart('tweetsChart', 'pie', data.charts.pie_chart);
    if (data.charts.engagement) {
        createChart('engagementChart', 'bar', data.charts.engagement);
    }
}

// Reply Analysis
async function analyzeReplies() {
    const input = document.getElementById('replyTweetId').value;
    const tweetId = extractTweetId(input);
    
    if (!tweetId) {
        showError('replyError', 'Please enter a tweet ID or URL');
        return;
    }
    
    showLoading('replyLoading');
    hideError('replyError');
    hideResults('replyResults');
    
    try {
        const response = await fetch('/api/tweet-replies', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({tweet_id: tweetId})
        });
        
        const data = await response.json();
        hideLoading('replyLoading');
        
        if (data.success) {
            displayReplyAnalysis(data);
        } else {
            showError('replyError', data.error);
        }
    } catch (error) {
        hideLoading('replyLoading');
        showError('replyError', 'Error: ' + error.message);
    }
}

function analyzeSpecificTweet(tweetId) {
    document.getElementById('replyTweetId').value = tweetId;
    switchTab('reply-analysis');
    analyzeReplies();
}

function displayReplyAnalysis(data) {
    const analysis = data.reply_analysis;
    
    let html = `
        <div class="chart-container">
            <h3>Original Tweet</h3>
            <p style="margin: 10px 0;">${data.tweet.text}</p>
            <div style="color: #999; font-size: 0.9em;">
                ❤️ ${data.tweet.likes} | 🔄 ${data.tweet.retweets} | 💬 ${data.tweet.replies}
            </div>
        </div>
        
        <h3 style="margin: 20px 0;">Reply Analysis (${analysis.total_replies} replies)</h3>
    `;
    
    if (analysis.total_replies > 0) {
        const stats = analysis.sentiment_stats;
        html += `
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>Positive</h3>
                    <div class="value">${stats.positive_pct}%</div>
                </div>
                <div class="stat-card">
                    <h3>Neutral</h3>
                    <div class="value">${stats.neutral_pct}%</div>
                </div>
                <div class="stat-card">
                    <h3>Negative</h3>
                    <div class="value">${stats.negative_pct}%</div>
                </div>
                <div class="stat-card">
                    <h3>Avg Confidence</h3>
                    <div class="value">${(stats.avg_confidence * 100).toFixed(1)}%</div>
                </div>
            </div>
            
            <div class="chart-container">
                <canvas id="replyChart"></canvas>
            </div>
            
            <h3 style="margin: 20px 0;">Sample Replies</h3>
            <div class="tweets-list">
        `;
        
        analysis.analyzed_replies.slice(0, 10).forEach(reply => {
            html += `
                <div class="tweet-card">
                    <span class="sentiment-badge ${reply.sentiment.toLowerCase()}">
                        ${reply.sentiment} (${(reply.confidence * 100).toFixed(1)}%)
                    </span>
                    <p style="margin: 10px 0;">${reply.text}</p>
                </div>
            `;
        });
        
        html += '</div>';
    } else {
        html += '<p>No replies found for this tweet.</p>';
    }
    
    document.getElementById('replyResults').innerHTML = html;
    showResults('replyResults');
    
    if (data.charts && data.charts.sentiment_distribution) {
        createChart('replyChart', 'pie', data.charts.sentiment_distribution);
    }
}

// Compare Users
async function compareUsers() {
    const user1 = document.getElementById('compareUser1').value;
    const user2 = document.getElementById('compareUser2').value;
    
    if (!user1 || !user2) {
        showError('compareUsersError', 'Please enter both usernames');
        return;
    }
    
    showLoading('compareUsersLoading');
    hideError('compareUsersError');
    hideResults('compareUsersResults');
    
    try {
        const response = await fetch('/api/compare-users', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username1: user1, username2: user2, max_tweets: 50})
        });
        
        const data = await response.json();
        hideLoading('compareUsersLoading');
        
        if (data.success) {
            displayUserComparison(data);
        } else {
            showError('compareUsersError', data.error);
        }
    } catch (error) {
        hideLoading('compareUsersLoading');
        showError('compareUsersError', 'Error: ' + error.message);
    }
}

function displayUserComparison(data) {
    const html = `
        <h2 style="margin-bottom: 20px;">User Comparison</h2>
        
        <div class="chart-grid">
            <div class="chart-container">
                <h3>Profile Metrics</h3>
                <canvas id="profileCompareChart"></canvas>
            </div>
            <div class="chart-container">
                <h3>Sentiment Comparison</h3>
                <canvas id="sentimentCompareChart"></canvas>
            </div>
        </div>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
            <div class="chart-container">
                <h3>@${data.user1.info.username}</h3>
                <p>Positive: ${data.user1.stats.positive_pct}%</p>
                <p>Neutral: ${data.user1.stats.neutral_pct}%</p>
                <p>Negative: ${data.user1.stats.negative_pct}%</p>
            </div>
            <div class="chart-container">
                <h3>@${data.user2.info.username}</h3>
                <p>Positive: ${data.user2.stats.positive_pct}%</p>
                <p>Neutral: ${data.user2.stats.neutral_pct}%</p>
                <p>Negative: ${data.user2.stats.negative_pct}%</p>
            </div>
        </div>
    `;
    
    document.getElementById('compareUsersResults').innerHTML = html;
    showResults('compareUsersResults');
    
    createChart('profileCompareChart', 'bar', data.charts.profile_comparison);
    createChart('sentimentCompareChart', 'bar', data.charts.sentiment_comparison);
}

// Compare Tweets
async function compareTweets() {
    const tweet1 = extractTweetId(document.getElementById('compareTweet1').value);
    const tweet2 = extractTweetId(document.getElementById('compareTweet2').value);
    
    if (!tweet1 || !tweet2) {
        showError('compareTweetsError', 'Please enter both tweet IDs');
        return;
    }
    
    showLoading('compareTweetsLoading');
    hideError('compareTweetsError');
    hideResults('compareTweetsResults');
    
    try {
        const response = await fetch('/api/compare-tweets', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({tweet_id1: tweet1, tweet_id2: tweet2})
        });
        
        const data = await response.json();
        hideLoading('compareTweetsLoading');
        
        if (data.success) {
            displayTweetComparison(data);
        } else {
            showError('compareTweetsError', data.error);
        }
    } catch (error) {
        hideLoading('compareTweetsLoading');
        showError('compareTweetsError', 'Error: ' + error.message);
    }
}

function displayTweetComparison(data) {
    const html = `
        <h2 style="margin-bottom: 20px;">Tweet Comparison</h2>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
            <div class="chart-container">
                <h3>Tweet 1</h3>
                <p>${data.tweet1.details.text}</p>
                <p style="margin-top: 10px;">
                    Positive: ${data.tweet1.stats.positive_pct}% | 
                    Neutral: ${data.tweet1.stats.neutral_pct}% | 
                    Negative: ${data.tweet1.stats.negative_pct}%
                </p>
            </div>
            <div class="chart-container">
                <h3>Tweet 2</h3>
                <p>${data.tweet2.details.text}</p>
                <p style="margin-top: 10px;">
                    Positive: ${data.tweet2.stats.positive_pct}% | 
                    Neutral: ${data.tweet2.stats.neutral_pct}% | 
                    Negative: ${data.tweet2.stats.negative_pct}%
                </p>
            </div>
        </div>
        
        <div class="chart-container">
            <h3>Reply Sentiment Comparison</h3>
            <canvas id="tweetCompareChart"></canvas>
        </div>
    `;
    
    document.getElementById('compareTweetsResults').innerHTML = html;
    showResults('compareTweetsResults');
    
    createChart('tweetCompareChart', 'bar', data.charts.comparison);
}

// Search and Analyze
async function searchAndAnalyze() {
    const query = document.getElementById('searchQuery').value;
    const maxResults = document.getElementById('searchMax').value;
    
    if (!query) {
        showError('searchError', 'Please enter a search query');
        return;
    }
    
    showLoading('searchLoading');
    hideError('searchError');
    hideResults('searchResults');
    
    try {
        const response = await fetch('/api/search-analyze', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({query, max_results: maxResults})
        });
        
        const data = await response.json();
        hideLoading('searchLoading');
        
        if (data.success) {
            displaySearchResults(data);
        } else {
            showError('searchError', data.error);
        }
    } catch (error) {
        hideLoading('searchLoading');
        showError('searchError', 'Error: ' + error.message);
    }
}

function displaySearchResults(data) {
    const stats = data.stats;
    
    let html = `
        <h2 style="margin-bottom: 20px;">Search Results: "${data.query}"</h2>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Total Tweets</h3>
                <div class="value">${stats.total}</div>
            </div>
            <div class="stat-card">
                <h3>Positive</h3>
                <div class="value">${stats.positive_pct}%</div>
            </div>
            <div class="stat-card">
                <h3>Neutral</h3>
                <div class="value">${stats.neutral_pct}%</div>
            </div>
            <div class="stat-card">
                <h3>Negative</h3>
                <div class="value">${stats.negative_pct}%</div>
            </div>
        </div>
        
        <div class="chart-grid">
            <div class="chart-container">
                <canvas id="searchPieChart"></canvas>
            </div>
            <div class="chart-container">
                <canvas id="searchEngagementChart"></canvas>
            </div>
        </div>
    `;
    
    document.getElementById('searchResults').innerHTML = html;
    showResults('searchResults');
    
    createChart('searchPieChart', 'pie', data.charts.pie_chart);
    if (data.charts.engagement) {
        createChart('searchEngagementChart', 'bar', data.charts.engagement);
    }
}

// Test Sentiment
async function testSentiment() {
    const text = document.getElementById('testText').value;
    
    if (!text) return;
    
    try {
        const response = await fetch('/api/test-sentiment', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({text})
        });
        
        const data = await response.json();
        
        if (data.success) {
            const html = `
                <div class="chart-container" style="margin-top: 20px;">
                    <div class="tweet-card">
                        <span class="sentiment-badge ${data.sentiment.toLowerCase()}">
                            ${data.sentiment} (${data.confidence}%)
                        </span>
                        <p style="margin: 10px 0;"><strong>Text:</strong> ${data.text}</p>
                        <p><strong>Cleaned:</strong> ${data.cleaned_text}</p>
                    </div>
                </div>
            `;
            document.getElementById('testResults').innerHTML = html;
            showResults('testResults');
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

// Chart Creation Helper
function createChart(canvasId, type, chartData) {
    // Destroy existing chart if it exists
    if (chartInstances[canvasId]) {
        chartInstances[canvasId].destroy();
    }
    
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    chartInstances[canvasId] = new Chart(ctx, {
        type: type,
        data: chartData,
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}