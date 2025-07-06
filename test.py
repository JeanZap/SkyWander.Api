import RPi.GPIO as GPIO
import time
from RpiMotorLib import RpiMotorLib
from RpiMotorLib.RpiMotorLib import A4988Nema
import shared.configuracao as conf


motorDec = RpiMotorLib.A4988Nema(conf.DIR_PIN_DEC, conf.STEP_PIN_DEC, (True, True, True), "A4988")
motorRa = RpiMotorLib.A4988Nema(conf.DIR_PIN_RA, conf.STEP_PIN_RA, (True, True, True), "A4988")

while True:
    print("Rotating 1 revolution clockwise")
    motorDec.motor_go(
            clockwise=True,
            steptype=conf.TIPO_PASSO,
            steps=1800,
            stepdelay=0.001,
            verbose=False,
            initdelay=0.5
        )
    motorRa.motor_go(
            clockwise=True,
            steptype=conf.TIPO_PASSO,
            steps=1800*16,
            stepdelay=0.001,
            verbose=False,
            initdelay=0.5
        )

    print("Rotating 1 revolution counter-clockwise")
    motorDec.motor_go(
            clockwise=False,
            steptype=conf.TIPO_PASSO,
            steps=1800,
            stepdelay=0.001,
            verbose=False,
            initdelay=0.5
        )
    motorRa.motor_go(
            clockwise=False,
            steptype=conf.TIPO_PASSO,
            steps=1800*16,
            stepdelay=0.001,
            verbose=False,
            initdelay=0.5
        )


# # Set up GPIO pins
# GPIO.setmode(GPIO.BCM)

# # Define motor pins (change these to match your wiring)
# STEP_PIN = 20       # Step pin (pulse to move)
# DIR_PIN = 21        # Direction pin
# ENABLE_PIN = 22     # Enable pin (optional, can be held low)

# # Set up pins as outputs
# GPIO.setup(STEP_PIN, GPIO.OUT)
# GPIO.setup(DIR_PIN, GPIO.OUT)
# GPIO.setup(ENABLE_PIN, GPIO.OUT)

# # Motor settings
# STEPS_PER_REV = 200 * 16  # Change this to match your motor's steps per revolution
# DELAY = 0.001        # Time between steps in seconds (controls speed)


# def rotate_motor(steps, direction):
#     """Rotate the motor a given number of steps in specified direction"""
#     GPIO.output(DIR_PIN, direction)
#     GPIO.output(ENABLE_PIN, GPIO.LOW)  # Enable motor
    
#     for _ in range(steps):
#         GPIO.output(STEP_PIN, GPIO.HIGH)
#         time.sleep(DELAY)
#         GPIO.output(STEP_PIN, GPIO.LOW)
#         time.sleep(DELAY)
    
#     GPIO.output(ENABLE_PIN, GPIO.HIGH)  # Disable motor

# try:
#     print("Stepper motor test - Press CTRL+C to exit")
    
#     while True:
#         # Rotate clockwise
#         print("Rotating 1 revolution clockwise")
#         rotate_motor(STEPS_PER_REV, GPIO.HIGH)
#         time.sleep(1)
        
#         # Rotate counter-clockwise
#         print("Rotating 1 revolution counter-clockwise")
#         rotate_motor(STEPS_PER_REV, GPIO.LOW)
#         time.sleep(1)
        
#         # Rotate multiple steps faster
#         print("Rotating 400 steps faster")
#         rotate_motor(STEPS_PER_REV * 2, GPIO.HIGH)
#         time.sleep(2)

# except KeyboardInterrupt:
#     print("Test stopped by user")
# finally:
#     GPIO.cleanup()  # Clean up GPIO