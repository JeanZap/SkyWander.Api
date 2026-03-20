import threading
import time
from dataclasses import dataclass
from typing import Callable, Optional

import pygame


@dataclass(frozen=True)
class GamepadEvent:
    event_type: str
    timestamp_ms: float
    capture_enabled: bool
    left_x: Optional[float] = None
    left_y: Optional[float] = None


class GamepadButtonListener:
    def __init__(
        self,
        callback: Callable[[GamepadEvent], None],
        button_index: Optional[int] = 0,
        bouncetime_ms: int = 300,
        analog_deadzone: float = 0.12,
    ):
        self.callback = callback
        self.button_index = button_index
        self.bouncetime_ms = bouncetime_ms
        self.analog_deadzone = analog_deadzone
        self._running = False
        self._thread = None
        self._last_event_ts = 0.0
        self._joystick = None
        self._capture_enabled = False

    def start(self):
        if self._running:
            return

        pygame.init()
        pygame.joystick.init()

        if pygame.joystick.get_count() <= 0:
            print("Nenhum gamepad detectado para home via gamepad.")
            pygame.quit()
            return

        self._joystick = pygame.joystick.Joystick(0)
        self._joystick.init()
        self._running = True
        self._thread = threading.Thread(target=self._event_loop, daemon=True)
        self._thread.start()

        print(f"Gamepad conectado: {self._joystick.get_name()}")

    def _event_loop(self):
        while self._running:
            for event in pygame.event.get():
                if event.type == pygame.JOYBUTTONDOWN:
                    if self.button_index is not None and event.button != self.button_index:
                        continue

                    now = time.monotonic() * 1000
                    if now - self._last_event_ts < self.bouncetime_ms:
                        continue

                    self._last_event_ts = now
                    self._capture_enabled = not self._capture_enabled
                    self.callback(
                        GamepadEvent(
                            event_type="toggle_capture",
                            timestamp_ms=now,
                            capture_enabled=self._capture_enabled,
                        )
                    )
                    continue

                if event.type == pygame.JOYAXISMOTION and self._capture_enabled:
                    if event.axis not in (0, 1):
                        continue

                    left_x = self._joystick.get_axis(0)
                    left_y = self._joystick.get_axis(1)
                    if abs(left_x) < self.analog_deadzone and abs(left_y) < self.analog_deadzone:
                        continue

                    self.callback(
                        GamepadEvent(
                            event_type="left_analog_motion",
                            timestamp_ms=time.monotonic() * 1000,
                            capture_enabled=self._capture_enabled,
                            left_x=left_x,
                            left_y=left_y,
                        )
                    )

            time.sleep(0.01)

    def stop(self):
        if not self._running:
            return

        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)

        if self._joystick:
            self._joystick.quit()

        pygame.joystick.quit()
        pygame.quit()
