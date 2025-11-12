import RPi.GPIO as GPIO
import time

# Defina o número do pino que deseja usar
PIN = 20  # você pode mudar para o pino desejado

# Configura o modo de numeração e o pino
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN, GPIO.OUT)

print(f"Pino {PIN} está em HIGH. Pressione Ctrl + C para encerrar.")

try:
    # Mantém o pino em HIGH até o programa ser interrompido
    GPIO.output(PIN, GPIO.HIGH)
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("\nEncerrando script...")

finally:
    # Limpa as configurações GPIO ao sair
    GPIO.cleanup()
    print("GPIO restaurado ao estado padrão.")
