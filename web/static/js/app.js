/**
 * Smart Monitor Web - 主应用JavaScript
 * 使用原生JavaScript，无框架依赖
 * 仿照GUI的两页设计
 */

class SmartMonitorApp {
    constructor() {
        this.currentPage = 'page1';
        this.refreshInterval = null;
        this.selectedFile = null;
        this.selectedLabels = {};
        this.alarms = [];
        this.logs = [];
        this.init();
    }

    init() {
        this.setupNavigation();
        this.loadPage1();
        this.startAutoRefresh();
        this.setupFileUpload();
    }

    // ==================== 导航管理 ====================
    setupNavigation() {
        const navItems = document.querySelectorAll('.nav-item');
        navItems.forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const page = item.dataset.page;
                this.navigateTo(page);
            });
        });
    }

    navigateTo(page) {
        // 如果离开页面2，停止自动刷新
        if (this.currentPage === 'page2' && page !== 'page2') {
            this.stopAutoRefresh();
        }
        
        // 更新导航状态
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-page="${page}"]`).classList.add('active');

        // 隐藏所有页面
        document.querySelectorAll('.page').forEach(pageElement => {
            pageElement.classList.remove('active');
            pageElement.classList.add('hidden');
        });

        // 显示目标页面
        const targetPage = document.getElementById(page);
        if (targetPage) {
            targetPage.classList.remove('hidden');
            targetPage.classList.add('active');
        }

        // 加载页面内容
        this.currentPage = page;
        this.loadPage(page);
    }

    loadPage(page) {
        switch (page) {
            case 'page1':
                this.loadPage1();
                break;
            case 'page2':
                this.loadPage2();
                break;
            case 'config':
                this.loadConfig();
                break;
            case 'system':
                this.loadSystem();
                break;
        }
    }

    // ==================== 页面1: 文件选择和标签匹配 ====================
    async loadPage1() {
        await this.loadFileList();
        await this.loadLabelConfiguration();
    }

    async loadFileList() {
        try {
            const data = await this.fetchAPI('/api/file/list');
            this.updateFileSelector(data);
        } catch (error) {
            console.error('Failed to load file list:', error);
            this.showError('加载文件列表失败');
        }
    }

    updateFileSelector(data) {
        const fileSelector = document.getElementById('file-selector');
        
        if (data.success && data.files) {
            fileSelector.innerHTML = '<option value="">请选择数据文件...</option>';
            
            data.files.forEach(file => {
                const option = document.createElement('option');
                option.value = file.path;
                option.textContent = `${file.name} (${file.size_mb} MB)`;
                fileSelector.appendChild(option);
            });

            // 添加文件选择事件
            fileSelector.addEventListener('change', (e) => {
                this.onFileSelected(e.target.value);
            });
        } else {
            fileSelector.innerHTML = '<option value="">没有找到数据文件</option>';
        }
    }

    async onFileSelected(filePath) {
        if (!filePath) {
            this.updateFileInfo('请选择数据文件以查看详细信息');
            return;
        }

        this.selectedFile = filePath;
        
        // 更新状态指示器为加载中
        const statusIndicator = document.querySelector('.label-selection-container .status-indicator');
        if (statusIndicator) {
            statusIndicator.className = 'status-indicator status-info';
            statusIndicator.textContent = '正在加载标签配置...';
        }
        
        try {
            // 获取文件信息
            const fileInfo = await this.fetchAPI(`/api/file/info/${filePath.split('/').pop()}`);
            this.updateFileInfo(fileInfo);
            
            // 自动推断工作站ID
            const workstationInfo = await this.fetchAPI('/api/file/infer-workstation', {
                method: 'POST',
                body: JSON.stringify({ file_path: filePath })
            });
            
            if (workstationInfo.success && workstationInfo.workstation_id) {
                this.showSuccess(`自动推断工作站ID: ${workstationInfo.workstation_id}`);
            }
            
            // 加载标签配置
            await this.loadLabelConfiguration();
            
        } catch (error) {
            console.error('Failed to get file info:', error);
            this.showError('获取文件信息失败');
            
            // 更新状态指示器为错误
            if (statusIndicator) {
                statusIndicator.className = 'status-indicator status-error';
                statusIndicator.textContent = '文件信息获取失败';
            }
        }
    }

    updateFileInfo(data) {
        const fileInfo = document.getElementById('file-info');
        
        if (data.success && data.file_info) {
            const info = data.file_info;
            fileInfo.innerHTML = `
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <p><strong>文件名:</strong> ${info.name}</p>
                        <p><strong>文件大小:</strong> ${info.size_mb} MB</p>
                        <p><strong>修改时间:</strong> ${new Date(info.modified * 1000).toLocaleString()}</p>
                    </div>
                    <div>
                        <p><strong>验证状态:</strong> <span class="status-indicator status-success">有效</span></p>
                        <p><strong>工作站ID:</strong> ${info.workstation_id || '自动推断'}</p>
                    </div>
                </div>
            `;
        } else {
            fileInfo.innerHTML = '<p class="text-error">无法获取文件信息</p>';
        }
    }

    async loadLabelConfiguration() {
        try {
            const data = await this.fetchAPI('/api/config/labels');
            this.updateLabelSelection(data);
        } catch (error) {
            console.error('Failed to load label configuration:', error);
            this.showError('加载标签配置失败');
        }
    }

    updateLabelSelection(data) {
        const labelSelection = document.getElementById('label-selection');
        const statusIndicator = document.querySelector('.label-selection-container .status-indicator');
        
        if (data.categories && Object.keys(data.categories).length > 0) {
            // 更新状态指示器
            if (statusIndicator) {
                statusIndicator.className = 'status-indicator status-success';
                statusIndicator.textContent = '标签配置已加载';
            }
            
            let html = '<div class="grid grid-cols-1 gap-4">';
            
            // 定义优先级顺序
            const priorityOrder = ['environment_temp', 'total_power'];
            
            // 将类别分为优先级和非优先级
            const priorityCategories = [];
            const otherCategories = [];
            
            Object.entries(data.categories).forEach(([categoryKey, category]) => {
                if (priorityOrder.includes(categoryKey)) {
                    priorityCategories.push([categoryKey, category]);
                } else {
                    otherCategories.push([categoryKey, category]);
                }
            });
            
            // 按字母顺序排序非优先级类别
            otherCategories.sort((a, b) => a[0].localeCompare(b[0]));
            
            // 合并所有类别：优先级在前，其他在后
            const sortedCategories = [...priorityCategories, ...otherCategories];
            
            sortedCategories.forEach(([categoryKey, category]) => {
                // 获取英文名称和描述
                const categoryName = category.category_name?.en || categoryKey;
                const categoryDescription = category.category_description?.en || '';
                
                html += `
                    <div class="label-category">
                        <h4 class="font-semibold mb-2">${categoryName}</h4>
                        <p class="text-sm text-secondary mb-3">${categoryDescription}</p>
                        <div class="label-options">
                `;
                
                if (category.channels) {
                    category.channels.forEach(channel => {
                        html += `
                            <div class="label-channel mb-3">
                                <h5 class="font-medium mb-2">${channel.channel_id}</h5>
                                <div class="label-radio-group">
                        `;
                        
                        if (channel.available_subtypes) {
                            channel.available_subtypes.forEach(subtype => {
                                const isDefault = subtype.is_default ? ' (默认)' : '';
                                html += `
                                    <label class="label-radio">
                                        <input type="radio" name="label_${channel.channel_id}" 
                                               value="${subtype.subtype_id}" 
                                               ${subtype.is_default ? 'checked' : ''}>
                                        <span>${subtype.label}${isDefault}</span>
                                    </label>
                                `;
                            });
                        }
                        
                        html += `
                                </div>
                            </div>
                        `;
                    });
                }
                
                html += `
                        </div>
                    </div>
                `;
            });
            
            html += '</div>';
            labelSelection.innerHTML = html;
            
            // 添加标签选择事件
            this.setupLabelSelectionEvents();
        } else {
            // 更新状态指示器
            if (statusIndicator) {
                statusIndicator.className = 'status-indicator status-error';
                statusIndicator.textContent = '标签配置加载失败';
            }
            labelSelection.innerHTML = '<p class="text-error">无法加载标签配置</p>';
        }
    }

    setupLabelSelectionEvents() {
        const radioButtons = document.querySelectorAll('input[type="radio"]');
        radioButtons.forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.onLabelChoiceChange(e);
            });
        });
    }

    onLabelChoiceChange(event) {
        const channelId = event.target.name.replace('label_', '');
        const subtypeId = event.target.value;
        
        this.selectedLabels[channelId] = subtypeId;
        console.log('Label selection updated:', this.selectedLabels);
    }

    async confirmAndGoToPage2() {
        if (!this.selectedFile) {
            this.showError('请先选择数据文件');
            return;
        }

        if (Object.keys(this.selectedLabels).length === 0) {
            this.showError('请配置标签匹配');
            return;
        }

        try {
            // 保存标签选择
            const saveResult = await this.fetchAPI('/api/config/labels/save', {
                method: 'POST',
                body: JSON.stringify({ selected_labels: this.selectedLabels })
            });

            if (saveResult.success) {
                this.showSuccess('配置已保存');
                this.navigateTo('page2');
            } else {
                this.showError('保存配置失败');
            }
        } catch (error) {
            console.error('Failed to save configuration:', error);
            this.showError('保存配置时发生错误');
        }
    }

    async loadLastLabelSelection() {
        try {
            const data = await this.fetchAPI('/api/config/labels/load');
            if (data.success && data.labels) {
                this.selectedLabels = data.labels;
                this.showSuccess('已加载上次配置');
                this.updateLabelSelectionFromSaved();
            } else {
                this.showError('没有找到保存的配置');
            }
        } catch (error) {
            console.error('Failed to load last selection:', error);
            this.showError('加载上次配置失败');
        }
    }

    updateLabelSelectionFromSaved() {
        Object.entries(this.selectedLabels).forEach(([channelId, subtypeId]) => {
            const radio = document.querySelector(`input[name="label_${channelId}"][value="${subtypeId}"]`);
            if (radio) {
                radio.checked = true;
            }
        });
    }

    // ==================== 页面2: 控制面板和监控状态 ====================
    async loadPage2() {
        await this.loadMonitoringStatus();
        await this.loadSessionStats();
        
        // 启动自动刷新
        this.startAutoRefresh();
    }

    async loadMonitoringStatus() {
        try {
            const data = await this.fetchAPI('/api/monitor/status');
            this.updateMonitoringStatus(data);
        } catch (error) {
            console.error('Failed to load monitoring status:', error);
        }
    }

    updateMonitoringStatus(data) {
        const statusElement = document.getElementById('monitoring-status');
        const detailsElement = document.getElementById('monitoring-details');

        if (data.success && data.status) {
            const status = data.status;
            const isMonitoring = status.is_monitoring || status.web_monitoring_active;
            const fileProvider = status.file_provider || {};

            if (isMonitoring) {
                statusElement.className = 'status-indicator status-success';
                statusElement.textContent = '运行中';
                
                let detailsHtml = '';
                
                if (status.web_session_id) {
                    detailsHtml += `<p><strong>会话ID:</strong> ${status.web_session_id}</p>`;
                }
                
                if (status.web_current_file) {
                    detailsHtml += `<p><strong>当前文件:</strong> ${status.web_current_file}</p>`;
                }
                
                if (fileProvider.total_records_pushed !== undefined) {
                    detailsHtml += `<p><strong>推送记录:</strong> ${fileProvider.total_records_pushed}</p>`;
                }
                
                if (status.stats && status.stats.total_records_processed !== undefined) {
                    detailsHtml += `<p><strong>处理记录:</strong> ${status.stats.total_records_processed}</p>`;
                }
                
                if (status.stats && status.stats.total_alarms_generated !== undefined) {
                    detailsHtml += `<p><strong>生成告警:</strong> ${status.stats.total_alarms_generated}</p>`;
                }
                
                if (fileProvider.simulation_duration !== undefined) {
                    detailsHtml += `<p><strong>模拟时长:</strong> ${fileProvider.simulation_duration.toFixed(1)}秒</p>`;
                }
                
                detailsElement.innerHTML = detailsHtml;
            } else {
                statusElement.className = 'status-indicator status-warning';
                statusElement.textContent = '已停止';
                detailsElement.innerHTML = '<p>监控已停止</p>';
            }
        } else {
            statusElement.className = 'status-indicator status-error';
            statusElement.textContent = '错误';
            detailsElement.innerHTML = '<p>无法获取监控状态</p>';
        }
    }

    async loadSessionStats() {
        try {
            const data = await this.fetchAPI('/api/monitor/status');
            this.updateSessionStats(data);
        } catch (error) {
            console.error('Failed to load session stats:', error);
        }
    }

    updateSessionStats(data) {
        const sessionStart = document.getElementById('session-start');
        const totalRecords = document.getElementById('total-records');
        const totalAlarms = document.getElementById('total-alarms');
        const processingSpeed = document.getElementById('processing-speed');
        
        if (data.success && data.status) {
            const status = data.status;
            const stats = status.stats || {};
            const fileProvider = status.file_provider || {};
            
            // 更新处理记录数
            const recordsProcessed = stats.total_records_processed || 0;
            totalRecords.textContent = recordsProcessed;
            
            // 更新告警数量
            const alarmsGenerated = stats.total_alarms_generated || 0;
            totalAlarms.textContent = alarmsGenerated;
            
            // 更新开始时间
            if (fileProvider.start_time) {
                const startTime = new Date(fileProvider.start_time);
                sessionStart.textContent = startTime.toLocaleString();
            } else {
                sessionStart.textContent = '-';
            }
            
            // 计算处理速度
            if (fileProvider.start_time && recordsProcessed > 0) {
                const startTime = new Date(fileProvider.start_time);
                const now = new Date();
                const elapsedSeconds = (now - startTime) / 1000;
                
                if (elapsedSeconds > 0) {
                    const speed = recordsProcessed / elapsedSeconds;
                    processingSpeed.textContent = speed.toFixed(2);
                } else {
                    processingSpeed.textContent = '0.00';
                }
            } else {
                processingSpeed.textContent = '0.00';
            }
        } else {
            sessionStart.textContent = '-';
            totalRecords.textContent = '0';
            totalAlarms.textContent = '0';
            processingSpeed.textContent = '0.00';
        }
    }

    // ==================== 监控控制 ====================
    async startMonitoring() {
        console.log('startMonitoring called');
        console.log('selectedFile:', this.selectedFile);
        
        const configFile = document.getElementById('config-selector')?.value;
        const runId = document.getElementById('run-id')?.value || undefined;

        if (!this.selectedFile) {
            this.showError('请先选择数据文件');
            return;
        }

        try {
            console.log('Sending monitoring start request...');
            const data = await this.fetchAPI('/api/monitor/start', {
                method: 'POST',
                body: JSON.stringify({
                    file_path: this.selectedFile,
                    config_path: configFile,
                    run_id: runId
                })
            });

            console.log('Monitoring start response:', data);

            if (data.success) {
                this.showSuccess('监控启动成功');
                this.loadMonitoringStatus();
            } else {
                this.showError(data.error || '监控启动失败');
            }
        } catch (error) {
            console.error('Monitoring start error:', error);
            this.showError('启动监控时发生错误');
        }
    }

    async stopMonitoring() {
        console.log('stopMonitoring called');
        try {
            const data = await this.fetchAPI('/api/monitor/stop', {
                method: 'POST'
            });

            console.log('Monitoring stop response:', data);

            if (data.success) {
                this.showSuccess('监控已停止');
                this.loadMonitoringStatus();
            } else {
                this.showError(data.error || '停止监控失败');
            }
        } catch (error) {
            console.error('Monitoring stop error:', error);
            this.showError('停止监控时发生错误');
        }
    }

    async startSimulation() {
        console.log('startSimulation called');
        console.log('selectedFile:', this.selectedFile);
        
        if (!this.selectedFile) {
            this.showError('请先选择数据文件');
            return;
        }

        try {
            console.log('Sending simulation start request...');
            const data = await this.fetchAPI('/api/monitor/simulation', {
                method: 'POST',
                body: JSON.stringify({
                    file_path: this.selectedFile,
                    workstation_id: '1'
                })
            });

            console.log('Simulation start response:', data);

            if (data.success) {
                this.showSuccess('模拟启动成功');
                this.loadMonitoringStatus();
            } else {
                this.showError(data.error || '模拟启动失败');
            }
        } catch (error) {
            console.error('Simulation start error:', error);
            this.showError('启动模拟时发生错误');
        }
    }

    // ==================== 告警和日志管理 ====================
    clearAlarms() {
        this.alarms = [];
        this.updateAlarmTable();
        this.showSuccess('告警记录已清空');
    }

    clearLogs() {
        this.logs = [];
        this.updateLogViewer();
        this.showSuccess('日志已清空');
    }

    updateAlarmTable() {
        const tbody = document.getElementById('alarm-tbody');
        
        if (this.alarms.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center">暂无告警记录</td></tr>';
            return;
        }

        tbody.innerHTML = this.alarms.map(alarm => `
            <tr>
                <td>${new Date(alarm.timestamp).toLocaleString()}</td>
                <td>${alarm.workstation_id}</td>
                <td>${alarm.channel_name}</td>
                <td>${alarm.value}</td>
                <td>${alarm.threshold}</td>
                <td>${alarm.rule_name}</td>
            </tr>
        `).join('');
    }

    updateLogViewer() {
        fetch('/api/logs')
            .then(response => response.json())
            .then(data => {
                if (data.success && data.logs) {
                    const logContainer = document.getElementById('log-viewer');
                    if (logContainer) {
                        // 清空现有日志
                        logContainer.innerHTML = '';
                        
                        // 添加新的日志条目
                        data.logs.forEach(log => {
                            const logEntry = document.createElement('div');
                            logEntry.className = 'log-entry';
                            logEntry.textContent = log;
                            logContainer.appendChild(logEntry);
                        });
                        
                        // 滚动到底部
                        logContainer.scrollTop = logContainer.scrollHeight;
                    }
                }
            })
            .catch(error => {
                console.error('Failed to load logs:', error);
            });
    }

    addAlarm(alarm) {
        this.alarms.push(alarm);
        this.updateAlarmTable();
    }

    addLog(message) {
        this.logs.push({
            timestamp: new Date(),
            level: 'INFO',
            message: message
        });
        this.updateLogViewer();
    }

    // ==================== 其他页面 ====================
    async loadConfig() {
        const configContent = document.getElementById('config-content');
        configContent.innerHTML = '<p>配置管理功能开发中...</p>';
    }

    async loadSystem() {
        try {
            const [systemInfo, healthCheck] = await Promise.all([
                this.fetchAPI('/api/system/info'),
                this.fetchAPI('/api/system/health')
            ]);

            this.updateSystemInfo(systemInfo);
            this.updateHealthCheck(healthCheck);
        } catch (error) {
            console.error('Failed to load system info:', error);
        }
    }

    updateSystemInfo(data) {
        const systemInfo = document.getElementById('system-info');
        
        if (data.success) {
            const system = data.system;
            const memory = data.memory;
            
            systemInfo.innerHTML = `
                <p><strong>平台:</strong> ${system.platform}</p>
                <p><strong>内存:</strong> ${memory.available_gb}GB / ${memory.total_gb}GB</p>
                <p><strong>使用率:</strong> ${memory.percent}%</p>
            `;
        } else {
            systemInfo.innerHTML = '<p class="text-error">无法获取系统信息</p>';
        }
    }

    updateHealthCheck(data) {
        const healthCheck = document.getElementById('health-check');
        
        if (data.success) {
            const health = data.health;
            healthCheck.innerHTML = `
                <p><strong>Python进程:</strong> ${health.python_processes?.length || 0} 个</p>
                <p><strong>端口使用:</strong> ${health.port_usage?.length || 0} 个</p>
            `;
        } else {
            healthCheck.innerHTML = '<p class="text-error">无法获取健康检查信息</p>';
        }
    }

    // ==================== 文件上传功能 ====================
    setupFileUpload() {
        const uploadArea = document.getElementById('upload-area');
        const fileUpload = document.getElementById('file-upload');
        
        if (!uploadArea || !fileUpload) return;
        
        // 文件选择事件
        fileUpload.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.uploadFile(e.target.files[0]);
            }
        });
        
        // 拖拽上传事件
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        
        uploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            
            if (e.dataTransfer.files.length > 0) {
                this.uploadFile(e.dataTransfer.files[0]);
            }
        });
        
        // 点击上传区域触发文件选择
        uploadArea.addEventListener('click', () => {
            fileUpload.click();
        });
    }

    async uploadFile(file) {
        // 验证文件类型
        if (!file.name.toLowerCase().endsWith('.dat')) {
            this.showError('只支持 .dat 文件');
            return;
        }
        
        // 显示上传进度
        this.showUploadProgress();
        
        try {
            const formData = new FormData();
            formData.append('file', file);
            
            const response = await fetch('/api/file/upload', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showSuccess('文件上传成功');
                this.hideUploadProgress();
                
                // 刷新文件列表
                await this.loadFileList();
                
                // 自动选择上传的文件
                const fileSelector = document.getElementById('file-selector');
                if (fileSelector) {
                    fileSelector.value = result.file_info.path;
                    this.onFileSelected(result.file_info.path);
                }
            } else {
                this.showError(result.error || '文件上传失败');
                this.hideUploadProgress();
            }
        } catch (error) {
            console.error('Upload failed:', error);
            this.showError('文件上传时发生错误');
            this.hideUploadProgress();
        }
    }

    showUploadProgress() {
        const progress = document.getElementById('upload-progress');
        const progressFill = document.getElementById('progress-fill');
        const progressText = document.getElementById('progress-text');
        
        if (progress) {
            progress.classList.remove('hidden');
            progressFill.style.width = '0%';
            progressText.textContent = '准备上传...';
            
            // 模拟上传进度
            let progressValue = 0;
            const interval = setInterval(() => {
                progressValue += Math.random() * 15;
                if (progressValue > 90) {
                    progressValue = 90;
                    clearInterval(interval);
                }
                progressFill.style.width = progressValue + '%';
                progressText.textContent = `上传中... ${Math.round(progressValue)}%`;
            }, 100);
        }
    }

    hideUploadProgress() {
        const progress = document.getElementById('upload-progress');
        const progressFill = document.getElementById('progress-fill');
        const progressText = document.getElementById('progress-text');
        
        if (progress) {
            progressFill.style.width = '100%';
            progressText.textContent = '上传完成';
            
            setTimeout(() => {
                progress.classList.add('hidden');
            }, 1000);
        }
    }

    // ==================== 工具方法 ====================
    async fetchAPI(endpoint, options = {}) {
        try {
            const response = await fetch(endpoint, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error(`API call failed for ${endpoint}:`, error);
            throw error;
        }
    }

    refreshFileList() {
        this.loadFileList();
        this.showSuccess('文件列表已刷新');
    }

    startAutoRefresh() {
        // 清除之前的定时器
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
        
        // 每2秒自动刷新一次
        this.refreshInterval = setInterval(() => {
            if (this.currentPage === 'page2') {
                this.loadMonitoringStatus();
                this.loadSessionStats();
                this.updateAlarmTable();
                this.updateLogViewer();
            }
        }, 2000);
    }

    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showNotification(message, type = 'info') {
        const container = document.getElementById('notification-container');
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        container.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
}

// 初始化应用
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new SmartMonitorApp();
}); 