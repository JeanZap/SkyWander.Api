from flask import Flask, request
import threading
import time

app = Flask(__name__)

# Variáveis compartilhadas
posicao_alvo = {"az": None, "alt": None}
rastreamento_ativo = False
lock = threading.Lock()

def loop_rastreamento():
    global rastreamento_ativo
    print("Iniciando rastreamento...")
    while rastreamento_ativo:
        with lock:
            az = posicao_alvo.get("az")
            alt = posicao_alvo.get("alt")
        if az is not None and alt is not None:
            print(f"Movendo para Az: {az}, Alt: {alt}")
            # Aqui você chama o controle real do motor, ex: mover_motor(az, alt)
        time.sleep(5)  # Atualiza a cada 5 segundos

@app.route('/apontar', methods=['POST'])
def apontar():
    global rastreamento_ativo
    data = request.json
    az = data.get('az')
    alt = data.get('alt')

    if az is None or alt is None:
        return {"erro": "az e alt são obrigatórios"}, 400

    with lock:
        posicao_alvo["az"] = az
        posicao_alvo["alt"] = alt

    # Inicia o loop de rastreamento, se ainda não estiver ativo
    if not rastreamento_ativo:
        rastreamento_ativo = True
        t = threading.Thread(target=loop_rastreamento)
        t.daemon = True
        t.start()

    return {"status": "rastreamento iniciado ou atualizado"}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)