from flask import Flask, request, jsonify
from instagrapi import Client
from instagrapi.exceptions import TwoFactorRequired
import os
import traceback

app = Flask(__name__)

username = "kauamktpro"
password = "100711Ma.?"
session_file = "session.json"

cl = Client()

# Carrega sessão se existir
if os.path.exists(session_file):
    cl.load_settings(session_file)

# Verifica se a sessão atual ainda está válida
def is_session_valid():
    try:
        cl.get_timeline_feed()
        return True
    except Exception as e:
        print("Sessão inválida:", e)
        return False

# Realiza o login e salva a sessão
def do_login():
    try:
        cl.login(username, password)
    except TwoFactorRequired:
        code_2fa = input("Digite o código 2FA: ")
        cl.login(username, password, verification_code=code_2fa)
    finally:
        cl.dump_settings(session_file)
        print("✅ Sessão salva com sucesso.")

# Antes de cada requisição, verifica se está logado
@app.before_request
def ensure_logged_in():
    if not cl.user_id or not is_session_valid():
        print("🔁 Sessão ausente ou inválida. Fazendo login...")
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
        print("Erro ao enviar mensagem:", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    try:
        cl.get_timeline_feed()
        return jsonify({"status": "online", "user_id": cl.user_id})
    except Exception as e:
        return jsonify({"status": "offline", "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
