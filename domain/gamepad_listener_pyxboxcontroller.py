import threading
import time
from dataclasses import dataclass
from typing import Callable, Optional


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
        self._controller = None
        self._button_keys = None
        self._capture_enabled = False
        self._prev_toggle_pressed = False
        self._last_left_x = 0.0
        self._last_left_y = 0.0

    def start(self):
        if self._running:
            return

        try:
            from pyxboxcontroller import XboxController
        except Exception as e:
            print(f"pyxboxcontroller nao disponivel: {e}")
            return

        try:
            self._controller = XboxController(0)
            _ = self._controller.state
        except Exception as e:
            print(f"Nenhum gamepad Xbox detectado para home via gamepad: {e}")
            self._controller = None
            return

        self._running = True
        self._thread = threading.Thread(target=self._event_loop, daemon=True)
        self._thread.start()

        print("Gamepad Xbox conectado via pyxboxcontroller.")

    def _event_loop(self):
        while self._running:
            state = self._read_state()
            if state is None:
                time.sleep(0.05)
                continue

            now = time.monotonic() * 1000
            toggle_pressed = self._is_toggle_pressed(state)

            if toggle_pressed and not self._prev_toggle_pressed:
                if now - self._last_event_ts >= self.bouncetime_ms:
                    self._last_event_ts = now
                    self._capture_enabled = not self._capture_enabled
                    self.callback(
                        GamepadEvent(
                            event_type="toggle_capture",
                            timestamp_ms=now,
                            capture_enabled=self._capture_enabled,
                        )
                    )
            self._prev_toggle_pressed = toggle_pressed

            if self._capture_enabled:
                left_x = float(getattr(state, "l_thumb_x", 0.0))
                left_y = float(getattr(state, "l_thumb_y", 0.0))
                if (
                    abs(left_x) >= self.analog_deadzone
                    or abs(left_y) >= self.analog_deadzone
                ):
                    changed = (
                        abs(left_x - self._last_left_x) >= 0.02
                        or abs(left_y - self._last_left_y) >= 0.02
                    )
                    if changed:
                        self._last_left_x = left_x
                        self._last_left_y = left_y
                        self.callback(
                            GamepadEvent(
                                event_type="left_analog_motion",
                                timestamp_ms=now,
                                capture_enabled=self._capture_enabled,
                                left_x=left_x,
                                left_y=left_y,
                            )
                        )

            time.sleep(0.01)

    def _read_state(self):
        if self._controller is None:
            return None
        try:
            return self._controller.state
        except Exception:
            return None

    def _is_toggle_pressed(self, state) -> bool:
        buttons = getattr(state, "buttons", None)
        if not isinstance(buttons, dict):
            return False

        if self.button_index is None:
            return any(bool(v) for v in buttons.values())

        key = self._resolve_button_key(buttons)
        if key is None:
            return False
        return bool(buttons.get(key, False))

    def _resolve_button_key(self, buttons: dict) -> Optional[str]:
        if isinstance(self.button_index, int):
            if self._button_keys is None:
                self._button_keys = list(buttons.keys())
            if self.button_index < 0 or self.button_index >= len(self._button_keys):
                return None
            return self._button_keys[self.button_index]
        return None

    def stop(self):
        if not self._running:
            return

        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
