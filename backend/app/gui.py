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
        self.config = {'categories': {}}  # Initialize with empty config
        
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
        
        # Confirm button
        button_frame = ttk.Frame(self.page1_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        self.confirm_button = ttk.Button(button_frame, text="✅ Confirm and Enter Monitoring", 
                                        command=self.confirm_and_go_to_page2)
        self.confirm_button.grid(row=0, column=0)
    
    def create_file_selector_page1(self):
        """Create file selector for first page"""
        file_frame = ttk.LabelFrame(self.page1_frame, text="📁 File Selection", padding="10")
        file_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Data file selection
        ttk.Label(file_frame, text="Data File:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.dat_file_var = tk.StringVar()
        self.dat_file_entry = ttk.Entry(file_frame, textvariable=self.dat_file_var, width=50)
        self.dat_file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(file_frame, text="Browse", command=self.browse_dat_file).grid(row=0, column=2)
        
        # Config file selection
        ttk.Label(file_frame, text="Config File:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(10, 0))
        self.config_file_var = tk.StringVar(value="config/rules.yaml")
        self.config_file_entry = ttk.Entry(file_frame, textvariable=self.config_file_var, width=50)
        self.config_file_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 5), pady=(10, 0))
        ttk.Button(file_frame, text="Browse", command=self.browse_config_file).grid(row=1, column=2, pady=(10, 0))
        
        # Run ID
        ttk.Label(file_frame, text="Run ID:").grid(row=2, column=0, sticky=tk.W, padx=(0, 5), pady=(10, 0))
        self.run_id_var = tk.StringVar()
        self.run_id_entry = ttk.Entry(file_frame, textvariable=self.run_id_var, width=50)
        self.run_id_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(0, 5), pady=(10, 0))
        
        # Workstation ID
        ttk.Label(file_frame, text="Workstation ID:").grid(row=3, column=0, sticky=tk.W, padx=(0, 5), pady=(10, 0))
        self.workstation_id_var = tk.StringVar()
        self.workstation_id_entry = ttk.Entry(file_frame, textvariable=self.workstation_id_var, width=50)
        self.workstation_id_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(0, 5), pady=(10, 0))
        
        # Configure grid weights
        file_frame.columnconfigure(1, weight=1)
    
    def create_label_matcher(self):
        """Create label matching area"""
        label_frame = ttk.LabelFrame(self.page1_frame, text="🏷️ Label Matching", padding="10")
        label_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Label matching selection
        ttk.Label(label_frame, text="Do you need to match labels?").grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        # Selection buttons
        button_frame = ttk.Frame(label_frame)
        button_frame.grid(row=1, column=0, sticky=tk.W, pady=(0, 10))
        
        self.label_choice_var = tk.StringVar(value="1")
        ttk.Radiobutton(button_frame, text="Yes, select labels again", variable=self.label_choice_var, value="1",
                        command=self.on_label_choice_change).grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(button_frame, text="Load previous label selection", variable=self.label_choice_var, value="2",
                        command=self.on_label_choice_change).grid(row=1, column=0, sticky=tk.W)
        ttk.Radiobutton(button_frame, text="No, use raw channel ID", variable=self.label_choice_var, value="3",
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
        
        self.label_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        self.label_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.label_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configure grid weights
        label_frame.columnconfigure(0, weight=1)
        label_frame.rowconfigure(2, weight=1)
        self.label_selection_frame.columnconfigure(0, weight=1)
        self.label_selection_frame.rowconfigure(0, weight=1)
        
        # Initial state
        self.on_label_choice_change()
    
    def create_page2(self):
        """Create second page: control panel and monitoring status"""
        self.page2_frame = ttk.Frame(self.main_frame)
        
        # Back button
        button_frame = ttk.Frame(self.page2_frame)
        button_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        back_button = ttk.Button(button_frame, text="⬅️ Back to File Selection", command=self.show_page1)
        back_button.grid(row=0, column=0, sticky=tk.W)
        
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
            ttk.Label(self.label_scrollable_frame, text="✅ Will use raw channel ID").grid(row=0, column=0, sticky=tk.W)
    
    def load_label_configuration(self):
        """Load label configuration"""
        try:
            self.channel_config_service = ChannelConfigurationService(str(self.label_config_path))
            self.config = self.channel_config_service.get_configuration_for_ui()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load label configuration: {str(e)}")
            self.label_mode = False
            # Keep the default empty config instead of setting to None
            self.config = {'categories': {}}
    
    def create_label_selection_ui(self):
        """Create label selection interface"""
        row = 0
        for category_key, category in self.config['categories'].items():
            # Category title - use English name
            category_name = category['category_name'].get('en', category['category_name']) if isinstance(category['category_name'], dict) else category['category_name']
            category_desc = category['category_description'].get('en', category['category_description']) if isinstance(category['category_description'], dict) else category['category_description']
            ttk.Label(self.label_scrollable_frame, text=f"【{category_name}】{category_desc}", 
                      font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky=tk.W, pady=(10, 5))
            row += 1
            
            for ch in category['channels']:
                ch_id = ch['channel_id']
                
                # Channel title
                ttk.Label(self.label_scrollable_frame, text=f"  Channel: {ch_id}", 
                          font=('Arial', 9, 'bold')).grid(row=row, column=0, sticky=tk.W, padx=(20, 0))
                row += 1
                
                # Create radio button
                label_var = tk.StringVar(value=ch.get('default_subtype_id', ''))
                self.channel_labels[ch_id] = label_var
                
                for st in ch['available_subtypes']:
                    default_mark = " (Default)" if st['subtype_id'] == ch.get('default_subtype_id', '') else ""
                    ttk.Radiobutton(self.label_scrollable_frame, text=st['label'], 
                                   variable=label_var, value=st['subtype_id']).grid(row=row, column=0, sticky=tk.W, padx=(40, 0))
                    row += 1
                
                row += 1  # Add empty line
    
    def load_last_label_selection(self):
        """Load previous label selection record"""
        if not self.label_selection_path.exists():
            messagebox.showwarning("Warning", "No previous label selection record found, will select again.")
            self.label_choice_var.set("1")
            self.on_label_choice_change()
            return
        
        try:
            with open(self.label_selection_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Load channel labels
            for ch_id, label in data['labels'].items():
                if ch_id in self.channel_labels:
                    self.channel_labels[ch_id].set(label)
            
            ttk.Label(self.label_scrollable_frame, text="✅ Loaded previous label selection record (Time: Unknown)").grid(row=0, column=0, sticky=tk.W)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load label selection record: {str(e)}")
            self.label_choice_var.set("1")
            self.on_label_choice_change()
    
    def confirm_and_go_to_page2(self):
        """Confirm and go to second page"""
        # Validate file selection
        if not self.dat_file_var.get():
            messagebox.showerror("Error", "Please select data file")
            return
        
        if not self.config_file_var.get():
            messagebox.showerror("Error", "Please select config file")
            return
        
        if not self.run_id_var.get():
            messagebox.showerror("Error", "Please input run ID")
            return
        
        if not self.workstation_id_var.get():
            messagebox.showerror("Error", "Please input workstation ID")
            return
        
        # Check if files exist
        if not Path(self.dat_file_var.get()).exists():
            messagebox.showerror("Error", "Data file does not exist")
            return
        
        if not Path(self.config_file_var.get()).exists():
            messagebox.showerror("Error", "Config file does not exist")
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
                        'timestamp': datetime.now().isoformat(),
                        'labels': selected_labels
                    }, f, ensure_ascii=False, indent=2)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save label selection: {str(e)}")
                return
        
        # Go to second page
        self.show_page2()
        
        # Initialize monitor service
        try:
            self.monitor_service.rule_loader.config_path = Path(self.config_file_var.get())
            self.monitor_service.initialize()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize monitor service: {str(e)}")
            return
    
    def create_control_panel(self, parent):
        """Create control panel"""
        control_frame = ttk.LabelFrame(parent, text="🎮 Control Panel", padding="10")
        control_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Button area
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        self.start_button = ttk.Button(button_frame, text="🚀 Start Monitoring", command=self.start_monitoring)
        self.start_button.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="⏹️ Stop", command=self.stop_monitoring, state='disabled')
        self.stop_button.grid(row=0, column=1, padx=(0, 10))
        
        self.simulate_button = ttk.Button(button_frame, text="🎭 Start Simulation", command=self.start_simulation)
        self.simulate_button.grid(row=0, column=2, padx=(0, 10))
        
        self.clear_button = ttk.Button(button_frame, text="🗑️ Clear Results", command=self.clear_results)
        self.clear_button.grid(row=0, column=3, padx=(0, 10))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(control_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        control_frame.columnconfigure(0, weight=1)
    
    def create_status_panel(self, parent):
        """Create status panel"""
        status_frame = ttk.LabelFrame(parent, text="📊 Monitor Status", padding="10")
        status_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        # Status information
        self.status_text = tk.StringVar(value="Waiting to start...")
        ttk.Label(status_frame, textvariable=self.status_text, font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W)
        
        # Statistics
        stats_frame = ttk.Frame(status_frame)
        stats_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Label(stats_frame, text="Records:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.records_var = tk.StringVar(value="0")
        ttk.Label(stats_frame, textvariable=self.records_var).grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        ttk.Label(stats_frame, text="Alarms:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.alarms_var = tk.StringVar(value="0")
        ttk.Label(stats_frame, textvariable=self.alarms_var).grid(row=0, column=3, sticky=tk.W, padx=(0, 20))
        
        ttk.Label(stats_frame, text="Processing Time:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.time_var = tk.StringVar(value="0.00s")
        ttk.Label(stats_frame, textvariable=self.time_var).grid(row=1, column=1, sticky=tk.W, padx=(0, 20), pady=(5, 0))
        
        ttk.Label(stats_frame, text="Processing Speed:").grid(row=1, column=2, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.speed_var = tk.StringVar(value="0 records/sec")
        ttk.Label(stats_frame, textvariable=self.speed_var).grid(row=1, column=3, sticky=tk.W, pady=(5, 0))
        
        status_frame.columnconfigure(0, weight=1)
    
    def create_alarm_table(self, parent):
        """Create alarm table"""
        alarm_frame = ttk.LabelFrame(parent, text="🚨 Alarm Events", padding="10")
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
        log_frame = ttk.LabelFrame(parent, text="📝 Log Output", padding="10")
        log_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        # Create text widget with scrollbar
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Configure main window grid weights
        parent.rowconfigure(2, weight=1)
        parent.rowconfigure(3, weight=1)
    
    def browse_dat_file(self):
        """Browse data file"""
        filename = filedialog.askopenfilename(
            title="Select Data File",
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
                    print(f"Auto inferred workstation ID: {workstation_id} (from filename: {path.stem})")
    
    def browse_config_file(self):
        """Browse config file"""
        filename = filedialog.askopenfilename(
            title="Select Config File",
            filetypes=[("YAML files", "*.yaml"), ("All files", "*.*")]
        )
        if filename:
            self.config_file_var.set(filename)
    
    def start_monitoring(self):
        """Start monitoring"""
        # Validate input
        dat_file = self.dat_file_var.get().strip()
        config_file = self.config_file_var.get().strip()
        run_id = self.run_id_var.get().strip()
        workstation_id = self.workstation_id_var.get().strip()
        
        if not dat_file or not config_file or not run_id or not workstation_id:
            messagebox.showerror("Error", "Please fill in all required fields")
            return
        
        # Check if file exists
        if not Path(dat_file).exists():
            messagebox.showerror("Error", f"Data file does not exist: {dat_file}")
            return
        
        if not Path(config_file).exists():
            messagebox.showerror("Error", f"Config file does not exist: {config_file}")
            return
        
        # Clear previous results
        self.clear_results()
        
        # Update interface status
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.status_text.set("Processing...")
        self.progress_var.set(0)
        
        # Record session start time
        self.session_start_time = datetime.now()
        self.session_total_records = 0
        self.session_total_alarms = 0
        
        # Process in background thread
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_worker,
            args=(dat_file, config_file, run_id)
        )
        self.monitoring_thread.daemon = True
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
        
        # Update interface status
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.status_text.set("Stopped")
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
        self.speed_var.set("0 records/sec")
        
        # Clear log
        self.log_text.delete(1.0, tk.END)
    
    def start_simulation(self):
        """Start simulated file push"""
        # Validate input
        dat_file = self.dat_file_var.get().strip()
        config_file = self.config_file_var.get().strip()
        run_id = self.run_id_var.get().strip()
        workstation_id = self.workstation_id_var.get().strip()
        
        if not dat_file or not config_file or not run_id or not workstation_id:
            messagebox.showerror("Error", "Please fill in all required fields")
            return
        
        # Check if file exists
        if not Path(dat_file).exists():
            messagebox.showerror("Error", f"Data file does not exist: {dat_file}")
            return
        
        if not Path(config_file).exists():
            messagebox.showerror("Error", f"Config file does not exist: {config_file}")
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
                self.status_text.set("Simulation monitoring running...")
                self.progress_var.set(0)
                
                # Show success message
                messagebox.showinfo("Success", f"Simulation started!\nWorkstation ID: {workstation_id}\nPush one record every 10 seconds")
            else:
                messagebox.showerror("Error", "Failed to start simulation")
                self.status_text.set("Simulation failed")
        
        except Exception as e:
            messagebox.showerror("Error", f"Simulation failed: {str(e)}")
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
            
            # Calculate processing time and speed
            processing_time = (end_time - start_time).total_seconds()
            speed = records_count / processing_time if processing_time > 0 else 0
            
            # Update statistics
            self.records_var.set(str(records_count))
            self.alarms_var.set(str(len(alarms)))
            self.time_var.set(f"{processing_time:.2f}s")
            self.speed_var.set(f"{speed:.2f} records/sec")
            
            # Update status
            self.status_text.set("Processing complete")
            self.progress_var.set(100)
            
            # Display completion message
            messagebox.showinfo("Success", f"Processing complete! {records_count} records processed, {len(alarms)} alarms generated.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Processing failed: {str(e)}")
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
            "high": "🔴",
            "critical": "💀"
        }
        
        icon = severity_icons.get(alarm.severity.value.lower(), "⚪")
        severity_display = f"{icon} {alarm.severity.value.upper()}"
        
        # Truncate sensor value display
        sensor_values_str = str(alarm.sensor_values)[:50]
        if len(str(alarm.sensor_values)) > 50:
            sensor_values_str += "..."
        
        self.alarm_tree.insert("", "end", values=(
            alarm.timestamp.strftime("%H:%M:%S"),
            severity_display,
            alarm.rule_name,
            alarm.description,
            sensor_values_str
        ))
    
    def process_messages(self):
        """Process log messages"""
        try:
            while True:
                msg = self.message_queue.get_nowait()
                self.log_text.insert(tk.END, msg + "\n")
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
                    self.speed_var.set(f"{speed:.2f} records/sec")
                else:
                    self.speed_var.set("0.00 records/sec")
            else:
                self.time_var.set("0.0s")
                self.speed_var.set("0.00 records/sec")
            
            # Update record count and alarm count
            self.records_var.set(str(self.session_total_records))
            self.alarms_var.set(str(self.session_total_alarms))
            
            # Update status text
            if status.get('file_provider'):
                fp_status = status['file_provider']
                if fp_status.get('total_records_pushed'):
                    self.status_text.set(f"Simulation running - {fp_status['total_records_pushed']} records pushed")
                else:
                    self.status_text.set("Simulation monitoring running...")
        
        # Update status every 1 second
        self.root.after(1000, self.update_status)
    
    def update_alarm_table_headers(self):
        """Update alarm table column headers"""
        if hasattr(self, 'alarm_tree'):
            # Set column headers
            headers = [
                "Time",
                "Severity", 
                "Rule",
                "Description",
                "Sensor Values"
            ]
            
            for i, header in enumerate(headers):
                self.alarm_tree.heading(self.alarm_columns[i], text=header)
                self.alarm_tree.column(self.alarm_columns[i], width=100)
    
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
                print(f"Deleted temp file: {temp_file}")
            
            # Clean up offset records
            offset_file = Path(".offsets.json")
            if offset_file.exists():
                try:
                    with open(offset_file, 'r', encoding='utf-8') as f:
                        offsets = json.load(f)
                    
                    # Delete offset record for temp file
                    temp_file_key = f"data/mpl{workstation_id}_temp.dat"
                    if temp_file_key in offsets:
                        del offsets[temp_file_key]
                        
                        # Save updated offsets
                        with open(offset_file, 'w', encoding='utf-8') as f:
                            json.dump(offsets, f, ensure_ascii=False, indent=2)
                        
                        print(f"Cleaned offset record: {temp_file_key}")
                except Exception as e:
                    print(f"Failed to cleanup offset records: {str(e)}")
        
        except Exception as e:
            print(f"Failed to cleanup temp files: {str(e)}")
    
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