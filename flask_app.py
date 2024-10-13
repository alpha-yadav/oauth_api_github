
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, request,session,render_template,redirect
import requests
from flask_session import Session
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
CLIENT_ID = 'Ov23libtLqd2jwQ8ZlWM'
CLIENT_SECRET = '73bce66367b378681503b46f19532470c9267049'
REDIRECT_URI = 'https://adix.pythonanywhere.com/callback'
Session(app)
@app.route('/')
def home():
    if 'access_token' in session:
        return f'You are authorized with token: {session["access_token"]}'
    return render_template("login_page.html")
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
        res=create_webhook()
        with open("token.txt","w") as wr:
                wr.write(session['access_token'])
        return f'Authorization successful! Access token: {session["access_token"]}\n\
        {res}'
    else:
        return 'Authorization failed.'
@app.route('/payload', methods=['POST'])
def payload():
    payload_data = request.json
    # Process the pull request data and review it using an AI model
    state=str(review_pr(payload_data))
    return state, 200
def create_webhook():
    access_token = session['access_token']
    headers = {'Authorization': f'token {access_token}'}
    data = {
        'name': 'web',
        'active': True,
        'events': ['pull_request'],
        'config': {
            'url': 'https://adix.pythonanywhere.com/payload',
            'content_type': 'json'
        }
    }
    response = requests.post('https://api.github.com/repos/alpha-yadav/oauth_api_github/hooks', headers=headers, json=data)
    if response.status_code == 201:
        return('Webhook created successfully')
    else:
        return('Failed to create webhook')
def review_pr(pr_data):
    pr_url = pr_data["repository"]["hooks_url"]
    with open("token.txt","r") as rd:
        access_token = rd.read()
        #session['access_token']
    review_comment = "This is an automatic review comment."
    issue_number=1
    # Post the review comment
    headers = {'Authorization': f'token {access_token}'}
    comment_url = f'{pr_url}/issues/{issue_number}/comments'
    comment_data = {'body': review_comment}
    response = requests.post(comment_url, headers=headers, json=comment_data)
    return response.content
    if response.status_code == 201:
        return('Review comment posted successfully')
    else:
        return('Failed to post review comment')
