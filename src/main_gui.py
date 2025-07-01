"""
    Unibot GUI-Compatible Main Module
    Copyright (C) 2025 vike256

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
"""
import time
import numpy as np
import threading
import queue
from pathlib import Path

from cheats import Cheats
from mouse import Mouse
from screen import Screen
from utils import Utils
from user_input import UserInputListener

class UnibotCore:
    """Core bot functionality that can be controlled by GUI"""
    
    def __init__(self, config_path="../config.ini"):
        self.config_path = config_path
        self.running = False
        self.thread = None
        
        # Communication with GUI
        self.command_queue = queue.Queue()
        self.status_queue = queue.Queue()
        
        # Bot components
        self.user_input_listener = None
        self.utils = None
        self.config = None
        self.cheats = None
        self.mouse = None
        self.screen = None
        
        # Status information
        self.current_fps = 0
        self.target_frame_time = 0.016
        self.loop_times = []
        self.last_loop_fps_update = time.time()
    
    def start(self):
        """Start the bot in a separate thread"""
        if self.running:
            return False
        
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        return True
    
    def stop(self):
        """Stop the bot"""
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2.0)
    
    def send_command(self, command, value=None):
        """Send a command to the bot"""
        self.command_queue.put((command, value))
    
    def get_status(self):
        """Get current status from the bot"""
        status = {}
        try:
            while True:
                status.update(self.status_queue.get_nowait())
        except queue.Empty:
            pass
        return status
    
    def _update_status(self, key, value):
        """Update status information"""
        try:
            self.status_queue.put({key: value})
        except:
            pass
    
    def _process_commands(self):
        """Process commands from GUI"""
        try:
            while True:
                command, value = self.command_queue.get_nowait()
                
                if command == "reload_config":
                    self._reload_config()
                elif command == "update_config":
                    # Update configuration with new values
                    if isinstance(value, dict):
                        for section, settings in value.items():
                            if not self.config.has_section(section):
                                self.config.add_section(section)
                            for key, val in settings.items():
                                self.config.set(section, key, str(val))
                        # Reinitialize components with new config
                        self._reinitialize_components()
                
        except queue.Empty:
            pass
    
    def _reload_config(self):
        """Reload configuration from file"""
        try:
            if self.mouse:
                self.mouse.close_connection()
            
            # Wait for disconnection
            time.sleep(1)
            
            # Reload utils and config
            self.utils = Utils()
            self.config = self.utils.config
            
            # Reinitialize components
            self._reinitialize_components()
            
            self._update_status("message", "Configuration reloaded")
            
        except Exception as e:
            self._update_status("error", f"Failed to reload config: {e}")
    
    def _reinitialize_components(self):
        """Reinitialize bot components with current config"""
        try:
            self.cheats = Cheats(self.config)
            self.mouse = Mouse(self.config, self.user_input_listener)
            self.screen = Screen(self.config)
            
            self.target_frame_time = 1.0 / self.config.fps if self.config.fps else 0.016
            
        except Exception as e:
            self._update_status("error", f"Failed to reinitialize: {e}")
    
    def _run_loop(self):
        """Main bot loop"""
        try:
            # Initialize components
            self.user_input_listener = UserInputListener()
            self.utils = Utils()
            self.config = self.utils.config
            self.cheats = Cheats(self.config)
            self.mouse = Mouse(self.config, self.user_input_listener)
            self.screen = Screen(self.config)

            self.target_frame_time = 1.0 / self.config.fps if self.config.fps else 0.016
            
            self._update_status("message", f"Bot initialized - Target FPS: {self.config.fps}")
            self._update_status("status", "running")

            # Main loop
            start_time = time.time()
            
            while self.running:
                loop_start = time.time()
                delta_time = loop_start - start_time
                start_time = loop_start
                
                # Process GUI commands
                self._process_commands()
                
                # Track loop FPS
                self.loop_times.append(loop_start)
                if len(self.loop_times) > 30:
                    self.loop_times.pop(0)
                
                # Update loop FPS every 0.5 seconds
                if loop_start - self.last_loop_fps_update > 0.5 and len(self.loop_times) > 1:
                    time_span = self.loop_times[-1] - self.loop_times[0]
                    if time_span > 0:
                        self.current_fps = (len(self.loop_times) - 1) / time_span
                        self._update_status("fps", self.current_fps)
                    self.last_loop_fps_update = loop_start
                
                # Check for config reload request
                reload_config = self.utils.check_key_binds()
                if reload_config:
                    self._reload_config()
                    continue

                # Update screen with current loop FPS
                self.screen.current_loop_fps = self.current_fps
                
                # Bot logic
                if (self.utils.get_aim_state() or self.utils.get_trigger_state()) or (self.config.debug and self.config.debug_always_on):
                    # Get target position
                    target, trigger = self.screen.get_target(self.cheats.recoil_offset)

                    # Trigger bot
                    if self.utils.get_trigger_state() and trigger:
                        if (self.config.trigger_delay and self.config.trigger_delay != 0 and 
                            self.config.trigger_randomization is not None):
                            delay_before_click = (np.random.randint(self.config.trigger_randomization) + self.config.trigger_delay) / 1000
                        else:
                            delay_before_click = 0.0
                        self.mouse.click(delay_before_click)

                    # Calculate aim movement
                    self.cheats.calculate_aim(self.utils.get_aim_state(), target)

                # Rapid fire
                if self.utils.get_rapid_fire_state():
                    self.mouse.click()

                # Apply recoil
                self.cheats.apply_recoil(self.utils.recoil_state, delta_time)

                # Move mouse
                self.mouse.move(self.cheats.move_x, self.cheats.move_y)

                # Reset movement
                self.cheats.move_x, self.cheats.move_y = (0, 0)

                # Frame rate limiting
                if self.config.fps and self.config.fps > 0 and self.config.fps <= 200:
                    time_spent = time.time() - start_time
                    if time_spent < self.target_frame_time:
                        sleep_time = self.target_frame_time - time_spent
                        if sleep_time > 0.001:
                            time.sleep(sleep_time)

        except Exception as e:
            self._update_status("error", f"Bot error: {e}")
            self._update_status("status", "error")
        
        finally:
            # Cleanup
            if self.mouse:
                self.mouse.close_connection()
            self._update_status("status", "stopped")
            self._update_status("message", "Bot stopped")

def create_bot_instance(config_path="../config.ini"):
    """Create and return a bot instance"""
    return UnibotCore(config_path)

def main():
    """Main entry point for standalone operation"""
    print('''
Unibot  Copyright (C) 2025  vike256
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it under certain conditions.
For details see <LICENSE.txt>.

Reimplemented with Windows Capture API for improved performance.
    ''')

    bot = create_bot_instance()
    
    try:
        bot.start()
        
        print("Bot started. Press Ctrl+C to stop.")
        
        while bot.running:
            time.sleep(1)
            status = bot.get_status()
            if "fps" in status:
                print(f"\rFPS: {status['fps']:.1f}", end="", flush=True)
    
    except KeyboardInterrupt:
        print("\nStopping bot...")
        bot.stop()
        print("Bot stopped.")

if __name__ == "__main__":
    main()