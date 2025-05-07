# import RPi.GPIO as GPIO
# from RpiMotorLib import RpiMotorLib
import Aritmetica.Aritmetica as aritmetica
import Configuracao.Configuracao as configuracao
import threading
import datetime


class Atuadores:
    posicao = {"dec": 0, "ra": 0, "decPassos": 0, "raPassos": 0}

    def __init__(self):
        # GPIO.setmode(GPIO.BCM)

        # self.motorDec = RpiMotorLib.A4988Nema(
        #     configuracao.DIR_PIN_DEC, configuracao.STEP_PIN_DEC, (True, True, True), "A4988")
        # self.motorRa = RpiMotorLib.A4988Nema(
        #     configuracao.DIR_PIN_RA, configuracao.STEP_PIN_RA, (True, True, True), "A4988")
        # self._homing()
        pass

    def _homing(self):
        # todo: Executar homing
        pass

    def apontar(self, decAlvo, raAlvo):
        decAlvoPassos = aritmetica.converter_angulo_para_passos(decAlvo)
        raAlvoPassos = aritmetica.converter_angulo_para_passos(raAlvo)

        if self.posicao["decPassos"] != decAlvoPassos or self.posicao["raPassos"] != raAlvoPassos:
            print(
                f"Declination: {decAlvoPassos}, Right ascension: {raAlvoPassos} {datetime.datetime.now()}")

        decPassosRestantes, raPassosRestantes = self.diferencaPosicaoParaAlvo(
            decAlvoPassos, raAlvoPassos)

        # t1 = threading.Thread(target=self._mover_motor,
        #                       args=(None, decPassosRestantes))
        # t2 = threading.Thread(target=self._mover_motor,
        #                       args=(None, raPassosRestantes))

        # t1.start()
        # t2.start()

        # t1.join()
        # t2.join()

        if self.posicao["decPassos"] != decAlvoPassos or self.posicao["raPassos"] != raAlvoPassos:
            self.posicao = {"dec": decAlvo, "ra": raAlvo,
                            "decPassos": decAlvoPassos, "raPassos": raAlvoPassos}

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
