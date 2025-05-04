import RPi.GPIO as GPIO
from RpiMotorLib import RpiMotorLib
import Aritmetica.Aritmetica as aritmetica
import Configuracao.Configuracao as configuracao
import threading


class Atuadores:
    posicao = {"dec": 0, "ra": 0}

    def __init__(self):
        GPIO.setmode(GPIO.BCM)

        self.motorDec = RpiMotorLib.A4988Nema(
            configuracao.DIR_PIN_DEC, configuracao.STEP_PIN_DEC, (False, False, False), "A4988")
        self.motorRa = RpiMotorLib.A4988Nema(
            configuracao.DIR_PIN_RA, configuracao.STEP_PIN_RA, (False, False, False), "A4988")
        # Os 3 últimos valores são para MS1, MS2, MS3 - False assume controle físico no driver
        self._homing()

    def _homing(self):
        # todo: Executar homing
        pass

    def apontar(self, dec, ra):
        dec = aritmetica.converter_angulo_para_passos(dec)
        ra = aritmetica.converter_angulo_para_passos(ra)

        decRestante, raRestante = self.diferencaPosicaoParaAlvo(dec, ra)

        print(decRestante, raRestante)

        t1 = threading.Thread(target=self._mover_motor,
                              args=(self.motorDec, decRestante))
        t2 = threading.Thread(target=self._mover_motor,
                              args=(self.motorRa, raRestante))

        t1.start()
        t2.start()

        t1.join()
        t2.join()

        self.posicao = (dec, ra)

    def _mover_motor(self, motor, passos):
        sentido = passos > 0

        motor.motor_go(
            clockwise=sentido,
            steptype="Full",
            steps=passos,
            stepdelay=0.001,
            verbose=False,
            initdelay=0.05
        )

    def diferencaPosicaoParaAlvo(self, dec, ra):
        dec = dec-self.posicao['dec']
        ra = ra-self.posicao['ra']
        return dec, ra
