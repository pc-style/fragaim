"""
    Unibot GUI - Modern Interface
    Copyright (C) 2025 vike256

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
"""

import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
import threading
import configparser
import os
import sys
import time
from pathlib import Path
import subprocess

# Import the main bot components
try:
    from main_gui import create_bot_instance
    from configReader import ConfigReader
    from utils import Utils
except ImportError:
    print("Error: Cannot import bot components. Make sure you're running from the correct directory.")

class ModernWidget:
    """Custom styled widgets for the modern interface"""
    
    @staticmethod
    def create_toggle_button(parent, text, variable, command=None):
        """Create a modern toggle button"""
        frame = tk.Frame(parent, bg="#2a2a2a")
        
        label = tk.Label(frame, text=text, bg="#2a2a2a", fg="#ffffff", 
                        font=("Arial", 10), anchor="w")
        label.pack(side="left", fill="x", expand=True, padx=5)
        
        # Toggle switch container
        toggle_frame = tk.Frame(frame, bg="#2a2a2a", width=50, height=24)
        toggle_frame.pack(side="right", padx=5)
        toggle_frame.pack_propagate(False)
        
        canvas = tk.Canvas(toggle_frame, width=50, height=24, bg="#404040", 
                          highlightthickness=0, relief="flat")
        canvas.pack()
        
        def update_toggle():
            canvas.delete("all")
            if variable.get():
                # Enabled state - purple
                canvas.create_oval(2, 2, 48, 22, fill="#8b5fbf", outline="#a16dc7", width=1)
                canvas.create_oval(26, 4, 44, 20, fill="#ffffff", outline="")
            else:
                # Disabled state - gray
                canvas.create_oval(2, 2, 48, 22, fill="#404040", outline="#555555", width=1)
                canvas.create_oval(6, 4, 24, 20, fill="#666666", outline="")
        
        def toggle_click(event):
            variable.set(not variable.get())
            update_toggle()
            if command:
                command()
        
        canvas.bind("<Button-1>", toggle_click)
        update_toggle()
        
        # Update when variable changes externally
        def trace_callback(*args):
            update_toggle()
        variable.trace("w", trace_callback)
        
        return frame
    
    @staticmethod
    def create_slider(parent, text, variable, from_=0, to=100, resolution=1):
        """Create a modern slider"""
        frame = tk.Frame(parent, bg="#2a2a2a")
        
        # Label with value
        label_frame = tk.Frame(frame, bg="#2a2a2a")
        label_frame.pack(fill="x", padx=5, pady=2)
        
        label = tk.Label(label_frame, text=text, bg="#2a2a2a", fg="#ffffff", 
                        font=("Arial", 10), anchor="w")
        label.pack(side="left")
        
        value_label = tk.Label(label_frame, text=str(variable.get()), bg="#2a2a2a", 
                              fg="#8b5fbf", font=("Arial", 10, "bold"), anchor="e")
        value_label.pack(side="right")
        
        # Custom slider
        slider_frame = tk.Frame(frame, bg="#2a2a2a", height=30)
        slider_frame.pack(fill="x", padx=5)
        slider_frame.pack_propagate(False)
        
        scale = tk.Scale(slider_frame, from_=from_, to=to, resolution=resolution,
                        orient="horizontal", variable=variable, showvalue=0,
                        bg="#404040", fg="#ffffff", troughcolor="#606060",
                        highlightthickness=0, relief="flat", bd=0,
                        activebackground="#8b5fbf", sliderrelief="flat")
        scale.pack(fill="both", expand=True)
        
        def update_value(*args):
            value_label.config(text=str(variable.get()))
        
        variable.trace("w", update_value)
        
        return frame

class UnibotGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Fujiwara menyoo")
        self.root.geometry("1200x800")
        self.root.configure(bg="#1a1a1a")
        self.root.resizable(True, True)
        
        # Set window icon and style
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
        
        # Bot state
        self.bot_instance = None
        self.bot_running = False
        
        # Configuration
        self.config_path = "../config.ini"
        self.load_config()
        
        # Initialize variables
        self.init_variables()
        
        # Create GUI
        self.create_styles()
        self.create_gui()
        
        # Start status updates
        self.update_status()
    
    def load_config(self):
        """Load configuration from file"""
        self.config = configparser.ConfigParser()
        if os.path.exists(self.config_path):
            self.config.read(self.config_path)
        else:
            messagebox.showerror("Error", f"Config file not found: {self.config_path}")
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_path, 'w') as configfile:
                self.config.write(configfile)
            messagebox.showinfo("Success", "Configuration saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save config: {e}")
    
    def init_variables(self):
        """Initialize tkinter variables from config"""
        # Aimbot variables
        self.aim_enabled = tk.BooleanVar(value=True)
        self.fov = tk.IntVar(value=self.config.getint('screen', 'fov_x', fallback=250))
        self.smooth = tk.DoubleVar(value=self.config.getfloat('aim', 'smooth', fallback=0.9))
        self.speed = tk.DoubleVar(value=self.config.getfloat('aim', 'speed', fallback=0.3))
        self.y_speed = tk.DoubleVar(value=self.config.getfloat('aim', 'y_speed', fallback=0.2))
        self.aim_height = tk.DoubleVar(value=self.config.getfloat('aim', 'aim_height', fallback=0.7))
        
        # Visual variables
        self.wallhack_enabled = tk.BooleanVar(value=False)
        self.bullet_trace = tk.BooleanVar(value=False)
        self.silent_aim = tk.BooleanVar(value=self.config.getboolean('aim', 'enable_anti_shake', fallback=True))
        self.target_dead = tk.BooleanVar(value=False)
        self.magic_bullet = tk.BooleanVar(value=False)
        
        # Trigger variables
        self.trigger_enabled = tk.BooleanVar(value=False)
        self.trigger_delay = tk.IntVar(value=self.config.getint('trigger', 'trigger_delay', fallback=0))
        
        # Recoil variables
        self.auto_wall = tk.BooleanVar(value=False)
        self.auto_fire = tk.BooleanVar(value=False)
        self.quick_peek = tk.BooleanVar(value=False)
        self.recoil_x = tk.DoubleVar(value=self.config.getfloat('recoil', 'recoil_x', fallback=0.0))
        self.recoil_y = tk.DoubleVar(value=self.config.getfloat('recoil', 'recoil_y', fallback=0.8))
        
        # Misc variables
        self.glow_color = "#ff6b6b"
        self.main_color = "#cf4747"
        self.smooth_flow = tk.IntVar(value=0)
    
    def create_styles(self):
        """Create custom styles for the GUI"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure styles
        style.configure('Dark.TFrame', background='#2a2a2a', relief='flat')
        style.configure('Sidebar.TFrame', background='#1a1a1a', relief='flat')
        style.configure('Title.TLabel', background='#2a2a2a', foreground='#ffffff', 
                       font=('Arial', 14, 'bold'))
        style.configure('Section.TLabel', background='#1a1a1a', foreground='#8b5fbf', 
                       font=('Arial', 11, 'bold'))
        style.configure('Dark.TButton', background='#404040', foreground='#ffffff',
                       borderwidth=0, focuscolor='none')
        
    def create_gui(self):
        """Create the main GUI interface"""
        # Main container
        main_frame = tk.Frame(self.root, bg="#1a1a1a")
        main_frame.pack(fill="both", expand=True)
        
        # Create sidebar
        self.create_sidebar(main_frame)
        
        # Create main content area
        self.create_main_content(main_frame)
        
        # Create status bar
        self.create_status_bar(main_frame)
    
    def create_sidebar(self, parent):
        """Create the left sidebar with navigation"""
        sidebar = tk.Frame(parent, bg="#1a1a1a", width=200)
        sidebar.pack(side="left", fill="y", padx=10, pady=10)
        sidebar.pack_propagate(False)
        
        # Title
        title_label = tk.Label(sidebar, text="Unibot", bg="#1a1a1a", fg="#8b5fbf",
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Navigation sections
        sections = [
            ("🎯", "Aimbot", self.show_aimbot),
            ("👁", "Visuals", self.show_visuals),
            ("🎮", "Others", self.show_others),
            ("🔧", "Lua API", self.show_lua_api),
        ]
        
        self.nav_buttons = {}
        for icon, text, command in sections:
            btn_frame = tk.Frame(sidebar, bg="#1a1a1a")
            btn_frame.pack(fill="x", pady=2)
            
            btn = tk.Button(btn_frame, text=f"{icon} {text}", command=command,
                           bg="#2a2a2a", fg="#ffffff", relief="flat", bd=0,
                           font=("Arial", 11), anchor="w", padx=15, pady=8)
            btn.pack(fill="x")
            
            # Hover effects
            def on_enter(e, button=btn):
                button.config(bg="#3a3a3a")
            def on_leave(e, button=btn):
                button.config(bg="#2a2a2a")
            
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
            
            self.nav_buttons[text.lower()] = btn
        
        # Control buttons
        control_frame = tk.Frame(sidebar, bg="#1a1a1a")
        control_frame.pack(side="bottom", fill="x", pady=10)
        
        self.start_btn = tk.Button(control_frame, text="▶ START", command=self.toggle_bot,
                                  bg="#4CAF50", fg="#ffffff", relief="flat", bd=0,
                                  font=("Arial", 11, "bold"), pady=8)
        self.start_btn.pack(fill="x", pady=2)
        
        save_btn = tk.Button(control_frame, text="💾 SAVE CONFIG", command=self.save_config,
                            bg="#2196F3", fg="#ffffff", relief="flat", bd=0,
                            font=("Arial", 11), pady=8)
        save_btn.pack(fill="x", pady=2)
        
        exit_btn = tk.Button(control_frame, text="❌ EXIT", command=self.on_closing,
                            bg="#f44336", fg="#ffffff", relief="flat", bd=0,
                            font=("Arial", 11), pady=8)
        exit_btn.pack(fill="x", pady=2)
    
    def create_main_content(self, parent):
        """Create the main content area"""
        self.content_frame = tk.Frame(parent, bg="#2a2a2a")
        self.content_frame.pack(side="right", fill="both", expand=True, padx=(0, 10), pady=10)
        
        # Default to aimbot view
        self.current_view = None
        self.show_aimbot()
    
    def create_status_bar(self, parent):
        """Create the bottom status bar"""
        status_frame = tk.Frame(parent, bg="#1a1a1a", height=30)
        status_frame.pack(side="bottom", fill="x")
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(status_frame, text="Ready", bg="#1a1a1a", fg="#8b5fbf",
                                    font=("Arial", 9), anchor="w")
        self.status_label.pack(side="left", padx=10, pady=5)
        
        self.fps_label = tk.Label(status_frame, text="FPS: 0", bg="#1a1a1a", fg="#ffffff",
                                 font=("Arial", 9), anchor="e")
        self.fps_label.pack(side="right", padx=10, pady=5)
    
    def clear_content(self):
        """Clear the main content area"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Reset nav button colors
        for btn in self.nav_buttons.values():
            btn.config(bg="#2a2a2a")
    
    def show_aimbot(self):
        """Show aimbot settings"""
        if self.current_view == "aimbot":
            return
        
        self.clear_content()
        self.current_view = "aimbot"
        self.nav_buttons["aimbot"].config(bg="#8b5fbf")
        
        # Title
        title = tk.Label(self.content_frame, text="Fujiwara menyoo", bg="#2a2a2a", fg="#ffffff",
                        font=("Arial", 18, "bold"))
        title.pack(pady=(20, 30))
        
        # Create two columns
        columns_frame = tk.Frame(self.content_frame, bg="#2a2a2a")
        columns_frame.pack(fill="both", expand=True, padx=20)
        
        # Left column
        left_col = tk.Frame(columns_frame, bg="#2a2a2a")
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Aimbot settings
        self.create_aimbot_section(left_col)
        
        # Right column
        right_col = tk.Frame(columns_frame, bg="#2a2a2a")
        right_col.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Additional settings
        self.create_additional_settings(right_col)
    
    def create_aimbot_section(self, parent):
        """Create aimbot settings section"""
        # Enable toggle
        enable_frame = ModernWidget.create_toggle_button(
            parent, "Enable", self.aim_enabled, self.on_aim_toggle
        )
        enable_frame.pack(fill="x", pady=5)
        
        # FOV slider
        fov_frame = ModernWidget.create_slider(
            parent, "FOV", self.fov, 0, 1000, 10
        )
        fov_frame.pack(fill="x", pady=5)
        self.fov.trace("w", lambda *args: self.send_config_to_bot())
        
        # Smooth slider
        smooth_frame = ModernWidget.create_slider(
            parent, "Smooth", self.smooth, 0.1, 1.0, 0.01
        )
        smooth_frame.pack(fill="x", pady=5)
        self.smooth.trace("w", lambda *args: self.send_config_to_bot())
        
        # Speed slider
        speed_frame = ModernWidget.create_slider(
            parent, "Speed", self.speed, 0.1, 2.0, 0.01
        )
        speed_frame.pack(fill="x", pady=5)
        self.speed.trace("w", lambda *args: self.send_config_to_bot())
        
        # Y Speed slider
        y_speed_frame = ModernWidget.create_slider(
            parent, "Y Speed", self.y_speed, 0.1, 1.0, 0.01
        )
        y_speed_frame.pack(fill="x", pady=5)
        
        # Aim Height slider
        aim_height_frame = ModernWidget.create_slider(
            parent, "Aim Height", self.aim_height, 0.0, 1.0, 0.01
        )
        aim_height_frame.pack(fill="x", pady=5)
    
    def create_additional_settings(self, parent):
        """Create additional settings section"""
        # Bullet trace toggle
        bullet_trace_frame = ModernWidget.create_toggle_button(
            parent, "Bullet trace", self.bullet_trace
        )
        bullet_trace_frame.pack(fill="x", pady=5)
        
        # Silent aim toggle
        silent_aim_frame = ModernWidget.create_toggle_button(
            parent, "Silent Aim", self.silent_aim
        )
        silent_aim_frame.pack(fill="x", pady=5)
        
        # Target dead toggle
        target_dead_frame = ModernWidget.create_toggle_button(
            parent, "Target Dead", self.target_dead
        )
        target_dead_frame.pack(fill="x", pady=5)
        
        # Magic bullet toggle
        magic_bullet_frame = ModernWidget.create_toggle_button(
            parent, "Magic Bullet", self.magic_bullet
        )
        magic_bullet_frame.pack(fill="x", pady=5)
        
        # Color settings
        color_frame = tk.Frame(parent, bg="#2a2a2a")
        color_frame.pack(fill="x", pady=10)
        
        glow_btn = tk.Button(color_frame, text="Glow color", command=self.choose_glow_color,
                            bg="#ff6b6b", fg="#ffffff", relief="flat", bd=0,
                            font=("Arial", 10), pady=5)
        glow_btn.pack(fill="x", pady=2)
        
        main_btn = tk.Button(color_frame, text="Main color", command=self.choose_main_color,
                            bg="#cf4747", fg="#ffffff", relief="flat", bd=0,
                            font=("Arial", 10), pady=5)
        main_btn.pack(fill="x", pady=2)
    
    def show_visuals(self):
        """Show visual settings"""
        if self.current_view == "visuals":
            return
            
        self.clear_content()
        self.current_view = "visuals"
        self.nav_buttons["visuals"].config(bg="#8b5fbf")
        
        # Title
        title = tk.Label(self.content_frame, text="Visuals", bg="#2a2a2a", fg="#ffffff",
                        font=("Arial", 18, "bold"))
        title.pack(pady=(20, 30))
        
        # Visual settings
        settings_frame = tk.Frame(self.content_frame, bg="#2a2a2a")
        settings_frame.pack(fill="both", expand=True, padx=20)
        
        # Bounding box toggle
        bbox_frame = ModernWidget.create_toggle_button(
            settings_frame, "Bounding box", tk.BooleanVar()
        )
        bbox_frame.pack(fill="x", pady=5)
        
        # Snap lines toggle
        snaplines_frame = ModernWidget.create_toggle_button(
            settings_frame, "Snap lines", tk.BooleanVar(value=True)
        )
        snaplines_frame.pack(fill="x", pady=5)
        
        # Max distance slider
        max_dist_frame = ModernWidget.create_slider(
            settings_frame, "Max. distance", tk.IntVar(value=4096), 0, 10000, 50
        )
        max_dist_frame.pack(fill="x", pady=10)
        
        # Nickname section
        nickname_frame = ModernWidget.create_toggle_button(
            settings_frame, "Nickname", tk.BooleanVar()
        )
        nickname_frame.pack(fill="x", pady=5)
        
        # Hotkey section
        hotkey_frame = tk.Frame(settings_frame, bg="#2a2a2a")
        hotkey_frame.pack(fill="x", pady=10)
        
        hotkey_label = tk.Label(hotkey_frame, text="Hotkey", bg="#2a2a2a", fg="#ffffff",
                               font=("Arial", 10))
        hotkey_label.pack(side="left")
        
        hotkey_btn = tk.Button(hotkey_frame, text="Mouse X4", bg="#404040", fg="#ffffff",
                              relief="flat", bd=0, font=("Arial", 9))
        hotkey_btn.pack(side="right")
        
        # Skeleton dropdown
        skeleton_frame = tk.Frame(settings_frame, bg="#2a2a2a")
        skeleton_frame.pack(fill="x", pady=10)
        
        skeleton_label = tk.Label(skeleton_frame, text="Skeleton", bg="#2a2a2a", fg="#ffffff",
                                 font=("Arial", 10))
        skeleton_label.pack(side="left")
        
        skeleton_var = tk.StringVar(value="Head, Neck, Body...")
        skeleton_dropdown = ttk.Combobox(skeleton_frame, textvariable=skeleton_var,
                                        values=["Head, Neck, Body...", "Full Body", "Minimal"])
        skeleton_dropdown.pack(side="right")
        
        # Smooth flow
        smooth_flow_frame = ModernWidget.create_slider(
            settings_frame, "Smooth flow", self.smooth_flow, 0, 100, 1
        )
        smooth_flow_frame.pack(fill="x", pady=10)
    
    def show_others(self):
        """Show other settings"""
        if self.current_view == "others":
            return
            
        self.clear_content()
        self.current_view = "others"
        self.nav_buttons["others"].config(bg="#8b5fbf")
        
        # Title
        title = tk.Label(self.content_frame, text="Others", bg="#2a2a2a", fg="#ffffff",
                        font=("Arial", 18, "bold"))
        title.pack(pady=(20, 30))
        
        # Settings
        settings_frame = tk.Frame(self.content_frame, bg="#2a2a2a")
        settings_frame.pack(fill="both", expand=True, padx=20)
        
        # Auto wall toggle
        auto_wall_frame = ModernWidget.create_toggle_button(
            settings_frame, "Auto wall", self.auto_wall
        )
        auto_wall_frame.pack(fill="x", pady=5)
        
        # Auto fire toggle
        auto_fire_frame = ModernWidget.create_toggle_button(
            settings_frame, "Auto fire", self.auto_fire
        )
        auto_fire_frame.pack(fill="x", pady=5)
        
        # Quick peek toggle
        quick_peek_frame = ModernWidget.create_toggle_button(
            settings_frame, "Quick peek", self.quick_peek
        )
        quick_peek_frame.pack(fill="x", pady=5)
        
        # Trigger settings
        trigger_frame = tk.Frame(settings_frame, bg="#2a2a2a")
        trigger_frame.pack(fill="x", pady=20)
        
        trigger_title = tk.Label(trigger_frame, text="Trigger Bot", bg="#2a2a2a", fg="#8b5fbf",
                                font=("Arial", 12, "bold"))
        trigger_title.pack(anchor="w")
        
        trigger_enable_frame = ModernWidget.create_toggle_button(
            trigger_frame, "Enable Trigger", self.trigger_enabled
        )
        trigger_enable_frame.pack(fill="x", pady=5)
        
        trigger_delay_frame = ModernWidget.create_slider(
            trigger_frame, "Trigger Delay", self.trigger_delay, 0, 1000, 10
        )
        trigger_delay_frame.pack(fill="x", pady=5)
        
        # Recoil settings
        recoil_frame = tk.Frame(settings_frame, bg="#2a2a2a")
        recoil_frame.pack(fill="x", pady=20)
        
        recoil_title = tk.Label(recoil_frame, text="Recoil Control", bg="#2a2a2a", fg="#8b5fbf",
                               font=("Arial", 12, "bold"))
        recoil_title.pack(anchor="w")
        
        recoil_x_frame = ModernWidget.create_slider(
            recoil_frame, "Recoil X", self.recoil_x, -2.0, 2.0, 0.01
        )
        recoil_x_frame.pack(fill="x", pady=5)
        
        recoil_y_frame = ModernWidget.create_slider(
            recoil_frame, "Recoil Y", self.recoil_y, 0.0, 2.0, 0.01
        )
        recoil_y_frame.pack(fill="x", pady=5)
    
    def show_lua_api(self):
        """Show Lua API information"""
        if self.current_view == "lua_api":
            return
            
        self.clear_content()
        self.current_view = "lua_api"
        self.nav_buttons["lua api"].config(bg="#8b5fbf")
        
        # Title
        title = tk.Label(self.content_frame, text="Lua API", bg="#2a2a2a", fg="#ffffff",
                        font=("Arial", 18, "bold"))
        title.pack(pady=(20, 30))
        
        # Info text
        info_frame = tk.Frame(self.content_frame, bg="#2a2a2a")
        info_frame.pack(fill="both", expand=True, padx=20)
        
        info_text = tk.Text(info_frame, bg="#404040", fg="#ffffff", relief="flat", bd=0,
                           font=("Consolas", 10))
        info_text.pack(fill="both", expand=True)
        
        api_info = """
Unibot Lua API Documentation

-- Basic Functions
unibot.setAimEnabled(boolean)
unibot.setFOV(number)
unibot.setSmooth(number)
unibot.setSpeed(number)

-- Visual Functions
unibot.setWallhack(boolean)
unibot.setBulletTrace(boolean)
unibot.setSilentAim(boolean)

-- Trigger Functions
unibot.setTriggerEnabled(boolean)
unibot.setTriggerDelay(number)

-- Recoil Functions
unibot.setRecoilX(number)
unibot.setRecoilY(number)

-- Example Script:
function onTargetFound()
    unibot.setAimEnabled(true)
    unibot.setFOV(250)
end

function onTargetLost()
    unibot.setAimEnabled(false)
end
        """
        
        info_text.insert("1.0", api_info)
        info_text.config(state="disabled")
    
    def choose_glow_color(self):
        """Choose glow color"""
        color = colorchooser.askcolor(color=self.glow_color)
        if color[1]:
            self.glow_color = color[1]
    
    def choose_main_color(self):
        """Choose main color"""
        color = colorchooser.askcolor(color=self.main_color)
        if color[1]:
            self.main_color = color[1]
    
    def on_aim_toggle(self):
        """Handle aim toggle"""
        if self.aim_enabled.get():
            self.status_label.config(text="Aimbot enabled")
        else:
            self.status_label.config(text="Aimbot disabled")
    
    def toggle_bot(self):
        """Toggle bot on/off"""
        if not self.bot_running:
            self.start_bot()
        else:
            self.stop_bot()
    
    def start_bot(self):
        """Start the bot"""
        try:
            self.update_config_from_gui()
            self.save_config()
            
            # Create bot instance
            self.bot_instance = create_bot_instance(self.config_path)
            
            # Start the bot
            if self.bot_instance.start():
                self.bot_running = True
                self.start_btn.config(text="⏸ STOP", bg="#f44336")
                self.status_label.config(text="Bot started - Initializing...")
            else:
                messagebox.showerror("Error", "Failed to start bot - already running")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start bot: {e}")
            self.bot_running = False
            self.start_btn.config(text="▶ START", bg="#4CAF50")
    
    def stop_bot(self):
        """Stop the bot"""
        if self.bot_instance:
            self.bot_instance.stop()
            self.bot_instance = None
        
        self.bot_running = False
        self.start_btn.config(text="▶ START", bg="#4CAF50")
        self.status_label.config(text="Bot stopped")
    
    def send_config_to_bot(self):
        """Send updated configuration to running bot"""
        if self.bot_instance and self.bot_running:
            config_updates = {
                'aim': {
                    'smooth': self.smooth.get(),
                    'speed': self.speed.get(),
                    'y_speed': self.y_speed.get(),
                    'aim_height': self.aim_height.get(),
                    'enable_anti_shake': self.silent_aim.get(),
                },
                'screen': {
                    'fov_x': self.fov.get(),
                    'fov_y': self.fov.get(),
                },
                'trigger': {
                    'trigger_delay': self.trigger_delay.get(),
                },
                'recoil': {
                    'recoil_x': self.recoil_x.get(),
                    'recoil_y': self.recoil_y.get(),
                }
            }
            self.bot_instance.send_command("update_config", config_updates)
    
    def update_config_from_gui(self):
        """Update config object from GUI values"""
        # Update aim settings
        if not self.config.has_section('aim'):
            self.config.add_section('aim')
        
        self.config.set('aim', 'smooth', str(self.smooth.get()))
        self.config.set('aim', 'speed', str(self.speed.get()))
        self.config.set('aim', 'y_speed', str(self.y_speed.get()))
        self.config.set('aim', 'aim_height', str(self.aim_height.get()))
        self.config.set('aim', 'enable_anti_shake', str(self.silent_aim.get()))
        
        # Update screen settings
        if not self.config.has_section('screen'):
            self.config.add_section('screen')
        
        self.config.set('screen', 'fov_x', str(self.fov.get()))
        self.config.set('screen', 'fov_y', str(self.fov.get()))
        
        # Update trigger settings
        if not self.config.has_section('trigger'):
            self.config.add_section('trigger')
        
        self.config.set('trigger', 'trigger_delay', str(self.trigger_delay.get()))
        
        # Update recoil settings
        if not self.config.has_section('recoil'):
            self.config.add_section('recoil')
        
        self.config.set('recoil', 'recoil_x', str(self.recoil_x.get()))
        self.config.set('recoil', 'recoil_y', str(self.recoil_y.get()))
    
    def update_status(self):
        """Update status periodically"""
        if self.bot_running and self.bot_instance:
            # Get status from bot
            status = self.bot_instance.get_status()
            
            if "fps" in status:
                self.fps_label.config(text=f"FPS: {status['fps']:.1f}")
            
            if "message" in status:
                self.status_label.config(text=status["message"])
            
            if "error" in status:
                messagebox.showerror("Bot Error", status["error"])
            
            if "status" in status and status["status"] in ["stopped", "error"]:
                self.stop_bot()
        else:
            self.fps_label.config(text="FPS: 0")
        
        # Schedule next update
        self.root.after(500, self.update_status)
    
    def on_closing(self):
        """Handle window closing"""
        if self.bot_running:
            self.stop_bot()
        
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        """Run the GUI"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

def main():
    """Main entry point"""
    app = UnibotGUI()
    app.run()

if __name__ == "__main__":
    main()