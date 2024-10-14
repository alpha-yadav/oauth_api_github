# A very simple Flask Hello World app for you to get started with...
from flask import Flask, request,session,render_template,redirect
import requests
import time,json 
from flask_session import Session
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
CLIENT_ID = "Client id get from your github site/app" # Like this 'ORf3lLbtLqd2nwA8ZmWl'
CLIENT_SECRET = "" #same as client id place like'7fbcfe666e7b378e81503be6f19432470c9267049'
REDIRECT_URI = "" # after login this webpage show like 'https://www.pythonconfig.com/callback'
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
    with open("pull request.log","a") as wr:
        wr.write(time.ctime+":::"+json.dumps(payload_data)+"\n")
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
            'url': 'https://www.pythonconfig.com/payload',
            'content_type': 'json'
        }
    }
    response = requests.post('https://api.github.com/repos/user_id/rep0/hooks', headers=headers, json=data)
    if response.status_code == 201:
        return('Webhook created successfully')
    else:
        return('Failed to create webhook')
def review_pr(pr_data):
    with open("token.txt","r") as rd:
        access_token = rd.read()
        #session['access_token']
    review_comment = "This is an automatic review comment."
    issue_number = pr_data['pull_request']['number']
    # Post the review comment
    headers = {'Authorization': f'token {access_token}'}
    comment_url = f'https://api.github.com/repos/user_id/repo/issues/{issue_number}/comments'
    #comment_url = f'{pr_url}/issues/{issue_number}/comments'
    comment_data = {'body': review_comment}
    response = requests.post(comment_url, headers=headers, json=comment_data)
    return response.content
    if response.status_code == 201:
        return('Review comment posted successfully')
    else:
        return('Failed to post review comment')
