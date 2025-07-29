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

from .adapters.GUIAdapter import GUIAdapter
from .di.config import get_monitor_service, get_channel_service, create_file_provider
from .entities.AlarmEvent import AlarmEvent


class SmartMonitorGUI:
    """Smart Monitoring System GUI Main Class"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🔍 Smart Refrigerator Test Anomaly Monitoring System")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Initialize dependencies through DI container
        monitor_service = get_monitor_service()
        channel_service = get_channel_service()
        
        # Create GUI adapter
        self.adapter = GUIAdapter(monitor_service, channel_service)
        
        # FileProvider related
        self.file_provider: Optional[Any] = None
        self.monitoring_thread: Optional[threading.Thread] = None
        
        # Session statistics
        self.session_start_time: Optional[datetime] = None
        self.session_total_records = 0
        self.session_total_alarms = 0
        
        # Label matching related
        self.channel_labels = {}
        self.label_mode = False
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
            self.config = self.adapter.load_label_configuration()
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
        selected_labels = self.adapter.load_label_selection()
        
        if selected_labels is None:
            messagebox.showwarning("Warning", "No previous label selection record found, will select again.")
            self.label_choice_var.set("1")
            self.on_label_choice_change()
            return
        
        try:
            # Load channel labels
            for ch_id, label in selected_labels.items():
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
                
                # Save through adapter
                if not self.adapter.save_label_selection(selected_labels):
                    messagebox.showerror("Error", "Failed to save label selection")
                    return
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save label selection: {str(e)}")
                return
        
        # Go to second page
        self.show_page2()
    
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
            workstation_id = self.adapter.auto_infer_workstation_id(filename)
            if workstation_id:
                self.workstation_id_var.set(workstation_id)
                path = Path(filename)
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
        
        # Validate file path through adapter
        validation = self.adapter.validate_file_path(dat_file)
        if not validation['valid']:
            messagebox.showerror("Error", validation['error'])
            return
        
        validation = self.adapter.validate_file_path(config_file)
        if not validation['valid']:
            messagebox.showerror("Error", validation['error'])
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
        # Stop monitoring through adapter
        self.adapter.stop_monitoring()
        
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
        
        # Validate file path through adapter
        validation = self.adapter.validate_file_path(dat_file)
        if not validation['valid']:
            messagebox.showerror("Error", validation['error'])
            return
        
        validation = self.adapter.validate_file_path(config_file)
        if not validation['valid']:
            messagebox.showerror("Error", validation['error'])
            return
        
        try:
            # Create file provider
            self.file_provider = create_file_provider("simulated")
            
            # Start simulation through adapter
            result = self.adapter.start_simulation(dat_file, config_file, run_id, workstation_id, self.file_provider)
            
            if result['success']:
                # Update interface status
                self.start_button.config(state='disabled')
                self.stop_button.config(state='normal')
                self.status_text.set("Simulation monitoring running...")
                self.progress_var.set(0)
                
                # Show success message
                messagebox.showinfo("Success", f"Simulation started!\nWorkstation ID: {workstation_id}\nPush one record every 10 seconds")
            else:
                messagebox.showerror("Error", result['error'])
                self.status_text.set("Simulation failed")
        
        except Exception as e:
            messagebox.showerror("Error", f"Simulation failed: {str(e)}")
            self.status_text.set(f"Simulation failed: {str(e)}")
    
    def _monitoring_worker(self, dat_file: str, config_file: str, run_id: str):
        """Monitoring worker thread"""
        try:
            # Start monitoring through adapter
            result = self.adapter.start_monitoring(dat_file, config_file, run_id)
            
            if result['success']:
                # Update session statistics
                self.session_total_records = result['records_count']
                self.session_total_alarms = result['alarms_count']
                
                # Calculate processing time and speed
                if self.session_start_time:
                    processing_time = (datetime.now() - self.session_start_time).total_seconds()
                    speed = self.session_total_records / processing_time if processing_time > 0 else 0
                    
                    # Update statistics
                    self.records_var.set(str(self.session_total_records))
                    self.alarms_var.set(str(self.session_total_alarms))
                    self.time_var.set(f"{processing_time:.2f}s")
                    self.speed_var.set(f"{speed:.2f} records/sec")
                
                # Update status
                self.status_text.set("Processing complete")
                self.progress_var.set(100)
                
                # Display completion message
                messagebox.showinfo("Success", f"Processing complete! {self.session_total_records} records processed, {self.session_total_alarms} alarms generated.")
            else:
                messagebox.showerror("Error", result['error'])
                
        except Exception as e:
            messagebox.showerror("Error", f"Processing failed: {str(e)}")
        finally:
            # Restore interface status
            self.start_button.config(state='normal')
            self.stop_button.config(state='disabled')
    
    def _gui_alarm_handler(self, alarm: AlarmEvent):
        """GUI alarm handler"""
        # Add alarm to table in GUI thread
        self.root.after(0, self._add_alarm_to_table, alarm)
    
    def _add_alarm_to_table(self, alarm: AlarmEvent):
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
        # Get status through adapter
        status = self.adapter.get_monitoring_status()
        
        if status.get('is_monitoring'):
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