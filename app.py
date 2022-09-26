from flask import Flask, jsonify, render_template,request
from flask.views import MethodView
from chatbot import chatbot
from better_profanity import profanity
from flask_simplelogin import SimpleLogin, get_username, login_required
import pandas as pd
import numpy as np

my_users = {
    "217117929": {"password": "norris", "roles": ["admin"]},
    "lee": {"password": "douglas", "roles": []},
    "mary": {"password": "jane", "roles": []},
    "steven": {"password": "wilson", "roles": ["admin"]},
}


def check_my_users(user):
    """Check if user exists and its credentials.
    Take a look at encrypt_app.py and encrypt_cli.py
     to see how to encrypt passwords
    """
    user_data = my_users.get(user["username"])
    if not user_data:
        return False  # <--- invalid credentials
    elif user_data.get("password") == user["password"]:
        return True  # <--- user is logged in!

    return False  # <--- invalid credentials


app = Flask(__name__)
app.config.from_object("settings")
app.static_folder = 'static'


simple_login = SimpleLogin(app, login_checker=check_my_users)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/help")
def help():
    return render_template("help.html")

@app.route("/statistics")
def statistics():
    return render_template("statistics.html",context=frequentAskQuestions())


@app.route("/secret")
@login_required(username=["chuck", "mary"])
def secret():
    return render_template("secret.html")


@app.route("/api", methods=["POST"])
@login_required(basic=True)
def api():
    return jsonify(data="You are logged in with basic auth")


def be_admin(username):
    """Validator to check if user has admin role"""
    user_data = my_users.get(username)
    if not user_data or "admin" not in user_data.get("roles", []):
        return "User does not have admin role"


def have_approval(username):
    """Validator: all users approved, return None"""
    return


@app.route("/complex")
@login_required(must=[be_admin, have_approval])
def complexview():
    return render_template("secret.html")


@app.route("/get", )
def get_bot_response():
    userText = request.args.get('msg')

    #start  profanity checks
    profanity.load_censor_words()
    censored_text = profanity.censor(userText)
    if(userText != censored_text):
        userText = "PLEASE REFRAIN FROM SUCH LANGAUGE!!!"
        return userText
    #end    profanity checks

    botResponse = str(chatbot.get_response(userText))
    update_user_train_file(userText, botResponse)

    return botResponse

def update_user_train_file(userInput, botResponse):
    """
    function to push new user input to a training file
    """
    f= open("raw/user_input_data.txt","a+")
    
    userInputToSave = userInput[0].upper() + userInput[1:]
    f.write(userInputToSave + "\n")
    f.write(botResponse + "\n")

    f.close


def frequentAskQuestions():

    userInputQuestions =pd.read_csv('./raw/user_input_data.txt',on_bad_lines='skip',names=['User Input'])

    actualQuestions =pd.read_csv('./raw/FCI.txt',on_bad_lines='skip',names=['Questions'])
    questionOnly =actualQuestions.iloc[::2].to_numpy()

    flat_list = [num for sublist in questionOnly for num in sublist]


    inputOnly =userInputQuestions.to_numpy()

    flat_list_input = [num for sublist in inputOnly for num in sublist]

    dic={}

    for item in flat_list:
        count =flat_list_input.count(item)
        dic[item] = count
        
    return {x:y for x,y in dic.items() if y!=0}



class ProtectedView(MethodView):
    decorators = [login_required]

    def get(self):
        return "You are logged in as <b>{0}</b>".format(get_username())


app.add_url_rule("/protected", view_func=ProtectedView.as_view("protected"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, use_reloader=True, debug=True)


