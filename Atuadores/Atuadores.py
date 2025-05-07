import RPi.GPIO as GPIO
from RpiMotorLib import RpiMotorLib
import Aritmetica.Aritmetica as aritmetica
import Configuracao.Configuracao as configuracao
import threading
import datetime
import time


class Atuadores:
    posicao = {"dec": 0, "ra": 0, "decPassos": 0, "raPassos": 0}
    tracking_ativo = False
    taxa_sideral = 0.004178
    ultimo_tempo_tracking = None

    def __init__(self):
        GPIO.setmode(GPIO.BCM)

        self.motorDec = RpiMotorLib.A4988Nema(
            configuracao.DIR_PIN_DEC, configuracao.STEP_PIN_DEC, (True, True, True), "A4988")
        self.motorRa = RpiMotorLib.A4988Nema(
            configuracao.DIR_PIN_RA, configuracao.STEP_PIN_RA, (True, True, True), "A4988")
        self._homing()
        pass

    def _homing(self):
        # todo: Executar homing
        pass

    def apontar(self, decAlvo, raAlvo):
        self._parar_tracking()

        decAlvoPassos = aritmetica.converter_angulo_para_passos(decAlvo)
        raAlvoPassos = aritmetica.converter_angulo_para_passos(raAlvo)

        decPassosRestantes, raPassosRestantes = self.diferencaPosicaoParaAlvo(
            decAlvoPassos, raAlvoPassos)

        t1 = threading.Thread(target=self._mover_motor,
                              args=(self.motorDec, decPassosRestantes))
        t2 = threading.Thread(target=self._mover_motor,
                              args=(self.motorRa, raPassosRestantes))

        t1.start()
        t2.start()

        t1.join()
        t2.join()

        print(decAlvoPassos, raAlvoPassos, decAlvo, raAlvo)
        print(
            f"Declination: {decAlvoPassos}, Right ascension: {raAlvoPassos} {datetime.datetime.now()}", decAlvo, raAlvo)
        if self.posicao["decPassos"] != decAlvoPassos or self.posicao["raPassos"] != raAlvoPassos:
            self.posicao = {"dec": decAlvo, "ra": raAlvo,
                            "decPassos": decAlvoPassos, "raPassos": raAlvoPassos}
        print("ASDF")
        self.iniciar_tracking()

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
        dec = aritmetica.converter_angulo_para_passos(
            dec) - aritmetica.converter_angulo_para_passos(self.posicao["dec"])
        ra = aritmetica.converter_angulo_para_passos(
            ra) - aritmetica.converter_angulo_para_passos(self.posicao["ra"])
        return dec, ra

    def iniciar_tracking(self):
        self.tracking_ativo = True
        self.ultimo_tempo_tracking = time.time()
        threading.Thread(target=self._tracking_loop, daemon=True).start()

    def _parar_tracking(self):
        self.tracking_ativo = False

    def _tracking_loop(self):
        while self.tracking_ativo:
            agora = time.time()
            tempo_decorrido = agora - self.ultimo_tempo_tracking
            self.ultimo_tempo_tracking = agora

            movimento_ra = self.taxa_sideral * tempo_decorrido

            passos_ra = aritmetica.converter_angulo_para_passos(movimento_ra)

            print(passos_ra)
            if passos_ra != 0:
                self._mover_motor(self.motorRa, passos_ra)
                self.posicao["ra"] += movimento_ra
                self.posicao["raPassos"] += passos_ra

            time.sleep(0.1)

    def __del__(self):
        GPIO.cleanup()
