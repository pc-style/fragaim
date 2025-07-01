# Unibot GUI Setup Instructions for Windows

## Overview

This package includes a modern graphical user interface for the Unibot application, designed specifically for Windows users. The GUI provides an intuitive way to configure and control the aimbot with a sleek, dark theme interface inspired by modern cheat menus.

## Quick Setup (Windows)

### Step 1: Install Python
1. Download Python 3.8+ from [python.org](https://python.org)
2. During installation, check "Add Python to PATH"
3. Verify installation: Open Command Prompt and run `python --version`

### Step 2: Launch the GUI
Choose one of these methods:

**Method A: Batch File (Easiest)**
1. Double-click `launch_gui.bat`
2. The script will automatically check dependencies and launch the GUI

**Method B: Python Script**
1. Open Command Prompt in the project directory
2. Run: `python launch_gui.py`

**Method C: Direct Launch**
1. Open Command Prompt in the `src` directory
2. Run: `python gui.py`

### Step 3: Test the Interface
If you want to test the GUI without the full bot functionality:
1. Run: `python test_gui.py`
2. This shows the interface in demo mode

## Files Created

### Main GUI Components
- `src/gui.py` - Complete GUI interface with bot integration
- `src/main_gui.py` - Bot core modified for GUI control
- `launch_gui.py` - Cross-platform launcher script
- `launch_gui.bat` - Windows batch launcher with dependency checking
- `test_gui.py` - Standalone GUI test without bot dependencies

### Documentation
- `GUI_README.md` - Comprehensive GUI user guide
- `SETUP_INSTRUCTIONS.md` - This file
- `README.md` - Updated main README with GUI information

## GUI Features

### Interface Layout
- **Dark Theme**: Professional dark interface with purple accents
- **Sidebar Navigation**: Easy switching between different settings categories
- **Modern Controls**: Custom toggle switches and sliders
- **Real-time Updates**: Settings applied instantly while bot is running
- **Status Bar**: Live FPS counter and status messages

### Settings Categories

#### 🎯 Aimbot
- Enable/Disable toggle
- FOV (Field of View) adjustment
- Smoothing controls
- Speed and Y-speed settings
- Aim height configuration
- Real-time configuration updates

#### 👁 Visuals
- Bounding box options
- Snap lines
- Maximum distance settings
- Nickname display
- Skeleton visualization
- Smooth flow controls

#### 🎮 Others
- Auto wall features
- Auto fire controls
- Quick peek settings
- Trigger bot configuration
- Recoil control settings

### Control Buttons
- **START/STOP**: Control bot execution
- **SAVE CONFIG**: Save current settings to file
- **EXIT**: Close application safely

## Troubleshooting

### Common Issues

**"Python not found"**
- Install Python from python.org
- Make sure "Add to PATH" was checked during installation
- Try using `python3` instead of `python`

**"tkinter not available"**
- On Windows: Reinstall Python with "tcl/tk and IDLE" option checked
- On Linux: Install `python3-tk` package

**GUI doesn't appear**
- Check if running in a headless environment
- Ensure you have a display/desktop environment
- Try running the test GUI first: `python test_gui.py`

**Bot fails to start**
- Verify `config.ini` exists and is valid
- Check that all bot source files are present in `src/` directory
- Ensure you have necessary permissions for mouse/screen access

### Performance Issues

**High CPU usage**
- Reduce FPS setting in configuration
- Close other resource-intensive applications
- Disable debug mode if enabled

**Slow GUI response**
- Update graphics drivers
- Reduce window size if on older hardware
- Close unnecessary background applications

## Configuration Integration

The GUI automatically:
- Loads settings from `config.ini` on startup
- Saves changes to configuration file
- Applies real-time updates to running bot
- Validates setting ranges and values

### Real-time Features
When the bot is running, these settings update immediately:
- FOV adjustments
- Speed and smoothing changes
- Aim height modifications
- Trigger delays
- Recoil compensation values

## Security Notes

- The GUI includes the same security disclaimers as the main application
- Some antivirus software may flag the application due to mouse automation
- Consider adding the project folder to antivirus exclusions
- Use only for educational/testing purposes

## Advanced Usage

### Custom Themes
The GUI supports customization through color pickers:
- Glow Color: Affects visual highlighting
- Main Color: Primary interface accents

### Lua API Integration
The GUI includes documentation for the Lua API, allowing advanced users to create custom scripts and automation.

### Configuration Backup
The GUI maintains configuration integrity:
- Automatic backup before major changes
- Validation of setting ranges
- Error recovery for corrupted configurations

## Support

If you encounter issues:
1. Check this setup guide first
2. Verify all dependencies are installed
3. Test with the demo GUI (`test_gui.py`)
4. Check console output for error messages
5. Ensure you're running with appropriate permissions

## Technical Details

### Dependencies
- Python 3.8+
- tkinter (included with Python)
- configparser (included with Python)
- threading (included with Python)

### Architecture
- Modular design with separate GUI and bot cores
- Thread-safe communication between GUI and bot
- Real-time status updates via queue system
- Clean separation of concerns for maintainability

### Performance
- Optimized for Windows 10/11
- Minimal resource usage when idle
- Efficient real-time updates
- Responsive interface design

## License

This GUI extension maintains the same GPL v3 license as the original Unibot application. See LICENSE file for details.