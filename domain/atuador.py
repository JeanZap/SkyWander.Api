import RPi.GPIO as GPIO
from RpiMotorLib import RpiMotorLib
from RpiMotorLib.RpiMotorLib import A4988Nema
import shared.aritmetica as aritmetica
import shared.configuracao as conf


class Atuador:
    _motor: A4988Nema = None

    def __init__(
        self,
        dir_pin: int,
        step_pin: int,
        limit_switch_pin: int,
        nome: str,
        offset: float,
    ):
        GPIO.setmode(GPIO.BCM)

        GPIO.setup(limit_switch_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        self._motor = RpiMotorLib.A4988Nema(
            dir_pin, step_pin, (False, False, False), "A4988"
        )
        self.limit_switch_pin = limit_switch_pin
        self.offset = offset
        self.nome = nome

    def _read_limit_switch(self):
        read = GPIO.input(self.limit_switch_pin)
        print(read)
        return read

    def homing_motor(self):
        print(f"1 - Recuando {self.nome}...", self._read_limit_switch(), GPIO.LOW)
        while self._read_limit_switch() == GPIO.LOW:
            self._motor.motor_go(True, conf.TIPO_PASSO, 1000, conf.STEP_DELAY, False, 0.0)

        # print(f"2 - Avancando {self.nome}...", self._read_limit_switch())
        # while self._read_limit_switch() == GPIO.HIGH:
        #     self._motor.motor_go(False, conf.TIPO_PASSO, 1000, conf.STEP_DELAY, False, 0.0)

        # print(f"3 - Aplicando offset {self.nome}...", self._read_limit_switch())
        # self._motor.motor_go(
        #     False,
        #     conf.TIPO_PASSO,
        #     aritmetica.converter_angulo_para_passos(self.offset),
        #     conf.STEP_DELAY,
        #     False,
        #     0.0,
        # )

        print(f"{self.nome} homing completo.")

    def mover_motor(self, passos: int):
        sentido = passos < 0

        self._motor.motor_go(
            clockwise=sentido,
            steptype=conf.TIPO_PASSO,
            steps=abs(passos),
            stepdelay=conf.STEP_DELAY,
            verbose=False,
            initdelay=conf.INIT_STEP_DELAY,
        )

    def __del__(self):
        GPIO.cleanup()
