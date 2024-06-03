import hvac
from flask import Flask, render_template, request, redirect, url_for
from db import DBManager


dbm = DBManager()
app = Flask(__name__)


# def client():
#     client = hvac.Client(
#         url='http://127.0.0.1:8200'
#     )
#
#     print(f"Client Auth: {client.is_authenticated()}")
#
#     try:
#         client.auth.userpass.login(
#             username='alice',
#             password='alice'
#         )
#     except:
#         print("Wrong Pass or id")
#         exit(1)
#
#     print(f"Client Auth: {client.is_authenticated()}")
#     print("Autenticato, redirect to ...")
#
#     print(vars(client.auth.userpass))
#     print(client.auth.userpass.read_user('alice'))

@app.route('/login', methods=['POST'])
def login():
    if request.method != 'POST':
        return "<h1>ERRORE !</h1>"
    
    client = hvac.Client(
        url='http://127.0.0.1:8200'
    )

    # print(f"Client Auth: {client.is_authenticated()}")

    try:
        client.auth.userpass.login(
            username=request.form['user'],
            password=request.form['pass']
        )
    except:
        return "Wrong Pass or id"

    # return "NICE!"
    return redirect('/user')


@app.route('/user')
def user():
    return render_template('user.html')


@app.route("/")
def hellow_world():
    return render_template('index.html')

# print(vars(client.session))
# print(vars(client))
# print(client.read("/auth/userpass/users/alice"))
# config_response = client.secrets.activedirectory.read_config()
# print(config_response)
