import socket
import struct
import json
import numpy as np
import shared.aritmetica as aritmetica
from domain.montagem import Montagem
import time

atuadores = Montagem()

try:
    print("Stepper motor test - Press CTRL+C to exit")
    
    while True:
        # Rotate clockwise
        print("Rotating 1 revolution clockwise")
        atuadores.apontar(-90, 40)
        
        # Rotate counter-clockwise
        print("Rotating 1 revolution counter-clockwise")
        atuadores.apontar(90, 140)

except KeyboardInterrupt:
    print("Test stopped by user")
finally:
    GPIO.cleanup()  # Clean up GPIO

try:
    print("Stepper motor test - Press CTRL+C to exit")
    
    while True:
        # Rotate clockwise
        print("Rotating 1 revolution clockwise")
        atuadores.apontar(-90, 80)
        time.sleep(5)
        
        # Rotate counter-clockwise
        print("Rotating 1 revolution counter-clockwise")
        atuadores.apontar(90, 100)
        time.sleep(5)

except KeyboardInterrupt:
    print("Test stopped by user")
finally:
    GPIO.cleanup()  # Clean up GPIO