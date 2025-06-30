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
from configparser import ConfigParser
import numpy as np
import os
from typing import List, Union


class ConfigReader:
    def __init__(self):
        self.parser = ConfigParser()

        # Communication
        self.com_type = None
        self.ip = None
        self.port = None
        self.com_port = None

        # Screen
        self.detection_threshold = None
        self.upper_color = None
        self.lower_color = None
        self.fov_x = None
        self.fov_y = None
        self.aim_fov_x = None
        self.aim_fov_y = None
        self.fps = None
        self.auto_detect_resolution = None
        self.resolution_x = None
        self.resolution_y = None

        # Aim
        self.offset = None
        self.smooth = None
        self.speed = None
        self.y_speed = None
        self.aim_height = None
        self.smoothing_type = None
        self.ease_factor = None
        self.movement_randomness = None
        self.deadzone = None
        self.min_ease_speed = None

        # Recoil
        self.recoil_mode = None
        self.recoil_x = None
        self.recoil_y = None
        self.max_offset = None
        self.recoil_recover = None

        # Trigger
        self.trigger_delay = None
        self.trigger_randomization = None
        self.trigger_threshold = None

        # Rapid fire
        self.target_cps = None

        # Key binds
        self.key_reload_config = None
        self.key_toggle_aim = None
        self.key_toggle_recoil = None
        self.key_exit = None
        self.key_trigger = None
        self.key_rapid_fire = None
        self.aim_keys: List[Union[int, str]] = []

        # Debug
        self.debug = None
        self.debug_always_on = None
        self.display_mode = None
        
        # Clustering and filtering
        self.min_contour_area = None
        self.density_threshold = None
        self.enable_clustering = None
        self.cluster_distance = None
        self.min_cluster_size = None
        self.max_cluster_size = None

        # Get config path and read it
        self.path = os.path.join(os.path.dirname(__file__), '../config.ini')
        self.parser.read(self.path)

    def read_config(self):
        # Get communication settings
        value = self.parser.get('communication', 'type').lower()
        com_type_list = ['none', 'driver', 'serial', 'socket']
        if value in com_type_list:
            self.com_type = value
        else:
            print('WARNING: Invalid com_type value')
        
        match self.com_type:
            case 'socket':
                self.ip = self.parser.get('communication', 'ip')
                self.port = int(self.parser.get('communication', 'port'))
            case 'serial':
                self.com_port = self.parser.get('communication', 'com_port')

        # Get screen settings
        values_str = self.parser.get('screen', 'detection_threshold').split(',')
        self.detection_threshold = (int(values_str[0].strip()), int(values_str[1].strip()))

        upper_color_str = self.parser.get('screen', 'upper_color').split(',')
        lower_color_str = self.parser.get('screen', 'lower_color').split(',')
        upper_color = [int(val.strip()) for val in upper_color_str]
        lower_color = [int(val.strip()) for val in lower_color_str]
        self.upper_color = np.array(upper_color)
        self.lower_color = np.array(lower_color)

        self.fov_x = int(self.parser.get('screen', 'fov_x'))
        self.fov_y = int(self.parser.get('screen', 'fov_y'))
        self.aim_fov_x = int(self.parser.get('screen', 'aim_fov_x'))
        self.aim_fov_y = int(self.parser.get('screen', 'aim_fov_y'))
        self.fps = int(self.parser.get('screen', 'fps'))

        value = self.parser.get('screen', 'auto_detect_resolution').lower()
        if value == 'true':
            self.auto_detect_resolution = True
        else:
            self.auto_detect_resolution = False

        self.resolution_x = int(self.parser.get('screen', 'resolution_x'))
        self.resolution_y = int(self.parser.get('screen', 'resolution_y'))

        # Get aim settings
        self.offset = int(self.parser.get('aim', 'offset'))

        value = float(self.parser.get('aim', 'smooth'))
        if 0 <= value <= 1:
            self.smooth = 1 - value / 1.25
        else:
            print('WARNING: Invalid smooth value')

        self.speed = float(self.parser.get('aim', 'speed'))
        self.y_speed = float(self.parser.get('aim', 'y_speed'))

        value = float(self.parser.get('aim', 'aim_height'))
        if 0 <= value <= 1:
            self.aim_height = value
        else:
            print('WARNING: Invalid aim_height value')

        self.smoothing_type = self.parser.get('aim', 'smoothing_type', fallback='linear').lower()
        self.ease_factor = float(self.parser.get('aim', 'ease_factor', fallback='2.0'))
        self.movement_randomness = float(self.parser.get('aim', 'movement_randomness', fallback='0.0'))
        self.deadzone = int(self.parser.get('aim', 'deadzone', fallback='0'))
        self.min_ease_speed = float(self.parser.get('aim', 'min_ease_speed', fallback='0.0'))

        # Get recoil settings
        value = self.parser.get('recoil', 'mode').lower()
        recoil_mode_list = ['move', 'offset']
        if value in recoil_mode_list:
            self.recoil_mode = value
        else:
            print('WARNING: Invalid recoil_mode value')

        self.recoil_x = float(self.parser.get('recoil', 'recoil_x'))
        self.recoil_y = float(self.parser.get('recoil', 'recoil_y'))
        self.max_offset = int(self.parser.get('recoil', 'max_offset'))
        self.recoil_recover = float(self.parser.get('recoil', 'recover'))

        # Get trigger settings
        self.trigger_delay = int(self.parser.get('trigger', 'trigger_delay'))
        self.trigger_randomization = int(self.parser.get('trigger', 'trigger_randomization'))
        self.trigger_threshold = int(self.parser.get('trigger', 'trigger_threshold'))

        # Get rapid fire settings
        self.target_cps = int(self.parser.get('rapid_fire', 'target_cps'))

        # Get keybind settings
        self.key_reload_config = read_hex(self.parser.get('key_binds', 'key_reload_config'))
        self.key_toggle_aim = read_hex(self.parser.get('key_binds', 'key_toggle_aim'))
        self.key_toggle_recoil = read_hex(self.parser.get('key_binds', 'key_toggle_recoil'))
        self.key_exit = read_hex(self.parser.get('key_binds', 'key_exit'))
        self.key_trigger = read_hex(self.parser.get('key_binds', 'key_trigger'))
        self.key_rapid_fire = read_hex(self.parser.get('key_binds', 'key_rapid_fire'))
        aim_keys_str = self.parser.get('key_binds', 'aim_keys')
        if not aim_keys_str == 'off':
            aim_keys_str = aim_keys_str.split(',')
            for key in aim_keys_str:
                self.aim_keys.append(read_hex(key))
        else:
            self.aim_keys = ['off']

        # Get debug settings
        value = self.parser.get('debug', 'enabled').lower()
        if value == 'true':
            self.debug = True
        else:
            self.debug = False

        value = self.parser.get('debug', 'always_on').lower()
        if value == 'true':
            self.debug_always_on = True
        else:
            self.debug_always_on = False

        value = self.parser.get('debug', 'display_mode').lower()
        display_mode_list = ['game', 'mask']
        if value in display_mode_list:
            self.display_mode = value
        else:
            print('WARNING: Invalid display_mode value')

        # Get clustering and filtering settings
        self.min_contour_area = int(self.parser.get('screen', 'min_contour_area', fallback='10'))
        self.density_threshold = float(self.parser.get('screen', 'density_threshold', fallback='0.3'))
        value = self.parser.get('screen', 'enable_clustering', fallback='true').lower()
        self.enable_clustering = value == 'true'
        self.cluster_distance = int(self.parser.get('screen', 'cluster_distance', fallback='50'))
        self.min_cluster_size = int(self.parser.get('screen', 'min_cluster_size', fallback='20'))
        self.max_cluster_size = int(self.parser.get('screen', 'max_cluster_size', fallback='2000'))


def read_hex(string):
    return int(string, 16) 