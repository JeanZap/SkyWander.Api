import RPi.GPIO as GPIO
from RpiMotorLib import RpiMotorLib
import Aritmetica.Aritmetica as aritmetica
import Configuracao.Configuracao as configuracao
import threading
import datetime


class Atuadores:
    ultimoDec = 0
    ultimoRa = 0
    posicao = {"dec": 0, "ra": 0}

    def __init__(self):
        GPIO.setmode(GPIO.BCM)

        self.motorDec = RpiMotorLib.A4988Nema(
            configuracao.DIR_PIN_DEC, configuracao.STEP_PIN_DEC, (True, True, True), "A4988")
        self.motorRa = RpiMotorLib.A4988Nema(
            configuracao.DIR_PIN_RA, configuracao.STEP_PIN_RA, (True, True, True), "A4988")
        self._homing()

    def _homing(self):
        # todo: Executar homing
        pass

    def apontar(self, dec, ra):
        dec = aritmetica.converter_angulo_para_passos(dec)
        ra = aritmetica.converter_angulo_para_passos(ra)

        if self.ultimoDec != dec or self.ultimoRa != ra:
            print(f"Declination: {dec}, Right ascension: {ra} {datetime.datetime.now()}")
            self.ultimoDec = dec
            self.ultimoRa = ra

        decPassosRestantes, raPassosRestantes = self.diferencaPosicaoParaAlvo(
            dec, ra)

        t1 = threading.Thread(target=self._mover_motor,
                              args=(None, decPassosRestantes))
        t2 = threading.Thread(target=self._mover_motor,
                              args=(None, raPassosRestantes))

        t1.start()
        t2.start()

        t1.join()
        t2.join()

        self.posicao = {"dec": dec, "ra": ra}

    def _mover_motor(self, motor, passos):
        sentido = passos > 0

        motor.motor_go(
            clockwise=sentido,
            steptype=configuracao.TIPO_PASSO,
            steps=passos,
            stepdelay=0.01,
            verbose=False,
            initdelay=0.5
        )

    def diferencaPosicaoParaAlvo(self, dec, ra):
        dec = (dec - self.posicao["dec"])/configuracao.RESOLUCAO_ATUADOR
        ra = (ra - self.posicao["ra"])/configuracao.RESOLUCAO_ATUADOR
        return dec, ra

    def __del__(self):
        GPIO.cleanup()
