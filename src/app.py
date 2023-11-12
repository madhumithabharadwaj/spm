from flask import Flask, render_template, request, redirect, url_for
import requests
from datetime import datetime
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import pandas as pd
import matplotlib
matplotlib.use('Agg')
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


#app = Flask(__name__)

# Your GitHub personal access token
personal_access_token = "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"

# Set up headers
headers = {
    "Authorization": f"token {personal_access_token}",
    "Accept": "application/vnd.github.cloak-preview",
}

def get_commit_frequency(repo_owner, repo_name, start_date, end_date):
    # Get commits from the GitHub API within the specified date range
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/commits"
    params = {
        'since': start_date.isoformat(),
        'until': end_date.isoformat(),
    }
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        commits = [commit["commit"]["author"]["date"] for commit in data]
        commits = [datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ') for date in commits]
        return commits
    else:
        print(f"Error: {response.status_code}")
        return []
    
# Existing code for fetching contributor activity
def get_contributor_activity(repo_owner, repo_name, start_date, end_date):
    # ... (your existing code for get_contributor_activity)
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/stats/contributors"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        contributor_activity = []

        for contributor in data:
            login = contributor["author"]["login"]
            weeks = contributor["weeks"]
            activity = [(datetime.fromtimestamp(week["w"]), week["c"]) for week in weeks]
            # Filter activity within the specified date range
            filtered_activity = [(date, commits) for date, commits in activity if start_date <= date <= end_date]
            contributor_activity.append((login, filtered_activity))

        return contributor_activity
    else:
        print(f"Error: Unable to fetch data from GitHub API. Status code: {response.status_code}")
        return []

# Existing code for fetching issue resolution time
def get_avg_resolution_time(owner, repo):
    # ... (your existing code for get_avg_resolution_time)
    # API endpoint
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"

    # API request headers
    headers = {
        "Accept": "application/vnd.github+json"
    }

    # API request parameters
    params = {
        "state": "closed",
        "sort": "created",
        "direction": "desc"
    }

    # Make the API request
    response = requests.get(url, headers=headers, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        issues = response.json()

        # Initialize variables for calculation
        total_time = 0
        issue_count = 0

        # Iterate through the issues
        for issue in issues:
            # Extract the closed_at date of the issue
            closed_at = datetime.strptime(issue["closed_at"], "%Y-%m-%dT%H:%M:%SZ")

            # Extract the created_at date of the issue
            created_at = datetime.strptime(issue["created_at"], "%Y-%m-%dT%H:%M:%SZ")

            # Calculate the time taken to resolve the issue
            time_taken = closed_at - created_at

            # Add the time taken to the total time
            total_time += time_taken.total_seconds()

            # Increment the issue count
            issue_count += 1

        # Calculate the average resolution time
        avg_resolution_time = total_time / issue_count if issue_count > 0 else 0

        return avg_resolution_time
    else:
        # Handle errors
        print(f"Error: {response.status_code}")
        return None

# Function to get pull request trends within a date range
def get_pull_request_trends_within_date_range(repo_owner, repo_name, start_date, end_date):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        trends = [pull["created_at"] for pull in data]
        trends = [datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ') for date in trends]
        trends = [date for date in trends if start_date <= date <= end_date]
        return trends
    else:
        print(f"Error: {response.status_code}")
        return []

@app.route('/')
def search():
    return render_template('search.html')

# Route for processing the form and displaying results
@app.route('/redirect', methods=['POST'])
def redirect_page():
    repo_owner = request.form['repo_owner']
    repo_name = request.form['repo_name']
    start_date_str = request.form['start_date']
    end_date_str = request.form['end_date']

    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

    # Fetch contributor activity
    activity_data = get_contributor_activity(repo_owner, repo_name, start_date, end_date)

    # Fetch average resolution time
    avg_resolution_time = get_avg_resolution_time(repo_owner, repo_name)

    # Fetch pull request trends
    trends = get_pull_request_trends_within_date_range(repo_owner, repo_name, start_date, end_date)

    if not activity_data:
        return "No data available for the specified date range."

    # Plot contributor activity
    plt.figure(figsize=(12, 6))
    for contributor, activity in activity_data:
        dates, commits = zip(*activity)
        plt.plot(dates, commits, label=contributor)

    plt.xlabel("Date")
    plt.ylabel("Commits")
    plt.title(f"Contributor Activity for {repo_owner}/{repo_name} (Date Range: {start_date_str} to {end_date_str})")
    plt.legend()

    # Save the contributor activity plot to a BytesIO object
    image_stream_contributor = BytesIO()
    plt.savefig(image_stream_contributor, format='png')
    plt.close()

    # Encode the contributor activity plot to base64 for displaying in HTML
    image_base64_contributor = base64.b64encode(image_stream_contributor.getvalue()).decode('utf-8')

    # Create a DataFrame and parse dates for pull request trends
    df = pd.DataFrame({'created_at': trends})
    df["created_at"] = pd.to_datetime(df["created_at"])

    # Group data by month and count for pull request trends
    monthly_data = df.groupby(df["created_at"].dt.to_period("M")).size().reset_index(name="count")

    # Convert the "created_at" column to strings for plotting
    monthly_data["created_at"] = monthly_data["created_at"].dt.strftime('%Y-%m')

    # Create a bar graph for pull request trends
    plt.figure(figsize=(12, 6))
    plt.bar(monthly_data["created_at"], monthly_data["count"])
    plt.xlabel("Month")
    plt.ylabel("Number of Pull Requests")
    plt.title(f"Pull Request Trends for {repo_owner}/{repo_name} (Date Range: {start_date_str} to {end_date_str})")
    plt.xticks(rotation=45)

    # Save the pull request trends plot to a BytesIO object
    image_stream_pull_request = BytesIO()
    plt.savefig(image_stream_pull_request, format='png')
    plt.close()

    # Encode the pull request trends plot to base64 for displaying in HTML
    image_base64_pull_request = base64.b64encode(image_stream_pull_request.getvalue()).decode('utf-8')

    # Get commit frequency
    commits = get_commit_frequency(repo_owner, repo_name, start_date, end_date)

    if commits:
        # Plot commit frequency
    # Create a DataFrame and parse dates
        df = pd.DataFrame({'commit_date': commits})
        df["commit_date"] = pd.to_datetime(df["commit_date"])

        # Group data by day and count
        daily_data = df.groupby(df["commit_date"].dt.to_period("D")).size().reset_index(name="count")

        # Convert the "commit_date" column to strings for plotting
        daily_data["commit_date"] = daily_data["commit_date"].dt.strftime('%Y-%m-%d')

        # Create a bar graph
        plt.figure(figsize=(12, 6))
        plt.bar(daily_data["commit_date"], daily_data["count"])
        plt.xlabel("Date")
        plt.ylabel("Number of Commits")
        plt.title(f"Commit Frequency for {repo_owner}/{repo_name} (Date Range: {start_date} to {end_date})")
        plt.xticks(rotation=45)
        #plt.show()

        # Save the pull request trends plot to a BytesIO object
        image_stream_commit_frequency = BytesIO()
        plt.savefig(image_stream_commit_frequency, format='png')
        plt.close()

    # Encode the pull request trends plot to base64 for displaying in HTML
    image_base64_commit_frequency = base64.b64encode(image_stream_commit_frequency.getvalue()).decode('utf-8')

    return render_template('redirect.html', 
                           image_base64_contributor=image_base64_contributor, 
                           image_base64_pull_request=image_base64_pull_request,
                           avg_resolution_time=avg_resolution_time,
                           image_base64_commit_frequency=image_base64_commit_frequency)

# ... (remaining code)

# Run the application
if __name__ == '__main__':
    app.run(debug=True)
