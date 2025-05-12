from flask import Flask, request
from flask_cors import CORS
import threading
from domain.montagem import Montagem
import shared.configuracao as config
import json
import requests

app = Flask(__name__)
CORS(app)

# Variáveis compartilhadas
HEADERS = {'Content-Type': 'application/json'}
posicao_alvo = {"ra": None, "dec": None, "name": None}
rastreamento_ativo = False
lock = threading.Lock()
atuadores = Montagem()


def obterPosicaoAstro(name):
    resposta = requests.get(
        f"{config.SERVER_STELARIUM}/objects/info?name={name}&format=json", headers=HEADERS)

    if resposta.status_code == 200:
        return resposta.json()
    else:
        return json.dumps({'erro': 'Falha ao acessar API externa'}), 500


def iniciar_rastreamento():
    global rastreamento_ativo

    name = posicao_alvo.get("name")

    posicao = obterPosicaoAstro(name)

    with lock:
        dec = posicao.get("dec")
        ra = posicao.get("hourAngle-dd")

    if ra is not None and dec is not None:
        # print(f"Movendo para Ra: {ra}, Dec: {dec}")
        atuadores.apontar(dec, ra)


@app.route('/apontar', methods=['POST'])
def apontar():
    print(f"LOG: /apontar {request.json}")
    global rastreamento_ativo
    data = request.json
    name = data.get('name')

    if name is None:
        return {"erro": "name é obrigatórios"}, 400

    with lock:
        posicao_alvo["name"] = name

    if not rastreamento_ativo:
        rastreamento_ativo = True
        t = threading.Thread(target=iniciar_rastreamento)
        t.daemon = True
        t.start()

    return {"status": "Rastreamento iniciado ou atualizado"}, 200


@app.route('/desligar', methods=['POST'])
def desligar():
    print(f"LOG: /desligar {request.json}")

    atuadores.mover_home()

    return {"status": "Desligado com sucesso"}, 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
