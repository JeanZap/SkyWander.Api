import RPi.GPIO as GPIO
from RpiMotorLib import RpiMotorLib
from RpiMotorLib.RpiMotorLib import A4988Nema
import shared.aritmetica as aritmetica
import shared.configuracao as conf
import threading
import time


class Montagem:
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
        GPIO.setmode(GPIO.BCM)

        GPIO.setup(conf.PIN_BUTTON_HOME, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(
            conf.PIN_BUTTON_HOME, GPIO.FALLING, callback=self.mover_home, bouncetime=300
        )

        GPIO.setup(conf.LIMIT_SWITCH_DEC, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(conf.LIMIT_SWITCH_RA, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        self.motor_dec = RpiMotorLib.A4988Nema(
            conf.DIR_PIN_DEC, conf.STEP_PIN_DEC, (False, False, False), "A4988"
        )
        self.motor_ra = RpiMotorLib.A4988Nema(
            conf.DIR_PIN_RA, conf.STEP_PIN_RA, (False, False, False), "A4988"
        )

        self._homing()

    def _homing(self):
        return
        print("Iniciando homing...")

        dir_dec = True
        dir_ra = True

        def homing_motor(
            motor: A4988Nema, limit_pin: int, direction: bool, nome: str, offset: int
        ):
            print(f"Homing motor {nome}...")

            while GPIO.input(limit_pin) == GPIO.HIGH:
                motor.motor_go(
                    direction, conf.TIPO_PASSO, 1, conf.STEP_DELAY, False, 0.0
                )
            print(f"Switch {nome} pressionado. Recuando offset...")

            motor.motor_go(
                not direction, conf.TIPO_PASSO, offset, conf.STEP_DELAY, False, 0.0
            )
            print(f"{nome} homing completo.")

        # t1 = threading.Thread(
        #     target=homing_motor, args=(self.motor_dec, self.LIMIT_SWITCH_DEC,
        #                                dir_dec, "DEC", conf.OFFSET_DEC)
        # )
        # t2 = threading.Thread(
        #     target=homing_motor, args=(self.motor_ra, self.LIMIT_SWITCH_RA,
        #                                dir_ra, "RA", conf.OFFSET_RA)
        # )

        # t1.start()
        # t2.start()

        # t1.join()
        # t2.join()

        print("Homing finalizado.")

    def mover_home(self):
        self._parar_tracking()
        self.apontar(0, 0)

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
            target=self._mover_motor, args=(self.motor_dec, dec_passos_restantes)
        )
        t2 = threading.Thread(
            target=self._mover_motor, args=(self.motor_ra, ra_passos_restantes)
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

    def _mover_motor(self, motor: A4988Nema, passos: int):
        sentido = passos > 0

        motor.motor_go(
            clockwise=sentido,
            steptype=conf.TIPO_PASSO,
            steps=abs(passos),
            stepdelay=conf.STEP_DELAY,
            verbose=False,
            initdelay=conf.INIT_STEP_DELAY,
        )

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
        diferenca = aritmetica.calcular_diferenca_angular(angulo_atual, angulo_alvo)
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
                self._mover_motor(self.motor_ra, passos_ra)
                self.posicao["ra"] += movimento_ra
                self.posicao["raPassos"] += passos_ra

            time.sleep(conf.DELAY_ATUALIZACAO)

    def _parar_tracking(self):
        self.tracking_ativo = False

    def __del__(self):
        GPIO.cleanup()
