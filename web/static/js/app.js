/**
 * Smart Monitor Web - Main Application JavaScript
 * Uses native JavaScript, no framework dependencies
 * New page flow: Test Selection -> Workstation Selection/File Configuration -> Monitoring Panel
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

    // ==================== Navigation Management ====================
    navigateTo(page) {
        // If leaving monitoring page, stop auto-refresh
        if ((this.currentPage === 'old-test-monitor-panel' || this.currentPage === 'new-test-monitor-panel') && 
            page !== 'old-test-monitor-panel' && page !== 'new-test-monitor-panel') {
            this.stopAutoRefresh();
        }

        // Hide all pages
        document.querySelectorAll('.page').forEach(pageElement => {
            pageElement.classList.remove('active');
            pageElement.classList.add('hidden');
        });

        // Show target page
        const targetPage = document.getElementById(page);
        if (targetPage) {
            targetPage.classList.remove('hidden');
            targetPage.classList.add('active');
        }

        this.currentPage = page;
        this.loadPage(page);
        
        // If it's a monitoring panel, record current session information
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

    // ==================== Test Selection Functions ====================
    selectTest(testType) {
        // Reset all states
        this.testType = testType;
        this.selectedFile = null;
        this.selectedLabels = {};
        this.selectedWorkstation = null;
        this.currentSessionId = null;
        this.currentSessionName = null;
        
        if (testType === 'old') {
            // Force jump to workstation selection page
            this.navigateTo('workstation-selection');
            this.showSuccess('Selected Old Test, please select workstation');
        } else if (testType === 'new') {
            // Jump to file configuration page
            this.navigateTo('file-config');
            this.showSuccess('Selected New Test, please configure files and labels');
        }
    }

    showTestSelection() {
        // Return to test selection page
        this.navigateTo('test-selection');
        
        // Reset all states
        this.testType = null;
        this.selectedWorkstation = null;
        this.selectedFile = null;
        this.selectedLabels = {};
        this.currentSessionId = null;
        this.currentSessionName = null;
        
        // Clear file selector
        const fileSelector = document.getElementById('file-selector');
        if (fileSelector) {
            fileSelector.value = '';
        }
        
        // Clear file information
        const fileInfo = document.getElementById('file-info');
        if (fileInfo) {
            fileInfo.innerHTML = '<p>Please select a data file to view details</p>';
        }
        
        // Clear label selection
        const labelSelection = document.getElementById('label-selection');
        if (labelSelection) {
            labelSelection.innerHTML = '<p>Please select a data file first to configure label matching</p>';
        }
        
        // Reset status indicator
        const statusIndicator = document.querySelector('.label-selection-container .status-indicator');
        if (statusIndicator) {
            statusIndicator.className = 'status-indicator status-info';
            statusIndicator.textContent = 'Waiting for file selection';
        }
        
        // Disable confirm button
        this.disableConfirmButton();
    }

    // ==================== Test Selection Page ====================
    loadTestSelection() {
        // Reset all states
        this.testType = null;
        this.selectedWorkstation = null;
        this.selectedFile = null;
        this.selectedLabels = {};
    }

    // ==================== Workstation Selection Page ====================
    async loadWorkstationSelection() {
        // Reset workstation selection page state
        this.selectedWorkstation = null;
        this.currentSessionId = null;
        this.currentSessionName = null;
        
        // Clear workstation selection state
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
            this.showError('Failed to load workstation list');
        }
    }

    updateWorkstationList(data) {
        const workstationList = document.getElementById('workstation-list');
        
        if (data.success && data.workstations && data.workstations.length > 0) {
            let html = '';
            
            data.workstations.forEach(workstation => {
                const statusClass = workstation.status === 'running' ? 'running' : 'stopped';
                const statusText = workstation.status === 'running' ? 'Running' : 'Stopped';
                
                html += `
                    <div class="workstation-item">
                        <div class="workstation-header">
                            <div class="workstation-name">${workstation.name}</div>
                            <div class="workstation-status ${statusClass}">${statusText}</div>
                        </div>
                        <div class="workstation-details">
                            <p><strong>ID:</strong> ${workstation.id}</p>
                            <p><strong>Start Time:</strong> ${workstation.start_time || '-'}</p>
                            <p><strong>Records Processed:</strong> ${workstation.records_processed || 0}</p>
                            <p><strong>Alarms Generated:</strong> ${workstation.alarms_generated || 0}</p>
                            <p><strong>Test Type:</strong> ${
                                workstation.test_type === 'new' ? 'New Test' : 
                                workstation.test_type === 'simulation' ? 'Simulation Test' : 'Old Test'
                            }</p>
                        </div>
                        <div class="workstation-actions">
                            <button class="btn btn-primary btn-sm" onclick="app.selectWorkstation('${workstation.id}')">
                                <i class="fas fa-play"></i>
                                Select This Workstation
                            </button>
                            <button class="btn btn-warning btn-sm" onclick="app.stopWorkstation('${workstation.id}')">
                                <i class="fas fa-stop"></i>
                                Stop Session
                            </button>
                        </div>
                    </div>
                `;
            });
            
            workstationList.innerHTML = html;
        } else {
            workstationList.innerHTML = '<div class="text-center text-secondary">No available workstations</div>';
        }
    }

    selectWorkstation(workstationId) {
        this.selectedWorkstation = workstationId;
        
        // Update selection state
        document.querySelectorAll('.workstation-item').forEach(item => {
            item.classList.remove('active');
        });
        
        const selectedItem = document.querySelector(`[onclick="app.selectWorkstation('${workstationId}')"]`);
        if (selectedItem) {
            selectedItem.classList.add('active');
        }
        
                    // Jump to Old Test monitoring panel
            this.navigateTo('old-test-monitor-panel');
            this.showSuccess(`Selected workstation: ${workstationId}`);
    }

    async stopWorkstation(workstationId) {
        try {
            const data = await this.fetchAPI('/api/monitor/stop', {
                method: 'POST',
                body: JSON.stringify({ session_id: workstationId })
            });

            if (data.success) {
                this.showSuccess(`Workstation ${workstationId} stopped`);
                
                // Refresh workstation list
                this.loadWorkstationList();
                
                // If stopping the currently selected workstation, clear selection
                if (this.selectedWorkstation === workstationId) {
                    this.selectedWorkstation = null;
                }
            } else {
                this.showError(data.error || 'Failed to stop workstation');
            }
        } catch (error) {
            console.error('Stop workstation error:', error);
            this.showError('Error occurred while stopping workstation');
        }
    }

    // ==================== File Configuration Page ====================
    async loadFileConfig() {
        // Reset file configuration page state
        this.selectedFile = null;
        this.selectedLabels = {};
        this.currentSessionId = null;
        this.currentSessionName = null;
        
        // Clear file selector
        const fileSelector = document.getElementById('file-selector');
        if (fileSelector) {
            fileSelector.value = '';
        }
        
        // Clear file information
        const fileInfo = document.getElementById('file-info');
        if (fileInfo) {
            fileInfo.innerHTML = '<p>Please select a data file to view details</p>';
        }
        
        // Clear label selection
        const labelSelection = document.getElementById('label-selection');
        if (labelSelection) {
            labelSelection.innerHTML = '<p>Please select a data file first to configure label matching</p>';
        }
        
        // Reset status indicator
        const statusIndicator = document.querySelector('.label-selection-container .status-indicator');
        if (statusIndicator) {
            statusIndicator.className = 'status-indicator status-info';
            statusIndicator.textContent = 'Waiting for file selection';
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
            this.showError('Failed to load file list');
        }
    }

    updateFileSelector(data) {
        const fileSelector = document.getElementById('file-selector');
        
        if (data.success && data.files) {
            fileSelector.innerHTML = '<option value="">Please select data file...</option>';
            
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
            fileSelector.innerHTML = '<option value="">No data files found</option>';
        }
    }

    async onFileSelected(filePath) {
        if (!filePath) {
            this.updateFileInfo('Please select a data file to view details');
            return;
        }

        this.selectedFile = filePath;
        
        const statusIndicator = document.querySelector('.card-header .status-indicator');
        if (statusIndicator) {
            statusIndicator.className = 'status-indicator status-info';
            statusIndicator.textContent = 'Loading label configuration...';
        }
        
        try {
            const fileInfo = await this.fetchAPI(`/api/file/info/${filePath.split('/').pop()}`);
            this.updateFileInfo(fileInfo);
            
            const workstationInfo = await this.fetchAPI('/api/file/infer-workstation', {
                method: 'POST',
                body: JSON.stringify({ file_path: filePath })
            });
            
            if (workstationInfo.success && workstationInfo.workstation_id) {
                this.showSuccess(`Auto-inferred workstation ID: ${workstationInfo.workstation_id}`);
            }
            
            await this.loadLabelConfiguration();
            this.enableConfirmButton();
            
        } catch (error) {
            console.error('Failed to get file info:', error);
            this.showError('Failed to get file information');
            
            if (statusIndicator) {
                statusIndicator.className = 'status-indicator status-error';
                statusIndicator.textContent = 'Failed to get file information';
            }
        }
    }

    onFileDeselected() {
        this.selectedFile = null;
        
        const fileInfo = document.getElementById('file-info');
        if (fileInfo) {
            fileInfo.innerHTML = '<p>Please select a data file to view details</p>';
        }
        
        const labelSelection = document.getElementById('label-selection');
        if (labelSelection) {
            labelSelection.innerHTML = '<p>Please select a data file first to configure label matching</p>';
        }
        
        const statusIndicator = document.querySelector('.card-header .status-indicator');
        if (statusIndicator) {
            statusIndicator.className = 'status-indicator status-info';
            statusIndicator.textContent = 'Waiting for file selection';
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
                        <p><strong>File Name:</strong> ${info.name}</p>
                        <p><strong>File Size:</strong> ${info.size_mb} MB</p>
                        <p><strong>Modified Time:</strong> ${new Date(info.modified * 1000).toLocaleString()}</p>
                    </div>
                    <div>
                        <p><strong>Validation Status:</strong> <span class="status-indicator status-success">Valid</span></p>
                        <p><strong>Workstation ID:</strong> ${info.workstation_id || 'Auto-inferred'}</p>
                    </div>
                </div>
            `;
        } else {
            fileInfo.innerHTML = '<p class="text-error">Unable to get file information</p>';
        }
    }

    async loadLabelConfiguration() {
        try {
            const data = await this.fetchAPI('/api/config/labels');
            this.updateLabelSelection(data);
        } catch (error) {
            console.error('Failed to load label configuration:', error);
            this.showError('Failed to load label configuration');
        }
    }

    updateLabelSelection(data) {
        const labelSelection = document.getElementById('label-selection');
        const statusIndicator = document.querySelector('.card-header .status-indicator');
        
        if (data.categories && Object.keys(data.categories).length > 0) {
            if (statusIndicator) {
                statusIndicator.className = 'status-indicator status-success';
                statusIndicator.textContent = 'Label configuration loaded';
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
                                <div class="label-radio-group" data-channel-name="${channel.channel_id}">
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
                statusIndicator.textContent = 'Failed to load label configuration';
            }
            labelSelection.innerHTML = '<p class="text-error">Unable to load label configuration</p>';
        }
    }

    setupLabelSelectionEvents() {
        const radios = document.querySelectorAll('.label-radio-group input[type="radio"]');
        radios.forEach(radio => {
            radio.addEventListener('change', (e) => this.onLabelChoiceChange(e));
        });
    }

    onLabelChoiceChange(event) {
        const channelId = event.target.name.replace('label_', '');
        const subtypeId = event.target.value;
        this.selectedLabels[channelId] = subtypeId;
        console.log('Label selection updated:', this.selectedLabels);

        // Reset all radio visual states in the same group
        const groupRadios = document.querySelectorAll(`input[name="label_${channelId}"]`);
        groupRadios.forEach(radio => {
            const labelElement = radio.closest('.label-radio');
            if (labelElement) {
                labelElement.style.borderColor = '';
                labelElement.style.backgroundColor = '';
            }
        });

        // Highlight current selection
        const currentLabelElement = event.target.closest('.label-radio');
        if (currentLabelElement) {
            currentLabelElement.style.borderColor = 'var(--primary-color)';
            currentLabelElement.style.backgroundColor = 'rgba(37, 99, 235, 0.1)';
        }
    }

    async confirmAndGoToMonitor() {
        if (!this.selectedFile) {
            this.showError('Please select a data file first');
            return;
        }
        if (Object.keys(this.selectedLabels).length === 0) {
            this.showError('Please configure label matching');
            return;
        }

        try {
            // Save label configuration first
            const saveResult = await this.fetchAPI('/api/config/labels/save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ selected_labels: this.selectedLabels })
            });

            if (!saveResult.success) {
                this.showError('Failed to save label configuration');
                return;
            }

            this.showSuccess('Configuration saved. Starting monitoring...');

            // Auto-start monitoring
            await this.startNewTestMonitoring();
        } catch (error) {
            console.error('Failed to confirm configuration:', error);
            this.showError('Failed to confirm configuration');
        }
    }

    async loadLastLabelSelection() {
        try {
            console.log('loadLastLabelSelection called');
            const data = await this.fetchAPI('/api/config/labels/load');
            if (data.success && data.labels) {
                // API response data structure is data.labels.labels
                this.selectedLabels = data.labels.labels || data.labels;
                console.log('Set selectedLabels to:', this.selectedLabels);
                this.updateLabelSelectionFromSaved();
                this.showSuccess('Loaded last configuration');
            } else {
                this.showError('No saved configuration found');
            }
        } catch (error) {
            console.error('Failed to load last selection:', error);
            this.showError('Failed to load last configuration');
        }
    }

    updateLabelSelectionFromSaved() {
        console.log('updateLabelSelectionFromSaved called with:', this.selectedLabels);
        Object.entries(this.selectedLabels).forEach(([channelId, subtypeId]) => {
            const radio = document.querySelector(`input[name="label_${channelId}"][value="${subtypeId}"]`);
            console.log(`Looking for radio: label_${channelId}, value: ${subtypeId}, found:`, radio);
            if (radio) {
                radio.checked = true;
                // Add visual feedback for selected state
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

    // New: Quick Match (Test) - select first available option per channel
    quickMatchTest() {
        try {
            const groups = document.querySelectorAll('.label-radio-group');
            let matchedCount = 0;
            groups.forEach(group => {
                const channelName = group.getAttribute('data-channel-name');
                const radios = group.querySelectorAll('input[type="radio"]');
                if (radios.length > 0) {
                    const radio = radios[0];
                    radio.checked = true;
                    const channelId = radio.name.replace('label_', '');
                    const subtypeId = radio.value;
                    this.selectedLabels[channelId] = subtypeId;
                    const labelElement = radio.closest('.label-radio');
                    if (labelElement) {
                        // Reset peers
                        group.querySelectorAll('.label-radio').forEach(el => {
                            el.style.borderColor = '';
                            el.style.backgroundColor = '';
                        });
                        // Highlight selection
                        labelElement.style.borderColor = 'var(--primary-color)';
                        labelElement.style.backgroundColor = 'rgba(37, 99, 235, 0.1)';
                    }
                    matchedCount += 1;
                }
            });
            this.showSuccess(`Quick matched ${matchedCount} channels (test)`);
        } catch (error) {
            console.error('Quick match failed:', error);
            this.showError('Quick match failed');
        }
    }

    // ==================== Old Test Monitoring Panel Page ====================
    async loadOldTestMonitorPanel() {
        console.log('Loading Old Test monitor panel - Selected workstation:', this.selectedWorkstation);
        
        // Update workstation information
        this.updateWorkstationInfo();
        
        await this.loadOldTestMonitoringStatus();
        await this.loadOldTestSessionStats();
        this.startOldTestAutoRefresh();
    }

    // ==================== New Test Monitoring Panel Page ====================
    async loadNewTestMonitorPanel() {
        console.log('Loading New Test monitor panel - Current session:', this.currentSessionId, this.currentSessionName);
        
        // Update file information
        this.updateFileInfoDisplay();
        
        // Update label configuration display
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
                statusElement.textContent = 'Running';
                
                let detailsHtml = '';
                
                if (this.selectedWorkstation) {
                    detailsHtml += `<p><strong>Workstation ID:</strong> ${this.selectedWorkstation}</p>`;
                }
                
                if (status.web_session_id) {
                    detailsHtml += `<p><strong>Session ID:</strong> ${status.web_session_id}</p>`;
                }
                
                if (status.web_current_file) {
                    detailsHtml += `<p><strong>Current File:</strong> ${status.web_current_file}</p>`;
                }
                
                if (fileProvider.total_records_pushed !== undefined) {
                    detailsHtml += `<p><strong>Records Pushed:</strong> ${fileProvider.total_records_pushed}</p>`;
                }
                
                if (status.stats && status.stats.total_records_processed !== undefined) {
                    detailsHtml += `<p><strong>Records Processed:</strong> ${status.stats.total_records_processed}</p>`;
                }
                
                if (status.stats && status.stats.total_alarms_generated !== undefined) {
                    detailsHtml += `<p><strong>Alarms Generated:</strong> ${status.stats.total_alarms_generated}</p>`;
                }
                
                if (fileProvider.simulation_duration !== undefined) {
                    detailsHtml += `<p><strong>Simulation Duration:</strong> ${fileProvider.simulation_duration.toFixed(1)}s</p>`;
                }
                
                detailsElement.innerHTML = detailsHtml;
            } else {
                statusElement.className = 'status-indicator status-warning';
                statusElement.textContent = 'Stopped';
                detailsElement.innerHTML = '<p>Monitoring stopped</p>';
            }
        } else {
            statusElement.className = 'status-indicator status-error';
            statusElement.textContent = 'Error';
            detailsElement.innerHTML = '<p>Unable to get monitoring status</p>';
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
                statusElement.textContent = 'Running';
                
                let detailsHtml = '';
                
                if (this.selectedFile) {
                    const fileName = this.selectedFile.split('/').pop();
                    detailsHtml += `<p><strong>Current File:</strong> ${fileName}</p>`;
                }
                
                if (status.web_session_id) {
                    detailsHtml += `<p><strong>Session ID:</strong> ${status.web_session_id}</p>`;
                }
                
                if (status.web_current_file) {
                    detailsHtml += `<p><strong>File Path:</strong> ${status.web_current_file}</p>`;
                }
                
                if (fileProvider.total_records_pushed !== undefined) {
                    detailsHtml += `<p><strong>Records Pushed:</strong> ${fileProvider.total_records_pushed}</p>`;
                }
                
                if (status.stats && status.stats.total_records_processed !== undefined) {
                    detailsHtml += `<p><strong>Records Processed:</strong> ${status.stats.total_records_processed}</p>`;
                }
                
                if (status.stats && status.stats.total_alarms_generated !== undefined) {
                    detailsHtml += `<p><strong>Alarms Generated:</strong> ${status.stats.total_alarms_generated}</p>`;
                }
                
                if (fileProvider.simulation_duration !== undefined) {
                    detailsHtml += `<p><strong>Simulation Duration:</strong> ${fileProvider.simulation_duration.toFixed(1)}s</p>`;
                }
                
                detailsElement.innerHTML = detailsHtml;
            } else {
                statusElement.className = 'status-indicator status-warning';
                statusElement.textContent = 'Stopped';
                detailsElement.innerHTML = '<p>Monitoring stopped</p>';
            }
        } else {
            statusElement.className = 'status-indicator status-error';
            statusElement.textContent = 'Error';
            detailsElement.innerHTML = '<p>Unable to get monitoring status</p>';
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
                statusElement.textContent = 'Running';
                
                let detailsHtml = '';
                
                if (status.web_session_id) {
                    detailsHtml += `<p><strong>Session ID:</strong> ${status.web_session_id}</p>`;
                }
                
                if (status.web_current_file) {
                    detailsHtml += `<p><strong>Current File:</strong> ${status.web_current_file}</p>`;
                }
                
                if (fileProvider.total_records_pushed !== undefined) {
                    detailsHtml += `<p><strong>Records Pushed:</strong> ${fileProvider.total_records_pushed}</p>`;
                }
                
                if (status.stats && status.stats.total_records_processed !== undefined) {
                    detailsHtml += `<p><strong>Records Processed:</strong> ${status.stats.total_records_processed}</p>`;
                }
                
                if (status.stats && status.stats.total_alarms_generated !== undefined) {
                    detailsHtml += `<p><strong>Alarms Generated:</strong> ${status.stats.total_alarms_generated}</p>`;
                }
                
                if (fileProvider.simulation_duration !== undefined) {
                    detailsHtml += `<p><strong>Simulation Duration:</strong> ${fileProvider.simulation_duration.toFixed(1)}s</p>`;
                }
                
                detailsElement.innerHTML = detailsHtml;
            } else {
                statusElement.className = 'status-indicator status-warning';
                statusElement.textContent = 'Stopped';
                detailsElement.innerHTML = '<p>Monitoring stopped</p>';
            }
        } else {
            statusElement.className = 'status-indicator status-error';
            statusElement.textContent = 'Error';
            detailsElement.innerHTML = '<p>Unable to get monitoring status</p>';
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
            workstationStatus.textContent = 'Selected';
            
            workstationInfo.innerHTML = `
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <p><strong>Workstation ID:</strong> ${this.selectedWorkstation}</p>
                        <p><strong>Status:</strong> <span class="status-indicator status-success">Running</span></p>
                    </div>
                    <div>
                        <p><strong>Test Type:</strong> Old Test</p>
                        <p><strong>Selection Time:</strong> ${new Date().toLocaleString()}</p>
                    </div>
                </div>
            `;
        } else {
            workstationStatus.className = 'status-indicator status-warning';
            workstationStatus.textContent = 'Not Selected';
            workstationInfo.innerHTML = '<p>Please select a workstation first</p>';
        }
    }

    updateFileInfoDisplay() {
        const fileStatus = document.getElementById('current-file-status');
        const fileInfoDisplay = document.getElementById('file-info-display');
        
        if (this.selectedFile) {
            fileStatus.className = 'status-indicator status-success';
            fileStatus.textContent = 'Selected';
            
            const fileName = this.selectedFile.split('/').pop();
            fileInfoDisplay.innerHTML = `
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <p><strong>File Name:</strong> ${fileName}</p>
                        <p><strong>File Path:</strong> ${this.selectedFile}</p>
                    </div>
                    <div>
                        <p><strong>Test Type:</strong> New Test</p>
                        <p><strong>Selection Time:</strong> ${new Date().toLocaleString()}</p>
                    </div>
                </div>
            `;
        } else {
            fileStatus.className = 'status-indicator status-warning';
            fileStatus.textContent = 'Not Selected';
            fileInfoDisplay.innerHTML = '<p>Please select a data file first</p>';
        }
    }

    updateLabelConfigDisplay() {
        const labelConfigStatus = document.getElementById('label-config-status');
        const labelConfigDisplay = document.getElementById('label-config-display');
        
        if (this.selectedLabels && Object.keys(this.selectedLabels).length > 0) {
            labelConfigStatus.className = 'status-indicator status-success';
            labelConfigStatus.textContent = 'Configured';
            
            let configHtml = '<div class="grid grid-cols-1 gap-2">';
            Object.entries(this.selectedLabels).forEach(([channelId, subtypeId]) => {
                configHtml += `<p><strong>${channelId}:</strong> ${subtypeId}</p>`;
            });
            configHtml += '</div>';
            
            labelConfigDisplay.innerHTML = configHtml;
        } else {
            labelConfigStatus.className = 'status-indicator status-warning';
            labelConfigStatus.textContent = 'Not Configured';
            labelConfigDisplay.innerHTML = '<p>Please configure label matching first</p>';
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

    // ==================== Old Test Monitoring Control ====================
    async startOldTestMonitoring() {
        console.log('startOldTestMonitoring called');
        
        if (!this.selectedWorkstation) {
            this.showError('Please select a workstation first');
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
                // Save session information
                this.currentSessionId = data.session_id;
                this.currentSessionName = data.session_name;
                
                this.showSuccess(`Old Test monitoring started successfully - ${data.session_name}`);
                this.loadOldTestMonitoringStatus();
                
                // Refresh workstation list
                if (this.currentPage === 'workstation-selection') {
                    this.loadWorkstationList();
                }
            } else {
                this.showError(data.error || 'Failed to start Old Test monitoring');
            }
        } catch (error) {
            console.error('Old Test monitoring start error:', error);
            this.showError('Error occurred while starting Old Test monitoring');
        }
    }

    async stopOldTestMonitoring() {
        console.log('stopOldTestMonitoring called');
        try {
            const requestBody = {};
            
            // If there is a current session ID, stop the specific session
            if (this.currentSessionId) {
                requestBody.session_id = this.currentSessionId;
            }
            
            const data = await this.fetchAPI('/api/monitor/stop', {
                method: 'POST',
                body: JSON.stringify(requestBody)
            });

            console.log('Old Test monitoring stop response:', data);

            if (data.success) {
                this.showSuccess('Old Test monitoring stopped');
                this.loadOldTestMonitoringStatus();
                
                // Clear current session information
                this.currentSessionId = null;
                this.currentSessionName = null;
                
                // Refresh workstation list
                if (this.currentPage === 'workstation-selection') {
                    this.loadWorkstationList();
                }
            } else {
                this.showError(data.error || 'Failed to stop Old Test monitoring');
            }
        } catch (error) {
            console.error('Old Test monitoring stop error:', error);
            this.showError('Error occurred while stopping Old Test monitoring');
        }
    }

    async startOldTestSimulation() {
        console.log('startOldTestSimulation called');
        
        if (!this.selectedWorkstation) {
            this.showError('Please select a workstation first');
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
                // Save session information
                this.currentSessionId = data.session_id;
                this.currentSessionName = data.session_name;
                
                this.showSuccess(`Old Test simulation started successfully - ${data.session_name}`);
                this.loadOldTestMonitoringStatus();
                
                // Refresh workstation list
                if (this.currentPage === 'workstation-selection') {
                    this.loadWorkstationList();
                }
            } else {
                this.showError(data.error || 'Failed to start Old Test simulation');
            }
        } catch (error) {
            console.error('Old Test simulation start error:', error);
            this.showError('Error occurred while starting Old Test simulation');
        }
    }

    // ==================== New Test Monitoring Control ====================
    async startNewTestMonitoring() {
        console.log('startNewTestMonitoring called');
        
        if (!this.selectedFile) {
            this.showError('Please select a data file first');
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
                // Save session information
                this.currentSessionId = data.session_id;
                this.currentSessionName = data.session_name;
                
                this.showSuccess(`New Test monitoring started successfully - ${data.session_name}`);
                this.loadNewTestMonitoringStatus();
            } else {
                this.showError(data.error || 'Failed to start New Test monitoring');
            }
        } catch (error) {
            console.error('New Test monitoring start error:', error);
            this.showError('Error occurred while starting New Test monitoring');
        }
    }

    async stopNewTestMonitoring() {
        console.log('stopNewTestMonitoring called');
        try {
            const requestBody = {};
            
            // If there is a current session ID, stop the specific session
            if (this.currentSessionId) {
                requestBody.session_id = this.currentSessionId;
            }
            
            const data = await this.fetchAPI('/api/monitor/stop', {
                method: 'POST',
                body: JSON.stringify(requestBody)
            });

            console.log('New Test monitoring stop response:', data);

            if (data.success) {
                this.showSuccess('New Test monitoring stopped');
                this.loadNewTestMonitoringStatus();
                
                // Clear current session information
                this.currentSessionId = null;
                this.currentSessionName = null;
            } else {
                this.showError(data.error || 'Failed to stop New Test monitoring');
            }
        } catch (error) {
            console.error('New Test monitoring stop error:', error);
            this.showError('Error occurred while stopping New Test monitoring');
        }
    }

    async startNewTestSimulation() {
        console.log('startNewTestSimulation called');
        
        if (!this.selectedFile) {
            this.showError('Please select a data file first');
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
                // Save session information
                this.currentSessionId = data.session_id;
                this.currentSessionName = data.session_name;
                
                this.showSuccess(`New Test simulation started successfully - ${data.session_name}`);
                this.loadNewTestMonitoringStatus();
            } else {
                this.showError(data.error || 'Failed to start New Test simulation');
            }
        } catch (error) {
            console.error('New Test simulation start error:', error);
            this.showError('Error occurred while starting New Test simulation');
        }
    }

    // ==================== General Monitoring Control ====================
    async startMonitoring() {
        console.log('startMonitoring called');
        
        const configFile = document.getElementById('config-selector')?.value;
        const runId = document.getElementById('run-id')?.value || undefined;

        if (this.testType === 'new' && !this.selectedFile) {
            this.showError('Please select a data file first');
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
                // Save session information
                this.currentSessionId = data.session_id;
                this.currentSessionName = data.session_name;
                
                this.showSuccess(`Monitoring started successfully - ${data.session_name}`);
                this.loadMonitoringStatus();
                
                // Refresh workstation list
                if (this.currentPage === 'workstation-selection') {
                    this.loadWorkstationList();
                }
            } else {
                this.showError(data.error || 'Failed to start monitoring');
            }
        } catch (error) {
            console.error('Monitoring start error:', error);
            this.showError('Error occurred while starting monitoring');
        }
    }

    async stopMonitoring() {
        console.log('stopMonitoring called');
        try {
            const requestBody = {};
            
            // If there is a current session ID, stop the specific session
            if (this.currentSessionId) {
                requestBody.session_id = this.currentSessionId;
            }
            
            const data = await this.fetchAPI('/api/monitor/stop', {
                method: 'POST',
                body: JSON.stringify(requestBody)
            });

            console.log('Monitoring stop response:', data);

            if (data.success) {
                this.showSuccess('Monitoring stopped');
                this.loadMonitoringStatus();
                
                // Clear current session information
                this.currentSessionId = null;
                this.currentSessionName = null;
                
                // Refresh workstation list
                if (this.currentPage === 'workstation-selection') {
                    this.loadWorkstationList();
                }
            } else {
                this.showError(data.error || 'Failed to stop monitoring');
            }
        } catch (error) {
            console.error('Monitoring stop error:', error);
            this.showError('Error occurred while stopping monitoring');
        }
    }

    async startSimulation() {
        console.log('startSimulation called');
        
        if (this.testType === 'new' && !this.selectedFile) {
            this.showError('Please select a data file first');
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
                // Save session information
                this.currentSessionId = data.session_id;
                this.currentSessionName = data.session_name;
                
                this.showSuccess(`Simulation started successfully - ${data.session_name}`);
                this.loadMonitoringStatus();
                
                // Refresh workstation list
                if (this.currentPage === 'workstation-selection') {
                    this.loadWorkstationList();
                }
            } else {
                this.showError(data.error || 'Failed to start simulation');
            }
        } catch (error) {
            console.error('Simulation start error:', error);
            this.showError('Error occurred while starting simulation');
        }
    }

    // ==================== Old Test Alarm and Log Management ====================
    clearOldTestAlarms() {
        this.alarms = [];
        this.updateOldTestAlarmTable();
        this.showSuccess('Old Test alarm records cleared');
    }

    clearOldTestLogs() {
        this.logs = [];
        this.updateOldTestLogViewer();
        this.showSuccess('Old Test logs cleared');
    }

    // ==================== New Test Alarm and Log Management ====================
    clearNewTestAlarms() {
        this.alarms = [];
        this.updateOldTestAlarmTable();
        this.showSuccess('New Test alarm records cleared');
    }

    clearNewTestLogs() {
        this.logs = [];
        this.updateNewTestLogViewer();
        this.showSuccess('New Test logs cleared');
    }

    // ==================== General Alarm and Log Management ====================
    clearAlarms() {
        this.alarms = [];
        this.updateAlarmTable();
        this.showSuccess('Alarm records cleared');
    }

    clearLogs() {
        this.logs = [];
        this.updateLogViewer();
        this.showSuccess('Logs cleared');
    }

    updateOldTestAlarmTable() {
        const tbody = document.getElementById('old-alarm-tbody');
        
        if (this.alarms.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center">No alarm records</td></tr>';
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
            tbody.innerHTML = '<tr><td colspan="6" class="text-center">No alarm records</td></tr>';
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
            tbody.innerHTML = '<tr><td colspan="6" class="text-center">No alarm records</td></tr>';
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

    // ==================== Other Pages ====================
    async loadConfig() {
        const configContent = document.getElementById('config-content');
        configContent.innerHTML = '<p>Configuration management feature under development...</p>';
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
                <p><strong>Platform:</strong> ${system.platform}</p>
                <p><strong>Memory:</strong> ${memory.available_gb}GB / ${memory.total_gb}GB</p>
                <p><strong>Usage:</strong> ${memory.percent}%</p>
            `;
        } else {
            systemInfo.innerHTML = '<p class="text-error">Unable to get system information</p>';
        }
    }

    updateHealthCheck(data) {
        const healthCheck = document.getElementById('health-check');
        
        if (data.success) {
            const health = data.health;
            healthCheck.innerHTML = `
                <p><strong>Python Processes:</strong> ${health.python_processes?.length || 0}</p>
                <p><strong>Port Usage:</strong> ${health.port_usage?.length || 0}</p>
            `;
        } else {
            healthCheck.innerHTML = '<p class="text-error">Unable to get health check information</p>';
        }
    }

    // ==================== File Upload Functionality ====================
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
            this.showError('Only .dat files are supported');
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
                this.showSuccess('File uploaded successfully');
                this.hideUploadProgress();
                
                await this.loadFileList();
                
                const fileSelector = document.getElementById('file-selector');
                if (fileSelector) {
                    fileSelector.value = result.file_info.path;
                    this.onFileSelected(result.file_info.path);
                }
            } else {
                this.showError(result.error || 'File upload failed');
                this.hideUploadProgress();
            }
        } catch (error) {
            console.error('Upload failed:', error);
            this.showError('Error occurred while uploading file');
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
            progressText.textContent = 'Preparing upload...';
            
            let progressValue = 0;
            const interval = setInterval(() => {
                progressValue += Math.random() * 15;
                if (progressValue > 90) {
                    progressValue = 90;
                    clearInterval(interval);
                }
                progressFill.style.width = progressValue + '%';
                progressText.textContent = `Uploading... ${Math.round(progressValue)}%`;
            }, 100);
        }
    }

    hideUploadProgress() {
        const progress = document.getElementById('upload-progress');
        const progressFill = document.getElementById('progress-fill');
        const progressText = document.getElementById('progress-text');
        
        if (progress) {
            progressFill.style.width = '100%';
            progressText.textContent = 'Upload complete';
            
            setTimeout(() => {
                progress.classList.add('hidden');
            }, 1000);
        }
    }

    // ==================== Utility Methods ====================
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
                    this.showSuccess('File list refreshed');
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

// Initialize application
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new SmartMonitorApp();
}); 