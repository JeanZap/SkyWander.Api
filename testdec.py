import RPi.GPIO as GPIO
import time
from RpiMotorLib import RpiMotorLib
from RpiMotorLib.RpiMotorLib import A4988Nema
import shared.configuracao as conf


motorDec = RpiMotorLib.A4988Nema(conf.DIR_PIN_DEC, conf.STEP_PIN_DEC, (True, True, True), "A4988")

while True:
    motorDec.motor_go(
            clockwise=True,
            steptype=conf.TIPO_PASSO,
            steps=18000,
            stepdelay=0.001,
            verbose=False,
            initdelay=0.5
        )
