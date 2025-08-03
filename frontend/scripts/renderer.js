// 全局变量
let currentData = null;
let regressionModels = [];
let currentSettings = {
    backendPort: 5000,
    autoStartBackend: true,
    theme: 'dark',
    language: 'zh-CN',
    defaultFormat: 'csv',
    autoSave: false
};

// API基础URL
const API_BASE_URL = 'http://127.0.0.1:5000';

// DOM 加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// 应用初始化
async function initializeApp() {
    console.log('🚀 初始化中药多组分均化分析客户端...');
    
    // 设置事件监听器
    setupEventListeners();
    
    // 加载设置
    loadSettings();
    
    // 更新状态栏
    updateStatusBar();
    
    // 启动后端服务（如果启用）
    if (currentSettings.autoStartBackend) {
        await startBackendService();
    }
    
    // 显示欢迎通知
    showNotification('欢迎使用中药多组分均化分析客户端', 'success');
    
    console.log('✅ 应用初始化完成');
}

// 设置事件监听器
function setupEventListeners() {
    // 导航按钮事件
    const navButtons = document.querySelectorAll('.nav-btn');
    navButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tabName = this.getAttribute('data-tab');
            switchTab(tabName);
        });
    });
    
    // 文件输入事件
    const regressionDataInput = document.getElementById('regression-data');
    if (regressionDataInput) {
        regressionDataInput.addEventListener('change', handleFileUpload);
    }
    
    // 菜单事件监听
    if (window.electronAPI) {
        window.electronAPI.onMenuImportData(() => importData());
        window.electronAPI.onMenuExportResults(() => exportResults());
        window.electronAPI.onMenuSymbolicRegression(() => switchTab('regression'));
        window.electronAPI.onMenuMonteCarlo(() => switchTab('monte-carlo'));
        window.electronAPI.onMenuAbout(() => showAboutDialog());
    }
    
    // 设置变更事件
    const settingInputs = document.querySelectorAll('#settings input, #settings select');
    settingInputs.forEach(input => {
        input.addEventListener('change', function() {
            updateSetting(this.id, this.value || this.checked);
        });
    });
}

// 切换标签页
function switchTab(tabName) {
    // 隐藏所有标签页内容
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(content => {
        content.classList.remove('active');
    });
    
    // 移除所有导航按钮的激活状态
    const navButtons = document.querySelectorAll('.nav-btn');
    navButtons.forEach(button => {
        button.classList.remove('active');
    });
    
    // 显示选中的标签页
    const targetTab = document.getElementById(tabName);
    if (targetTab) {
        targetTab.classList.add('active');
    }
    
    // 激活对应的导航按钮
    const targetButton = document.querySelector(`[data-tab="${tabName}"]`);
    if (targetButton) {
        targetButton.classList.add('active');
    }
    
    // 更新状态栏
    updateStatusBar();
}

// 处理文件上传
async function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    showLoading('正在上传文件...');
    
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch(`${API_BASE_URL}/api/data/upload`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (!result.success) {
            throw new Error(result.message || '文件上传失败');
        }
        
        // 使用API返回的数据
        currentData = {
            data: result.result.data_preview,
            headers: result.result.columns_list,
            rows: result.result.rows,
            columns: result.result.columns,
            filename: result.result.filename
        };
        
        // 更新目标列选择
        updateTargetColumnSelect(result.result.columns_list);
        
        // 更新特征列复选框
        updateFeatureColumnsCheckboxes(result.result.columns_list);
        
        showNotification('文件上传成功', 'success');
    } catch (error) {
        showNotification('文件上传失败: ' + error.message, 'error');
        console.error('❌ 文件上传错误:', error);
    } finally {
        hideLoading();
    }
}

// 解析文件
async function parseFile(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            try {
                const content = e.target.result;
                const data = parseCSV(content);
                resolve(data);
            } catch (error) {
                reject(error);
            }
        };
        
        reader.onerror = function() {
            reject(new Error('文件读取失败'));
        };
        
        reader.readAsText(file);
    });
}

// 解析CSV内容
function parseCSV(content) {
    const lines = content.trim().split('\n');
    const headers = lines[0].split(',').map(h => h.trim());
    const data = [];
    
    for (let i = 1; i < lines.length; i++) {
        const values = lines[i].split(',');
        const row = {};
        
        headers.forEach((header, index) => {
            const value = values[index] ? values[index].trim() : '';
            row[header] = isNaN(value) ? value : parseFloat(value);
        });
        
        data.push(row);
    }
    
    return {
        data: data,
        headers: headers,
        rows: data.length,
        columns: headers.length
    };
}

// 更新目标列选择
function updateTargetColumnSelect(columns) {
    const select = document.getElementById('target-column');
    if (!select) return;
    
    select.innerHTML = '<option value="">请选择目标变量</option>';
    columns.forEach(column => {
        const option = document.createElement('option');
        option.value = column;
        option.textContent = column;
        select.appendChild(option);
    });
}

// 更新特征列复选框
function updateFeatureColumnsCheckboxes(columns) {
    const container = document.getElementById('feature-columns');
    if (!container) return;
    
    container.innerHTML = '';
    columns.forEach(column => {
        const div = document.createElement('div');
        div.className = 'checkbox-item';
        div.innerHTML = `
            <input type="checkbox" id="feature-${column}" value="${column}" checked>
            <label for="feature-${column}">${column}</label>
        `;
        container.appendChild(div);
    });
}

// 开始符号回归分析
async function startRegression() {
    const targetColumn = document.getElementById('target-column').value;
    const featureCheckboxes = document.querySelectorAll('#feature-columns input[type="checkbox"]:checked');
    const populationSize = parseInt(document.getElementById('population-size').value) || 100;
    const generations = parseInt(document.getElementById('generations').value) || 50;
    
    if (!targetColumn) {
        showNotification('请选择目标变量', 'warning');
        return;
    }
    
    if (featureCheckboxes.length === 0) {
        showNotification('请选择至少一个特征变量', 'warning');
        return;
    }
    
    if (!currentData) {
        showNotification('请先上传数据', 'warning');
        return;
    }
    
    const featureColumns = Array.from(featureCheckboxes).map(cb => cb.value);
    
    showLoading('正在进行符号回归分析...');
    
    try {
        const result = await performSymbolicRegression({
            data: currentData.data,
            target_column: targetColumn,
            feature_columns: featureColumns,
            population_size: populationSize,
            generations: generations
        });
        
        // 保存模型到列表
        regressionModels.push(result);
        updateRegressionModelList();
        
        displayRegressionResults(result);
        showNotification('符号回归分析完成', 'success');
    } catch (error) {
        showNotification('符号回归分析失败: ' + error.message, 'error');
        console.error('❌ 符号回归分析错误:', error);
    } finally {
        hideLoading();
    }
}

// 执行符号回归（真实API调用）
async function performSymbolicRegression(params) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/regression/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(params)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (!result.success) {
            throw new Error(result.message || 'API调用失败');
        }
        
        return result.result;
    } catch (error) {
        console.error('API调用失败:', error);
        throw error;
    }
}

// 显示回归结果
function displayRegressionResults(result) {
    const container = document.getElementById('regression-results');
    if (!container) return;
    
    container.innerHTML = `
        <div class="result-item">
            <h4>回归表达式</h4>
            <p class="expression">${result.expression}</p>
        </div>
        
        <div class="result-item">
            <h4>模型性能</h4>
            <p>R² = ${result.r2.toFixed(3)}</p>
            <p>MSE = ${result.mse.toFixed(3)}</p>
        </div>
        
        <div class="result-item">
            <h4>特征重要性</h4>
            <ul>
                ${result.feature_importance.map(f => 
                    `<li>${f.feature}: ${f.importance.toFixed(3)}</li>`
                ).join('')}
            </ul>
        </div>
        
        <div class="result-item">
            <h4>预测结果</h4>
            <p>样本数量: ${result.predictions.length}</p>
            <button class="btn-secondary" onclick="visualizeResults(${result.id})">查看图表</button>
        </div>
    `;
}

// 更新回归模型列表
function updateRegressionModelList() {
    const select = document.getElementById('mc-model');
    if (!select) return;
    
    select.innerHTML = '<option value="">请选择回归模型</option>';
    regressionModels.forEach(model => {
        const option = document.createElement('option');
        option.value = model.id;
        option.textContent = `模型 ${model.id} (R²=${model.r2.toFixed(3)})`;
        select.appendChild(option);
    });
}

// 开始蒙特卡罗分析
async function startMonteCarlo() {
    const modelId = document.getElementById('mc-model').value;
    const iterations = parseInt(document.getElementById('mc-iterations').value);
    const targetEfficacy = parseFloat(document.getElementById('target-efficacy').value);
    const tolerance = parseFloat(document.getElementById('tolerance').value);
    
    if (!modelId) {
        showNotification('请先完成符号回归分析', 'warning');
        return;
    }
    
    if (!targetEfficacy) {
        showNotification('请输入目标药效值', 'warning');
        return;
    }
    
    showLoading('正在进行蒙特卡罗分析...');
    
    try {
        const result = await performMonteCarloAnalysis({
            model_id: parseInt(modelId),
            iterations,
            target_efficacy: targetEfficacy,
            tolerance
        });
        
        displayMonteCarloResults(result);
        showNotification('蒙特卡罗分析完成', 'success');
    } catch (error) {
        showNotification('蒙特卡罗分析失败: ' + error.message, 'error');
        console.error('❌ 蒙特卡罗分析错误:', error);
    } finally {
        hideLoading();
    }
}

// 执行蒙特卡罗分析（真实API调用）
async function performMonteCarloAnalysis(params) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/monte-carlo/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(params)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (!result.success) {
            throw new Error(result.message || 'API调用失败');
        }
        
        return result.result;
    } catch (error) {
        console.error('API调用失败:', error);
        throw error;
    }
}

// 显示蒙特卡罗结果
function displayMonteCarloResults(result) {
    const container = document.getElementById('monte-carlo-results');
    if (!container) return;
    
    container.innerHTML = `
        <div class="result-item">
            <h4>分析参数</h4>
            <p>模拟次数: ${result.iterations}</p>
            <p>目标药效: ${result.target_efficacy}</p>
            <p>容差: ${result.tolerance}</p>
        </div>
        
        <div class="result-item">
            <h4>分析结果</h4>
            <p>有效样本数: ${result.valid_samples}</p>
            <p>成功率: ${(result.success_rate * 100).toFixed(1)}%</p>
            <p>分析时间: ${result.analysis_time}秒</p>
        </div>
        
        <div class="result-item">
            <h4>最优配比范围</h4>
            <ul>
                ${result.optimal_ranges.map(r => 
                    `<li>${r.component}: ${r.min.toFixed(2)} - ${r.max.toFixed(2)} (均值: ${r.mean.toFixed(2)})</li>`
                ).join('')}
            </ul>
        </div>
        
        <div class="result-item">
            <h4>操作</h4>
            <button class="btn-secondary" onclick="exportMonteCarloResults(${result.iterations})">导出结果</button>
        </div>
    `;
}

// 导入数据
async function importData() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.csv,.xlsx,.xls';
    
    input.onchange = async function(e) {
        const file = e.target.files[0];
        if (file) {
            try {
                const data = await parseFile(file);
                currentData = data;
                updateTargetColumnSelect(Object.keys(data.data[0]));
                updateFeatureColumnsCheckboxes(Object.keys(data.data[0]));
                showNotification('数据导入成功', 'success');
            } catch (error) {
                showNotification('数据导入失败: ' + error.message, 'error');
            }
        }
    };
    
    input.click();
}

// 导出结果
async function exportResults() {
    if (regressionModels.length === 0) {
        showNotification('没有可导出的结果', 'warning');
        return;
    }
    
    const dataStr = JSON.stringify(regressionModels, null, 2);
    const dataBlob = new Blob([dataStr], {type: 'application/json'});
    
    const link = document.createElement('a');
    link.href = URL.createObjectURL(dataBlob);
    link.download = `regression_results_${Date.now()}.json`;
    link.click();
    
    showNotification('结果导出成功', 'success');
}

// 启动后端服务
async function startBackendService() {
    try {
        // 检查后端健康状态
        const healthResponse = await fetch(`${API_BASE_URL}/api/health`);
        if (healthResponse.ok) {
            updateConnectionStatus('已连接');
            showNotification('后端服务已连接', 'success');
        } else {
            updateConnectionStatus('连接失败');
            showNotification('后端服务连接失败', 'error');
        }
    } catch (error) {
        updateConnectionStatus('连接失败');
        showNotification('后端服务连接失败: ' + error.message, 'error');
    }
}

// 测试后端连接
async function testBackendConnection() {
    showLoading('正在测试后端连接...');
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/health`);
        if (response.ok) {
            const data = await response.json();
            showNotification(`后端连接正常: ${data.service}`, 'success');
        } else {
            showNotification('后端连接失败', 'error');
        }
    } catch (error) {
        showNotification('后端连接测试失败: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

// 保存设置
async function saveSettings() {
    try {
        // 这里应该保存到本地存储或配置文件
        localStorage.setItem('tcm-settings', JSON.stringify(currentSettings));
        showNotification('设置保存成功', 'success');
    } catch (error) {
        showNotification('设置保存失败: ' + error.message, 'error');
    }
}

// 加载设置
function loadSettings() {
    try {
        const saved = localStorage.getItem('tcm-settings');
        if (saved) {
            currentSettings = { ...currentSettings, ...JSON.parse(saved) };
        }
        
        // 应用设置到界面
        Object.keys(currentSettings).forEach(key => {
            const element = document.getElementById(key);
            if (element) {
                if (element.type === 'checkbox') {
                    element.checked = currentSettings[key];
                } else {
                    element.value = currentSettings[key];
                }
            }
        });
    } catch (error) {
        console.error('加载设置失败:', error);
    }
}

// 更新设置
function updateSetting(key, value) {
    currentSettings[key] = value;
}

// 更新连接状态
function updateConnectionStatus(status) {
    const element = document.getElementById('connection-status');
    if (element) {
        element.textContent = `后端服务：${status}`;
    }
}

// 更新状态栏
function updateStatusBar() {
    const timeElement = document.getElementById('current-time');
    if (timeElement) {
        const updateTime = () => {
            const now = new Date();
            timeElement.textContent = now.toLocaleString('zh-CN');
        };
        updateTime();
        setInterval(updateTime, 1000);
    }
}

// 显示加载状态
function showLoading(text = '正在处理...') {
    const overlay = document.getElementById('loading-overlay');
    const textElement = document.getElementById('loading-text');
    
    if (overlay) {
        overlay.style.display = 'flex';
    }
    
    if (textElement) {
        textElement.textContent = text;
    }
}

// 隐藏加载状态
function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.style.display = 'none';
    }
}

// 显示通知
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <span class="notification-message">${message}</span>
        <button class="notification-close" onclick="this.parentElement.remove()">×</button>
    `;
    
    // 添加到页面
    document.body.appendChild(notification);
    
    // 自动移除
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

// 显示关于对话框
function showAboutDialog() {
    alert('中药多组分均化分析客户端 v1.0.0\n\n基于Electron + Flask的跨平台桌面应用');
}

// 可视化结果
function visualizeResults(modelId) {
    showNotification('图表功能开发中...', 'info');
}

// 导出蒙特卡罗结果
function exportMonteCarloResults(iterations) {
    showNotification('导出功能开发中...', 'info');
}

// 全局函数（供HTML调用）
window.switchTab = switchTab;
window.startRegression = startRegression;
window.startMonteCarlo = startMonteCarlo;
window.importData = importData;
window.exportResults = exportResults;
window.testBackendConnection = testBackendConnection;
window.saveSettings = saveSettings; 