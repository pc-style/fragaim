"""
    Unibot, an open-source colorbot.
    Copyright (C) 2025 vike256

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import win32api
from typing import Tuple, Optional
import numpy as np


class Cheats:
    def __init__(self, config):
        # Aim
        self.move_x, self.move_y = (0, 0)
        self.previous_x, self.previous_y = (0, 0)
        self.smooth = config.smooth
        self.speed = config.speed
        self.y_speed = config.y_speed
        self.smoothing_type = config.smoothing_type
        self.ease_factor = config.ease_factor
        self.movement_randomness = config.movement_randomness
        self.fov_x = config.fov_x
        self.deadzone = config.deadzone
        self.min_ease_speed = config.min_ease_speed

        # Recoil
        self.recoil_offset = 0
        self.recoil_mode = config.recoil_mode
        self.recoil_x = config.recoil_x
        self.recoil_y = config.recoil_y
        self.max_offset = config.max_offset
        self.recoil_recover = config.recoil_recover

    def calculate_aim(self, state: bool, target: Optional[Tuple[int, int]]):
        if state and target is not None:
            x, y = target

            dist = np.sqrt(x**2 + y**2)

            # Apply deadzone
            if self.deadzone > 0 and dist <= self.deadzone:
                self.previous_x, self.previous_y = (0, 0)
                self.move_x, self.move_y = (0, 0)
                return

            effective_speed = self.speed
            if self.smoothing_type == 'ease_in_out':
                # Normalize distance based on FOV
                max_dist = self.fov_x / 2
                if max_dist > 0:
                    norm_dist = min(dist / max_dist, 1.0)

                    # Apply ease_factor to create a curve.
                    speed_factor = pow(norm_dist, self.ease_factor)

                    # Clamp speed factor to min_ease_speed
                    speed_factor = self.min_ease_speed + (1.0 - self.min_ease_speed) * speed_factor
                    effective_speed *= speed_factor

            # Calculate x and y speed
            x *= effective_speed
            y *= effective_speed * self.y_speed

            # Apply smoothing with the previous x and y value
            x = (1 - self.smooth) * self.previous_x + self.smooth * x
            y = (1 - self.smooth) * self.previous_y + self.smooth * y

            # Add randomness
            if self.movement_randomness > 0:
                x += np.random.uniform(-1, 1) * self.movement_randomness
                y += np.random.uniform(-1, 1) * self.movement_randomness

            # Store the calculated values for next calculation
            self.previous_x, self.previous_y = (x, y)
            # Apply x and y to the move variables
            self.move_x, self.move_y = (x, y)

    def apply_recoil(self, state: bool, delta_time: float):
        if state and delta_time != 0:
            # Mode move just applies configured movement to the move values
            if self.recoil_mode == 'move' and win32api.GetAsyncKeyState(0x01) < 0:
                self.move_x += self.recoil_x * delta_time
                self.move_y += self.recoil_y * delta_time
            # Mode offset moves the camera upward, so it aims below target
            elif self.recoil_mode == 'offset':
                # Add recoil_y to the offset when mouse1 is down
                if win32api.GetAsyncKeyState(0x01) < 0:
                    if self.recoil_offset < self.max_offset:
                        self.recoil_offset += self.recoil_y * delta_time
                        if self.recoil_offset > self.max_offset:
                            self.recoil_offset = self.max_offset
                # Start resetting the offset bit by bit if mouse1 is not down
                else:
                    if self.recoil_offset > 0:
                        self.recoil_offset -= self.recoil_recover * delta_time
                        if self.recoil_offset < 0:
                            self.recoil_offset = 0
        else:
            # Reset recoil offset if recoil is off
            self.recoil_offset = 0 