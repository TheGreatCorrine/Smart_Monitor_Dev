"""
web/app.py
------------------------------------
Smart Monitor Web Application
Flask-based Web interface, reusing existing Clean Architecture
"""
from flask import Flask, render_template, request, jsonify
import os
import sys
import traceback

# Add backend path to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import Web Adapter
from adapters.WebAdapter import WebAdapter
import uuid
import time
from datetime import datetime
import threading

app = Flask(__name__)

# Session Manager - Store all active monitoring sessions
active_sessions = {}
session_counter = 0

# Initialize Web Adapter
try:
    web_adapter = WebAdapter()
    print("✅ Web Adapter initialized successfully")
except Exception as e:
    print(f"❌ Web Adapter initialization failed: {e}")
    web_adapter = None

def create_session_id():
    """Create unique session ID"""
    global session_counter
    session_counter += 1
    return f"WS{session_counter:03d}"

def get_session_info(session_id):
    """Get session information"""
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
    """Main page - Modern dashboard"""
    return render_template('dashboard.html')

@app.route('/api/health')
def health_check():
    """Health check API"""
    return jsonify({
        'status': 'ok',
        'message': 'Smart Monitor Web API is running',
        'version': '1.0.0',
        'web_adapter_ready': web_adapter is not None
    })

@app.route('/api/test')
def test_api():
    """Test API"""
    return jsonify({
        'status': 'success',
        'data': {
            'message': 'Flask integration successful',
            'timestamp': '2024-01-01T00:00:00Z',
            'web_adapter_ready': web_adapter is not None
        }
    })

# ==================== Configuration Management API ====================

@app.route('/api/config/labels', methods=['GET'])
def get_label_configuration():
    """Get label configuration"""
    if not web_adapter:
        return jsonify({'error': 'Web adapter not available'}), 500
    
    try:
        config = web_adapter.get_label_configuration()
        return jsonify(config)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/config/labels', methods=['POST'])
def save_label_selection():
    """Save label selection"""
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
    """Load label selection"""
    if not web_adapter:
        return jsonify({'error': 'Web adapter not available'}), 500
    
    try:
        result = web_adapter.load_label_selection()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/config/labels/save', methods=['POST'])
def save_label_selection_save():
    """Save label selection (save endpoint)"""
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
    """Get system logs"""
    if not web_adapter:
        return jsonify({'error': 'Web adapter not available'}), 500
    
    try:
        result = web_adapter.get_logs()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== File Management API ====================

@app.route('/api/file/upload', methods=['POST'])
def upload_file():
    """Upload data file"""
    if not web_adapter:
        return jsonify({'error': 'Web adapter not available'}), 500
    
    try:
        from pathlib import Path
        import shutil
        
        # Check if a file is uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check file extension
        if not file.filename.lower().endswith('.dat'):
            return jsonify({'error': 'Only .dat files are allowed'}), 400
        
        # Get the data directory of the project root
        current_dir = Path(__file__).parent
        project_root = current_dir.parent
        data_dir = project_root / "data"
        
        # Ensure data directory exists
        data_dir.mkdir(exist_ok=True)
        
        # Save file
        filename = file.filename
        file_path = data_dir / filename
        
        # If file already exists, add timestamp
        if file_path.exists():
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name, ext = filename.rsplit('.', 1)
            filename = f"{name}_{timestamp}.{ext}"
            file_path = data_dir / filename
        
        file.save(str(file_path))
        
        # Get file information
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
    """Validate file path"""
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
    """Automatically infer workstation ID"""
    if not web_adapter:
        return jsonify({'error': 'Web adapter not available'}), 500
    
    try:
        data = request.get_json()
        file_path = data.get('file_path', '')
        
        result = web_adapter.auto_infer_workstation_id(file_path)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== Monitoring Management API ====================

@app.route('/api/monitor/start', methods=['POST'])
def start_monitoring():
    """Start monitoring"""
    if not web_adapter:
        return jsonify({'error': 'Web adapter not available'}), 500
    
    try:
        data = request.get_json()
        file_path = data.get('file_path', '')
        config_path = data.get('config_path', 'config/rules.yaml')
        run_id = data.get('run_id')
        workstation_id = data.get('workstation_id')
        
        # Create new session
        session_id = create_session_id()
        session_name = f"Workstation {session_id}"
        
        # Create session record
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
        
        # Call backend to start monitoring
        result = web_adapter.start_monitoring(file_path, config_path, run_id)
        
        if result.get('success'):
            result['session_id'] = session_id
            result['session_name'] = session_name
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/monitor/simulation', methods=['POST'])
def start_simulation():
    """Start simulation"""
    if not web_adapter:
        return jsonify({'error': 'Web adapter not available'}), 500
    
    try:
        data = request.get_json()
        file_path = data.get('file_path', '')
        config_path = data.get('config_path', 'config/rules.yaml')
        run_id = data.get('run_id')
        workstation_id = data.get('workstation_id', '1')
        
        # Infer workstation ID from filename
        if file_path:
            workstation_info = web_adapter.auto_infer_workstation_id(file_path)
            if workstation_info.get('success') and workstation_info.get('workstation_id'):
                workstation_id = workstation_info['workstation_id']
        
        # Create new session
        session_id = create_session_id()
        session_name = f"Workstation {workstation_id}"
        
        # Create session record
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
        
        # Call backend to start simulation
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
    """Stop monitoring"""
    if not web_adapter:
        return jsonify({'error': 'Web adapter not available'}), 500
    
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if session_id and session_id in active_sessions:
            # Update session status
            active_sessions[session_id]['status'] = 'stopped'
            
            # Call backend to stop monitoring
            result = web_adapter.stop_monitoring()
            
            # Remove from active sessions
            del active_sessions[session_id]
            
            result['session_id'] = session_id
            return jsonify(result)
        else:
            # If no session_id is specified, stop all monitoring
            result = web_adapter.stop_monitoring()
            
            # Clear all sessions
            active_sessions.clear()
            
            return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/monitor/status', methods=['GET'])
def get_monitoring_status():
    """Get monitoring status"""
    if not web_adapter:
        return jsonify({'error': 'Web adapter not available'}), 500
    
    try:
        result = web_adapter.get_monitoring_status()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/monitor/workstations', methods=['GET'])
def get_workstations():
    """Get available workstation list"""
    if not web_adapter:
        return jsonify({'error': 'Web adapter not available'}), 500
    
    try:
        # Get workstation data from active sessions
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

# ==================== File Management Enhanced API ====================

@app.route('/api/file/list', methods=['GET'])
def list_data_files():
    """List available data files"""
    if not web_adapter:
        return jsonify({'error': 'Web adapter not available'}), 500
    
    try:
        import os
        from pathlib import Path
        
        # Fix path issue: find the project root's data directory from the web directory
        current_dir = Path(__file__).parent  # web directory
        project_root = current_dir.parent     # project root directory
        data_dir = project_root / "data"     # data directory
        
        if not data_dir.exists():
            return jsonify({
                'success': True,
                'files': [],
                'message': f'Data directory not found at {data_dir}'
            })
        
        # Find all .dat files
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
        
        # Sort by modification time
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
    """Get detailed file information"""
    if not web_adapter:
        return jsonify({'error': 'Web adapter not available'}), 500
    
    try:
        from pathlib import Path
        from datetime import datetime
        
        # Fix path issue: find the project root's data directory from the web directory
        current_dir = Path(__file__).parent  # web directory
        project_root = current_dir.parent     # project root directory
        file_path = project_root / "data" / filename
        
        if not file_path.exists():
            return jsonify({'error': 'File not found'}), 404
        
        stat = file_path.stat()
        
        # Validate file
        validation = web_adapter.validate_file_path(str(file_path))
        
        # Infer workstation ID
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

# ==================== Configuration Management Enhanced API ====================

@app.route('/api/config/rules', methods=['GET'])
def get_rules_config():
    """Get rule configuration"""
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
    """Get channel configuration"""
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

# ==================== System Information API ====================

@app.route('/api/system/info', methods=['GET'])
def get_system_info():
    """Get system information"""
    try:
        import platform
        import psutil
        from datetime import datetime
        from pathlib import Path
        
        # Basic system information
        system_info = {
            'platform': platform.system(),
            'platform_version': platform.version(),
            'python_version': platform.python_version(),
            'processor': platform.processor(),
            'machine': platform.machine()
        }
        
        # Memory information
        memory = psutil.virtual_memory()
        memory_info = {
            'total': memory.total,
            'available': memory.available,
            'percent': memory.percent,
            'total_gb': round(memory.total / (1024**3), 2),
            'available_gb': round(memory.available / (1024**3), 2)
        }
        
        # Disk information
        disk = psutil.disk_usage('/')
        disk_info = {
            'total': disk.total,
            'used': disk.used,
            'free': disk.free,
            'percent': disk.percent,
            'total_gb': round(disk.total / (1024**3), 2),
            'free_gb': round(disk.free / (1024**3), 2)
        }
        
        # Project file information
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
    """Get system health status"""
    try:
        import psutil
        
        # Check critical processes
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
        
        # Check port usage
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

# ==================== Web Status API ====================

@app.route('/api/web/status', methods=['GET'])
def get_web_status():
    """Get Web application status"""
    if not web_adapter:
        return jsonify({'error': 'Web adapter not available'}), 500
    
    try:
        result = web_adapter.get_web_status()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/web/reset', methods=['POST'])
def reset_web_session():
    """Reset Web session"""
    if not web_adapter:
        return jsonify({'error': 'Web adapter not available'}), 500
    
    try:
        result = web_adapter.reset_web_session()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== Error Handling ====================

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