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
    
    // 特殊处理
    if (tabName === 'regression') {
        updateRegressionModelList();
    }
}

// 处理文件上传
async function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    showLoading('正在解析数据文件...');
    
    try {
        const data = await parseFile(file);
        currentData = data;
        
        // 更新目标变量选择
        updateTargetColumnSelect(data.columns);
        
        // 更新特征变量选择
        updateFeatureColumnsCheckboxes(data.columns);
        
        showNotification('数据文件加载成功', 'success');
        console.log('📊 数据加载完成:', data);
    } catch (error) {
        showNotification('数据文件解析失败: ' + error.message, 'error');
        console.error('❌ 数据解析错误:', error);
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
                let data;
                
                if (file.name.endsWith('.csv')) {
                    data = parseCSV(content);
                } else if (file.name.endsWith('.json')) {
                    data = JSON.parse(content);
                } else {
                    reject(new Error('不支持的文件格式'));
                    return;
                }
                
                resolve(data);
            } catch (error) {
                reject(error);
            }
        };
        
        reader.onerror = () => reject(new Error('文件读取失败'));
        
        if (file.name.endsWith('.csv')) {
            reader.readAsText(file);
        } else {
            reader.readAsText(file);
        }
    });
}

// 解析CSV
function parseCSV(content) {
    const lines = content.trim().split('\n');
    const headers = lines[0].split(',').map(h => h.trim());
    const data = [];
    
    for (let i = 1; i < lines.length; i++) {
        const values = lines[i].split(',').map(v => v.trim());
        const row = {};
        headers.forEach((header, index) => {
            row[header] = values[index] || '';
        });
        data.push(row);
    }
    
    return {
        columns: headers,
        data: data
    };
}

// 更新目标变量选择
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

// 更新特征变量复选框
function updateFeatureColumnsCheckboxes(columns) {
    const container = document.getElementById('feature-columns');
    if (!container) return;
    
    container.innerHTML = '';
    columns.forEach(column => {
        const label = document.createElement('label');
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.value = column;
        checkbox.checked = true;
        
        label.appendChild(checkbox);
        label.appendChild(document.createTextNode(column));
        container.appendChild(label);
    });
}

// 开始符号回归
async function startRegression() {
    if (!currentData) {
        showNotification('请先选择数据文件', 'warning');
        return;
    }
    
    const targetColumn = document.getElementById('target-column').value;
    const featureColumns = Array.from(document.querySelectorAll('#feature-columns input:checked'))
        .map(input => input.value);
    
    if (!targetColumn) {
        showNotification('请选择目标变量', 'warning');
        return;
    }
    
    if (featureColumns.length === 0) {
        showNotification('请选择至少一个特征变量', 'warning');
        return;
    }
    
    const populationSize = parseInt(document.getElementById('population-size').value);
    const generations = parseInt(document.getElementById('generations').value);
    
    showLoading('正在进行符号回归分析...');
    
    try {
        const result = await performSymbolicRegression({
            data: currentData,
            targetColumn,
            featureColumns,
            populationSize,
            generations
        });
        
        displayRegressionResults(result);
        regressionModels.push(result);
        updateRegressionModelList();
        
        showNotification('符号回归分析完成', 'success');
    } catch (error) {
        showNotification('符号回归分析失败: ' + error.message, 'error');
        console.error('❌ 回归分析错误:', error);
    } finally {
        hideLoading();
    }
}

// 执行符号回归（模拟）
async function performSymbolicRegression(params) {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // 模拟结果
    return {
        id: Date.now(),
        expression: `${params.featureColumns[0]} * 0.5 + ${params.featureColumns[1]} * 0.3 + 0.1`,
        r2: 0.85,
        mse: 0.12,
        featureImportance: params.featureColumns.map((col, i) => ({
            feature: col,
            importance: 0.8 - i * 0.2
        })),
        predictions: params.data.data.map((row, i) => ({
            actual: parseFloat(row[params.targetColumn]) || 0,
            predicted: Math.random() * 10
        }))
    };
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
                ${result.featureImportance.map(f => 
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
            modelId: parseInt(modelId),
            iterations,
            targetEfficacy,
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

// 执行蒙特卡罗分析（模拟）
async function performMonteCarloAnalysis(params) {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // 模拟结果
    return {
        iterations: params.iterations,
        targetEfficacy: params.targetEfficacy,
        tolerance: params.tolerance,
        validSamples: Math.floor(params.iterations * 0.15),
        optimalRanges: [
            { component: '成分A', min: 0.2, max: 0.4, mean: 0.3 },
            { component: '成分B', min: 0.1, max: 0.3, mean: 0.2 },
            { component: '成分C', min: 0.05, max: 0.15, mean: 0.1 }
        ],
        distribution: Array.from({length: 100}, () => Math.random() * 2)
    };
}

// 显示蒙特卡罗结果
function displayMonteCarloResults(result) {
    const container = document.getElementById('monte-carlo-results');
    if (!container) return;
    
    container.innerHTML = `
        <div class="result-item">
            <h4>分析参数</h4>
            <p>模拟次数: ${result.iterations.toLocaleString()}</p>
            <p>目标药效: ${result.targetEfficacy}</p>
            <p>容差范围: ±${result.tolerance}</p>
        </div>
        
        <div class="result-item">
            <h4>有效样本</h4>
            <p>符合条件样本数: ${result.validSamples.toLocaleString()}</p>
            <p>有效率: ${((result.validSamples / result.iterations) * 100).toFixed(2)}%</p>
        </div>
        
        <div class="result-item">
            <h4>推荐配比区间</h4>
            <table class="result-table">
                <thead>
                    <tr>
                        <th>成分</th>
                        <th>最小值</th>
                        <th>最大值</th>
                        <th>平均值</th>
                    </tr>
                </thead>
                <tbody>
                    ${result.optimalRanges.map(range => `
                        <tr>
                            <td>${range.component}</td>
                            <td>${range.min.toFixed(3)}</td>
                            <td>${range.max.toFixed(3)}</td>
                            <td>${range.mean.toFixed(3)}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
        
        <div class="result-item">
            <button class="btn-secondary" onclick="exportMonteCarloResults(${result.iterations})">导出结果</button>
        </div>
    `;
}

// 导入数据
async function importData() {
    try {
        const result = await window.electronAPI.openFile();
        if (result && !result.canceled) {
            showNotification('数据导入成功', 'success');
        }
    } catch (error) {
        showNotification('数据导入失败: ' + error.message, 'error');
    }
}

// 导出结果
async function exportResults() {
    try {
        const result = await window.electronAPI.saveFile();
        if (result && !result.canceled) {
            showNotification('结果导出成功', 'success');
        }
    } catch (error) {
        showNotification('结果导出失败: ' + error.message, 'error');
    }
}

// 启动后端服务
async function startBackendService() {
    try {
        const result = await window.electronAPI.startBackend();
        if (result.success) {
            updateConnectionStatus('已连接');
            showNotification('后端服务启动成功', 'success');
        } else {
            updateConnectionStatus('连接失败');
            showNotification('后端服务启动失败', 'error');
        }
    } catch (error) {
        updateConnectionStatus('连接失败');
        showNotification('后端服务启动失败: ' + error.message, 'error');
    }
}

// 测试后端连接
async function testBackendConnection() {
    showLoading('正在测试后端连接...');
    
    try {
        // 模拟连接测试
        await new Promise(resolve => setTimeout(resolve, 1000));
        showNotification('后端连接测试成功', 'success');
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
        overlay.classList.remove('hidden');
    }
    if (textElement) {
        textElement.textContent = text;
    }
}

// 隐藏加载状态
function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.classList.add('hidden');
    }
}

// 显示通知
function showNotification(message, type = 'info') {
    const container = document.getElementById('notification-container');
    if (!container) return;
    
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <p>${message}</p>
        </div>
    `;
    
    container.appendChild(notification);
    
    // 自动移除通知
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 5000);
}

// 显示关于对话框
function showAboutDialog() {
    showNotification('中药多组分均化分析客户端 v1.0.0', 'info');
}

// 可视化结果
function visualizeResults(modelId) {
    showNotification('图表功能开发中...', 'warning');
}

// 导出蒙特卡罗结果
function exportMonteCarloResults(iterations) {
    showNotification(`导出 ${iterations.toLocaleString()} 次模拟结果`, 'success');
}

// 全局函数（供HTML调用）
window.switchTab = switchTab;
window.startRegression = startRegression;
window.startMonteCarlo = startMonteCarlo;
window.importData = importData;
window.exportResults = exportResults;
window.testBackendConnection = testBackendConnection;
window.saveSettings = saveSettings; 