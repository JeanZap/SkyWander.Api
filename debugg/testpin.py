import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

PIN = 4  # GPIO que será lido

# Se não tiver resistor externo, use pull-up ou pull-down
GPIO.setup(PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

try:
    while True:
        estado = GPIO.input(PIN)
        print("PIN HIGH" if estado else "PIN LOW")
        time.sleep(0.2)  # intervalo de leitura

except KeyboardInterrupt:
    print("\nEncerrando leitura...")

finally:
    GPIO.cleanup()
