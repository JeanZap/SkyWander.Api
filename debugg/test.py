from RpiMotorLib import RpiMotorLib
from RpiMotorLib.RpiMotorLib import A4988Nema
import shared.configuracao as conf
import threading


motorDec = RpiMotorLib.A4988Nema(
    conf.DIR_PIN_DEC, conf.STEP_PIN_DEC, (True, True, True), "A4988"
)
motorRa = RpiMotorLib.A4988Nema(
    conf.DIR_PIN_RA, conf.STEP_PIN_RA, (True, True, True), "A4988"
)


def _mover_motor(motor: A4988Nema, passos: int):
    sentido = passos > 0

    motor.motor_go(
        clockwise=sentido,
        steptype=conf.TIPO_PASSO,
        steps=abs(passos),
        stepdelay=conf.STEP_DELAY,
        verbose=False,
        initdelay=conf.INIT_STEP_DELAY,
    )


while True:
    t1 = threading.Thread(target=_mover_motor, args=(motorDec, 18000))
    t2 = threading.Thread(target=_mover_motor, args=(motorRa, 18000))

    t1.start()
    t2.start()

    t1.join()
    t2.join()
