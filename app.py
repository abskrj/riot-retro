import json

from constants import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_TOKEN_ENDPOINT, GOOGLE_AUTHORIZATION_ENDPOINT, GOOGLE_USERINFO_ENDPOINT
from init_app import create_app
from flask_login import (
    LoginManager,
    current_user,
    login_user,
    logout_user,
    UserMixin
)
from oauthlib.oauth2 import WebApplicationClient
import requests
from flask import redirect, request, url_for, render_template
contant_header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
}

requests.packages.urllib3.util.connection.HAS_IPV6 = False

app, dynamo = create_app()
login_manager = LoginManager()
login_manager.init_app(app)

client = WebApplicationClient(GOOGLE_CLIENT_ID)

class User(UserMixin):
    def __init__(self, id, name, email, picture, days_to_go, city):
        self.id = id
        self.name = name
        self.email = email
        self.picture = picture
        self.days_to_go = days_to_go
        self.city = city
    
    @staticmethod
    def create(id, name, email, picture):
        dynamo.tables["users"].put_item(Item={
            'id': id,
            'email': email,
            'name': name,
            'picture': picture,
            'is_active': True,
            'is_anonymous': False,
            'is_authenticated': True,
            'days_to_go': 0,
            'city': None
        })

    @staticmethod
    def get(id):
        try:
            _user = dynamo.tables["users"].get_item(Key={"id": id}).get("Item")
            return User(
                id=_user.get("id"),
                name=_user.get("name"),
                email=_user.get("email"),
                picture=_user.get("picture"),
                days_to_go=_user.get("days_to_go"),
                city=_user.get("city")
            )
        except:
            return None
    
    @staticmethod
    def update(id, days_to_go, city):
        dynamo.tables["users"].update_item(
            Key={"id": id},
            UpdateExpression="SET days_to_go = :days_to_go, city = :city",
            ExpressionAttributeValues={
                ":days_to_go": days_to_go,
                ":city": city
            }
        )
        
    def get_id(self):
        return self.id

# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route("/")
def index():
    return render_template("index.html", user=current_user)

@app.route("/login")
def login():
    request_uri = client.prepare_request_uri(
        GOOGLE_AUTHORIZATION_ENDPOINT,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )

    return redirect(request_uri)

@app.route("/login/callback")
def callback():
    code = request.args.get("code")

    token_url, headers, body = client.prepare_token_request(
        GOOGLE_TOKEN_ENDPOINT,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers={**headers, **contant_header},
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
        timeout=2
    )


    client.parse_request_body_response(json.dumps(token_response.json()))

    uri, headers, body = client.add_token(GOOGLE_USERINFO_ENDPOINT)
    userinfo_response = requests.get(uri, headers=headers, data=body, timeout=2)

    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400
    
    user = User(
        id=unique_id, name=users_name, email=users_email, picture=picture
    )

    if not User.get(unique_id):
        User.create(unique_id, users_name, users_email, picture)
    
    login_user(user)
    return redirect(url_for("index"))

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/schedule", methods=["GET", "POST"])
def schedule():
    if not current_user.is_authenticated:
        return redirect(url_for("index"))
    
    if request.method == "POST":
        days_to_go = request.form.get("days_to_go")
        city = request.form.get("city")
        User.update(current_user.id, days_to_go, city)
        return render_template("schedule.html", user=current_user)

    if current_user.days_to_go and current_user.city:
        return render_template("schedule.html", user=current_user)

    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(ssl_context="adhoc")