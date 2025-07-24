from flask import Flask, request, jsonify
from instagrapi import Client
from instagrapi.exceptions import TwoFactorRequired
import os

app = Flask(__name__)

username = "kauamktpro"
password = "100711Ma.?"
session_file = "session.json"

cl = Client()

if os.path.exists(session_file):
    cl.load_settings(session_file)

def do_login():
    try:
        cl.login(username, password)
    except TwoFactorRequired:
        code_2fa = input("Digite o código 2FA: ")
        cl.login(username, password, verification_code=code_2fa)
    cl.dump_settings(session_file)

@app.before_request
def ensure_logged_in():
    if not cl.user_id:
        do_login()

@app.route('/send-message', methods=['POST'])
def send_message():
    data = request.json
    user_id = data.get('user_id')
    mensagem = data.get('mensagem')
    if not user_id or not mensagem:
        return jsonify({"error": "user_id e mensagem são obrigatórios"}), 400

    try:
        cl.direct_send(mensagem, [user_id])
        return jsonify({"status": "Mensagem enviada com sucesso!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
