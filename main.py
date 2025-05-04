from flask import Flask, request, jsonify
import threading
import time
from Atuador import Atuador
import Configuracao.Configuracao as config
import requests

app = Flask(__name__)

# Variáveis compartilhadas
posicao_alvo = {"ra": None, "dec": None, "name": None}
rastreamento_ativo = False
lock = threading.Lock()


def obterPosicaoAstro(name):
    resposta = requests.get(
        f"{config.server_stelarium}/objects/info?name={name}&format=json")

    if resposta.status_code == 200:
        dados_api = resposta.json()
        return jsonify(dados_api)
    else:
        return jsonify({'erro': 'Falha ao acessar API externa'}), 500


def loop_rastreamento():
    global rastreamento_ativo

    while rastreamento_ativo:
        name = posicao_alvo.get("name")

        posicao = obterPosicaoAstro(name)

        with lock:
            ra = posicao.get("ra")
            dec = posicao.get("dec")

        if ra is not None and dec is not None:
            print(f"Movendo para Ra: {ra}, Dec: {dec}")
            # Aqui você chama o controle real do motor, ex: mover_motor(az, alt)
        time.sleep(5)  # Atualiza a cada 5 segundos


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
        t = threading.Thread(target=loop_rastreamento)
        t.daemon = True
        t.start()

    return {"status": "rastreamento iniciado ou atualizado"}, 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
