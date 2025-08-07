/**
 * Smart Monitor Web - 重构后的前端JavaScript
 * 纯View层，只负责UI交互和数据展示
 * 所有业务逻辑已移到后端SessionController
 */

// ==================== 配置管理器 ====================
class ConfigurationManager {
    constructor() {
        this.localStatus = {
            file_selected: false,
            labels_configured: false,
            fully_configured: false
        };
        this.backendValidation = null;
        this.lastSyncTime = 0;
        this.syncInProgress = false;
        this.listeners = [];
        this.requiredLabels = []; // 存储必需的标签
        this.configuredLabels = new Set(); // 存储已配置的标签
        this.labelToChannelMap = new Map(); // 存储标签到通道的映射
        this.channelToLabelMap = new Map(); // 存储通道到标签的映射
        this.duplicateMatches = []; // 存储重复匹配
    }
    
    // 添加状态变化监听器
    addListener(callback) {
        this.listeners.push(callback);
    }
    
    // 通知所有监听器
    notifyListeners() {
        const status = this.getStatus();
        this.listeners.forEach(callback => callback(status));
    }
    
    // 本地快速响应
    updateLocalStatus(updates) {
        Object.assign(this.localStatus, updates);
        this.notifyListeners();
        
        // 异步验证后端
        this.validateWithBackend();
    }
    
    // 后端验证（可选）
    async validateWithBackend() {
        if (this.syncInProgress) return;
        
        this.syncInProgress = true;
        try {
            const response = await fetch('/api/session/validate-configuration');
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    this.backendValidation = data.configuration_status;
                    this.lastSyncTime = Date.now();
                    
                    // 如果后端验证结果与本地不同，更新UI
                    if (JSON.stringify(this.localStatus) !== JSON.stringify(this.backendValidation)) {
                        this.notifyListeners();
                    }
                }
            }
        } catch (error) {
            console.log('后端验证失败，使用本地状态');
        } finally {
            this.syncInProgress = false;
        }
    }
    
    // 获取最终状态
    getStatus() {
        // 优先使用后端验证结果，如果失败则使用本地状态
        return this.backendValidation || this.localStatus;
    }
    
    // 检查文件选择状态
    checkFileSelection(filePath) {
        const fileSelected = Boolean(filePath && filePath.trim() !== '');
        this.updateLocalStatus({ 
            file_selected: fileSelected,
            fully_configured: fileSelected && this.localStatus.labels_configured
        });
    }
    
    // 设置必需的标签列表
    setRequiredLabels(labels) {
        this.requiredLabels = labels;
        this.checkLabelConfiguration();
    }
    
    // 检查标签配置状态
    checkLabelConfiguration() {
        // 检查是否所有必需的标签都已配置
        const allLabelsConfigured = this.requiredLabels.length > 0 && 
                                  this.requiredLabels.every(label => this.configuredLabels.has(label));
        
        this.updateLocalStatus({ 
            labels_configured: allLabelsConfigured,
            fully_configured: this.localStatus.file_selected && allLabelsConfigured
        });
    }
    
    // 添加标签配置
    addLabelConfiguration(channelId, labelId) {
        // 检查是否有重复匹配（在设置新映射之前）
        this.checkDuplicateMatches(channelId, labelId);
        
        // 设置映射关系
        this.configuredLabels.add(channelId);
        this.labelToChannelMap.set(labelId, channelId);
        this.channelToLabelMap.set(channelId, labelId);
        
        this.checkLabelConfiguration();
    }
    
    // 移除标签配置
    removeLabelConfiguration(channelId) {
        const labelId = this.channelToLabelMap.get(channelId);
        if (labelId) {
            this.labelToChannelMap.delete(labelId);
        }
        this.channelToLabelMap.delete(channelId);
        this.configuredLabels.delete(channelId);
        this.checkLabelConfiguration();
    }
    
    // 检查重复匹配
    checkDuplicateMatches(channelId, labelId) {
        this.duplicateMatches = [];
        
        // None是特殊选项，不参与重复匹配检测
        if (labelId === 'no_match') {
            return;
        }
        
        // 获取通道类型（temperature、pressure、environment、power等）
        const channelType = this.getChannelType(channelId);
        
        // 检查是否有其他通道已经使用了相同的标签
        const existingChannel = this.labelToChannelMap.get(labelId);
        if (existingChannel && existingChannel !== channelId) {
            // 检查是否是相同类型的通道
            const existingChannelType = this.getChannelType(existingChannel);
            if (existingChannelType === channelType) {
                this.duplicateMatches.push({
                    labelId: labelId,
                    channel1: existingChannel,
                    channel2: channelId,
                    channelType: channelType
                });
            }
        }
    }
    
    // 获取通道类型
    getChannelType(channelId) {
        // 根据通道ID判断属于哪个大类型
        if (channelId.startsWith('T') || channelId.startsWith('TRC') || channelId.startsWith('temp')) {
            return 'temperature';
        }
        if (channelId.startsWith('P') || channelId.startsWith('pressure')) {
            return 'pressure';
        }
        if (channelId.startsWith('at') || channelId.startsWith('environment')) {
            return 'environment';
        }
        if (channelId.startsWith('p') || channelId.startsWith('power')) {
            return 'power';
        }
        // 默认类型
        return 'other';
    }
    
    // 获取重复匹配信息
    getDuplicateMatches() {
        return this.duplicateMatches;
    }
    
    // 检查是否有重复匹配
    hasDuplicateMatches() {
        return this.duplicateMatches.length > 0;
    }
    
    // 重置状态
    reset() {
        this.localStatus = {
            file_selected: false,
            labels_configured: false,
            fully_configured: false
        };
        this.backendValidation = null;
        this.lastSyncTime = 0;
        this.requiredLabels = [];
        this.configuredLabels.clear();
        this.labelToChannelMap.clear();
        this.channelToLabelMap.clear();
        this.duplicateMatches = [];
        this.notifyListeners();
    }
}

class SmartMonitorApp {
    constructor() {
        this.currentPage = 'test-selection';
        this.refreshInterval = null;
        this.currentSessionId = null;
        
        // 初始化配置管理器
        this.configManager = new ConfigurationManager();
        this.configManager.addListener((status) => {
            this.updateConfigurationStatus(status);
            this.updateStartMonitoringButton(status.fully_configured);
        });
        
        this.init();
    }

    init() {
        this.loadTestSelection();
        this.setupFileUpload();
    }

    // ==================== 导航管理 ====================
    navigateTo(page) {
        // 如果离开监控页面，停止自动刷新
        if ((this.currentPage === 'old-test-monitor-panel' || this.currentPage === 'new-test-monitor-panel') && 
            page !== 'old-test-monitor-panel' && page !== 'new-test-monitor-panel') {
            this.stopAutoRefresh();
        }

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

        this.currentPage = page;
        this.loadPage(page);
    }

    loadPage(page) {
        switch (page) {
            case 'test-selection':
                this.loadTestSelection();
                break;
            case 'workstation-selection':
                this.loadWorkstationSelection();
                break;
            case 'file-config':
                this.loadFileConfig();
                break;
            case 'old-test-monitor-panel':
                this.loadOldTestMonitorPanel();
                break;
            case 'new-test-monitor-panel':
                this.loadNewTestMonitorPanel();
                break;
            case 'config':
                this.loadConfig();
                break;
            case 'system':
                this.loadSystem();
                break;
        }
    }

    // ==================== 测试选择功能 ====================
    async selectTest(testType) {
        try {
            const response = await this.fetchAPI('/api/session/select-test', {
                method: 'POST',
                body: JSON.stringify({ test_type: testType })
            });

            if (response.success) {
                this.currentSessionId = response.session_id;
                
                if (testType === 'old') {
                    this.navigateTo('workstation-selection');
                    this.showSuccess('已选择 Old Test，请选择工作台');
                } else if (testType === 'new') {
                    this.navigateTo('file-config');
                    this.showSuccess('已选择 New Test，请配置文件和标签');
                }
            } else {
                this.showError(response.error || '选择测试类型失败');
            }
        } catch (error) {
            console.error('Failed to select test type:', error);
            this.showError('选择测试类型时发生错误');
        }
    }

    showTestSelection() {
        this.navigateTo('test-selection');
        this.currentSessionId = null;
    }

    // ==================== 测试选择页面 ====================
    loadTestSelection() {
        // 重置状态
        this.currentSessionId = null;
    }

    // ==================== 工作台选择页面 ====================
    async loadWorkstationSelection() {
        await this.loadWorkstationList();
    }

    async loadWorkstationList() {
        try {
            const data = await this.fetchAPI('/api/session/workstations');
            this.updateWorkstationList(data);
        } catch (error) {
            console.error('Failed to load workstation list:', error);
            this.showError('加载工作台列表失败');
        }
    }

    updateWorkstationList(data) {
        const workstationList = document.getElementById('workstation-list');
        
        if (data.success && data.workstations && data.workstations.length > 0) {
            let html = '';
            
            data.workstations.forEach(workstation => {
                const statusClass = workstation.status === 'running' ? 'running' : 'stopped';
                const statusText = workstation.status === 'running' ? '运行中' : '已停止';
                
                html += `
                    <div class="workstation-item">
                        <div class="workstation-header">
                            <div class="workstation-name">${workstation.name}</div>
                            <div class="workstation-status ${statusClass}">${statusText}</div>
                        </div>
                        <div class="workstation-details">
                            <p><strong>ID:</strong> ${workstation.id}</p>
                            <p><strong>开始时间:</strong> ${workstation.start_time || '-'}</p>
                            <p><strong>处理记录:</strong> ${workstation.records_processed || 0}</p>
                            <p><strong>生成告警:</strong> ${workstation.alarms_generated || 0}</p>
                            <p><strong>测试类型:</strong> ${
                                workstation.test_type === 'new' ? '新测试' : 
                                workstation.test_type === 'simulation' ? '模拟测试' : '旧测试'
                            }</p>
                        </div>
                        <div class="workstation-actions">
                            <button class="btn btn-primary btn-sm" onclick="app.selectWorkstation('${workstation.id}')">
                                <i class="fas fa-play"></i>
                                选择此工作台
                            </button>
                            <button class="btn btn-warning btn-sm" onclick="app.stopWorkstation('${workstation.id}')">
                                <i class="fas fa-stop"></i>
                                停止会话
                            </button>
                        </div>
                    </div>
                `;
            });
            
            workstationList.innerHTML = html;
        } else {
            workstationList.innerHTML = '<div class="text-center text-secondary">暂无可用工作台</div>';
        }
    }

    async selectWorkstation(workstationId) {
        try {
            const response = await this.fetchAPI('/api/session/select-workstation', {
                method: 'POST',
                body: JSON.stringify({ workstation_id: workstationId })
            });

            if (response.success) {
                this.currentSessionId = response.session_id;
                this.navigateTo('old-test-monitor-panel');
                this.showSuccess(`已选择工作台: ${workstationId}`);
            } else {
                this.showError(response.error || '选择工作台失败');
            }
        } catch (error) {
            console.error('Failed to select workstation:', error);
            this.showError('选择工作台时发生错误');
        }
    }

    async stopWorkstation(workstationId) {
        try {
            const response = await this.fetchAPI('/api/session/stop-workstation', {
                method: 'POST',
                body: JSON.stringify({ workstation_id: workstationId })
            });

            if (response.success) {
                this.showSuccess(`工作台 ${workstationId} 已停止`);
                this.loadWorkstationList();
            } else {
                this.showError(response.error || '停止工作台失败');
            }
        } catch (error) {
            console.error('Failed to stop workstation:', error);
            this.showError('停止工作台时发生错误');
        }
    }

    // ==================== 文件配置页面 ====================
    async loadFileConfig() {
        await this.loadFileList();
        await this.loadLabelConfiguration();
        // 检查是否有保存的配置
        await this.checkSavedConfiguration();
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

            fileSelector.addEventListener('change', (e) => {
                const selectedValue = e.target.value;
                if (!selectedValue) {
                    this.onFileDeselected();
                } else {
                    this.onFileSelected(selectedValue);
                }
            });
        } else {
            fileSelector.innerHTML = '<option value="">没有找到数据文件</option>';
        }
    }

    async onFileSelected(filePath) {
        if (!filePath) {
            this.updateFileInfo('请选择数据文件以查看详细信息');
            this.configManager.checkFileSelection('');
            return;
        }

        const statusIndicator = document.querySelector('.label-selection-container .status-indicator');
        if (statusIndicator) {
            statusIndicator.className = 'status-indicator status-info';
            statusIndicator.textContent = '正在加载标签配置...';
        }
        
        try {
            const fileInfo = await this.fetchAPI(`/api/file/info/${filePath.split('/').pop()}`);
            this.updateFileInfo(fileInfo);
            
            const workstationInfo = await this.fetchAPI('/api/file/infer-workstation', {
                method: 'POST',
                body: JSON.stringify({ file_path: filePath })
            });
            
            if (workstationInfo.success && workstationInfo.workstation_id) {
                this.showSuccess(`自动推断工作站ID: ${workstationInfo.workstation_id}`);
            }
            
            await this.loadLabelConfiguration();
            
            // 使用配置管理器检查文件选择状态
            this.configManager.checkFileSelection(filePath);

        } catch (error) {
            console.error('Failed to get file info:', error);
            this.showError('获取文件信息失败');
            
            if (statusIndicator) {
                statusIndicator.className = 'status-indicator status-error';
                statusIndicator.textContent = '文件信息获取失败';
            }
        }
    }

    onFileDeselected() {
        // 清除文件信息
        const fileInfo = document.getElementById('file-info');
        if (fileInfo) {
            fileInfo.innerHTML = '<p>请选择数据文件以查看详细信息</p>';
        }

        // 清除标签选择
        const labelSelection = document.getElementById('label-selection');
        if (labelSelection) {
            labelSelection.innerHTML = '<p>请先选择数据文件以配置标签匹配</p>';
        }

        // 更新状态指示器
        const statusIndicator = document.querySelector('#file-config .card-header .status-indicator');
        if (statusIndicator) {
            statusIndicator.textContent = '等待文件选择';
            statusIndicator.className = 'status-indicator status-info';
        }

        // 使用配置管理器重置文件选择状态
        this.configManager.checkFileSelection('');
    }

    // ==================== 配置状态管理 ====================
    
    updateConfigurationStatus(status) {
        // 更新状态指示器
        const statusIndicator = document.querySelector('#file-config .card-header .status-indicator');
        if (statusIndicator) {
            if (status.fully_configured) {
                statusIndicator.textContent = '配置完成';
                statusIndicator.className = 'status-indicator status-success';
            } else if (status.file_selected && !status.labels_configured) {
                statusIndicator.textContent = '请配置标签匹配';
                statusIndicator.className = 'status-indicator status-warning';
            } else if (!status.file_selected) {
                statusIndicator.textContent = '等待文件选择';
                statusIndicator.className = 'status-indicator status-info';
            }
        }
        
        // 检查并显示重复匹配警告
        this.checkAndShowDuplicateWarning();
    }
    
    checkAndShowDuplicateWarning() {
        if (this.configManager.hasDuplicateMatches()) {
            const duplicates = this.configManager.getDuplicateMatches();
            let warningMessage = '⚠️ 检测到同类型重复匹配:\n';
            duplicates.forEach(dup => {
                warningMessage += `• 标签 "${dup.labelId}" 在${dup.channelType}类型中被多个通道使用\n`;
            });
            warningMessage += '\n请检查并修正重复匹配，确保同类型内每个标签只对应一个通道。';
            this.showNotification(warningMessage, 'warning');
        }
    }

    updateStartMonitoringButton(enabled) {
        const startButton = document.getElementById('start-monitoring-btn');
        if (startButton) {
            startButton.disabled = !enabled;
            if (enabled) {
                startButton.classList.remove('btn-disabled');
                startButton.classList.add('btn-primary');
            } else {
                startButton.classList.add('btn-disabled');
                startButton.classList.remove('btn-primary');
            }
        }
    }

    async confirmConfiguration() {
        // 使用配置管理器获取当前状态
        const status = this.configManager.getStatus();
        
        if (!status.file_selected) {
            this.showError('请先选择数据文件');
            return;
        }
        
        if (!status.labels_configured) {
            const missingLabels = this.configManager.requiredLabels.filter(
                label => !this.configManager.configuredLabels.has(label)
            );
            this.showError(`请配置所有必需的标签: ${missingLabels.join(', ')}`);
            return;
        }
        
        // 检查重复匹配
        if (this.configManager.hasDuplicateMatches()) {
            const duplicates = this.configManager.getDuplicateMatches();
            let duplicateMessage = '检测到同类型重复匹配:\n';
            duplicates.forEach(dup => {
                duplicateMessage += `- 标签 "${dup.labelId}" 在${dup.channelType}类型中被多个通道使用\n`;
            });
            duplicateMessage += '\n请检查并修正重复匹配，确保同类型内每个标签只对应一个通道。';
            this.showError(duplicateMessage);
            return;
        }
        
        // 配置完整，可以启动监控
        this.showSuccess('配置已确认');
        
        // 强制同步后端验证
        await this.configManager.validateWithBackend();
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
            if (statusIndicator) {
                statusIndicator.className = 'status-indicator status-success';
                statusIndicator.textContent = '标签配置已加载';
            }
            
            let html = '<div class="grid grid-cols-1 gap-4">';
            
            const priorityOrder = ['environment_temp', 'total_power'];
            const priorityCategories = [];
            const otherCategories = [];
            
            // 收集所有必需的标签
            const requiredLabels = [];
            
            Object.entries(data.categories).forEach(([categoryKey, category]) => {
                if (priorityOrder.includes(categoryKey)) {
                    priorityCategories.push([categoryKey, category]);
                } else {
                    otherCategories.push([categoryKey, category]);
                }
                
                // 收集所有通道ID作为必需标签
                if (category.channels) {
                    category.channels.forEach(channel => {
                        requiredLabels.push(channel.channel_id);
                    });
                }
            });
            
            // 设置必需的标签列表
            this.configManager.setRequiredLabels(requiredLabels);
            
            otherCategories.sort((a, b) => a[0].localeCompare(b[0]));
            const sortedCategories = [...priorityCategories, ...otherCategories];
            
            sortedCategories.forEach(([categoryKey, category]) => {
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
                                html += `
                                    <label class="label-radio">
                                        <input type="radio" name="label_${channel.channel_id}" 
                                               value="${subtype.subtype_id}">
                                        <span>${subtype.label}</span>
                                    </label>
                                `;
                            });
                        }
                        
                        // 为除了at和p之外的通道添加"None"选项
                        if (!channel.channel_id.startsWith('at') && !channel.channel_id.startsWith('p')) {
                            html += `
                                <label class="label-radio">
                                    <input type="radio" name="label_${channel.channel_id}" 
                                           value="no_match">
                                    <span>None</span>
                                </label>
                            `;
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
            
            this.setupLabelSelectionEvents();
        } else {
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
        
        // 清除同组其他选项的选中状态
        const radioGroup = document.querySelectorAll(`input[name="${event.target.name}"]`);
        radioGroup.forEach(radio => {
            const labelElement = radio.closest('.label-radio');
            if (labelElement) {
                labelElement.style.borderColor = '';
                labelElement.style.backgroundColor = '';
            }
        });
        
        // 设置当前选中项的视觉反馈
        const currentLabelElement = event.target.closest('.label-radio');
        if (currentLabelElement) {
            currentLabelElement.style.borderColor = 'var(--primary-color)';
            currentLabelElement.style.backgroundColor = 'rgba(37, 99, 235, 0.1)';
        }

        // 更新配置管理器中的标签状态
        if (event.target.checked) {
            if (subtypeId === 'no_match') {
                // 选择"无需匹配"时，只标记为已配置，不建立映射关系
                this.configManager.configuredLabels.add(channelId);
                this.configManager.checkLabelConfiguration();
            } else {
                this.configManager.addLabelConfiguration(channelId, subtypeId);
            }
        } else {
            this.configManager.removeLabelConfiguration(channelId);
        }

        // 保存标签选择到会话
        this.saveLabelSelectionToSession();
    }

    async saveLabelSelectionToSession() {
        if (!this.currentSessionId) {
            return;
        }

        try {
            // 收集标签选择
            const selectedLabels = {};
            const radioButtons = document.querySelectorAll('input[type="radio"]:checked');
            radioButtons.forEach(radio => {
                const channelId = radio.name.replace('label_', '');
                selectedLabels[channelId] = radio.value;
            });

            // 保存到会话
            const response = await this.fetchAPI('/api/session/configure-new-test', {
                method: 'POST',
                body: JSON.stringify({
                    session_id: this.currentSessionId,
                    file_path: document.getElementById('file-selector')?.value || '',
                    selected_labels: selectedLabels
                })
            });

            if (!response.success) {
                console.error('Failed to save label selection to session:', response.error);
            }
        } catch (error) {
            console.error('Failed to save label selection to session:', error);
        }
    }

    async confirmAndGoToMonitor() {
        const fileSelector = document.getElementById('file-selector');
        const selectedFile = fileSelector?.value;
        
        if (!selectedFile) {
            this.showError('请先选择数据文件');
            return;
        }

        // 收集标签选择
        const selectedLabels = {};
        const radioButtons = document.querySelectorAll('input[type="radio"]:checked');
        radioButtons.forEach(radio => {
            const channelId = radio.name.replace('label_', '');
            selectedLabels[channelId] = radio.value;
        });

        if (Object.keys(selectedLabels).length === 0) {
            this.showError('请配置标签匹配');
            return;
        }

        try {
            const response = await this.fetchAPI('/api/session/configure-new-test', {
                method: 'POST',
                body: JSON.stringify({
                    session_id: this.currentSessionId,
                    file_path: selectedFile,
                    selected_labels: selectedLabels
                })
            });

            if (response.success) {
                this.showSuccess('配置已保存，正在启动监控...');
                
                // 启动监控
                const startResponse = await this.fetchAPI('/api/session/start-new-test', {
                    method: 'POST',
                    body: JSON.stringify({ session_id: this.currentSessionId })
                });

                if (startResponse.success) {
                    this.navigateTo('new-test-monitor-panel');
                } else {
                    this.showError(startResponse.error || '启动监控失败');
                }
            } else {
                this.showError(response.error || '保存配置失败');
            }
        } catch (error) {
            console.error('Failed to configure and start monitoring:', error);
            this.showError('配置和启动监控时发生错误');
        }
    }

    async loadLastLabelSelection() {
        try {
            const data = await this.fetchAPI('/api/config/labels/load');
            if (data.success && data.labels) {
                this.updateLabelSelectionFromSaved(data.labels);
                this.showSuccess('已加载上次配置');
                
                // 保存到会话并使用配置管理器检查状态
                await this.saveLabelSelectionToSession();
                this.configManager.checkLabelConfiguration();
            } else {
                this.showError('没有找到保存的配置');
                // 更新按钮状态为禁用
                this.updateLoadLastConfigButton(false);
            }
        } catch (error) {
            console.error('Failed to load last selection:', error);
            this.showError('加载上次配置失败');
            // 更新按钮状态为禁用
            this.updateLoadLastConfigButton(false);
        }
    }

    async checkSavedConfiguration() {
        try {
            const data = await this.fetchAPI('/api/config/labels/load');
            const hasSavedConfig = data.success && data.labels && Object.keys(data.labels).length > 0;
            this.updateLoadLastConfigButton(hasSavedConfig);
        } catch (error) {
            console.error('Failed to check saved configuration:', error);
            this.updateLoadLastConfigButton(false);
        }
    }

    updateLoadLastConfigButton(hasSavedConfig) {
        const loadButton = document.getElementById('load-last-config-btn');
        if (loadButton) {
            if (hasSavedConfig) {
                loadButton.disabled = false;
                loadButton.classList.remove('btn-disabled');
                loadButton.classList.add('btn-outline');
                loadButton.innerHTML = '<i class="fas fa-history"></i> 加载上次配置';
                // 清除内联样式
                loadButton.style.opacity = '';
                loadButton.style.cursor = '';
                loadButton.style.pointerEvents = '';
            } else {
                loadButton.disabled = true;
                loadButton.classList.remove('btn-outline');
                loadButton.classList.add('btn-disabled');
                loadButton.innerHTML = '<i class="fas fa-history"></i> 无保存配置';
            }
        }
    }

    updateLabelSelectionFromSaved(labels) {
        // 清除所有已配置的标签
        this.configManager.configuredLabels.clear();
        this.configManager.labelToChannelMap.clear();
        this.configManager.channelToLabelMap.clear();
        this.configManager.duplicateMatches = [];
        
        // 先清除所有radio按钮的选中状态和样式
        const allRadios = document.querySelectorAll('input[type="radio"]');
        allRadios.forEach(radio => {
            radio.checked = false;
            const labelElement = radio.closest('.label-radio');
            if (labelElement) {
                labelElement.style.borderColor = '';
                labelElement.style.backgroundColor = '';
            }
        });
        
        Object.entries(labels).forEach(([channelId, subtypeId]) => {
            const radio = document.querySelector(`input[name="label_${channelId}"][value="${subtypeId}"]`);
            if (radio) {
                radio.checked = true;
                const labelElement = radio.closest('.label-radio');
                if (labelElement) {
                    labelElement.style.borderColor = '#2563eb';
                    labelElement.style.backgroundColor = 'rgba(37, 99, 235, 0.1)';
                }
                
                // 添加到已配置标签列表
                if (subtypeId === 'no_match') {
                    this.configManager.configuredLabels.add(channelId);
                } else {
                    this.configManager.addLabelConfiguration(channelId, subtypeId);
                }
            }
        });
    }

    // ==================== 监控面板页面 ====================
    async loadOldTestMonitorPanel() {
        await this.loadOldTestMonitoringStatus();
        await this.loadOldTestSessionStats();
        this.startOldTestAutoRefresh();
    }

    async loadNewTestMonitorPanel() {
        await this.loadNewTestMonitoringStatus();
        await this.loadNewTestSessionStats();
        this.startNewTestAutoRefresh();
    }

    async loadOldTestMonitoringStatus() {
        try {
            const data = await this.fetchAPI('/api/session/status');
            this.updateOldTestMonitoringStatus(data);
        } catch (error) {
            console.error('Failed to load Old Test monitoring status:', error);
        }
    }

    async loadNewTestMonitoringStatus() {
        try {
            const data = await this.fetchAPI('/api/session/status');
            this.updateNewTestMonitoringStatus(data);
        } catch (error) {
            console.error('Failed to load New Test monitoring status:', error);
        }
    }

    updateOldTestMonitoringStatus(data) {
        const statusElement = document.getElementById('old-monitoring-status');
        const detailsElement = document.getElementById('old-monitoring-details');

        if (data.success && data.session) {
            const session = data.session;
            const isMonitoring = session.is_monitoring || session.status === 'running';

            if (isMonitoring) {
                statusElement.className = 'status-indicator status-success';
                statusElement.textContent = '运行中';
                
                let detailsHtml = '';
                if (session.configuration?.selected_workstation) {
                    detailsHtml += `<p><strong>工作台ID:</strong> ${session.configuration.selected_workstation}</p>`;
                }
                if (session.session_id) {
                    detailsHtml += `<p><strong>会话ID:</strong> ${session.session_id}</p>`;
                }
                if (session.statistics?.records_processed !== undefined) {
                    detailsHtml += `<p><strong>处理记录:</strong> ${session.statistics.records_processed}</p>`;
                }
                if (session.statistics?.alarms_generated !== undefined) {
                    detailsHtml += `<p><strong>生成告警:</strong> ${session.statistics.alarms_generated}</p>`;
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

    updateNewTestMonitoringStatus(data) {
        const statusElement = document.getElementById('new-monitoring-status');
        const detailsElement = document.getElementById('new-monitoring-details');

        if (data.success && data.session) {
            const session = data.session;
            const isMonitoring = session.is_monitoring || session.status === 'running';

            if (isMonitoring) {
                statusElement.className = 'status-indicator status-success';
                statusElement.textContent = '运行中';
                
                let detailsHtml = '';
                if (session.configuration?.selected_file) {
                    const fileName = session.configuration.selected_file.split('/').pop();
                    detailsHtml += `<p><strong>当前文件:</strong> ${fileName}</p>`;
                }
                if (session.session_id) {
                    detailsHtml += `<p><strong>会话ID:</strong> ${session.session_id}</p>`;
                }
                if (session.statistics?.records_processed !== undefined) {
                    detailsHtml += `<p><strong>处理记录:</strong> ${session.statistics.records_processed}</p>`;
                }
                if (session.statistics?.alarms_generated !== undefined) {
                    detailsHtml += `<p><strong>生成告警:</strong> ${session.statistics.alarms_generated}</p>`;
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

    async loadOldTestSessionStats() {
        try {
            const data = await this.fetchAPI('/api/session/status');
            this.updateOldTestSessionStats(data);
        } catch (error) {
            console.error('Failed to load Old Test session stats:', error);
        }
    }

    async loadNewTestSessionStats() {
        try {
            const data = await this.fetchAPI('/api/session/status');
            this.updateNewTestSessionStats(data);
        } catch (error) {
            console.error('Failed to load New Test session stats:', error);
        }
    }

    updateOldTestSessionStats(data) {
        const sessionStart = document.getElementById('old-session-start');
        const totalRecords = document.getElementById('old-total-records');
        const totalAlarms = document.getElementById('old-total-alarms');
        const processingSpeed = document.getElementById('old-processing-speed');
        
        if (data.success && data.session) {
            const session = data.session;
            const stats = session.statistics || {};
            
            totalRecords.textContent = stats.records_processed || 0;
            totalAlarms.textContent = stats.alarms_generated || 0;
            sessionStart.textContent = stats.started_at ? new Date(stats.started_at).toLocaleString() : '-';
            processingSpeed.textContent = (stats.processing_speed || 0).toFixed(2);
        } else {
            sessionStart.textContent = '-';
            totalRecords.textContent = '0';
            totalAlarms.textContent = '0';
            processingSpeed.textContent = '0.00';
        }
    }

    updateNewTestSessionStats(data) {
        const sessionStart = document.getElementById('new-session-start');
        const totalRecords = document.getElementById('new-total-records');
        const totalAlarms = document.getElementById('new-total-alarms');
        const processingSpeed = document.getElementById('new-processing-speed');
        
        if (data.success && data.session) {
            const session = data.session;
            const stats = session.statistics || {};
            
            totalRecords.textContent = stats.records_processed || 0;
            totalAlarms.textContent = stats.alarms_generated || 0;
            sessionStart.textContent = stats.started_at ? new Date(stats.started_at).toLocaleString() : '-';
            processingSpeed.textContent = (stats.processing_speed || 0).toFixed(2);
        } else {
            sessionStart.textContent = '-';
            totalRecords.textContent = '0';
            totalAlarms.textContent = '0';
            processingSpeed.textContent = '0.00';
        }
    }

    // ==================== 监控控制 ====================
    async startOldTestMonitoring() {
        try {
            const response = await this.fetchAPI('/api/session/start-old-test', {
                method: 'POST',
                body: JSON.stringify({ session_id: this.currentSessionId })
            });

            if (response.success) {
                this.showSuccess(`Old Test 监控启动成功 - ${response.session_name}`);
                this.loadOldTestMonitoringStatus();
            } else {
                this.showError(response.error || 'Old Test 监控启动失败');
            }
        } catch (error) {
            console.error('Old Test monitoring start error:', error);
            this.showError('启动 Old Test 监控时发生错误');
        }
    }

    async stopOldTestMonitoring() {
        try {
            const response = await this.fetchAPI('/api/session/stop-monitoring', {
                method: 'POST',
                body: JSON.stringify({ session_id: this.currentSessionId })
            });

            if (response.success) {
                this.showSuccess('Old Test 监控已停止');
                this.loadOldTestMonitoringStatus();
            } else {
                this.showError(response.error || '停止 Old Test 监控失败');
            }
        } catch (error) {
            console.error('Old Test monitoring stop error:', error);
            this.showError('停止 Old Test 监控时发生错误');
        }
    }

    async startNewTestMonitoring() {
        if (!this.currentSessionId) {
            this.showError('没有活动的会话');
            return;
        }

        // 使用配置管理器获取当前状态
        const status = this.configManager.getStatus();
        
        if (!status.file_selected) {
            this.showError('请先选择数据文件');
            return;
        }
        
        if (!status.labels_configured) {
            this.showError('请配置标签匹配');
            return;
        }

        try {
            // 启动监控
            const response = await this.fetchAPI('/api/session/start-new-test', {
                method: 'POST',
                body: JSON.stringify({ session_id: this.currentSessionId })
            });

            if (response.success) {
                this.showSuccess('监控已启动');
                this.navigateTo('new-test-monitor-panel');
            } else {
                this.showError(response.error || '启动监控失败');
            }
        } catch (error) {
            console.error('Failed to start new test monitoring:', error);
            this.showError('启动监控时发生错误');
        }
    }

    async stopNewTestMonitoring() {
        try {
            const response = await this.fetchAPI('/api/session/stop-monitoring', {
                method: 'POST',
                body: JSON.stringify({ session_id: this.currentSessionId })
            });

            if (response.success) {
                this.showSuccess('New Test 监控已停止');
                this.loadNewTestMonitoringStatus();
            } else {
                this.showError(response.error || '停止 New Test 监控失败');
            }
        } catch (error) {
            console.error('New Test monitoring stop error:', error);
            this.showError('停止 New Test 监控时发生错误');
        }
    }

    // ==================== 自动刷新 ====================
    startOldTestAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
        
        this.refreshInterval = setInterval(() => {
            if (this.currentPage === 'old-test-monitor-panel') {
                this.loadOldTestMonitoringStatus();
                this.loadOldTestSessionStats();
            }
        }, 2000);
    }

    startNewTestAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
        
        this.refreshInterval = setInterval(() => {
            if (this.currentPage === 'new-test-monitor-panel') {
                this.loadNewTestMonitoringStatus();
                this.loadNewTestSessionStats();
            }
        }, 2000);
    }

    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
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

    // ==================== 文件上传功能 ====================
    setupFileUpload() {
        const uploadArea = document.getElementById('upload-area');
        const fileUpload = document.getElementById('file-upload');
        
        if (!uploadArea || !fileUpload) return;
        
        fileUpload.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.uploadFile(e.target.files[0]);
            }
        });
        
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
        
        uploadArea.addEventListener('click', () => {
            fileUpload.click();
        });
    }

    async uploadFile(file) {
        if (!file.name.toLowerCase().endsWith('.dat')) {
            this.showError('只支持 .dat 文件');
            return;
        }
        
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
                
                await this.loadFileList();
                
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
}

// 初始化应用
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new SmartMonitorApp();
}); 