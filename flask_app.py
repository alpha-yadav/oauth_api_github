
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, request,session,render_template,redirect
import requests
from flask_session import Session
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
"./flask_session"
CLIENT_ID = 'Ov23libtLqd2jwQ8ZlWM'
CLIENT_SECRET = '73bce66367b378681503b46f19532470c9267049'
REDIRECT_URI = '/callback'
Session(app)
@app.route('/')
def home():
    if 'access_token' in session:
        return f'You are authorized with token: {session["access_token"]}'
    return "login_page.html"
@app.route('/login')
def login():
    return redirect(f'https://github.com/login/oauth/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=repo,user')

@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_response = requests.post(
        'https://github.com/login/oauth/access_token',
        headers={'Accept': 'application/json'},
        data={
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'code': code,
            'redirect_uri': REDIRECT_URI
        }
    )
    token_json = token_response.json()
    session['access_token'] = token_json.get('access_token')

    if session['access_token']:
        create_webhook()
        return f'Authorization successful! Access token: {session["access_token"]}'
    else:
        return 'Authorization failed.'
@app.route('/payload', methods=['POST'])
def payload():
    payload_data = request.json
    # Process the pull request data and review it using an AI model
    review_pr(payload_data)
    return 'OK', 200
def create_webhook():
    access_token = session['access_token']
    headers = {'Authorization': f'token {access_token}'}
    data = {
        'name': 'web',
        'active': True,
        'events': ['pull_request'],
        'config': {
            'url': 'http://your_server_url/payload',
            'content_type': 'json'
        }
    }
    response = requests.post('https://api.github.com/repos/your_username/your_repo/hooks', headers=headers, json=data)
    if response.status_code == 201:
        print('Webhook created successfully')
    else:
        print('Failed to create webhook')
def review_pr(pr_data):
    pr_url = pr_data['pull_request']['url']
    access_token = session['access_token']
    review_comment = "This is an automatic review comment."

    # Post the review comment
    headers = {'Authorization': f'token {access_token}'}
    comment_url = f'{pr_url}/comments'
    comment_data = {'body': review_comment}
    response = requests.post(comment_url, headers=headers, json=comment_data)

    if response.status_code == 201:
        print('Review comment posted successfully')
    else:
        print('Failed to post review comment')
