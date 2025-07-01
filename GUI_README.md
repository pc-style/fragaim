# Unibot GUI - Windows Interface

A modern, clean graphical user interface for the Unibot aimbot application, designed specifically for Windows users.

![Unibot GUI](https://img.shields.io/badge/Platform-Windows-blue) ![Python](https://img.shields.io/badge/Python-3.8+-green) ![GUI](https://img.shields.io/badge/GUI-Tkinter-purple)

## Features

- **Modern Dark Theme**: Sleek purple and dark interface inspired by modern cheat menus
- **Real-time Configuration**: Adjust settings while the bot is running
- **Live Status Updates**: Real-time FPS counter and status messages
- **Easy Setup**: One-click launch with automatic dependency checking
- **Multiple Sections**: Organized settings for Aimbot, Visuals, Triggers, and more
- **Color Customization**: Choose custom colors for visual elements
- **Lua API Documentation**: Built-in API reference for advanced users

## Quick Start

### Method 1: Windows Batch File (Easiest)
1. Double-click `launch_gui.bat`
2. The launcher will automatically check for Python and dependencies
3. If needed, it will install missing packages automatically

### Method 2: Python Script
1. Open Command Prompt or PowerShell
2. Navigate to the Unibot directory
3. Run: `python launch_gui.py`

### Method 3: Direct Launch
1. Open Command Prompt in the `src` directory
2. Run: `python gui.py`

## System Requirements

- **Operating System**: Windows 10/11
- **Python**: 3.8 or higher
- **Memory**: 4GB RAM minimum
- **Display**: 1024x768 minimum resolution (1920x1080 recommended)

## GUI Interface Overview

### Navigation Sidebar
- **🎯 Aimbot**: Main aiming settings and controls
- **👁 Visuals**: Visual enhancements and display options
- **🎮 Others**: Trigger bot, recoil control, and misc settings
- **🔧 Lua API**: Documentation for scripting

### Main Content Area

#### Aimbot Section
- **Enable Toggle**: Turn aimbot on/off
- **FOV Slider**: Field of view radius (0-1000 pixels)
- **Smooth Slider**: Movement smoothing (0.1-1.0)
- **Speed Slider**: Base movement speed (0.1-2.0)
- **Y Speed Slider**: Vertical speed multiplier (0.1-1.0)
- **Aim Height Slider**: Target height preference (0.0-1.0)

#### Additional Settings
- **Bullet Trace**: Visual bullet trajectory
- **Silent Aim**: Anti-detection aiming
- **Target Dead**: Target elimination features
- **Magic Bullet**: Advanced targeting
- **Color Settings**: Customize glow and main colors

#### Visuals Section
- **Bounding Box**: Draw boxes around targets
- **Snap Lines**: Draw lines to targets
- **Max Distance**: Maximum detection range
- **Nickname Display**: Show player names
- **Skeleton**: Bone structure visualization
- **Smooth Flow**: Animation smoothness

#### Others Section
- **Auto Wall**: Automatic wall penetration
- **Auto Fire**: Automatic shooting
- **Quick Peek**: Rapid peek mechanics
- **Trigger Bot**: Automatic trigger when crosshair on target
- **Recoil Control**: Compensate for weapon recoil

### Control Buttons
- **▶ START**: Launch the bot with current settings
- **⏸ STOP**: Stop the running bot
- **💾 SAVE CONFIG**: Save current settings to file
- **❌ EXIT**: Close the application

### Status Bar
- **Left**: Current status messages and notifications
- **Right**: Real-time FPS counter

## Configuration

The GUI automatically loads settings from `config.ini` and saves changes back to the file. All settings are applied in real-time when the bot is running.

### Real-time Updates
When the bot is running, most settings can be adjusted without restarting:
- FOV adjustments
- Speed and smoothing changes
- Aim height modifications
- Trigger delays

### Configuration File
Settings are stored in `config.ini` with the following sections:
- `[aim]` - Aiming parameters
- `[screen]` - Display and detection settings
- `[trigger]` - Trigger bot configuration
- `[recoil]` - Recoil compensation
- `[key_binds]` - Keyboard shortcuts

## Troubleshooting

### Common Issues

**"Error: Cannot import bot components"**
- Make sure you're running from the correct directory
- Ensure all Python files are present in the `src` folder
- Try running `python -m pip install -r requirements.txt`

**GUI doesn't start**
- Check if Python is installed: `python --version`
- Verify tkinter is available: `python -c "import tkinter"`
- On some systems, try `python3` instead of `python`

**Bot fails to start**
- Check config.ini file exists and is valid
- Verify communication settings (COM port, etc.)
- Make sure no other instance is running

**High CPU usage**
- Reduce FPS setting in configuration
- Disable debug mode if enabled
- Close other resource-intensive applications

### Windows-Specific Notes

**Antivirus Software**
- Some antivirus programs may flag the application
- Add the Unibot folder to your antivirus exclusions
- This is a false positive due to the nature of mouse automation

**Windows Defender**
- May block execution on first run
- Click "More info" → "Run anyway" if prompted
- Consider adding folder to Windows Defender exclusions

**Admin Privileges**
- Some features may require administrator privileges
- Right-click `launch_gui.bat` and select "Run as administrator"

## Keyboard Shortcuts

While the GUI is running, these shortcuts are still active:
- **F1**: Reload configuration
- **Delete**: Toggle aim
- **Home**: Toggle recoil
- **F4**: Exit program
- **Mouse5**: Trigger bot
- **Mouse6**: Rapid fire

## Customization

### Colors
Use the color buttons in the Aimbot section to customize:
- **Glow Color**: Visual effect color
- **Main Color**: Primary interface color

### Themes
The GUI uses a dark theme optimized for low-light environments and reduced eye strain.

## Performance Tips

1. **Optimize FPS**: Set target FPS to match your monitor refresh rate
2. **Reduce FOV**: Smaller FOV values improve performance
3. **Disable Debug**: Turn off debug mode when not needed
4. **Close Background Apps**: Free up system resources

## Security Note

This software is for educational purposes only. Users are responsible for complying with all applicable laws and regulations. The GUI includes the same disclaimers as the main application.

## Support

For issues specific to the GUI:
1. Check this README first
2. Verify all dependencies are installed
3. Test with the original command-line interface
4. Check the console output for error messages

## Credits

- **Original Unibot**: vike256
- **GUI Implementation**: Modern interface with Windows optimization
- **Theme Inspiration**: Contemporary gaming overlay designs