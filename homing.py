from RpiMotorLib import RpiMotorLib
from RpiMotorLib.RpiMotorLib import A4988Nema
import shared.configuracao as conf


motorDec = RpiMotorLib.A4988Nema(
    conf.DIR_PIN_DEC, conf.STEP_PIN_DEC, (True, True, True), "A4988"
)
motorRa = RpiMotorLib.A4988Nema(
    conf.DIR_PIN_RA, conf.STEP_PIN_RA, (True, True, True), "A4988"
)

while True:
    print("Rotating 1 revolution clockwise")
    motorDec.motor_go(
        clockwise=True,
        steptype=conf.TIPO_PASSO,
        steps=1800,
        stepdelay=0.001,
        verbose=False,
        initdelay=0.5,
    )
    motorRa.motor_go(
        clockwise=True,
        steptype=conf.TIPO_PASSO,
        steps=1800,
        stepdelay=0.001,
        verbose=False,
        initdelay=0.5,
    )
