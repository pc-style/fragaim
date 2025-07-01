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
import time
import numpy as np

from cheats import Cheats
from mouse import Mouse
from screen import Screen
from utils import Utils
from user_input import UserInputListener


def main():
    # Print licensing info
    print('''
Unibot  Copyright (C) 2025  vike256
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it under certain conditions.
For details see <LICENSE.txt>.

Reimplemented with Windows Capture API for improved performance.
    ''')

    # Program loop
    while True:
        # Track delta time
        start_time = time.time()

        try:
            user_input_listener = UserInputListener()
            utils = Utils()
            config = utils.config
            cheats = Cheats(config)
            mouse = Mouse(config, user_input_listener)
            screen = Screen(config)

            target_frame_time = 1.0 / config.fps if config.fps else 0.016
            print(f'Unibot ON (Windows Capture) - Target FPS: {config.fps} (Frame time: {target_frame_time*1000:.2f}ms)')

            # Loop FPS tracking
            loop_times = []
            last_loop_fps_update = time.time()
            current_loop_fps = 0.0

            # Cheat loop
            while True:
                loop_start = time.time()
                delta_time = loop_start - start_time
                start_time = loop_start
                
                # Track loop FPS
                loop_times.append(loop_start)
                if len(loop_times) > 30:
                    loop_times.pop(0)
                
                # Update loop FPS every 0.5 seconds
                if loop_start - last_loop_fps_update > 0.5 and len(loop_times) > 1:
                    time_span = loop_times[-1] - loop_times[0]
                    if time_span > 0:
                        current_loop_fps = (len(loop_times) - 1) / time_span
                    last_loop_fps_update = loop_start
                
                reload_config = utils.check_key_binds()
                if reload_config:
                    print("Config reload requested. Disconnecting from serial...")
                    # Close the current connection
                    mouse.close_connection()
                    print("Waiting 3 seconds for Pico to process disconnection...")
                    for i in range(3, 0, -1):
                        print(f"Reconnecting in {i}...")
                        time.sleep(1)
                    print("Reconnecting now...")
                    utils.reload_config()
                    break

                # Always update screen with current loop FPS for debug display (even when not actively aiming)
                screen.current_loop_fps = current_loop_fps
                
                if (utils.get_aim_state() or utils.get_trigger_state()) or (config.debug and config.debug_always_on):
                    # Get target position and check if there is a target in the center of the screen
                    target, trigger = screen.get_target(cheats.recoil_offset)

                    # Shoot if target in the center of the screen
                    if utils.get_trigger_state() and trigger:
                        if (config.trigger_delay and config.trigger_delay != 0 and 
                            config.trigger_randomization is not None):
                            delay_before_click = (np.random.randint(config.trigger_randomization) + config.trigger_delay) / 1000
                        else:
                            delay_before_click = 0.0
                        mouse.click(delay_before_click)

                    # Calculate movement based on target position
                    cheats.calculate_aim(utils.get_aim_state(), target)

                if utils.get_rapid_fire_state():
                    mouse.click()

                # Apply recoil
                cheats.apply_recoil(utils.recoil_state, delta_time)

                # Move the mouse based on the previous calculations
                mouse.move(cheats.move_x, cheats.move_y)

                # Reset move values so the aim doesn't keep drifting when no targets are on the screen
                cheats.move_x, cheats.move_y = (0, 0)

                # Do not loop above the set refresh rate
                if config.fps and config.fps > 0 and config.fps <= 200:  # Only limit if reasonable FPS
                    target_frame_time = 1.0 / config.fps  # Convert FPS to seconds per frame
                    time_spent = time.time() - start_time
                    if time_spent < target_frame_time:
                        # Use more precise sleep for high FPS
                        sleep_time = target_frame_time - time_spent
                        if sleep_time > 0.001:  # Only sleep if > 1ms
                            time.sleep(sleep_time)

        except Exception as e:
            print(f'Error: {e}')
            print('Retrying in 5 seconds...')
            time.sleep(5)
            continue

        print('Reloading')


if __name__ == "__main__":
    main() 