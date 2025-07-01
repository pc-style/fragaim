import threading
from pynput import mouse

class UserInputListener:
    def __init__(self):
        self.user_dx = 0
        self.user_dy = 0
        self.lock = threading.Lock()
        self.last_x = None
        self.last_y = None

        # Start listening in a background thread
        self.listener_thread = threading.Thread(target=self._run_listener, daemon=True)
        self.listener_thread.start()
        print("User input listener started.")

    def _on_move(self, x, y):
        with self.lock:
            if self.last_x is not None and self.last_y is not None:
                self.user_dx += x - self.last_x
                self.user_dy += y - self.last_y
            self.last_x = x
            self.last_y = y

    def _run_listener(self):
        with mouse.Listener(on_move=self._on_move) as listener:
            try:
                listener.join()
            except Exception as e:
                print(f"Exception in mouse listener: {e}")

    def get_and_reset_movement(self):
        with self.lock:
            dx = self.user_dx
            dy = self.user_dy
            self.user_dx = 0
            self.user_dy = 0
            return dx, dy 