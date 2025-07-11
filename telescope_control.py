import socket
import struct
import json
import numpy as np
import shared.aritmetica as aritmetica
from domain.montagem import Montagem

atuadores = Montagem()

def start_stellarium_receiver(host='0.0.0.0', port=10000):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        s.bind((host, port))
        s.listen(1)

        print("Iniciado")
        while True:
            try:
                conn, addr = s.accept()

                with conn:
                    print(f"Conexão estabelecida com {addr}")

                    while True:

                        data = conn.recv(1024)

                        if not data:
                            break

                        try:
                            data = struct.unpack("3iIi", data)

                            ra = data[3]*(np.pi / 0x80000000)
                            dec = data[4]*(np.pi / 0x80000000)
                            ra_deg = ra * (180.0 / np.pi)
                            dec_deg = dec * (180.0 / np.pi)
                            hour_angle = aritmetica.ra_to_hour_angle(ra_deg)

                            print("Dec: ", dec_deg, "Hh: ", hour_angle)

                            atuadores.apontar(dec_deg, hour_angle)

                        except json.JSONDecodeError:
                            print("Dados recebidos não são JSON válido:", data)

            except KeyboardInterrupt:
                atuadores.mover_home()
                print("\nServidor encerrado pelo usuário.")
                break
            except Exception as e:
                print(f"Erro na conexão: {e}")
                continue


if __name__ == "__main__":
    HOST = '0.0.0.0'
    PORT = 10000

    start_stellarium_receiver(HOST, PORT)
