import RPi.GPIO as GPIO
from RpiMotorLib import RpiMotorLib
from RpiMotorLib.RpiMotorLib import A4988Nema
import shared.aritmetica as aritmetica
import shared.configuracao as conf
import threading
import datetime
import time


class Montagem:
    posicaoInicial = {
        "dec": -90,
        "ra": 90,
        "decPassos": aritmetica.converter_angulo_para_passos(-90),
        "raPassos": aritmetica.converter_angulo_para_passos(90),
    }
    posicao = {
        "dec": -90,
        "ra": 90,
        "decPassos": aritmetica.converter_angulo_para_passos(-90),
        "raPassos": aritmetica.converter_angulo_para_passos(90),
    }
    tracking_ativo = False
    taxa_sideral = 0.004178
    ultimo_tempo_tracking = None

    def __init__(self):
        GPIO.setmode(GPIO.BCM)

        self.motorDec = RpiMotorLib.A4988Nema(
            conf.DIR_PIN_DEC, conf.STEP_PIN_DEC, (False, False, False), "A4988"
        )
        self.motorRa = RpiMotorLib.A4988Nema(
            conf.DIR_PIN_RA, conf.STEP_PIN_RA, (False, False, False), "A4988"
        )

        self._homing()

    def _homing(self):
        # todo: Executar homing
        pass

    def mover_home(self):
        self._parar_tracking()
        self.apontar(self, 0, 90)

    def apontar(self, decAlvo: float, raAlvo: float):
        self._parar_tracking()

        decAlvoPassos = aritmetica.converter_angulo_para_passos(decAlvo)
        raAlvoPassos = aritmetica.converter_angulo_para_passos(raAlvo)

        decPassosRestantes, raPassosRestantes = self.diferenca_posicao_alvo(
            decAlvo, raAlvo
        )

        print(decPassosRestantes, raPassosRestantes, datetime.datetime.now())
        t1 = threading.Thread(
            target=self._mover_motor, args=(self.motorDec, decPassosRestantes)
        )
        t2 = threading.Thread(
            target=self._mover_motor, args=(self.motorRa, raPassosRestantes)
        )

        t1.start()
        t2.start()

        t1.join()
        t2.join()

        print(raPassosRestantes, datetime.datetime.now())
        self.posicao = {
            "dec": decAlvo,
            "ra": raAlvo,
            "decPassos": decAlvoPassos,
            "raPassos": raAlvoPassos,
        }

        self.iniciar_tracking()

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

    def diferenca_posicao_alvo(self, dec: float, ra: float):
        dec = aritmetica.converter_angulo_para_passos(
            dec
        ) - aritmetica.converter_angulo_para_passos(self.posicao["dec"])
        ra = aritmetica.converter_angulo_para_passos(
            ra
        ) - aritmetica.converter_angulo_para_passos(self.posicao["ra"])
        return dec, ra

    def iniciar_tracking(self):
        self.tracking_ativo = True
        self.ultimo_tempo_tracking = time.time()
        threading.Thread(target=self._tracking_loop, daemon=True).start()

    def _tracking_loop(self):
        while self.tracking_ativo:
            agora = time.time()
            tempo_decorrido = agora - self.ultimo_tempo_tracking
            self.ultimo_tempo_tracking = agora

            movimento_ra = self.taxa_sideral * tempo_decorrido

            passos_ra = aritmetica.converter_angulo_para_passos(movimento_ra)

            if passos_ra != 0:
                self._mover_motor(self.motorRa, passos_ra)
                self.posicao["ra"] += movimento_ra
                self.posicao["raPassos"] += passos_ra

            time.sleep(conf.DELAY_ATUALIZACAO)

    def _parar_tracking(self):
        self.tracking_ativo = False

    def __del__(self):
        GPIO.cleanup()
