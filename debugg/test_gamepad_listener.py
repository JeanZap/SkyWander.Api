import os
import sys
import time


ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import shared.configuracao as conf
from domain.gamepad_listener_pygamepad import GamepadButtonListener, GamepadEvent


def _test_gamepad(evento: GamepadEvent):
    if evento.event_type == "toggle_capture":
        estado = "ATIVA" if evento.capture_enabled else "INATIVA"
        print(f"[TOGGLE] Captura {estado} | t={evento.timestamp_ms:.0f}ms")
        return

    if evento.event_type == "left_analog_motion":
        print(
            f"[LEFT_ANALOG] x={evento.left_x:+.3f} y={evento.left_y:+.3f}"
            f" | t={evento.timestamp_ms:.0f}ms"
        )


def main():
    print("Teste do GamepadButtonListener")
    print(f"GAMEPAD_HOME_BUTTON={conf.GAMEPAD_HOME_BUTTON}")
    print(f"GAMEPAD_BOUNCETIME_MS={conf.GAMEPAD_BOUNCETIME_MS}")
    print("")
    print("Instrucoes:")
    print("1. Pressione GAMEPAD_HOME_BUTTON para iniciar captura do analogico esquerdo.")
    print("2. Mova o analogico esquerdo para receber eventos.")
    print("3. Pressione GAMEPAD_HOME_BUTTON novamente para parar captura.")
    print("4. Ctrl+C para encerrar.")

    listener = GamepadButtonListener(
        callback=_test_gamepad,
        button_index=conf.GAMEPAD_HOME_BUTTON,
        bouncetime_ms=conf.GAMEPAD_BOUNCETIME_MS,
    )
    listener.start()
    controller = getattr(listener, "_controller", None)
    if controller is not None:
        try:
            buttons = list(controller.state.buttons.keys())
            print("")
            print("Mapeamento atual de botoes (indice -> nome):")
            for idx, name in enumerate(buttons):
                print(f"{idx}: {name}")
        except Exception:
            pass

    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nEncerrando teste...")
    finally:
        listener.stop()


if __name__ == "__main__":
    main()
