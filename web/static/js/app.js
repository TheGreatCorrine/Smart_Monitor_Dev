/**
 * Smart Monitor Web - 主应用JavaScript
 * 使用原生JavaScript，无框架依赖
 * 新的页面流程：测试选择 -> 工作台选择/文件配置 -> 监控面板
 */

class SmartMonitorApp {
    constructor() {
        this.currentPage = 'test-selection';
        this.refreshInterval = null;
        this.selectedFile = null;
        this.selectedLabels = {};
        this.selectedWorkstation = null;
        this.currentSessionId = null;
        this.currentSessionName = null;
        this.alarms = [];
        this.logs = [];
        this.testType = null;
        this.init();
    }

    init() {
        this.loadTestSelection();
        this.setupFileUpload();
        this.disableConfirmButton();
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
        
        // 如果是监控面板，记录当前会话信息
        if (page === 'old-test-monitor-panel' || page === 'new-test-monitor-panel') {
            console.log('Navigating to monitor panel - Test type:', this.testType);
            console.log('Current session ID:', this.currentSessionId);
            console.log('Selected workstation:', this.selectedWorkstation);
        }
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
    selectTest(testType) {
        // 重置所有状态
        this.testType = testType;
        this.selectedFile = null;
        this.selectedLabels = {};
        this.selectedWorkstation = null;
        this.currentSessionId = null;
        this.currentSessionName = null;
        
        if (testType === 'old') {
            // 强制跳转到工作台选择页面
            this.navigateTo('workstation-selection');
            this.showSuccess('已选择 Old Test，请选择工作台');
        } else if (testType === 'new') {
            // 跳转到文件配置页面
            this.navigateTo('file-config');
            this.showSuccess('已选择 New Test，请配置文件和标签');
        }
    }

    showTestSelection() {
        // 返回测试选择页面
        this.navigateTo('test-selection');
        
        // 重置所有状态
        this.testType = null;
        this.selectedWorkstation = null;
        this.selectedFile = null;
        this.selectedLabels = {};
        this.currentSessionId = null;
        this.currentSessionName = null;
        
        // 清空文件选择器
        const fileSelector = document.getElementById('file-selector');
        if (fileSelector) {
            fileSelector.value = '';
        }
        
        // 清空文件信息
        const fileInfo = document.getElementById('file-info');
        if (fileInfo) {
            fileInfo.innerHTML = '<p>请选择数据文件以查看详细信息</p>';
        }
        
        // 清空标签选择
        const labelSelection = document.getElementById('label-selection');
        if (labelSelection) {
            labelSelection.innerHTML = '<p>请先选择数据文件以配置标签匹配</p>';
        }
        
        // 重置状态指示器
        const statusIndicator = document.querySelector('.label-selection-container .status-indicator');
        if (statusIndicator) {
            statusIndicator.className = 'status-indicator status-info';
            statusIndicator.textContent = '等待文件选择';
        }
        
        // 禁用确认按钮
        this.disableConfirmButton();
    }

    // ==================== 测试选择页面 ====================
    loadTestSelection() {
        // 重置所有状态
        this.testType = null;
        this.selectedWorkstation = null;
        this.selectedFile = null;
        this.selectedLabels = {};
    }

    // ==================== 工作台选择页面 ====================
    async loadWorkstationSelection() {
        // 重置工作台选择页面的状态
        this.selectedWorkstation = null;
        this.currentSessionId = null;
        this.currentSessionName = null;
        
        // 清除工作台选择状态
        document.querySelectorAll('.workstation-item').forEach(item => {
            item.classList.remove('active');
        });
        
        await this.loadWorkstationList();
    }

    async loadWorkstationList() {
        try {
            const data = await this.fetchAPI('/api/monitor/workstations');
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

    selectWorkstation(workstationId) {
        this.selectedWorkstation = workstationId;
        
        // 更新选中状态
        document.querySelectorAll('.workstation-item').forEach(item => {
            item.classList.remove('active');
        });
        
        const selectedItem = document.querySelector(`[onclick="app.selectWorkstation('${workstationId}')"]`);
        if (selectedItem) {
            selectedItem.classList.add('active');
        }
        
        // 跳转到Old Test监控面板
        this.navigateTo('old-test-monitor-panel');
        this.showSuccess(`已选择工作台: ${workstationId}`);
    }

    async stopWorkstation(workstationId) {
        try {
            const data = await this.fetchAPI('/api/monitor/stop', {
                method: 'POST',
                body: JSON.stringify({ session_id: workstationId })
            });

            if (data.success) {
                this.showSuccess(`工作台 ${workstationId} 已停止`);
                
                // 刷新工作台列表
                this.loadWorkstationList();
                
                // 如果停止的是当前选中的工作台，清除选择
                if (this.selectedWorkstation === workstationId) {
                    this.selectedWorkstation = null;
                }
            } else {
                this.showError(data.error || '停止工作台失败');
            }
        } catch (error) {
            console.error('Stop workstation error:', error);
            this.showError('停止工作台时发生错误');
        }
    }

    // ==================== 文件配置页面 ====================
    async loadFileConfig() {
        // 重置文件配置页面的状态
        this.selectedFile = null;
        this.selectedLabels = {};
        this.currentSessionId = null;
        this.currentSessionName = null;
        
        // 清空文件选择器
        const fileSelector = document.getElementById('file-selector');
        if (fileSelector) {
            fileSelector.value = '';
        }
        
        // 清空文件信息
        const fileInfo = document.getElementById('file-info');
        if (fileInfo) {
            fileInfo.innerHTML = '<p>请选择数据文件以查看详细信息</p>';
        }
        
        // 清空标签选择
        const labelSelection = document.getElementById('label-selection');
        if (labelSelection) {
            labelSelection.innerHTML = '<p>请先选择数据文件以配置标签匹配</p>';
        }
        
        // 重置状态指示器
        const statusIndicator = document.querySelector('.label-selection-container .status-indicator');
        if (statusIndicator) {
            statusIndicator.className = 'status-indicator status-info';
            statusIndicator.textContent = '等待文件选择';
        }
        
        await this.loadFileList();
        await this.loadLabelConfiguration();
        this.disableConfirmButton();
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
            return;
        }

        this.selectedFile = filePath;
        
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
            this.enableConfirmButton();
            
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
        this.selectedFile = null;
        
        const fileInfo = document.getElementById('file-info');
        if (fileInfo) {
            fileInfo.innerHTML = '<p>请选择数据文件以查看详细信息</p>';
        }
        
        const labelSelection = document.getElementById('label-selection');
        if (labelSelection) {
            labelSelection.innerHTML = '<p>请先选择数据文件以配置标签匹配</p>';
        }
        
        const statusIndicator = document.querySelector('.label-selection-container .status-indicator');
        if (statusIndicator) {
            statusIndicator.className = 'status-indicator status-info';
            statusIndicator.textContent = '等待文件选择';
        }
        
        this.disableConfirmButton();
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
            
            Object.entries(data.categories).forEach(([categoryKey, category]) => {
                if (priorityOrder.includes(categoryKey)) {
                    priorityCategories.push([categoryKey, category]);
                } else {
                    otherCategories.push([categoryKey, category]);
                }
            });
            
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
        
        this.selectedLabels[channelId] = subtypeId;
        console.log('Label selection updated:', this.selectedLabels);
        
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
    }

    async confirmAndGoToMonitor() {
        if (!this.selectedFile) {
            this.showError('请先选择数据文件');
            return;
        }

        if (Object.keys(this.selectedLabels).length === 0) {
            this.showError('请配置标签匹配');
            return;
        }

        try {
            // 先保存标签配置
            const saveResult = await this.fetchAPI('/api/config/labels/save', {
                method: 'POST',
                body: JSON.stringify({ selected_labels: this.selectedLabels })
            });

            if (saveResult.success) {
                this.showSuccess('配置已保存，正在启动监控...');
                
                // 自动启动监控
                await this.startNewTestMonitoring();
                
                // 跳转到New Test监控面板
                this.navigateTo('new-test-monitor-panel');
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
            console.log('loadLastLabelSelection called');
            const data = await this.fetchAPI('/api/config/labels/load');
            console.log('API response:', data);
            if (data.success && data.labels) {
                // API返回的数据结构是 data.labels.labels
                this.selectedLabels = data.labels.labels || data.labels;
                console.log('Set selectedLabels to:', this.selectedLabels);
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
        console.log('updateLabelSelectionFromSaved called with:', this.selectedLabels);
        Object.entries(this.selectedLabels).forEach(([channelId, subtypeId]) => {
            const radio = document.querySelector(`input[name="label_${channelId}"][value="${subtypeId}"]`);
            console.log(`Looking for radio: label_${channelId}, value: ${subtypeId}, found:`, radio);
            if (radio) {
                radio.checked = true;
                // 添加选中状态的视觉反馈
                const labelElement = radio.closest('.label-radio');
                console.log('Found label element:', labelElement);
                if (labelElement) {
                    labelElement.style.borderColor = '#2563eb';
                    labelElement.style.backgroundColor = 'rgba(37, 99, 235, 0.1)';
                    console.log('Applied visual feedback to:', labelElement);
                }
            }
        });
        console.log('updateLabelSelectionFromSaved completed');
    }

    // ==================== Old Test 监控面板页面 ====================
    async loadOldTestMonitorPanel() {
        console.log('Loading Old Test monitor panel - Selected workstation:', this.selectedWorkstation);
        
        // 更新工作台信息
        this.updateWorkstationInfo();
        
        await this.loadOldTestMonitoringStatus();
        await this.loadOldTestSessionStats();
        this.startOldTestAutoRefresh();
    }

    // ==================== New Test 监控面板页面 ====================
    async loadNewTestMonitorPanel() {
        console.log('Loading New Test monitor panel - Current session:', this.currentSessionId, this.currentSessionName);
        
        // 更新文件信息
        this.updateFileInfoDisplay();
        
        // 更新标签配置显示
        this.updateLabelConfigDisplay();
        
        await this.loadNewTestMonitoringStatus();
        await this.loadNewTestSessionStats();
        this.startNewTestAutoRefresh();
    }

    async loadOldTestMonitoringStatus() {
        try {
            const data = await this.fetchAPI('/api/monitor/status');
            this.updateOldTestMonitoringStatus(data);
        } catch (error) {
            console.error('Failed to load Old Test monitoring status:', error);
        }
    }

    async loadNewTestMonitoringStatus() {
        try {
            const data = await this.fetchAPI('/api/monitor/status');
            this.updateNewTestMonitoringStatus(data);
        } catch (error) {
            console.error('Failed to load New Test monitoring status:', error);
        }
    }

    async loadMonitoringStatus() {
        try {
            const data = await this.fetchAPI('/api/monitor/status');
            this.updateMonitoringStatus(data);
        } catch (error) {
            console.error('Failed to load monitoring status:', error);
        }
    }

    updateOldTestMonitoringStatus(data) {
        const statusElement = document.getElementById('old-monitoring-status');
        const detailsElement = document.getElementById('old-monitoring-details');

        if (data.success && data.status) {
            const status = data.status;
            const isMonitoring = status.is_monitoring || status.web_monitoring_active;
            const fileProvider = status.file_provider || {};

            if (isMonitoring) {
                statusElement.className = 'status-indicator status-success';
                statusElement.textContent = '运行中';
                
                let detailsHtml = '';
                
                if (this.selectedWorkstation) {
                    detailsHtml += `<p><strong>工作台ID:</strong> ${this.selectedWorkstation}</p>`;
                }
                
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

    updateNewTestMonitoringStatus(data) {
        const statusElement = document.getElementById('new-monitoring-status');
        const detailsElement = document.getElementById('new-monitoring-details');

        if (data.success && data.status) {
            const status = data.status;
            const isMonitoring = status.is_monitoring || status.web_monitoring_active;
            const fileProvider = status.file_provider || {};

            if (isMonitoring) {
                statusElement.className = 'status-indicator status-success';
                statusElement.textContent = '运行中';
                
                let detailsHtml = '';
                
                if (this.selectedFile) {
                    const fileName = this.selectedFile.split('/').pop();
                    detailsHtml += `<p><strong>当前文件:</strong> ${fileName}</p>`;
                }
                
                if (status.web_session_id) {
                    detailsHtml += `<p><strong>会话ID:</strong> ${status.web_session_id}</p>`;
                }
                
                if (status.web_current_file) {
                    detailsHtml += `<p><strong>文件路径:</strong> ${status.web_current_file}</p>`;
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

    async loadOldTestSessionStats() {
        try {
            const data = await this.fetchAPI('/api/monitor/status');
            this.updateOldTestSessionStats(data);
        } catch (error) {
            console.error('Failed to load Old Test session stats:', error);
        }
    }

    async loadNewTestSessionStats() {
        try {
            const data = await this.fetchAPI('/api/monitor/status');
            this.updateNewTestSessionStats(data);
        } catch (error) {
            console.error('Failed to load New Test session stats:', error);
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

    updateWorkstationInfo() {
        const workstationStatus = document.getElementById('current-workstation-status');
        const workstationInfo = document.getElementById('workstation-info');
        
        if (this.selectedWorkstation) {
            workstationStatus.className = 'status-indicator status-success';
            workstationStatus.textContent = '已选择';
            
            workstationInfo.innerHTML = `
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <p><strong>工作台ID:</strong> ${this.selectedWorkstation}</p>
                        <p><strong>状态:</strong> <span class="status-indicator status-success">运行中</span></p>
                    </div>
                    <div>
                        <p><strong>测试类型:</strong> Old Test</p>
                        <p><strong>选择时间:</strong> ${new Date().toLocaleString()}</p>
                    </div>
                </div>
            `;
        } else {
            workstationStatus.className = 'status-indicator status-warning';
            workstationStatus.textContent = '未选择';
            workstationInfo.innerHTML = '<p>请先选择工作台</p>';
        }
    }

    updateFileInfoDisplay() {
        const fileStatus = document.getElementById('current-file-status');
        const fileInfoDisplay = document.getElementById('file-info-display');
        
        if (this.selectedFile) {
            fileStatus.className = 'status-indicator status-success';
            fileStatus.textContent = '已选择';
            
            const fileName = this.selectedFile.split('/').pop();
            fileInfoDisplay.innerHTML = `
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <p><strong>文件名:</strong> ${fileName}</p>
                        <p><strong>文件路径:</strong> ${this.selectedFile}</p>
                    </div>
                    <div>
                        <p><strong>测试类型:</strong> New Test</p>
                        <p><strong>选择时间:</strong> ${new Date().toLocaleString()}</p>
                    </div>
                </div>
            `;
        } else {
            fileStatus.className = 'status-indicator status-warning';
            fileStatus.textContent = '未选择';
            fileInfoDisplay.innerHTML = '<p>请先选择数据文件</p>';
        }
    }

    updateLabelConfigDisplay() {
        const labelConfigStatus = document.getElementById('label-config-status');
        const labelConfigDisplay = document.getElementById('label-config-display');
        
        if (this.selectedLabels && Object.keys(this.selectedLabels).length > 0) {
            labelConfigStatus.className = 'status-indicator status-success';
            labelConfigStatus.textContent = '已配置';
            
            let configHtml = '<div class="grid grid-cols-1 gap-2">';
            Object.entries(this.selectedLabels).forEach(([channelId, subtypeId]) => {
                configHtml += `<p><strong>${channelId}:</strong> ${subtypeId}</p>`;
            });
            configHtml += '</div>';
            
            labelConfigDisplay.innerHTML = configHtml;
        } else {
            labelConfigStatus.className = 'status-indicator status-warning';
            labelConfigStatus.textContent = '未配置';
            labelConfigDisplay.innerHTML = '<p>请先配置标签匹配</p>';
        }
    }

    updateOldTestSessionStats(data) {
        const sessionStart = document.getElementById('old-session-start');
        const totalRecords = document.getElementById('old-total-records');
        const totalAlarms = document.getElementById('old-total-alarms');
        const processingSpeed = document.getElementById('old-processing-speed');
        
        if (data.success && data.status) {
            const status = data.status;
            const stats = status.stats || {};
            const fileProvider = status.file_provider || {};
            
            const recordsProcessed = stats.total_records_processed || 0;
            totalRecords.textContent = recordsProcessed;
            
            const alarmsGenerated = stats.total_alarms_generated || 0;
            totalAlarms.textContent = alarmsGenerated;
            
            if (fileProvider.start_time) {
                const startTime = new Date(fileProvider.start_time);
                sessionStart.textContent = startTime.toLocaleString();
            } else {
                sessionStart.textContent = '-';
            }
            
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

    updateNewTestSessionStats(data) {
        const sessionStart = document.getElementById('new-session-start');
        const totalRecords = document.getElementById('new-total-records');
        const totalAlarms = document.getElementById('new-total-alarms');
        const processingSpeed = document.getElementById('new-processing-speed');
        
        if (data.success && data.status) {
            const status = data.status;
            const stats = status.stats || {};
            const fileProvider = status.file_provider || {};
            
            const recordsProcessed = stats.total_records_processed || 0;
            totalRecords.textContent = recordsProcessed;
            
            const alarmsGenerated = stats.total_alarms_generated || 0;
            totalAlarms.textContent = alarmsGenerated;
            
            if (fileProvider.start_time) {
                const startTime = new Date(fileProvider.start_time);
                sessionStart.textContent = startTime.toLocaleString();
            } else {
                sessionStart.textContent = '-';
            }
            
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

    updateSessionStats(data) {
        const sessionStart = document.getElementById('session-start');
        const totalRecords = document.getElementById('total-records');
        const totalAlarms = document.getElementById('total-alarms');
        const processingSpeed = document.getElementById('processing-speed');
        
        if (data.success && data.status) {
            const status = data.status;
            const stats = status.stats || {};
            const fileProvider = status.file_provider || {};
            
            const recordsProcessed = stats.total_records_processed || 0;
            totalRecords.textContent = recordsProcessed;
            
            const alarmsGenerated = stats.total_alarms_generated || 0;
            totalAlarms.textContent = alarmsGenerated;
            
            if (fileProvider.start_time) {
                const startTime = new Date(fileProvider.start_time);
                sessionStart.textContent = startTime.toLocaleString();
            } else {
                sessionStart.textContent = '-';
            }
            
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

    // ==================== Old Test 监控控制 ====================
    async startOldTestMonitoring() {
        console.log('startOldTestMonitoring called');
        
        if (!this.selectedWorkstation) {
            this.showError('请先选择工作台');
            return;
        }

        const configFile = document.getElementById('old-config-selector')?.value;
        const runId = document.getElementById('old-run-id')?.value || undefined;

        try {
            console.log('Sending Old Test monitoring start request...');
            const requestBody = {
                config_path: configFile,
                run_id: runId,
                workstation_id: this.selectedWorkstation
            };

            const data = await this.fetchAPI('/api/monitor/start', {
                method: 'POST',
                body: JSON.stringify(requestBody)
            });

            console.log('Old Test monitoring start response:', data);

            if (data.success) {
                // 保存会话信息
                this.currentSessionId = data.session_id;
                this.currentSessionName = data.session_name;
                
                this.showSuccess(`Old Test 监控启动成功 - ${data.session_name}`);
                this.loadOldTestMonitoringStatus();
                
                // 刷新工作台列表
                if (this.currentPage === 'workstation-selection') {
                    this.loadWorkstationList();
                }
            } else {
                this.showError(data.error || 'Old Test 监控启动失败');
            }
        } catch (error) {
            console.error('Old Test monitoring start error:', error);
            this.showError('启动 Old Test 监控时发生错误');
        }
    }

    async stopOldTestMonitoring() {
        console.log('stopOldTestMonitoring called');
        try {
            const requestBody = {};
            
            // 如果有当前会话ID，停止特定会话
            if (this.currentSessionId) {
                requestBody.session_id = this.currentSessionId;
            }
            
            const data = await this.fetchAPI('/api/monitor/stop', {
                method: 'POST',
                body: JSON.stringify(requestBody)
            });

            console.log('Old Test monitoring stop response:', data);

            if (data.success) {
                this.showSuccess('Old Test 监控已停止');
                this.loadOldTestMonitoringStatus();
                
                // 清除当前会话信息
                this.currentSessionId = null;
                this.currentSessionName = null;
                
                // 刷新工作台列表
                if (this.currentPage === 'workstation-selection') {
                    this.loadWorkstationList();
                }
            } else {
                this.showError(data.error || '停止 Old Test 监控失败');
            }
        } catch (error) {
            console.error('Old Test monitoring stop error:', error);
            this.showError('停止 Old Test 监控时发生错误');
        }
    }

    async startOldTestSimulation() {
        console.log('startOldTestSimulation called');
        
        if (!this.selectedWorkstation) {
            this.showError('请先选择工作台');
            return;
        }

        try {
            console.log('Sending Old Test simulation start request...');
            const requestBody = {
                workstation_id: this.selectedWorkstation
            };

            const data = await this.fetchAPI('/api/monitor/simulation', {
                method: 'POST',
                body: JSON.stringify(requestBody)
            });

            console.log('Old Test simulation start response:', data);

            if (data.success) {
                // 保存会话信息
                this.currentSessionId = data.session_id;
                this.currentSessionName = data.session_name;
                
                this.showSuccess(`Old Test 模拟启动成功 - ${data.session_name}`);
                this.loadOldTestMonitoringStatus();
                
                // 刷新工作台列表
                if (this.currentPage === 'workstation-selection') {
                    this.loadWorkstationList();
                }
            } else {
                this.showError(data.error || 'Old Test 模拟启动失败');
            }
        } catch (error) {
            console.error('Old Test simulation start error:', error);
            this.showError('启动 Old Test 模拟时发生错误');
        }
    }

    // ==================== New Test 监控控制 ====================
    async startNewTestMonitoring() {
        console.log('startNewTestMonitoring called');
        
        if (!this.selectedFile) {
            this.showError('请先选择数据文件');
            return;
        }

        const configFile = document.getElementById('new-config-selector')?.value;
        const runId = document.getElementById('new-run-id')?.value || undefined;
        const workstationId = document.getElementById('new-workstation-id')?.value || '1';

        try {
            console.log('Sending New Test monitoring start request...');
            const requestBody = {
                config_path: configFile,
                run_id: runId,
                file_path: this.selectedFile,
                workstation_id: workstationId
            };

            const data = await this.fetchAPI('/api/monitor/start', {
                method: 'POST',
                body: JSON.stringify(requestBody)
            });

            console.log('New Test monitoring start response:', data);

            if (data.success) {
                // 保存会话信息
                this.currentSessionId = data.session_id;
                this.currentSessionName = data.session_name;
                
                this.showSuccess(`New Test 监控启动成功 - ${data.session_name}`);
                this.loadNewTestMonitoringStatus();
            } else {
                this.showError(data.error || 'New Test 监控启动失败');
            }
        } catch (error) {
            console.error('New Test monitoring start error:', error);
            this.showError('启动 New Test 监控时发生错误');
        }
    }

    async stopNewTestMonitoring() {
        console.log('stopNewTestMonitoring called');
        try {
            const requestBody = {};
            
            // 如果有当前会话ID，停止特定会话
            if (this.currentSessionId) {
                requestBody.session_id = this.currentSessionId;
            }
            
            const data = await this.fetchAPI('/api/monitor/stop', {
                method: 'POST',
                body: JSON.stringify(requestBody)
            });

            console.log('New Test monitoring stop response:', data);

            if (data.success) {
                this.showSuccess('New Test 监控已停止');
                this.loadNewTestMonitoringStatus();
                
                // 清除当前会话信息
                this.currentSessionId = null;
                this.currentSessionName = null;
            } else {
                this.showError(data.error || '停止 New Test 监控失败');
            }
        } catch (error) {
            console.error('New Test monitoring stop error:', error);
            this.showError('停止 New Test 监控时发生错误');
        }
    }

    async startNewTestSimulation() {
        console.log('startNewTestSimulation called');
        
        if (!this.selectedFile) {
            this.showError('请先选择数据文件');
            return;
        }

        try {
            console.log('Sending New Test simulation start request...');
            const requestBody = {
                file_path: this.selectedFile,
                workstation_id: '1'
            };

            const data = await this.fetchAPI('/api/monitor/simulation', {
                method: 'POST',
                body: JSON.stringify(requestBody)
            });

            console.log('New Test simulation start response:', data);

            if (data.success) {
                // 保存会话信息
                this.currentSessionId = data.session_id;
                this.currentSessionName = data.session_name;
                
                this.showSuccess(`New Test 模拟启动成功 - ${data.session_name}`);
                this.loadNewTestMonitoringStatus();
            } else {
                this.showError(data.error || 'New Test 模拟启动失败');
            }
        } catch (error) {
            console.error('New Test simulation start error:', error);
            this.showError('启动 New Test 模拟时发生错误');
        }
    }

    // ==================== 通用监控控制 ====================
    async startMonitoring() {
        console.log('startMonitoring called');
        
        const configFile = document.getElementById('config-selector')?.value;
        const runId = document.getElementById('run-id')?.value || undefined;

        if (this.testType === 'new' && !this.selectedFile) {
            this.showError('请先选择数据文件');
            return;
        }

        try {
            console.log('Sending monitoring start request...');
            const requestBody = {
                    config_path: configFile,
                    run_id: runId
            };

            if (this.testType === 'new') {
                requestBody.file_path = this.selectedFile;
            } else if (this.testType === 'old' && this.selectedWorkstation) {
                requestBody.workstation_id = this.selectedWorkstation;
            }

            const data = await this.fetchAPI('/api/monitor/start', {
                method: 'POST',
                body: JSON.stringify(requestBody)
            });

            console.log('Monitoring start response:', data);

            if (data.success) {
                // 保存会话信息
                this.currentSessionId = data.session_id;
                this.currentSessionName = data.session_name;
                
                this.showSuccess(`监控启动成功 - ${data.session_name}`);
                this.loadMonitoringStatus();
                
                // 刷新工作台列表
                if (this.currentPage === 'workstation-selection') {
                    this.loadWorkstationList();
                }
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
            const requestBody = {};
            
            // 如果有当前会话ID，停止特定会话
            if (this.currentSessionId) {
                requestBody.session_id = this.currentSessionId;
            }
            
            const data = await this.fetchAPI('/api/monitor/stop', {
                method: 'POST',
                body: JSON.stringify(requestBody)
            });

            console.log('Monitoring stop response:', data);

            if (data.success) {
                this.showSuccess('监控已停止');
                this.loadMonitoringStatus();
                
                // 清除当前会话信息
                this.currentSessionId = null;
                this.currentSessionName = null;
                
                // 刷新工作台列表
                if (this.currentPage === 'workstation-selection') {
                    this.loadWorkstationList();
                }
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
        
        if (this.testType === 'new' && !this.selectedFile) {
            this.showError('请先选择数据文件');
            return;
        }

        try {
            console.log('Sending simulation start request...');
            const requestBody = {};

            if (this.testType === 'new') {
                requestBody.file_path = this.selectedFile;
                requestBody.workstation_id = '1';
            } else if (this.testType === 'old' && this.selectedWorkstation) {
                requestBody.workstation_id = this.selectedWorkstation;
            }

            const data = await this.fetchAPI('/api/monitor/simulation', {
                method: 'POST',
                body: JSON.stringify(requestBody)
            });

            console.log('Simulation start response:', data);

            if (data.success) {
                // 保存会话信息
                this.currentSessionId = data.session_id;
                this.currentSessionName = data.session_name;
                
                this.showSuccess(`模拟启动成功 - ${data.session_name}`);
                this.loadMonitoringStatus();
                
                // 刷新工作台列表
                if (this.currentPage === 'workstation-selection') {
                    this.loadWorkstationList();
                }
            } else {
                this.showError(data.error || '模拟启动失败');
            }
        } catch (error) {
            console.error('Simulation start error:', error);
            this.showError('启动模拟时发生错误');
        }
    }

    // ==================== Old Test 告警和日志管理 ====================
    clearOldTestAlarms() {
        this.alarms = [];
        this.updateOldTestAlarmTable();
        this.showSuccess('Old Test 告警记录已清空');
    }

    clearOldTestLogs() {
        this.logs = [];
        this.updateOldTestLogViewer();
        this.showSuccess('Old Test 日志已清空');
    }

    // ==================== New Test 告警和日志管理 ====================
    clearNewTestAlarms() {
        this.alarms = [];
        this.updateNewTestAlarmTable();
        this.showSuccess('New Test 告警记录已清空');
    }

    clearNewTestLogs() {
        this.logs = [];
        this.updateNewTestLogViewer();
        this.showSuccess('New Test 日志已清空');
    }

    // ==================== 通用告警和日志管理 ====================
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

    updateOldTestAlarmTable() {
        const tbody = document.getElementById('old-alarm-tbody');
        
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

    updateNewTestAlarmTable() {
        const tbody = document.getElementById('new-alarm-tbody');
        
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

    updateOldTestLogViewer() {
        fetch('/api/logs')
            .then(response => response.json())
            .then(data => {
                if (data.success && data.logs) {
                    const logContainer = document.getElementById('old-log-viewer');
                    if (logContainer) {
                        logContainer.innerHTML = '';
                        
                        data.logs.forEach(log => {
                            const logEntry = document.createElement('div');
                            logEntry.className = 'log-entry';
                            logEntry.textContent = log;
                            logContainer.appendChild(logEntry);
                        });
                        
                        logContainer.scrollTop = logContainer.scrollHeight;
                    }
                }
            })
            .catch(error => {
                console.error('Failed to load Old Test logs:', error);
            });
    }

    updateNewTestLogViewer() {
        fetch('/api/logs')
            .then(response => response.json())
            .then(data => {
                if (data.success && data.logs) {
                    const logContainer = document.getElementById('new-log-viewer');
                    if (logContainer) {
                        logContainer.innerHTML = '';
                        
                        data.logs.forEach(log => {
                            const logEntry = document.createElement('div');
                            logEntry.className = 'log-entry';
                            logEntry.textContent = log;
                            logContainer.appendChild(logEntry);
                        });
                        
                        logContainer.scrollTop = logContainer.scrollHeight;
                    }
                }
            })
            .catch(error => {
                console.error('Failed to load New Test logs:', error);
            });
    }

    updateLogViewer() {
        fetch('/api/logs')
            .then(response => response.json())
            .then(data => {
                if (data.success && data.logs) {
                    const logContainer = document.getElementById('log-viewer');
                    if (logContainer) {
                        logContainer.innerHTML = '';
                        
                        data.logs.forEach(log => {
                            const logEntry = document.createElement('div');
                            logEntry.className = 'log-entry';
                            logEntry.textContent = log;
                            logContainer.appendChild(logEntry);
                        });
                        
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

    startOldTestAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
        
        this.refreshInterval = setInterval(() => {
            if (this.currentPage === 'old-test-monitor-panel') {
                this.loadOldTestMonitoringStatus();
                this.loadOldTestSessionStats();
                this.updateOldTestAlarmTable();
                this.updateOldTestLogViewer();
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
                this.updateNewTestAlarmTable();
                this.updateNewTestLogViewer();
            }
        }, 2000);
    }

    startAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
        
        this.refreshInterval = setInterval(() => {
            if (this.currentPage === 'monitor-panel') {
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

    disableConfirmButton() {
        const confirmButton = document.querySelector('button[onclick="app.confirmAndGoToMonitor()"]');
        if (confirmButton) {
            confirmButton.disabled = true;
            confirmButton.classList.add('disabled');
            confirmButton.style.opacity = '0.5';
            confirmButton.style.cursor = 'not-allowed';
        }
    }

    enableConfirmButton() {
        const confirmButton = document.querySelector('button[onclick="app.confirmAndGoToMonitor()"]');
        if (confirmButton) {
            confirmButton.disabled = false;
            confirmButton.classList.remove('disabled');
            confirmButton.style.opacity = '1';
            confirmButton.style.cursor = 'pointer';
        }
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