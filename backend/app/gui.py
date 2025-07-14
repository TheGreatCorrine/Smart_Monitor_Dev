#!/usr/bin/env python3
"""
backend/app/gui.py
------------------------------------
图形用户界面 - 智能监测系统GUI版本
基于Tkinter，提供友好的图形界面
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import queue
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

from .usecases.Monitor import MonitorService
from .controllers.MonitorController import MonitorController


class SmartMonitorGUI:
    """智能监测系统GUI主类"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🔍 冰箱测试异常状态智能监测系统")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # 初始化组件
        self.monitor_service = MonitorService()
        self.monitor_controller = MonitorController(self.monitor_service)
        
        # 消息队列用于线程间通信
        self.message_queue = queue.Queue()
        
        # 设置日志
        self.setup_logging()
        
        # 创建界面
        self.create_widgets()
        
        # 启动消息处理
        self.process_messages()
    
    def setup_logging(self):
        """设置日志"""
        # 创建日志处理器
        self.log_handler = LogHandler(self.message_queue)
        logging.getLogger().addHandler(self.log_handler)
        logging.getLogger().setLevel(logging.INFO)
    
    def create_widgets(self):
        """创建界面组件"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # 1. 文件选择区域
        self.create_file_selector(main_frame)
        
        # 2. 控制按钮区域
        self.create_control_panel(main_frame)
        
        # 3. 监控状态区域
        self.create_status_panel(main_frame)
        
        # 4. 告警表格区域
        self.create_alarm_table(main_frame)
        
        # 5. 日志显示区域
        self.create_log_viewer(main_frame)
    
    def create_file_selector(self, parent):
        """创建文件选择器"""
        file_frame = ttk.LabelFrame(parent, text="📁 文件选择", padding="10")
        file_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 数据文件选择
        ttk.Label(file_frame, text="数据文件:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.dat_file_var = tk.StringVar()
        self.dat_entry = ttk.Entry(file_frame, textvariable=self.dat_file_var, width=50)
        self.dat_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(file_frame, text="浏览", command=self.browse_dat_file).grid(row=0, column=2)
        
        # 配置文件选择
        ttk.Label(file_frame, text="配置文件:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(10, 0))
        self.config_file_var = tk.StringVar(value="config/rules.yaml")
        self.config_entry = ttk.Entry(file_frame, textvariable=self.config_file_var, width=50)
        self.config_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 5), pady=(10, 0))
        ttk.Button(file_frame, text="浏览", command=self.browse_config_file).grid(row=1, column=2, pady=(10, 0))
        
        # 运行ID
        ttk.Label(file_frame, text="运行ID:").grid(row=2, column=0, sticky=tk.W, padx=(0, 5), pady=(10, 0))
        self.run_id_var = tk.StringVar()
        self.run_id_entry = ttk.Entry(file_frame, textvariable=self.run_id_var, width=50)
        self.run_id_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(0, 5), pady=(10, 0))
        
        file_frame.columnconfigure(1, weight=1)
    
    def create_control_panel(self, parent):
        """创建控制面板"""
        control_frame = ttk.LabelFrame(parent, text="🎮 控制面板", padding="10")
        control_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 按钮区域
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        self.start_button = ttk.Button(button_frame, text="🚀 开始监控", command=self.start_monitoring)
        self.start_button.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="⏹️ 停止", command=self.stop_monitoring, state='disabled')
        self.stop_button.grid(row=0, column=1, padx=(0, 10))
        
        self.clear_button = ttk.Button(button_frame, text="🗑️ 清空结果", command=self.clear_results)
        self.clear_button.grid(row=0, column=2, padx=(0, 10))
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(control_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        control_frame.columnconfigure(0, weight=1)
    
    def create_status_panel(self, parent):
        """创建状态面板"""
        status_frame = ttk.LabelFrame(parent, text="📊 监控状态", padding="10")
        status_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        # 状态信息
        self.status_text = tk.StringVar(value="等待开始...")
        ttk.Label(status_frame, textvariable=self.status_text, font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W)
        
        # 统计信息
        stats_frame = ttk.Frame(status_frame)
        stats_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Label(stats_frame, text="记录数:").grid(row=0, column=0, sticky=tk.W)
        self.records_var = tk.StringVar(value="0")
        ttk.Label(stats_frame, textvariable=self.records_var, font=('Arial', 9, 'bold')).grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        
        ttk.Label(stats_frame, text="告警数:").grid(row=1, column=0, sticky=tk.W)
        self.alarms_var = tk.StringVar(value="0")
        ttk.Label(stats_frame, textvariable=self.alarms_var, font=('Arial', 9, 'bold')).grid(row=1, column=1, sticky=tk.W, padx=(5, 0))
        
        ttk.Label(stats_frame, text="处理时间:").grid(row=2, column=0, sticky=tk.W)
        self.time_var = tk.StringVar(value="0.00s")
        ttk.Label(stats_frame, textvariable=self.time_var, font=('Arial', 9, 'bold')).grid(row=2, column=1, sticky=tk.W, padx=(5, 0))
        
        ttk.Label(stats_frame, text="处理速度:").grid(row=3, column=0, sticky=tk.W)
        self.speed_var = tk.StringVar(value="0 记录/秒")
        ttk.Label(stats_frame, textvariable=self.speed_var, font=('Arial', 9, 'bold')).grid(row=3, column=1, sticky=tk.W, padx=(5, 0))
        
        status_frame.columnconfigure(0, weight=1)
    
    def create_alarm_table(self, parent):
        """创建告警表格"""
        alarm_frame = ttk.LabelFrame(parent, text="🚨 告警事件", padding="10")
        alarm_frame.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        
        # 创建表格
        columns = ('时间', '严重程度', '规则', '描述', '传感器值')
        self.alarm_tree = ttk.Treeview(alarm_frame, columns=columns, show='headings', height=10)
        
        # 设置列标题
        for col in columns:
            self.alarm_tree.heading(col, text=col)
            self.alarm_tree.column(col, width=150)
        
        # 添加滚动条
        alarm_scrollbar = ttk.Scrollbar(alarm_frame, orient=tk.VERTICAL, command=self.alarm_tree.yview)
        self.alarm_tree.configure(yscrollcommand=alarm_scrollbar.set)
        
        self.alarm_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        alarm_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        alarm_frame.columnconfigure(0, weight=1)
        alarm_frame.rowconfigure(0, weight=1)
    
    def create_log_viewer(self, parent):
        """创建日志查看器"""
        log_frame = ttk.LabelFrame(parent, text="📝 日志输出", padding="10")
        log_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, font=('Consolas', 9))
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # 配置主窗口网格权重
        parent.rowconfigure(2, weight=1)
        parent.rowconfigure(3, weight=1)
    
    def browse_dat_file(self):
        """浏览数据文件"""
        filename = filedialog.askopenfilename(
            title="选择数据文件",
            filetypes=[("DAT files", "*.dat"), ("All files", "*.*")]
        )
        if filename:
            self.dat_file_var.set(filename)
            # 自动生成运行ID
            if not self.run_id_var.get():
                path = Path(filename)
                run_id = f"RUN_{path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                self.run_id_var.set(run_id)
    
    def browse_config_file(self):
        """浏览配置文件"""
        filename = filedialog.askopenfilename(
            title="选择配置文件",
            filetypes=[("YAML files", "*.yaml"), ("YML files", "*.yml"), ("All files", "*.*")]
        )
        if filename:
            self.config_file_var.set(filename)
    
    def start_monitoring(self):
        """开始监控"""
        # 验证输入
        dat_file = self.dat_file_var.get().strip()
        config_file = self.config_file_var.get().strip()
        run_id = self.run_id_var.get().strip()
        
        if not dat_file:
            messagebox.showerror("错误", "请选择数据文件")
            return
        
        if not config_file:
            messagebox.showerror("错误", "请选择配置文件")
            return
        
        if not run_id:
            messagebox.showerror("错误", "请输入运行ID")
            return
        
        # 检查文件是否存在
        if not Path(dat_file).exists():
            messagebox.showerror("错误", f"数据文件不存在: {dat_file}")
            return
        
        if not Path(config_file).exists():
            messagebox.showerror("错误", f"配置文件不存在: {config_file}")
            return
        
        # 清空之前的结果
        self.clear_results()
        
        # 更新界面状态
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.status_text.set("正在处理...")
        self.progress_var.set(0)
        
        # 在后台线程中处理
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_worker,
            args=(dat_file, config_file, run_id),
            daemon=True
        )
        self.monitoring_thread.start()
    
    def stop_monitoring(self):
        """停止监控"""
        self.status_text.set("已停止")
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.progress_var.set(0)
    
    def clear_results(self):
        """清空结果"""
        # 清空告警表格
        for item in self.alarm_tree.get_children():
            self.alarm_tree.delete(item)
        
        # 重置统计
        self.records_var.set("0")
        self.alarms_var.set("0")
        self.time_var.set("0.00s")
        self.speed_var.set("0 记录/秒")
        
        # 清空日志
        self.log_text.delete(1.0, tk.END)
    
    def _monitoring_worker(self, dat_file: str, config_file: str, run_id: str):
        """监控工作线程"""
        try:
            # 初始化监控服务
            self.monitor_service.rule_loader.config_path = Path(config_file)
            self.monitor_service.initialize()
            
            # 添加告警处理器
            self.monitor_service.add_alarm_handler(self._gui_alarm_handler)
            
            # 处理数据文件
            start_time = datetime.now()
            alarms, records_count = self.monitor_service.process_data_file(dat_file, run_id)
            end_time = datetime.now()
            
            processing_time = (end_time - start_time).total_seconds()
            speed = records_count / processing_time if processing_time > 0 else 0
            
            # 更新统计信息
            self.records_var.set(str(records_count))
            self.alarms_var.set(str(len(alarms)))
            self.time_var.set(f"{processing_time:.2f}s")
            self.speed_var.set(f"{speed:.0f} 记录/秒")
            
            # 更新状态
            self.status_text.set("处理完成")
            self.progress_var.set(100)
            
            # 显示完成消息
            messagebox.showinfo("完成", f"处理完成！\n记录数: {records_count}\n告警数: {len(alarms)}")
            
        except Exception as e:
            self.status_text.set(f"处理失败: {str(e)}")
            messagebox.showerror("错误", f"处理失败: {str(e)}")
        finally:
            # 恢复界面状态
            self.start_button.config(state='normal')
            self.stop_button.config(state='disabled')
    
    def _gui_alarm_handler(self, alarm):
        """GUI告警处理器"""
        # 在GUI线程中添加告警到表格
        self.root.after(0, self._add_alarm_to_table, alarm)
    
    def _add_alarm_to_table(self, alarm):
        """添加告警到表格"""
        severity_icons = {
            "low": "🔵",
            "medium": "🟡", 
            "high": "🟠",
            "critical": "🔴"
        }
        
        icon = severity_icons.get(alarm.severity.value, "⚪")
        severity_display = f"{icon} {alarm.severity.value.upper()}"
        
        # 截断传感器值显示
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
        """处理日志消息"""
        try:
            while True:
                message = self.message_queue.get_nowait()
                self.log_text.insert(tk.END, message + '\n')
                self.log_text.see(tk.END)
        except queue.Empty:
            pass
        
        # 每100ms检查一次消息
        self.root.after(100, self.process_messages)
    
    def run(self):
        """运行GUI应用"""
        self.root.mainloop()


class LogHandler(logging.Handler):
    """自定义日志处理器，将日志发送到GUI"""
    
    def __init__(self, message_queue):
        super().__init__()
        self.message_queue = message_queue
    
    def emit(self, record):
        """发送日志消息"""
        msg = self.format(record)
        self.message_queue.put(msg)


def main():
    """主函数"""
    app = SmartMonitorGUI()
    app.run()


if __name__ == "__main__":
    main() 