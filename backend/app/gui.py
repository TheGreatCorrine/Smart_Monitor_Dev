#!/usr/bin/env python3
"""
backend/app/gui.py
------------------------------------
Graphical User Interface - Smart Monitoring System GUI Version
Based on Tkinter, providing a user-friendly graphical interface
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import queue
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import json

from .usecases.Monitor import MonitorService
from .controllers.MonitorController import MonitorController
from .infra.fileprovider import SimulatedFileProvider, LocalFileProvider
from .services.ChannelConfigurationService import ChannelConfigurationService


class SmartMonitorGUI:
    """Smart Monitoring System GUI Main Class"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🔍 Smart Refrigerator Test Anomaly Monitoring System")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Language setting
        self.current_language = "en"  # zh: Chinese, en: English
        self.texts = {
            "zh": {
                "title": "🔍 冰箱测试异常状态智能监测系统",
                "file_selection": "📁 文件选择",
                "data_file": "Data File:",
                "config_file": "Config File:",
                "run_id": "Run ID:",
                "workstation_id": "Workstation ID:",
                "browse": "Browse",
                "label_matching": "🏷️ Label Matching",
                "label_question": "Do you need to match labels?",
                "label_option1": "Yes, select labels again",
                "label_option2": "Load previous label selection",
                "label_option3": "No, use raw channel ID",
                "confirm_button": "✅ Confirm and Enter Monitoring",
                "back_button": "⬅️ Back to File Selection",
                "control_panel": "🎮 Control Panel",
                "start_monitor": "🚀 Start Monitoring",
                "stop": "⏹️ Stop",
                "start_simulation": "🎭 Start Simulation",
                "clear_results": "🗑️ Clear Results",
                "monitor_status": "📊 Monitor Status",
                "waiting": "Waiting to start...",
                "records": "Records:",
                "alarms": "Alarms:",
                "processing_time": "Processing Time:",
                "processing_speed": "Processing Speed:",
                "alarm_events": "🚨 Alarm Events",
                "log_output": "📝 Log Output",
                "error": "Error",
                "warning": "Warning",
                "success": "Success",
                "info": "Info",
                "select_data_file": "Select Data File",
                "select_config_file": "Select Config File",
                "no_label_record": "No previous label selection record found, will select again.",
                "loaded_label_record": "✅ Loaded previous label selection record (Time: {})",
                "will_use_raw_channel": "✅ Will use raw channel ID",
                "please_select_data_file": "Please select data file",
                "data_file_not_exist": "Data file does not exist",
                "config_file_not_exist": "Config file does not exist",
                "please_select_config_file": "Please select config file",
                "please_input_run_id": "Please input run ID",
                "please_input_workstation_id": "Please input workstation ID",
                "save_label_failed": "Failed to save label selection: {}",
                "init_monitor_failed": "Failed to initialize monitor service: {}",
                "load_label_config_failed": "Failed to load label configuration: {}",
                "load_label_record_failed": "Failed to load label selection record: {}",
                "processing": "Processing...",
                "processing_complete": "Processing complete",
                "processing_failed": "Processing failed: {}",
                "simulation_running": "Simulation monitoring running...",
                "simulation_failed": "Simulation failed: {}",
                "simulation_started": "Simulation started!\nWorkstation ID: {}\nPush one record every 10 seconds",
                "simulation_start_failed": "Failed to start simulation",
                "stopped": "Stopped",
                "no_anomaly": "No anomaly alarms",
                "records_per_second": "records/sec",
                "time_unknown": "Unknown",
                "auto_inferred_workstation": "Auto inferred workstation ID: {} (from filename: {})",
                "deleted_temp_file": "Deleted temp file: {}",
                "cleaned_offset_record": "Cleaned offset record: {}",
                "cleanup_temp_failed": "Failed to cleanup temp files: {}",
                "cleanup_offset_failed": "Failed to cleanup offset records: {}",
                "channel": "Channel",
                "default": "(Default)",
                "time": "Time",
                "severity": "Severity",
                "rule": "Rule",
                "description": "Description",
                "sensor_values": "Sensor Values"
            },
            "en": {
                "title": "🔍 Smart Refrigerator Test Anomaly Monitoring System",
                "file_selection": "📁 File Selection",
                "data_file": "Data File:",
                "config_file": "Config File:",
                "run_id": "Run ID:",
                "workstation_id": "Workstation ID:",
                "browse": "Browse",
                "label_matching": "🏷️ Label Matching",
                "label_question": "Do you need to match labels?",
                "label_option1": "Yes, select labels again",
                "label_option2": "Load previous label selection",
                "label_option3": "No, use raw channel ID",
                "confirm_button": "✅ Confirm and Enter Monitoring",
                "back_button": "⬅️ Back to File Selection",
                "control_panel": "🎮 Control Panel",
                "start_monitor": "🚀 Start Monitoring",
                "stop": "⏹️ Stop",
                "start_simulation": "🎭 Start Simulation",
                "clear_results": "🗑️ Clear Results",
                "monitor_status": "📊 Monitor Status",
                "waiting": "Waiting to start...",
                "records": "Records:",
                "alarms": "Alarms:",
                "processing_time": "Processing Time:",
                "processing_speed": "Processing Speed:",
                "alarm_events": "🚨 Alarm Events",
                "log_output": "📝 Log Output",
                "error": "Error",
                "warning": "Warning",
                "success": "Success",
                "info": "Info",
                "select_data_file": "Select Data File",
                "select_config_file": "Select Config File",
                "no_label_record": "No previous label selection record found, will select again.",
                "loaded_label_record": "✅ Loaded previous label selection record (Time: {})",
                "will_use_raw_channel": "✅ Will use raw channel ID",
                "please_select_data_file": "Please select data file",
                "data_file_not_exist": "Data file does not exist",
                "config_file_not_exist": "Config file does not exist",
                "please_select_config_file": "Please select config file",
                "please_input_run_id": "Please input run ID",
                "please_input_workstation_id": "Please input workstation ID",
                "save_label_failed": "Failed to save label selection: {}",
                "init_monitor_failed": "Failed to initialize monitor service: {}",
                "load_label_config_failed": "Failed to load label configuration: {}",
                "load_label_record_failed": "Failed to load label selection record: {}",
                "processing": "Processing...",
                "processing_complete": "Processing complete",
                "processing_failed": "Processing failed: {}",
                "simulation_running": "Simulation monitoring running...",
                "simulation_failed": "Simulation failed: {}",
                "simulation_started": "Simulation started!\nWorkstation ID: {}\nPush one record every 10 seconds",
                "simulation_start_failed": "Failed to start simulation",
                "stopped": "Stopped",
                "no_anomaly": "No anomaly alarms",
                "records_per_second": "records/sec",
                "time_unknown": "Unknown",
                "auto_inferred_workstation": "Auto inferred workstation ID: {} (from filename: {})",
                "deleted_temp_file": "Deleted temp file: {}",
                "cleaned_offset_record": "Cleaned offset record: {}",
                "cleanup_temp_failed": "Failed to cleanup temp files: {}",
                "cleanup_offset_failed": "Failed to cleanup offset records: {}",
                "channel": "Channel",
                "default": "(Default)",
                "time": "Time",
                "severity": "Severity",
                "rule": "Rule",
                "description": "Description",
                "sensor_values": "Sensor Values"
            }
        }
        
        # Initialize components
        self.monitor_service = MonitorService()
        self.monitor_controller = MonitorController(self.monitor_service)
        
        # FileProvider related
        self.file_provider: Optional[SimulatedFileProvider] = None
        self.monitoring_thread: Optional[threading.Thread] = None
        
        # Session statistics
        self.session_start_time: Optional[datetime] = None
        self.session_total_records = 0
        self.session_total_alarms = 0
        
        # Label matching related
        self.channel_labels = {}
        self.label_mode = False
        self.label_config_path = Path("config/label_channel_match.yaml")
        self.label_selection_path = Path("label_selection.json")
        
        # Message queue for inter-thread communication
        self.message_queue = queue.Queue()
        
        # Set up logging
        self.setup_logging()
        
        # Create interface
        self.create_widgets()
        
        # Start message processing
        self.process_messages()
        
        # Start status update timer
        self.update_status()
    
    def get_text(self, key, *args):
        """Get text in current language"""
        text = self.texts[self.current_language].get(key, key)
        if args:
            return text.format(*args)
        return text
    
    def toggle_language(self):
        """Toggle language"""
        self.current_language = "en" if self.current_language == "zh" else "zh"
        self.update_ui_language()
    
    def update_ui_language(self):
        """Update interface language"""
        # Update window title
        self.root.title(self.get_text("title"))
        
        # Update first page
        if hasattr(self, 'page1_frame') and self.page1_frame.winfo_exists():
            self.update_page1_language()
        
        # Update second page
        if hasattr(self, 'page2_frame') and self.page2_frame.winfo_exists():
            self.update_page2_language()
    
    def update_page1_language(self):
        """Update first page language"""
        # Update file selection area
        for widget in self.page1_frame.winfo_children():
            if isinstance(widget, ttk.LabelFrame):
                if "📁" in widget.cget("text"):
                    widget.configure(text=self.get_text("file_selection"))
                elif "🏷️" in widget.cget("text"):
                    widget.configure(text=self.get_text("label_matching"))
                
                # Update label text within file selection area
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Label):
                        text = child.cget("text")
                        if "Data File:" in text:
                            child.configure(text=self.get_text("data_file"))
                        elif "Config File:" in text:
                            child.configure(text=self.get_text("config_file"))
                        elif "Run ID:" in text:
                            child.configure(text=self.get_text("run_id"))
                        elif "Workstation ID:" in text:
                            child.configure(text=self.get_text("workstation_id"))
                    elif isinstance(child, ttk.Button):
                        text = child.cget("text")
                        if "Browse" in text:
                            child.configure(text=self.get_text("browse"))
        
        # Update label selection area
        if hasattr(self, 'label_scrollable_frame'):
            for widget in self.label_scrollable_frame.winfo_children():
                if isinstance(widget, ttk.Label):
                    text = widget.cget("text")
                    if "Do you need to match labels?" in text:
                        widget.configure(text=self.get_text("label_question"))
                    elif "Will use raw channel ID" in text:
                        widget.configure(text=self.get_text("will_use_raw_channel"))
                    elif "Loaded previous label selection record" in text:
                        widget.configure(text=self.get_text("loaded_label_record", self.get_text("time_unknown")))
        
        # Update confirm button text
        if hasattr(self, 'confirm_button'):
            self.confirm_button.configure(text=self.get_text("confirm_button"))
        
        # Update label matching area text
        for widget in self.page1_frame.winfo_children():
            if isinstance(widget, ttk.LabelFrame):
                # Find label question
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Label):
                        text = child.cget("text")
                        if "Do you need to match labels?" in text:
                            child.configure(text=self.get_text("label_question"))
                        elif "Will use raw channel ID" in text:
                            child.configure(text=self.get_text("will_use_raw_channel"))
                        elif "Loaded previous label selection record" in text:
                            child.configure(text=self.get_text("loaded_label_record", self.get_text("time_unknown")))
        
        # Update radio button text
        if hasattr(self, 'label_choice_var'):
            # Find and update radio button text
            for widget in self.page1_frame.winfo_children():
                if isinstance(widget, ttk.LabelFrame):
                    # Find button_frame within label frame
                    for child in widget.winfo_children():
                        if isinstance(child, ttk.Frame):
                            # Update radio button text
                            for radio in child.winfo_children():
                                if isinstance(radio, ttk.Radiobutton):
                                    value = radio.cget("value")
                                    if value == "1":
                                        radio.configure(text=self.get_text("label_option1"))
                                    elif value == "2":
                                        radio.configure(text=self.get_text("label_option2"))
                                    elif value == "3":
                                        radio.configure(text=self.get_text("label_option3"))
    
    def update_page2_language(self):
        """Update second page language"""
        # Update control panel
        for widget in self.page2_frame.winfo_children():
            if isinstance(widget, ttk.LabelFrame):
                if "🎮" in widget.cget("text"):
                    widget.configure(text=self.get_text("control_panel"))
                elif "📊" in widget.cget("text"):
                    widget.configure(text=self.get_text("monitor_status"))
                elif "🚨" in widget.cget("text"):
                    widget.configure(text=self.get_text("alarm_events"))
                elif "📝" in widget.cget("text"):
                    widget.configure(text=self.get_text("log_output"))
                
                # Update button text within control panel
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Frame):
                        for button in child.winfo_children():
                            if isinstance(button, ttk.Button):
                                text = button.cget("text")
                                if "🚀 Start Monitoring" in text or "🚀 Start Monitoring" in text:
                                    button.configure(text=self.get_text("start_monitor"))
                                elif "⏹️ Stop" in text or "⏹️ Stop" in text:
                                    button.configure(text=self.get_text("stop"))
                                elif "🎭 Start Simulation" in text or "🎭 Start Simulation" in text:
                                    button.configure(text=self.get_text("start_simulation"))
                                elif "🗑️ Clear Results" in text or "🗑️ Clear Results" in text:
                                    button.configure(text=self.get_text("clear_results"))
                
                # Update label text within status panel
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Frame):
                        for label in child.winfo_children():
                            if isinstance(label, ttk.Label):
                                text = label.cget("text")
                                if "Records:" in text or "Records:" in text:
                                    label.configure(text=self.get_text("records"))
                                elif "Alarms:" in text or "Alarms:" in text:
                                    label.configure(text=self.get_text("alarms"))
                                elif "Processing Time:" in text or "Processing Time:" in text:
                                    label.configure(text=self.get_text("processing_time"))
                                elif "Processing Speed:" in text or "Processing Speed:" in text:
                                    label.configure(text=self.get_text("processing_speed"))
        
        # Update back button text
        for widget in self.page2_frame.winfo_children():
            if isinstance(widget, ttk.Frame):
                for button in widget.winfo_children():
                    if isinstance(button, ttk.Button):
                        text = button.cget("text")
                        if "⬅️ Back to File Selection" in text or "⬅️ Back to File Selection" in text:
                            button.configure(text=self.get_text("back_button"))
        
        # Update status text variable
        if hasattr(self, 'status_text'):
            current_status = self.status_text.get()
            if current_status == "Waiting to start..." or current_status == "Waiting to start...":
                self.status_text.set(self.get_text("waiting"))
            elif current_status == "Stopped" or current_status == "Stopped":
                self.status_text.set(self.get_text("stopped"))
            elif current_status == "Processing..." or current_status == "Processing...":
                self.status_text.set(self.get_text("processing"))
            elif current_status == "Processing complete" or current_status == "Processing complete":
                self.status_text.set(self.get_text("processing_complete"))
            elif "Simulation running" in current_status or "Simulation monitoring running" in current_status:
                self.status_text.set(self.get_text("simulation_running"))
        
        # Update processing speed text
        if hasattr(self, 'speed_var'):
            current_speed = self.speed_var.get()
            if "records/sec" in current_speed:
                # Extract number part
                import re
                match = re.search(r'(\d+\.?\d*)', current_speed)
                if match:
                    speed_value = match.group(1)
                    self.speed_var.set(f"{speed_value} {self.get_text('records_per_second')}")
            elif "records/sec" in current_speed:
                # Extract number part
                import re
                match = re.search(r'(\d+\.?\d*)', current_speed)
                if match:
                    speed_value = match.group(1)
                    self.speed_var.set(f"{speed_value} {self.get_text('records_per_second')}")
        
        # Update alarm table column headers
        self.update_alarm_table_headers()
    
    def setup_logging(self):
        """Set up logging"""
        # Create log handler
        self.log_handler = LogHandler(self.message_queue)
        logging.getLogger().addHandler(self.log_handler)
        logging.getLogger().setLevel(logging.INFO)
    
    def create_widgets(self):
        """Create interface components"""
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(2, weight=1)
        
        # Create first page (file selection and label matching)
        self.create_page1()
        
        # Create second page (control panel and monitoring status)
        self.create_page2()
        
        # Default to show first page
        self.show_page1()
    
    def create_page1(self):
        """Create first page: file selection and label matching"""
        self.page1_frame = ttk.Frame(self.main_frame)
        
        # Upper part: file selection
        self.create_file_selector_page1()
        
        # Lower part: label matching
        self.create_label_matcher()
        
        # Confirm button and language toggle button
        button_frame = ttk.Frame(self.page1_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        self.confirm_button = ttk.Button(button_frame, text=self.get_text("confirm_button"), 
                                        command=self.confirm_and_go_to_page2)
        self.confirm_button.grid(row=0, column=0)
        
        # Language toggle button
        lang_button = ttk.Button(button_frame, text="🌐 中/EN", command=self.toggle_language)
        lang_button.grid(row=0, column=1, padx=(10, 0))
    
    def create_file_selector_page1(self):
        """Create file selector for first page"""
        file_frame = ttk.LabelFrame(self.page1_frame, text=self.get_text("file_selection"), padding="10")
        file_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Data file selection
        ttk.Label(file_frame, text=self.get_text("data_file")).grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.dat_file_var = tk.StringVar()
        self.dat_entry = ttk.Entry(file_frame, textvariable=self.dat_file_var, width=50)
        self.dat_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(file_frame, text=self.get_text("browse"), command=self.browse_dat_file).grid(row=0, column=2)
        
        # Config file selection
        ttk.Label(file_frame, text=self.get_text("config_file")).grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(10, 0))
        self.config_file_var = tk.StringVar(value="config/rules.yaml")
        self.config_entry = ttk.Entry(file_frame, textvariable=self.config_file_var, width=50)
        self.config_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 5), pady=(10, 0))
        ttk.Button(file_frame, text=self.get_text("browse"), command=self.browse_config_file).grid(row=1, column=2, pady=(10, 0))
        
        # Run ID
        ttk.Label(file_frame, text=self.get_text("run_id")).grid(row=2, column=0, sticky=tk.W, padx=(0, 5), pady=(10, 0))
        self.run_id_var = tk.StringVar()
        self.run_id_entry = ttk.Entry(file_frame, textvariable=self.run_id_var, width=50)
        self.run_id_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(0, 5), pady=(10, 0))
        
        # Workstation ID
        ttk.Label(file_frame, text=self.get_text("workstation_id")).grid(row=3, column=0, sticky=tk.W, padx=(0, 5), pady=(10, 0))
        self.workstation_id_var = tk.StringVar()
        self.workstation_id_entry = ttk.Entry(file_frame, textvariable=self.workstation_id_var, width=10)
        self.workstation_id_entry.grid(row=3, column=1, sticky=tk.W, padx=(0, 5), pady=(10, 0))
        
        file_frame.columnconfigure(1, weight=1)
    
    def create_label_matcher(self):
        """Create label matching area"""
        label_frame = ttk.LabelFrame(self.page1_frame, text=self.get_text("label_matching"), padding="10")
        label_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Label matching selection
        ttk.Label(label_frame, text=self.get_text("label_question")).grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        # Selection buttons
        button_frame = ttk.Frame(label_frame)
        button_frame.grid(row=1, column=0, sticky=tk.W, pady=(0, 10))
        
        self.label_choice_var = tk.StringVar(value="3")
        ttk.Radiobutton(button_frame, text=self.get_text("label_option1"), 
                       variable=self.label_choice_var, value="1", 
                       command=self.on_label_choice_change).grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(button_frame, text=self.get_text("label_option2"), 
                       variable=self.label_choice_var, value="2", 
                       command=self.on_label_choice_change).grid(row=1, column=0, sticky=tk.W)
        ttk.Radiobutton(button_frame, text=self.get_text("label_option3"), 
                       variable=self.label_choice_var, value="3", 
                       command=self.on_label_choice_change).grid(row=2, column=0, sticky=tk.W)
        
        # Label selection area
        self.label_selection_frame = ttk.Frame(label_frame)
        self.label_selection_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create scrollable area for label selection
        self.label_canvas = tk.Canvas(self.label_selection_frame, height=300)
        self.label_scrollbar = ttk.Scrollbar(self.label_selection_frame, orient="vertical", command=self.label_canvas.yview)
        self.label_scrollable_frame = ttk.Frame(self.label_canvas)
        
        self.label_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.label_canvas.configure(scrollregion=self.label_canvas.bbox("all"))
        )
        
        self.label_canvas.create_window((0, 0), window=self.label_scrollable_frame, anchor="nw")
        self.label_canvas.configure(yscrollcommand=self.label_scrollbar.set)
        
        # Add mouse wheel support
        def _on_mousewheel(event):
            self.label_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        self.label_canvas.bind("<MouseWheel>", _on_mousewheel)
        
        self.label_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.label_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        label_frame.columnconfigure(0, weight=1)
        label_frame.rowconfigure(2, weight=1)
        self.label_selection_frame.columnconfigure(0, weight=1)
        self.label_selection_frame.rowconfigure(0, weight=1)
        
        # Initial state
        self.on_label_choice_change()
    
    def create_page2(self):
        """Create second page: control panel and monitoring status"""
        self.page2_frame = ttk.Frame(self.main_frame)
        
        # Back button and language toggle button
        button_frame = ttk.Frame(self.page2_frame)
        button_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        back_button = ttk.Button(button_frame, text=self.get_text("back_button"), command=self.show_page1)
        back_button.grid(row=0, column=0, sticky=tk.W)
        
        # Language toggle button
        lang_button = ttk.Button(button_frame, text="🌐 中/EN", command=self.toggle_language)
        lang_button.grid(row=0, column=1, sticky=tk.E)
        
        button_frame.columnconfigure(1, weight=1)
        
        # Control buttons area
        self.create_control_panel(self.page2_frame)
        
        # Monitoring status area
        self.create_status_panel(self.page2_frame)
        
        # Alarm table area
        self.create_alarm_table(self.page2_frame)
        
        # Log viewer area
        self.create_log_viewer(self.page2_frame)
    
    def show_page1(self):
        """Show first page"""
        self.page2_frame.grid_remove()
        self.page1_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def show_page2(self):
        """Show second page"""
        self.page1_frame.grid_remove()
        self.page2_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def on_label_choice_change(self):
        """When label selection changes"""
        choice = self.label_choice_var.get()
        
        # Clear label selection area
        for widget in self.label_scrollable_frame.winfo_children():
            widget.destroy()
        
        if choice == "1":
            # Re-select labels
            self.label_mode = True
            self.load_label_configuration()
            self.create_label_selection_ui()
        elif choice == "2":
            # Load previous label selection record
            self.label_mode = True
            self.load_last_label_selection()
        else:
            # Skip label matching
            self.label_mode = False
            self.channel_labels = {}
            ttk.Label(self.label_scrollable_frame, text=self.get_text("will_use_raw_channel")).grid(row=0, column=0, sticky=tk.W)
    
    def load_label_configuration(self):
        """Load label configuration"""
        try:
            self.channel_config_service = ChannelConfigurationService(str(self.label_config_path))
            self.channel_config_service.load_configuration()
            self.config = self.channel_config_service.get_configuration_for_ui()
        except Exception as e:
            messagebox.showerror(self.get_text("error"), self.get_text("load_label_config_failed", str(e)))
            self.config = {'categories': {}}
    
    def create_label_selection_ui(self):
        """Create label selection interface"""
        row = 0
        for category_key, category in self.config['categories'].items():
            # Category title
            ttk.Label(self.label_scrollable_frame, text=f"【{category['category_name']}】{category['category_description']}", 
                     font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky=tk.W, pady=(10, 5))
            row += 1
            
            for ch in category['channels']:
                ch_id = ch['channel_id']
                
                # Channel title
                ttk.Label(self.label_scrollable_frame, text=f"  {self.get_text('channel')}: {ch_id}", 
                         font=('Arial', 9, 'bold')).grid(row=row, column=0, sticky=tk.W, padx=(20, 0))
                row += 1
                
                # Create radio button
                label_var = tk.StringVar(value=ch.get('default_subtype_id', ''))
                self.channel_labels[ch_id] = label_var
                
                for idx, st in enumerate(ch['available_subtypes']):
                    default_mark = self.get_text("default") if st['is_default'] else ""
                    ttk.Radiobutton(self.label_scrollable_frame, 
                                   text=f"    {st['label']}",
                                   variable=label_var, 
                                   value=st['subtype_id']).grid(row=row, column=0, sticky=tk.W, padx=(40, 0))
                    row += 1
                
                row += 1  # Add empty line
    
    def load_last_label_selection(self):
        """Load previous label selection record"""
        if not self.label_selection_path.exists():
            messagebox.showwarning(self.get_text("warning"), self.get_text("no_label_record"))
            self.label_choice_var.set("1")
            self.on_label_choice_change()
            return
        
        try:
            with open(self.label_selection_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.channel_labels = data['channel_labels']
            ttk.Label(self.label_scrollable_frame, 
                     text=self.get_text("loaded_label_record", data.get('timestamp', self.get_text("time_unknown")))).grid(row=0, column=0, sticky=tk.W)
            
        except Exception as e:
            messagebox.showerror(self.get_text("error"), self.get_text("load_label_record_failed", str(e)))
            self.label_choice_var.set("1")
            self.on_label_choice_change()
    
    def confirm_and_go_to_page2(self):
        """Confirm and go to second page"""
        # Validate file selection
        if not self.dat_file_var.get():
            messagebox.showerror(self.get_text("error"), self.get_text("please_select_data_file"))
            return
        
        if not Path(self.dat_file_var.get()).exists():
            messagebox.showerror(self.get_text("error"), self.get_text("data_file_not_exist"))
            return
        
        # Save label selection (if label matching is selected)
        if self.label_mode and self.label_choice_var.get() == "1":
            try:
                # Collect label selection
                selected_labels = {}
                for ch_id, var in self.channel_labels.items():
                    selected_labels[ch_id] = var.get()
                
                # Save to file
                with open(self.label_selection_path, 'w', encoding='utf-8') as f:
                    json.dump({
                        "timestamp": datetime.now().isoformat(),
                        "channel_labels": selected_labels
                    }, f, ensure_ascii=False, indent=2)
                
                self.channel_labels = selected_labels
                
            except Exception as e:
                messagebox.showerror(self.get_text("error"), self.get_text("save_label_failed", str(e)))
                return
        
        # Go to second page
        self.show_page2()
        
        # Initialize monitor service
        try:
            self.monitor_service.rule_loader.config_path = Path(self.config_file_var.get())
            self.monitor_service.initialize()
        except Exception as e:
            messagebox.showerror(self.get_text("error"), self.get_text("init_monitor_failed", str(e)))
            return
    

    
    def create_control_panel(self, parent):
        """Create control panel"""
        control_frame = ttk.LabelFrame(parent, text=self.get_text("control_panel"), padding="10")
        control_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Button area
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        self.start_button = ttk.Button(button_frame, text=self.get_text("start_monitor"), command=self.start_monitoring)
        self.start_button.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text=self.get_text("stop"), command=self.stop_monitoring, state='disabled')
        self.stop_button.grid(row=0, column=1, padx=(0, 10))
        
        self.simulate_button = ttk.Button(button_frame, text=self.get_text("start_simulation"), command=self.start_simulation)
        self.simulate_button.grid(row=0, column=2, padx=(0, 10))
        
        self.clear_button = ttk.Button(button_frame, text=self.get_text("clear_results"), command=self.clear_results)
        self.clear_button.grid(row=0, column=3, padx=(0, 10))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(control_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        control_frame.columnconfigure(0, weight=1)
    
    def create_status_panel(self, parent):
        """Create status panel"""
        status_frame = ttk.LabelFrame(parent, text=self.get_text("monitor_status"), padding="10")
        status_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        # Status information
        self.status_text = tk.StringVar(value=self.get_text("waiting"))
        ttk.Label(status_frame, textvariable=self.status_text, font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W)
        
        # Statistics
        stats_frame = ttk.Frame(status_frame)
        stats_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Label(stats_frame, text=self.get_text("records")).grid(row=0, column=0, sticky=tk.W)
        self.records_var = tk.StringVar(value="0")
        ttk.Label(stats_frame, textvariable=self.records_var, font=('Arial', 9, 'bold')).grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        
        ttk.Label(stats_frame, text=self.get_text("alarms")).grid(row=1, column=0, sticky=tk.W)
        self.alarms_var = tk.StringVar(value="0")
        ttk.Label(stats_frame, textvariable=self.alarms_var, font=('Arial', 9, 'bold')).grid(row=1, column=1, sticky=tk.W, padx=(5, 0))
        
        ttk.Label(stats_frame, text=self.get_text("processing_time")).grid(row=2, column=0, sticky=tk.W)
        self.time_var = tk.StringVar(value="0.00s")
        ttk.Label(stats_frame, textvariable=self.time_var, font=('Arial', 9, 'bold')).grid(row=2, column=1, sticky=tk.W, padx=(5, 0))
        
        ttk.Label(stats_frame, text=self.get_text("processing_speed")).grid(row=3, column=0, sticky=tk.W)
        self.speed_var = tk.StringVar(value=f"0 {self.get_text('records_per_second')}")
        ttk.Label(stats_frame, textvariable=self.speed_var, font=('Arial', 9, 'bold')).grid(row=3, column=1, sticky=tk.W, padx=(5, 0))
        
        status_frame.columnconfigure(0, weight=1)
    
    def create_alarm_table(self, parent):
        """Create alarm table"""
        alarm_frame = ttk.LabelFrame(parent, text=self.get_text("alarm_events"), padding="10")
        alarm_frame.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        
        # Create table
        self.alarm_columns = ('Time', 'Severity', 'Rule', 'Description', 'Sensor Values')
        self.alarm_tree = ttk.Treeview(alarm_frame, columns=self.alarm_columns, show='headings', height=10)
        
        # Set column headers
        self.update_alarm_table_headers()
        
        # Add scrollbar
        alarm_scrollbar = ttk.Scrollbar(alarm_frame, orient=tk.VERTICAL, command=self.alarm_tree.yview)
        self.alarm_tree.configure(yscrollcommand=alarm_scrollbar.set)
        
        # Add scrollbar
        alarm_scrollbar = ttk.Scrollbar(alarm_frame, orient=tk.VERTICAL, command=self.alarm_tree.yview)
        self.alarm_tree.configure(yscrollcommand=alarm_scrollbar.set)
        
        self.alarm_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        alarm_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        alarm_frame.columnconfigure(0, weight=1)
        alarm_frame.rowconfigure(0, weight=1)
    
    def create_log_viewer(self, parent):
        """Create log viewer"""
        log_frame = ttk.LabelFrame(parent, text=self.get_text("log_output"), padding="10")
        log_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, font=('Consolas', 9))
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Configure main window grid weights
        parent.rowconfigure(2, weight=1)
        parent.rowconfigure(3, weight=1)
    
    def browse_dat_file(self):
        """Browse data file"""
        filename = filedialog.askopenfilename(
            title=self.get_text("select_data_file"),
            filetypes=[("DAT files", "*.dat"), ("All files", "*.*")]
        )
        if filename:
            self.dat_file_var.set(filename)
            # Auto-generate run ID
            if not self.run_id_var.get():
                path = Path(filename)
                run_id = f"RUN_{path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                self.run_id_var.set(run_id)
            
            # Auto-infer workstation ID
            path = Path(filename)
            if path.stem.startswith('mpl') or path.stem.startswith('MPL'):
                # Extract workstation ID from filename
                import re
                match = re.search(r'mpl(\d+)', path.stem.lower())
                if match:
                    workstation_id = match.group(1)
                    self.workstation_id_var.set(workstation_id)
                    print(self.get_text("auto_inferred_workstation", workstation_id, path.stem))
    
    def browse_config_file(self):
        """Browse config file"""
        filename = filedialog.askopenfilename(
            title=self.get_text("select_config_file"),
            filetypes=[("YAML files", "*.yaml"), ("YML files", "*.yml"), ("All files", "*.*")]
        )
        if filename:
            self.config_file_var.set(filename)
    
    def start_monitoring(self):
        """Start monitoring"""
        # Validate input
        dat_file = self.dat_file_var.get().strip()
        config_file = self.config_file_var.get().strip()
        run_id = self.run_id_var.get().strip()
        
        if not dat_file:
            messagebox.showerror(self.get_text("error"), self.get_text("please_select_data_file"))
            return
        
        if not config_file:
            messagebox.showerror(self.get_text("error"), self.get_text("please_select_config_file"))
            return
        
        if not run_id:
            messagebox.showerror(self.get_text("error"), self.get_text("please_input_run_id"))
            return
        
        # Check if file exists
        if not Path(dat_file).exists():
            messagebox.showerror(self.get_text("error"), self.get_text("data_file_not_exist", dat_file))
            return
        
        if not Path(config_file).exists():
            messagebox.showerror(self.get_text("error"), self.get_text("config_file_not_exist", config_file))
            return
        
        # Clear previous results
        self.clear_results()
        
        # Update interface status
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.status_text.set(self.get_text("processing"))
        self.progress_var.set(0)
        
        # Record session start time
        self.session_start_time = datetime.now()
        self.session_total_records = 0
        self.session_total_alarms = 0
        
        # Process in background thread
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_worker,
            args=(dat_file, config_file, run_id),
            daemon=True
        )
        self.monitoring_thread.start()
    
    def stop_monitoring(self):
        """Stop monitoring"""
        # Stop continuous monitoring
        if self.monitor_service.is_monitoring:
            self.monitor_service.stop_continuous_monitoring()
        
        # Stop file provider
        if self.file_provider:
            self.file_provider.stop()
        
        # Clean up temporary files and offset records
        self._cleanup_temp_files()
        
        # Reset session statistics
        self.session_start_time = None
        self.session_total_records = 0
        self.session_total_alarms = 0
        
        self.status_text.set(self.get_text("stopped"))
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.simulate_button.config(state='normal')
        self.progress_var.set(0)
    
    def clear_results(self):
        """Clear results"""
        # Clear alarm table
        for item in self.alarm_tree.get_children():
            self.alarm_tree.delete(item)
        
        # Reset statistics
        self.records_var.set("0")
        self.alarms_var.set("0")
        self.time_var.set("0.00s")
        self.speed_var.set(f"0 {self.get_text('records_per_second')}")
        
        # Clear log
        self.log_text.delete(1.0, tk.END)
    
    def start_simulation(self):
        """Start simulated file push"""
        # Validate input
        dat_file = self.dat_file_var.get().strip()
        config_file = self.config_file_var.get().strip()
        run_id = self.run_id_var.get().strip()
        workstation_id = self.workstation_id_var.get().strip()
        
        if not dat_file:
            messagebox.showerror(self.get_text("error"), self.get_text("please_select_data_file"))
            return
        
        if not config_file:
            messagebox.showerror(self.get_text("error"), self.get_text("please_select_config_file"))
            return
        
        if not run_id:
            messagebox.showerror(self.get_text("error"), self.get_text("please_input_run_id"))
            return
        
        if not workstation_id:
            messagebox.showerror(self.get_text("error"), self.get_text("please_input_workstation_id"))
            return
        
        # Check if file exists
        if not Path(dat_file).exists():
            messagebox.showerror(self.get_text("error"), self.get_text("data_file_not_exist", dat_file))
            return
        
        if not Path(config_file).exists():
            messagebox.showerror(self.get_text("error"), self.get_text("config_file_not_exist", config_file))
            return
        
        try:
            # Clean up old temporary files and offset records
            self._cleanup_temp_files()
            
            # Reset session statistics
            self.session_start_time = datetime.now()
            self.session_total_records = 0
            self.session_total_alarms = 0
            
            # Initialize monitor service
            self.monitor_service.rule_loader.config_path = Path(config_file)
            self.monitor_service.initialize()
            
            # Add alarm handler
            self.monitor_service.add_alarm_handler(self._gui_alarm_handler)
            
            # Create simulated file provider
            self.file_provider = SimulatedFileProvider(dat_file, workstation_id)
            
            # Set file provider
            self.monitor_service.set_file_provider(self.file_provider)
            
            # Start continuous monitoring
            if self.monitor_service.start_continuous_monitoring(run_id):
                
                # Update interface status
                self.start_button.config(state='disabled')
                self.stop_button.config(state='normal')
                self.simulate_button.config(state='disabled')
                self.status_text.set(self.get_text("simulation_running"))
                self.progress_var.set(50)
                
                messagebox.showinfo(self.get_text("success"), self.get_text("simulation_started", workstation_id))
            else:
                messagebox.showerror(self.get_text("error"), self.get_text("simulation_start_failed"))
                
        except Exception as e:
            messagebox.showerror(self.get_text("error"), self.get_text("simulation_failed", str(e)))
            self.status_text.set(f"Simulation failed: {str(e)}")
    
    def _monitoring_worker(self, dat_file: str, config_file: str, run_id: str):
        """Monitoring worker thread"""
        try:
            # Initialize monitor service
            self.monitor_service.rule_loader.config_path = Path(config_file)
            self.monitor_service.initialize()
            
            # Add alarm handler
            self.monitor_service.add_alarm_handler(self._gui_alarm_handler)
            
            # Process data file
            start_time = datetime.now()
            alarms, records_count = self.monitor_service.process_data_file(dat_file, run_id)
            end_time = datetime.now()
            
            # Update session statistics
            self.session_total_records = records_count
            self.session_total_alarms = len(alarms)
            
            processing_time = (end_time - start_time).total_seconds()
            speed = records_count / processing_time if processing_time > 0 else 0
            
            # Update statistics
            self.records_var.set(str(records_count))
            self.alarms_var.set(str(len(alarms)))
            self.time_var.set(f"{processing_time:.2f}s")
            self.speed_var.set(f"{speed:.2f} {self.get_text('records_per_second')}")
            
            # Update status
            self.status_text.set(self.get_text("processing_complete"))
            self.progress_var.set(100)
            
            # Display completion message
            messagebox.showinfo(self.get_text("success"), self.get_text("processing_complete", records_count, len(alarms)))
            
        except Exception as e:
            self.status_text.set(self.get_text("processing_failed", str(e)))
            messagebox.showerror(self.get_text("error"), self.get_text("processing_failed", str(e)))
        finally:
            # Restore interface status
            self.start_button.config(state='normal')
            self.stop_button.config(state='disabled')
    
    def _gui_alarm_handler(self, alarm):
        """GUI alarm handler"""
        # Add alarm to table in GUI thread
        self.root.after(0, self._add_alarm_to_table, alarm)
    
    def _add_alarm_to_table(self, alarm):
        """Add alarm to table"""
        severity_icons = {
            "low": "🔵",
            "medium": "🟡", 
            "high": "🟠",
            "critical": "🔴"
        }
        
        icon = severity_icons.get(alarm.severity.value, "⚪")
        severity_display = f"{icon} {alarm.severity.value.upper()}"
        
        # Truncate sensor value display
        sensor_values_str = str(alarm.sensor_values)[:50]
        if len(str(alarm.sensor_values)) > 50:
            sensor_values_str += "..."
        
        self.alarm_tree.insert('', 'end', values=(
            alarm.timestamp.strftime('%H:%M:%S'),
            severity_display,
            alarm.rule_name,
            alarm.description[:30] + "..." if len(alarm.description) > 30 else alarm.description,
            sensor_values_str
        ))
    
    def process_messages(self):
        """Process log messages"""
        try:
            while True:
                message = self.message_queue.get_nowait()
                self.log_text.insert(tk.END, message + '\n')
                self.log_text.see(tk.END)
        except queue.Empty:
            pass
        
        # Check for messages every 100ms
        self.root.after(100, self.process_messages)
    
    def update_status(self):
        """Update monitoring status"""
        if self.monitor_service.is_monitoring:
            status = self.monitor_service.get_monitoring_status()
            stats = status.get('stats', {})
            
            # Update session statistics
            self.session_total_records = stats.get('total_records_processed', 0)
            self.session_total_alarms = stats.get('total_alarms_generated', 0)
            
            # Calculate session runtime and processing speed
            if self.session_start_time:
                elapsed_time = (datetime.now() - self.session_start_time).total_seconds()
                self.time_var.set(f"{elapsed_time:.1f}s")
                
                # Calculate processing speed (records/sec)
                if elapsed_time > 0:
                    speed = self.session_total_records / elapsed_time
                    self.speed_var.set(f"{speed:.2f} {self.get_text('records_per_second')}")
                else:
                    self.speed_var.set(f"0.00 {self.get_text('records_per_second')}")
            else:
                self.time_var.set("0.0s")
                self.speed_var.set(f"0.00 {self.get_text('records_per_second')}")
            
            # Update record count and alarm count
            self.records_var.set(str(self.session_total_records))
            self.alarms_var.set(str(self.session_total_alarms))
            
            # Update status text
            if status.get('file_provider'):
                fp_status = status['file_provider']
                if fp_status.get('total_records_pushed'):
                    self.status_text.set(f"Simulation running - {fp_status['total_records_pushed']} records pushed")
                else:
                    self.status_text.set(self.get_text("simulation_running"))
        
        # Update status every 1 second
        self.root.after(1000, self.update_status)
    
    def update_alarm_table_headers(self):
        """Update alarm table column headers"""
        if hasattr(self, 'alarm_tree'):
            # Set column headers
            headers = [
                self.get_text("time"),
                self.get_text("severity"),
                self.get_text("rule"),
                self.get_text("description"),
                self.get_text("sensor_values")
            ]
            
            for i, col in enumerate(self.alarm_columns):
                self.alarm_tree.heading(col, text=headers[i])
                self.alarm_tree.column(col, width=150)
    
    def _cleanup_temp_files(self):
        """Clean up temporary files and offset records"""
        try:
            import json
            from pathlib import Path
            
            # Clean up temp files
            workstation_id = self.workstation_id_var.get().strip() if hasattr(self, 'workstation_id_var') and self.workstation_id_var.get().strip() else "1"
            temp_file = Path(f"data/mpl{workstation_id}_temp.dat")
            if temp_file.exists():
                temp_file.unlink()
                print(self.get_text("deleted_temp_file", temp_file))
            
            # Clean up offset records
            offset_file = Path(".offsets.json")
            if offset_file.exists():
                try:
                    with open(offset_file, 'r') as f:
                        offsets = json.load(f)
                    
                    # Delete offset record for temp file
                    temp_file_key = f"data/mpl{workstation_id}_temp.dat"
                    if temp_file_key in offsets:
                        del offsets[temp_file_key]
                        with open(offset_file, 'w') as f:
                            json.dump(offsets, f)
                        print(self.get_text("cleaned_offset_record", temp_file_key))
                except Exception as e:
                    print(self.get_text("cleanup_offset_failed", str(e)))
            
        except Exception as e:
            print(self.get_text("cleanup_temp_failed", str(e)))
    
    def run(self):
        """Run GUI application"""
        self.root.mainloop()


class LogHandler(logging.Handler):
    """Custom log handler to send logs to GUI"""
    
    def __init__(self, message_queue):
        super().__init__()
        self.message_queue = message_queue
    
    def emit(self, record):
        """Send log message"""
        msg = self.format(record)
        self.message_queue.put(msg)


def main():
    """Main function"""
    app = SmartMonitorGUI()
    app.run()


if __name__ == "__main__":
    main() 