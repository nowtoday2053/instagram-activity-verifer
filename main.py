from flask import Flask, render_template, request, Response, url_for, send_file
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import pytz
import pandas as pd
import io
import csv
import json
import os

app = Flask(__name__)

# Store results in memory (in a production environment, use a proper database)
current_results = []
progress = {"current": 0, "total": 0}

def check_instagram_activity(driver, target_user):
    try:
        # Go to target profile
        driver.get(f"https://www.instagram.com/{target_user}/")
        time.sleep(3)  # Initial wait for page load

        result = {
            'user': target_user,
            'story': False,
            'last_post_time': None,
            'recent_post': False,
            'active': False
        }

        # Check for active story
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "canvas._aa63"))
            )
            result['story'] = True
            result['active'] = True
        except:
            pass

        # Check last post timestamp
        try:
            post = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "article time"))
            )
            timestamp = post.get_attribute('datetime')
            post_date = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            now = datetime.now(pytz.UTC)
            
            # Format the time ago
            time_diff = now - post_date
            if time_diff.days == 0:
                if time_diff.seconds < 3600:
                    time_ago = f"{time_diff.seconds // 60}m ago"
                else:
                    time_ago = f"{time_diff.seconds // 3600}h ago"
            else:
                time_ago = f"{time_diff.days}d ago"
            
            result['last_post_time'] = time_ago
            
            # Check if post is within last week
            if time_diff.days <= 7:
                result['recent_post'] = True
                result['active'] = True
        except:
            result['last_post_time'] = 'No recent posts'

        return result
    except Exception as e:
        return {
            'user': target_user,
            'story': False,
            'last_post_time': f'Error: {str(e)}',
            'recent_post': False,
            'active': False
        }

def update_progress(current, total):
    global progress
    progress["current"] = current
    progress["total"] = total

@app.route('/progress')
def progress_stream():
    def generate():
        while True:
            yield f"data: {json.dumps(progress)}\n\n"
            time.sleep(1)
            if progress["current"] == progress["total"] and progress["total"] > 0:
                break
    return Response(generate(), mimetype='text/event-stream')

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def check_activity():
    global current_results
    try:
        username = request.form['username']
        password = request.form['password']
        file = request.files['leads']
        
        # Read Excel file
        df = pd.read_excel(file)
        
        # Look for username column
        username_column = None
        for col in ['userName', 'Username', 'username', 'user_name', 'User Name', 'Instagram Username']:
            if col in df.columns:
                username_column = col
                break
                
        if not username_column:
            return "Could not find username column in Excel file", 400
            
        usernames = df[username_column].dropna().tolist()
        
        # Initialize progress
        update_progress(0, len(usernames))
        
        # Initialize Chrome
        options = uc.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        driver = uc.Chrome(options=options)
        
        try:
            # Login to Instagram
            driver.get("https://www.instagram.com/accounts/login/")
            time.sleep(3)

            username_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            password_input = driver.find_element(By.NAME, "password")
            
            username_input.send_keys(username)
            password_input.send_keys(password)
            password_input.send_keys(Keys.RETURN)
            time.sleep(5)

            # Check each username
            results = []
            for i, target_user in enumerate(usernames, 1):
                if target_user and isinstance(target_user, str):
                    result = check_instagram_activity(driver, target_user.strip())
                    results.append(result)
                    update_progress(i, len(usernames))
                    time.sleep(2)  # Avoid rate limiting
            
            current_results = results
            
            # Calculate statistics
            active_accounts = sum(1 for r in results if r['active'])
            
            return render_template('results.html', 
                                results=results,
                                total_accounts=len(results),
                                active_accounts=active_accounts,
                                inactive_accounts=len(results) - active_accounts)
            
        finally:
            driver.quit()
            
    except Exception as e:
        return f"An error occurred: {str(e)}", 500

@app.route('/download_csv/<type>')
def download_csv(type):
    if not current_results:
        return "No results available", 404
        
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Username', 'Status', 'Has Story', 'Last Post'])
    
    # Filter results based on type
    filtered_results = current_results
    if type == 'active':
        filtered_results = [r for r in current_results if r['active']]
    elif type == 'inactive':
        filtered_results = [r for r in current_results if not r['active']]
    
    # Write data
    for result in filtered_results:
        writer.writerow([
            result['user'],
            'Active' if result['active'] else 'Inactive',
            'Yes' if result['story'] else 'No',
            result['last_post_time']
        ])
    
    # Create response
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename=instagram_activity_{type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        }
    )

if __name__ == '__main__':
    app.run(debug=True)
