"""
web/app.py
------------------------------------
Smart Monitor Web Application
基于Flask的Web界面，复用现有Clean Architecture
"""
from flask import Flask, render_template, request, jsonify
import os
import sys
import traceback

# 添加backend路径到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# 导入Web适配器
from adapters.WebAdapter import WebAdapter
import uuid
import time
from datetime import datetime
import threading

app = Flask(__name__)

# 会话管理器 - 存储所有活动的监控会话
active_sessions = {}
session_counter = 0

# 初始化Web适配器
try:
    web_adapter = WebAdapter()
    print("✅ Web适配器初始化成功")
except Exception as e:
    print(f"❌ Web适配器初始化失败: {e}")
    web_adapter = None

def create_session_id():
    """创建唯一的会话ID"""
    global session_counter
    session_counter += 1
    return f"WS{session_counter:03d}"

def get_session_info(session_id):
    """获取会话信息"""
    if session_id in active_sessions:
        session = active_sessions[session_id]
        return {
            'id': session_id,
            'name': session['name'],
            'status': session['status'],
            'start_time': session['start_time'],
            'records_processed': session.get('records_processed', 0),
            'alarms_generated': session.get('alarms_generated', 0),
            'test_type': session.get('test_type', 'unknown'),
            'file_path': session.get('file_path'),
            'workstation_id': session.get('workstation_id')
        }
    return None

@app.route('/')
def index():
    """主页面 - 现代化仪表板"""
    return render_template('dashboard.html')

@app.route('/api/health')
def health_check():
    """健康检查API"""
    return jsonify({
        'status': 'ok',
        'message': 'Smart Monitor Web API is running',
        'version': '1.0.0',
        'web_adapter_ready': web_adapter is not None
    })

@app.route('/api/test')
def test_api():
    """测试API"""
    return jsonify({
        'status': 'success',
        'data': {
            'message': 'Flask integration successful',
            'timestamp': '2024-01-01T00:00:00Z',
            'web_adapter_ready': web_adapter is not None
        }
    })

# ==================== 会话管理API ====================

@app.route('/api/session/select-test', methods=['POST'])
def select_test_type():
    """选择测试类型"""
    if not web_adapter:
        return jsonify({'error': 'Web adapter not available'}), 500
    
    try:
        data = request.get_json()
        test_type = data.get('test_type')
        
        if not test_type or test_type not in ['old', 'new']:
            return jsonify({'error': 'Invalid test type'}), 400
        
        result = web_adapter.select_test_type(test_type)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/session/workstations', methods=['GET'])
def get_session_workstations():
    """获取工作台列表"""
    if not web_adapter:
        return jsonify({'error': 'Web adapter not available'}), 500
    
    try:
        result = web_adapter.get_workstations()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/session/select-workstation', methods=['POST'])
def select_workstation():
    """选择工作台"""
    if not web_adapter:
        return jsonify({'error': 'Web adapter not available'}), 500
    
    try:
        data = request.get_json()
        workstation_id = data.get('workstation_id')
        
        if not workstation_id:
            return jsonify({'error': 'Workstation ID is required'}), 400
        
        result = web_adapter.select_workstation(workstation_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/session/stop-workstation', methods=['POST'])
def stop_workstation():
    """停止工作台"""
    if not web_adapter:
        return jsonify({'error': 'Web adapter not available'}), 500
    
    try:
        data = request.get_json()
        workstation_id = data.get('workstation_id')
        
        if not workstation_id:
            return jsonify({'error': 'Workstation ID is required'}), 400
        
        result = web_adapter.stop_workstation(workstation_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/session/configure-new-test', methods=['POST'])
def configure_new_test_session():
    """配置New Test会话"""
    if not web_adapter:
        return jsonify({'error': 'Web adapter not available'}), 500
    
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        file_path = data.get('file_path')
        selected_labels = data.get('selected_labels', {})
        workstation_id = data.get('workstation_id', '1')
        
        if not session_id:
            return jsonify({'error': 'Session ID is required'}), 400
        if not file_path:
            return jsonify({'error': 'File path is required'}), 400
        
        result = web_adapter.configure_new_test_session(session_id, file_path, selected_labels, workstation_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/session/start-old-test', methods=['POST'])
def start_old_test_monitoring():
    """启动Old Test监控"""
    if not web_adapter:
        return jsonify({'error': 'Web adapter not available'}), 500
    
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({'error': 'Session ID is required'}), 400
        
        result = web_adapter.start_old_test_monitoring(session_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/session/start-new-test', methods=['POST'])
def start_new_test_monitoring():
    """启动New Test监控"""
    if not web_adapter:
        return jsonify({'error': 'Web adapter not available'}), 500
    
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({'error': 'Session ID is required'}), 400
        
        result = web_adapter.start_new_test_monitoring(session_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/session/stop-monitoring', methods=['POST'])
def stop_session_monitoring():
    """停止会话监控"""
    if not web_adapter:
        return jsonify({'error': 'Web adapter not available'}), 500
    
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({'error': 'Session ID is required'}), 400
        
        result = web_adapter.stop_session_monitoring(session_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/session/status', methods=['GET'])
def get_session_status():
    """获取会话状态"""
    if not web_adapter:
        return jsonify({'error': 'Web adapter not available'}), 500
    
    try:
        session_id = request.args.get('session_id')
        result = web_adapter.get_session_status(session_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/session/list', methods=['GET'])
def list_sessions():
    """列出所有会话"""
    if not web_adapter:
        return jsonify({'error': 'Web adapter not available'}), 500
    
    try:
        test_type = request.args.get('test_type')
        result = web_adapter.list_all_sessions(test_type)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/session/switch', methods=['POST'])
def switch_session():
    """切换到指定会话"""
    if not web_adapter:
        return jsonify({'error': 'Web adapter not available'}), 500
    
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({'error': 'Session ID is required'}), 400
        
        result = web_adapter.switch_to_session(session_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== 配置管理API ====================

@app.route('/api/config/labels', methods=['GET'])
def get_label_configuration():
    """获取标签配置"""
    if not web_adapter:
        return jsonify({'error': 'Web adapter not available'}), 500
    
    try:
        config = web_adapter.get_label_configuration()
        return jsonify(config)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/config/labels', methods=['POST'])
def save_label_selection():
    """保存标签选择"""
    if not web_adapter:
        return jsonify({'error': 'Web adapter not available'}), 500
    
    try:
        data = request.get_json()
        selected_labels = data.get('labels', {})
        
        result = web_adapter.save_label_selection(selected_labels)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/config/labels/load', methods=['GET'])
def load_label_selection():
    """加载标签选择"""
    if not web_adapter:
        return jsonify({'error': 'Web adapter not available'}), 500
    
    try:
        result = web_adapter.load_label_selection()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/config/labels/save', methods=['POST'])
def save_label_selection_save():
    """保存标签选择 (save端点)"""
    if not web_adapter:
        return jsonify({'error': 'Web adapter not available'}), 500
    
    try:
        data = request.get_json()
        selected_labels = data.get('selected_labels', {})
        
        result = web_adapter.save_label_selection(selected_labels)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/logs', methods=['GET'])
def get_logs():
    """获取系统日志"""
    if not web_adapter:
        return jsonify({'error': 'Web adapter not available'}), 500
    
    try:
        result = web_adapter.get_logs()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== 文件管理API ====================

@app.route('/api/file/upload', methods=['POST'])
def upload_file():
    """上传数据文件"""
    if not web_adapter:
        return jsonify({'error': 'Web adapter not available'}), 500
    
    try:
        from pathlib import Path
        import shutil
        
        # 检查是否有文件上传
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # 检查文件扩展名
        if not file.filename.lower().endswith('.dat'):
            return jsonify({'error': 'Only .dat files are allowed'}), 400
        
        # 获取项目根目录的data文件夹
        current_dir = Path(__file__).parent
        project_root = current_dir.parent
        data_dir = project_root / "data"
        
        # 确保data目录存在
        data_dir.mkdir(exist_ok=True)
        
        # 保存文件
        filename = file.filename
        file_path = data_dir / filename
        
        # 如果文件已存在，添加时间戳
        if file_path.exists():
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name, ext = filename.rsplit('.', 1)
            filename = f"{name}_{timestamp}.{ext}"
            file_path = data_dir / filename
        
        file.save(str(file_path))
        
        # 获取文件信息
        stat = file_path.stat()
        file_info = {
            'name': filename,
            'path': str(file_path),
            'size': stat.st_size,
            'size_mb': round(stat.st_size / (1024 * 1024), 2),
            'modified': stat.st_mtime
        }
        
        return jsonify({
            'success': True,
            'message': 'File uploaded successfully',
            'file_info': file_info
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/file/validate', methods=['POST'])
def validate_file():
    """验证文件路径"""
    if not web_adapter:
        return jsonify({'error': 'Web adapter not available'}), 500
    
    try:
        data = request.get_json()
        file_path = data.get('file_path', '')
        
        result = web_adapter.validate_file_path(file_path)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/file/infer-workstation', methods=['POST'])
def infer_workstation_id():
    """自动推断工作站ID"""
    if not web_adapter:
        return jsonify({'error': 'Web adapter not available'}), 500
    
    try:
        data = request.get_json()
        file_path = data.get('file_path', '')
        
        result = web_adapter.auto_infer_workstation_id(file_path)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== 监控管理API ====================

@app.route('/api/monitor/start', methods=['POST'])
def start_monitoring():
    """启动监控"""
    if not web_adapter:
        return jsonify({'error': 'Web adapter not available'}), 500
    
    try:
        data = request.get_json()
        file_path = data.get('file_path', '')
        config_path = data.get('config_path', 'config/rules.yaml')
        run_id = data.get('run_id')
        workstation_id = data.get('workstation_id')
        
        # 创建新的会话
        session_id = create_session_id()
        session_name = f"工作站 {session_id}"
        
        # 创建会话记录
        active_sessions[session_id] = {
            'name': session_name,
            'status': 'running',
            'start_time': datetime.now().isoformat(),
            'records_processed': 0,
            'alarms_generated': 0,
            'test_type': 'new' if file_path else 'old',
            'file_path': file_path,
            'workstation_id': workstation_id,
            'config_path': config_path,
            'run_id': run_id
        }
        
        # 调用后端启动监控
        result = web_adapter.start_monitoring(file_path, config_path, run_id)
        
        if result.get('success'):
            result['session_id'] = session_id
            result['session_name'] = session_name
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/monitor/simulation', methods=['POST'])
def start_simulation():
    """启动模拟"""
    if not web_adapter:
        return jsonify({'error': 'Web adapter not available'}), 500
    
    try:
        data = request.get_json()
        file_path = data.get('file_path', '')
        config_path = data.get('config_path', 'config/rules.yaml')
        run_id = data.get('run_id')
        workstation_id = data.get('workstation_id', '1')
        
        # 从文件名推断工作站ID
        if file_path:
            workstation_info = web_adapter.auto_infer_workstation_id(file_path)
            if workstation_info.get('success') and workstation_info.get('workstation_id'):
                workstation_id = workstation_info['workstation_id']
        
        # 创建新的会话
        session_id = create_session_id()
        session_name = f"工作站 {workstation_id}"
        
        # 创建会话记录
        active_sessions[session_id] = {
            'name': session_name,
            'status': 'running',
            'start_time': datetime.now().isoformat(),
            'records_processed': 0,
            'alarms_generated': 0,
            'test_type': 'simulation',
            'file_path': file_path,
            'workstation_id': workstation_id,
            'config_path': config_path,
            'run_id': run_id
        }
        
        # 调用后端启动模拟
        result = web_adapter.start_simulation(file_path, config_path, run_id, workstation_id)
        
        if result.get('success'):
            result['session_id'] = session_id
            result['session_name'] = session_name
            result['workstation_id'] = workstation_id
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/monitor/stop', methods=['POST'])
def stop_monitoring():
    """停止监控"""
    if not web_adapter:
        return jsonify({'error': 'Web adapter not available'}), 500
    
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if session_id and session_id in active_sessions:
            # 更新会话状态
            active_sessions[session_id]['status'] = 'stopped'
            
            # 调用后端停止监控
            result = web_adapter.stop_monitoring()
            
            # 从活动会话中移除
            del active_sessions[session_id]
            
            result['session_id'] = session_id
            return jsonify(result)
        else:
            # 如果没有指定session_id，停止所有监控
            result = web_adapter.stop_monitoring()
            
            # 清空所有会话
            active_sessions.clear()
            
            return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/monitor/status', methods=['GET'])
def get_monitoring_status():
    """获取监控状态"""
    if not web_adapter:
        return jsonify({'error': 'Web adapter not available'}), 500
    
    try:
        result = web_adapter.get_monitoring_status()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/monitor/workstations', methods=['GET'])
def get_workstations():
    """获取可用工作台列表"""
    if not web_adapter:
        return jsonify({'error': 'Web adapter not available'}), 500
    
    try:
        # 从活动会话中获取工作台数据
        workstations = []
        
        for session_id, session in active_sessions.items():
            if session['status'] == 'running':
                workstations.append({
                    'id': session_id,
                    'name': session['name'],
                    'status': session['status'],
                    'start_time': session['start_time'],
                    'records_processed': session.get('records_processed', 0),
                    'alarms_generated': session.get('alarms_generated', 0),
                    'test_type': session.get('test_type', 'unknown'),
                    'file_path': session.get('file_path'),
                    'workstation_id': session.get('workstation_id')
                })
        
        return jsonify({
            'success': True,
            'workstations': workstations
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== 文件管理增强API ====================

@app.route('/api/file/list', methods=['GET'])
def list_data_files():
    """列出可用的数据文件"""
    if not web_adapter:
        return jsonify({'error': 'Web adapter not available'}), 500
    
    try:
        import os
        from pathlib import Path
        
        # 修复路径问题：从web目录找到项目根目录的data文件夹
        current_dir = Path(__file__).parent  # web目录
        project_root = current_dir.parent     # 项目根目录
        data_dir = project_root / "data"     # data目录
        
        if not data_dir.exists():
            return jsonify({
                'success': True,
                'files': [],
                'message': f'Data directory not found at {data_dir}'
            })
        
        # 查找所有.dat文件
        dat_files = []
        for file_path in data_dir.glob("*.dat"):
            try:
                stat = file_path.stat()
                dat_files.append({
                    'name': file_path.name,
                    'path': str(file_path),
                    'size': stat.st_size,
                    'modified': stat.st_mtime,
                    'size_mb': round(stat.st_size / (1024 * 1024), 2)
                })
            except Exception as e:
                print(f"Error reading file {file_path}: {e}")
        
        # 按修改时间排序
        dat_files.sort(key=lambda x: x['modified'], reverse=True)
        
        return jsonify({
            'success': True,
            'files': dat_files,
            'total': len(dat_files)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/file/info/<path:filename>', methods=['GET'])
def get_file_info(filename):
    """获取文件详细信息"""
    if not web_adapter:
        return jsonify({'error': 'Web adapter not available'}), 500
    
    try:
        from pathlib import Path
        from datetime import datetime
        
        # 修复路径问题：从web目录找到项目根目录的data文件夹
        current_dir = Path(__file__).parent  # web目录
        project_root = current_dir.parent     # 项目根目录
        file_path = project_root / "data" / filename
        
        if not file_path.exists():
            return jsonify({'error': 'File not found'}), 404
        
        stat = file_path.stat()
        
        # 验证文件
        validation = web_adapter.validate_file_path(str(file_path))
        
        # 推断工作站ID
        workstation_info = web_adapter.auto_infer_workstation_id(str(file_path))
        
        return jsonify({
            'success': True,
            'file_info': {
                'name': file_path.name,
                'path': str(file_path),
                'size': stat.st_size,
                'size_mb': round(stat.st_size / (1024 * 1024), 2),
                'modified': stat.st_mtime,
                'modified_date': datetime.fromtimestamp(stat.st_mtime).isoformat()
            },
            'validation': validation,
            'workstation_info': workstation_info
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== 配置管理增强API ====================

@app.route('/api/config/rules', methods=['GET'])
def get_rules_config():
    """获取规则配置"""
    if not web_adapter:
        return jsonify({'error': 'Web adapter not available'}), 500
    
    try:
        import yaml
        from pathlib import Path
        
        config_path = Path("config/rules.yaml")
        if not config_path.exists():
            return jsonify({
                'success': False,
                'error': 'Rules configuration file not found'
            })
        
        with open(config_path, 'r', encoding='utf-8') as f:
            rules = yaml.safe_load(f)
        
        return jsonify({
            'success': True,
            'rules': rules
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/config/channels', methods=['GET'])
def get_channels_config():
    """获取通道配置"""
    if not web_adapter:
        return jsonify({'error': 'Web adapter not available'}), 500
    
    try:
        import yaml
        from pathlib import Path
        
        config_path = Path("config/channel_definitions.yaml")
        if not config_path.exists():
            return jsonify({
                'success': False,
                'error': 'Channel configuration file not found'
            })
        
        with open(config_path, 'r', encoding='utf-8') as f:
            channels = yaml.safe_load(f)
        
        return jsonify({
            'success': True,
            'channels': channels
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== 系统信息API ====================

@app.route('/api/system/info', methods=['GET'])
def get_system_info():
    """获取系统信息"""
    try:
        import platform
        import psutil
        from datetime import datetime
        from pathlib import Path
        
        # 基本系统信息
        system_info = {
            'platform': platform.system(),
            'platform_version': platform.version(),
            'python_version': platform.python_version(),
            'processor': platform.processor(),
            'machine': platform.machine()
        }
        
        # 内存信息
        memory = psutil.virtual_memory()
        memory_info = {
            'total': memory.total,
            'available': memory.available,
            'percent': memory.percent,
            'total_gb': round(memory.total / (1024**3), 2),
            'available_gb': round(memory.available / (1024**3), 2)
        }
        
        # 磁盘信息
        disk = psutil.disk_usage('/')
        disk_info = {
            'total': disk.total,
            'used': disk.used,
            'free': disk.free,
            'percent': disk.percent,
            'total_gb': round(disk.total / (1024**3), 2),
            'free_gb': round(disk.free / (1024**3), 2)
        }
        
        # 项目文件信息
        project_info = {
            'data_dir_exists': Path("data").exists(),
            'config_dir_exists': Path("config").exists(),
            'web_dir_exists': Path("web").exists(),
            'backend_dir_exists': Path("backend").exists()
        }
        
        return jsonify({
            'success': True,
            'system': system_info,
            'memory': memory_info,
            'disk': disk_info,
            'project': project_info,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/system/health', methods=['GET'])
def get_system_health():
    """获取系统健康状态"""
    try:
        import psutil
        
        # 检查关键进程
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                if 'python' in proc.info['name'].lower():
                    processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cpu_percent': proc.info['cpu_percent'],
                        'memory_percent': proc.info['memory_percent']
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # 检查端口占用
        ports = []
        try:
            import socket
            test_ports = [5000, 8000, 8080]
            for port in test_ports:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex(('localhost', port))
                sock.close()
                ports.append({
                    'port': port,
                    'in_use': result == 0
                })
        except Exception:
            pass
        
        return jsonify({
            'success': True,
            'health': {
                'python_processes': processes,
                'ports': ports,
                'web_adapter_ready': web_adapter is not None
            },
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== Web状态API ====================

@app.route('/api/web/status', methods=['GET'])
def get_web_status():
    """获取Web应用状态"""
    if not web_adapter:
        return jsonify({'error': 'Web adapter not available'}), 500
    
    try:
        result = web_adapter.get_web_status()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/web/reset', methods=['POST'])
def reset_web_session():
    """重置Web会话"""
    if not web_adapter:
        return jsonify({'error': 'Web adapter not available'}), 500
    
    try:
        result = web_adapter.reset_web_session()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== 配置状态验证API ====================

@app.route('/api/session/validate-configuration', methods=['GET'])
def validate_session_configuration():
    """验证会话配置状态"""
    if not web_adapter:
        return jsonify({'error': 'Web adapter not available'}), 500
    
    try:
        session_id = request.args.get('session_id')
        if not session_id:
            return jsonify({'error': 'Session ID is required'}), 400
        
        result = web_adapter.validate_configuration_status(session_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== 错误处理 ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'API endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("Starting Smart Monitor Web Application...")
    print("Access the application at: http://localhost:5001")
    print("Health check: http://localhost:5001/api/health")
    print("Web adapter status:", "✅ Ready" if web_adapter else "❌ Failed")
    # Change to project root directory
    import os
    project_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
    os.chdir(project_root)
    app.run(host='0.0.0.0', port=5002, debug=False) 