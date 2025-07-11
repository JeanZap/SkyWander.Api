from RpiMotorLib import RpiMotorLib
import shared.configuracao as conf


motorRa = RpiMotorLib.A4988Nema(
    conf.DIR_PIN_RA, conf.STEP_PIN_RA, (True, True, True), "A4988"
)

motorRa.motor_go(
    clockwise=False,
    steptype=conf.TIPO_PASSO,
    steps=18000,
    stepdelay=0.001,
    verbose=False,
    initdelay=0.5,
)

motorRa.motor_go(
    clockwise=True,
    steptype=conf.TIPO_PASSO,
    steps=18000,
    stepdelay=0.001,
    verbose=False,
    initdelay=0.5,
)
