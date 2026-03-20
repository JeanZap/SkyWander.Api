from typing import List

import RPi.GPIO as GPIO
from domain.atuador import Atuador
from domain.gamepad_listener_pygamepad import GamepadButtonListener, GamepadEvent
import shared.aritmetica as aritmetica
import shared.configuracao as conf
import threading
import time


class Montagem:
    MAX_PASSOS_ANALOGICO = 20
    posicao_inicial = {
        "dec": 0,
        "ra": 0,
        "decPassos": aritmetica.converter_angulo_para_passos(0),
        "raPassos": aritmetica.converter_angulo_para_passos(0),
    }
    posicao = {
        "dec": 0,
        "ra": 0,
        "decPassos": aritmetica.converter_angulo_para_passos(0),
        "raPassos": aritmetica.converter_angulo_para_passos(0),
    }
    tracking_ativo = False
    taxa_sideral = 0.004178
    ultimo_tempo_tracking = None
    esta_espelhado = False

    def __init__(self):
        self.kill_gamepad_threads = False
        self.gamepad_listener = None

        GPIO.setmode(GPIO.BCM)

        # GPIO.setup(conf.PIN_BUTTON_HOME, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        # GPIO.add_event_detect(
        #     conf.PIN_BUTTON_HOME, GPIO.FALLING, callback=self.mover_home, bouncetime=300
        # )

        self.motor_dec = Atuador(
            conf.DIR_PIN_DEC,
            conf.STEP_PIN_DEC,
            conf.LIMIT_SWITCH_DEC,
            "Dec",
            conf.OFFSET_DEC,
        )
        self.motor_ra = Atuador(
            conf.DIR_PIN_RA,
            conf.STEP_PIN_RA,
            conf.LIMIT_SWITCH_RA,
            "Ra",
            conf.OFFSET_RA,
        )

        self._homing()

        if conf.GAMEPAD_ENABLED:
            try:
                self.gamepad_listener = GamepadButtonListener(
                    callback=self._move_via_gamepad,
                    button_index=conf.GAMEPAD_HOME_BUTTON,
                    bouncetime_ms=conf.GAMEPAD_BOUNCETIME_MS,
                )
                self.gamepad_listener.start()
            except Exception as e:
                print(f"Falha ao iniciar listener de gamepad: {e}")

    def _homing(self):
        print("Iniciando homing...")

        t1 = threading.Thread(
            target=self.motor_dec.homing_motor,
        )
        t2 = threading.Thread(
            target=self.motor_ra.homing_motor,
        )

        t1.start()
        t2.start()

        t1.join()
        t2.join()

        print("Homing finalizado.")

    def mover_home(self):
        self._parar_tracking()
        self._homing()

    def _move_via_gamepad(self, evento: GamepadEvent):
        if evento.event_type == "toggle_capture":
            estado = "iniciada" if evento.capture_enabled else "parada"
            print(f"Captura do gamepad {estado}.")
            if evento.capture_enabled:
                self._parar_tracking()
            return

        if evento.event_type == "left_analog_motion":
            if not evento.capture_enabled:
                return

            left_x = float(evento.left_x or 0.0)
            left_y = float(evento.left_y or 0.0)

            passos_ra = self._converter_analogico_para_passos(left_x)
            passos_dec = self._converter_analogico_para_passos(left_y)

            if passos_ra == 0 and passos_dec == 0:
                return

            print(
                f"Analogico esquerdo x={left_x:.3f} y={left_y:.3f} "
                f"-> passos RA={passos_ra} DEC={passos_dec}"
            )

            self.kill_gamepad_threads = False
            threads: List[threading.Thread] = []

            if passos_ra != 0:
                threads.append(
                    threading.Thread(
                        target=self._mover_motor_loop, args=(self.motor_ra, passos_ra,))
                )
            if passos_dec != 0:
                threads.append(
                    threading.Thread(
                        target=self._mover_motor_loop, args=(self.motor_dec, passos_dec,))
                )

            for thread in threads:
                thread.start()

    def _mover_motor_loop(self, motor_ra: Atuador, passos: int):
        while not self.kill_gamepad_threads:
            motor_ra.mover_motor(passos)

    def _converter_analogico_para_passos(self, valor: float) -> int:
        intensidade = min(max(abs(valor), 0.0), 1.0)
        passos = int(round(intensidade * self.MAX_PASSOS_ANALOGICO))
        if passos == 0:
            return 0
        return passos if valor > 0 else -passos

    def apontar(self, dec_alvo: float, ra_alvo: float):
        self._parar_tracking()

        inicio = time.time()

        dec_alvo_passos = aritmetica.converter_angulo_para_passos(dec_alvo)
        ra_alvo_passos = aritmetica.converter_angulo_para_passos(ra_alvo)

        dec_alvo_protegido, ra_alvo_protegido = self.converter_angulos_protegidos(
            dec_alvo, ra_alvo
        )
        dec_passos_restantes, ra_passos_restantes = self.diferenca_posicao_alvo(
            dec_alvo_protegido, ra_alvo_protegido
        )

        print(
            "Dec: ",
            dec_alvo_protegido,
            "Hh: ",
            ra_alvo_protegido,
            " - protegido",
        )
        t1 = threading.Thread(
            target=self.motor_dec.mover_motor, args=(dec_passos_restantes,)
        )
        t2 = threading.Thread(
            target=self.motor_ra.mover_motor, args=(ra_passos_restantes,)
        )

        t1.start()
        t2.start()

        t1.join()
        t2.join()

        self.posicao = {
            "dec": dec_alvo_protegido,
            "ra": ra_alvo_protegido,
            "decPassos": dec_alvo_passos,
            "raPassos": ra_alvo_passos,
        }

        fim = time.time()
        tempo_decorrido = fim - inicio

        self.iniciar_tracking(tempo_decorrido)

    def deve_proteger(self, ra: float):
        return ra > 0 and ra <= 180

    def converter_angulos_protegidos(self, dec: float, ra: float):
        if self.deve_proteger(ra):
            dec = -dec
            dec += 180
            dec %= 360

            ra += 180
            ra %= 360

            self.esta_espelhado = True
        else:
            self.esta_espelhado = False

        return dec, ra

    def diferenca_posicao_alvo(self, dec: float, ra: float):
        dec_atual = self.posicao["dec"]
        ra_atual = self.posicao["ra"]

        dec = self.diferenca_posicao_alvo_eixo(dec_atual, dec)
        ra = self.diferenca_posicao_alvo_eixo(ra_atual, ra)

        return dec, ra

    def diferenca_posicao_alvo_eixo(self, angulo_atual: float, angulo_alvo: float):
        diferenca = aritmetica.calcular_diferenca_angular(
            angulo_atual, angulo_alvo)
        return aritmetica.converter_angulo_para_passos(diferenca)

    def iniciar_tracking(self, tempo_offset: float = 0.0):
        self.tracking_ativo = True
        self.ultimo_tempo_tracking = time.time() - tempo_offset
        threading.Thread(target=self._tracking_loop, daemon=True).start()

    def _tracking_loop(self):
        while self.tracking_ativo:
            agora = time.time()
            tempo_decorrido = agora - self.ultimo_tempo_tracking

            movimento_ra = self.taxa_sideral * tempo_decorrido

            passos_ra = aritmetica.converter_angulo_para_passos(movimento_ra)

            if self.esta_espelhado:
                passos_ra *= -1

            if passos_ra != 0:
                self.ultimo_tempo_tracking = agora
                self.motor_ra.mover_motor(passos_ra)
                self.posicao["ra"] += movimento_ra
                self.posicao["raPassos"] += passos_ra

            time.sleep(conf.DELAY_ATUALIZACAO)

    def _parar_tracking(self):
        self.tracking_ativo = False

    def __del__(self):
        if self.gamepad_listener is not None:
            self.gamepad_listener.stop()
        GPIO.cleanup()
