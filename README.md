# Unibot-WinCapture

An open-source color-based aimbot for Windows using advanced smoothing algorithms and human-like mouse movement patterns.

## Features

- **Advanced Smoothing**: Multiple smoothing algorithms including linear and ease-in-out with configurable curves
- **Human-like Movement**: Deadzone support, movement randomness, and variable speed profiles
- **Multiple Communication Methods**: Serial, Socket, Driver, or Direct Windows API
- **Real-time Target Detection**: Color-based detection with clustering and filtering
- **Recoil Control**: Configurable recoil compensation with multiple modes
- **Trigger Bot**: Automatic shooting with configurable delays and randomization
- **Rapid Fire**: Configurable clicks per second
- **Hot Reload**: Reload configuration without restarting the application
- **Debug Mode**: Real-time visualization of detection and performance metrics

## Installation

### Prerequisites
- Python 3.8 or higher
- Windows 10/11
- Required Python packages (see requirements.txt)

### Setup
1. Clone or download the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure your settings in `config.ini`
4. Run the application:
   ```bash
   python src/main.py
   ```

## Configuration

### Communication Settings
```ini
[communication]
type = serial          # Options: serial, socket, driver, none
ip = 0.0.0.0          # For socket communication
port = 50124          # For socket communication
com_port = COM10      # For serial communication
```

### Screen Detection
```ini
[screen]
detection_threshold = 3, 3
upper_color = 154, 165, 175    # Target color range (BGR)
lower_color = 141, 88, 58
fov_x = 500                    # Field of view width
fov_y = 500                    # Field of view height
fps = 120                      # Target frame rate
```

### Aim Settings
```ini
[aim]
offset = 0                     # Aim offset
smooth = 0.9                   # Smoothing factor (0-1)
speed = 0.5                    # Base movement speed
y_speed = 0.2                  # Vertical speed multiplier
aim_height = 0.7               # Aim height (0-1)
smoothing_type = ease_in_out   # linear or ease_in_out
ease_factor = 2.0              # Curve intensity for ease_in_out
min_ease_speed = 0.2           # Minimum speed for ease_in_out
movement_randomness = 0.1      # Random movement variation
deadzone = 10                  # Pixels radius where no movement occurs
```

### Recoil Control
```ini
[recoil]
mode = offset                  # move or offset
recoil_x = 0.0                 # Horizontal recoil
recoil_y = 0.7                 # Vertical recoil
max_offset = 600               # Maximum recoil offset
recover = 0.3                  # Recoil recovery speed
```

### Key Bindings
```ini
[key_binds]
key_reload_config = 0x70       # F1 - Reload configuration
key_toggle_aim = 0x2E          # Delete - Toggle aim
key_toggle_recoil = 0x24       # Home - Toggle recoil
key_exit = 0x73                # F4 - Exit program
key_trigger = 0x05             # Mouse5 - Trigger bot
key_rapid_fire = 0x06          # Mouse6 - Rapid fire
aim_keys = 0x01                # Mouse1 - Aim activation
```

## Usage

### Basic Operation
1. Start the application
2. Press the aim key (default: Mouse1) to activate aim assistance
3. The bot will automatically detect targets within the configured FOV
4. Use trigger bot (Mouse5) for automatic shooting
5. Toggle recoil control with Home key

### Advanced Features
- **Config Reload**: Press F1 to reload configuration (3-second delay for serial connections)
- **Debug Mode**: Enable in config to see detection visualization
- **Smoothing Types**:
  - `linear`: Traditional exponential smoothing
  - `ease_in_out`: Human-like curved movement with configurable intensity

### Smoothing Configuration
- **ease_factor**: Higher values create more pronounced curves (1.0-5.0 recommended)
- **min_ease_speed**: Prevents movement from becoming too slow (0.0-1.0)
- **deadzone**: Stops jitter by ignoring small movements near target
- **movement_randomness**: Adds subtle human-like variation

## Troubleshooting

### Common Issues
1. **No targets detected**: Check color values and detection threshold
2. **Movement too fast/slow**: Adjust `speed` and smoothing settings
3. **Serial connection fails**: Verify COM port and wait 3 seconds after config reload
4. **High CPU usage**: Reduce FPS or disable debug mode

### Performance Tips
- Use appropriate FOV size for your needs
- Disable debug mode for better performance
- Adjust detection threshold based on your target colors
- Use deadzone to prevent unnecessary micro-movements

## License

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

## Disclaimer

This software is provided for educational and research purposes only. Users are responsible for complying with all applicable laws and regulations in their jurisdiction. The authors are not responsible for any misuse of this software.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## Credits

- **Original Author**: vike256
- **Reimplementation**: Windows Capture API for improved performance
- **Enhanced Smoothing**: Advanced human-like movement algorithms
