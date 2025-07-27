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
    
    // 滑块事件
    const testRatioSlider = document.getElementById('test-ratio');
    const testRatioValue = document.getElementById('test-ratio-value');
    if (testRatioSlider && testRatioValue) {
        testRatioSlider.addEventListener('input', function() {
            testRatioValue.textContent = this.value + '%';
        });
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
    
    showLoading('正在解析文件...');
    
    try {
        const data = await parseFile(file);
        currentData = data;
        
        // 更新UI
        updateTargetColumnSelect(data.columns);
        updateFeatureColumnsCheckboxes(data.columns);
        
        showNotification(`文件解析成功，共 ${data.data.length} 行数据`, 'success');
        
    } catch (error) {
        showNotification('文件解析失败: ' + error.message, 'error');
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
                    throw new Error('不支持的文件格式');
                }
                
                resolve(data);
            } catch (error) {
                reject(error);
            }
        };
        
        reader.onerror = function() {
            reject(new Error('文件读取失败'));
        };
        
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
    if (lines.length < 2) {
        throw new Error('CSV文件至少需要包含标题行和一行数据');
    }
    
    const headers = lines[0].split(',').map(h => h.trim());
    const data = [];
    
    for (let i = 1; i < lines.length; i++) {
        const values = lines[i].split(',').map(v => v.trim());
        if (values.length !== headers.length) {
            console.warn(`第 ${i + 1} 行数据列数不匹配，跳过`);
            continue;
        }
        
        const row = {};
        headers.forEach((header, index) => {
            const value = values[index];
            // 尝试转换为数字
            const numValue = parseFloat(value);
            row[header] = isNaN(numValue) ? value : numValue;
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
    
    // 添加全选按钮
    const selectAllDiv = document.createElement('div');
    selectAllDiv.className = 'checkbox-item select-all-item';
    selectAllDiv.innerHTML = `
        <input type="checkbox" id="select-all-features">
        <label for="select-all-features"><strong>全选所有特征变量</strong></label>
    `;
    container.appendChild(selectAllDiv);
    
    // 添加分隔线
    const separator = document.createElement('div');
    separator.className = 'checkbox-separator';
    container.appendChild(separator);
    
    // 添加各个特征变量
    columns.forEach(column => {
        const div = document.createElement('div');
        div.className = 'checkbox-item';
        div.innerHTML = `
            <input type="checkbox" id="feature-${column}" value="${column}" class="feature-checkbox">
            <label for="feature-${column}">${column}</label>
        `;
        container.appendChild(div);
    });
    
    // 添加全选功能
    const selectAllCheckbox = document.getElementById('select-all-features');
    const featureCheckboxes = document.querySelectorAll('.feature-checkbox');
    
    selectAllCheckbox.addEventListener('change', function() {
        featureCheckboxes.forEach(checkbox => {
            checkbox.checked = this.checked;
        });
    });
    
    // 当单个复选框改变时，更新全选状态
    featureCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const allChecked = Array.from(featureCheckboxes).every(cb => cb.checked);
            const anyChecked = Array.from(featureCheckboxes).some(cb => cb.checked);
            selectAllCheckbox.checked = allChecked;
            selectAllCheckbox.indeterminate = anyChecked && !allChecked;
        });
    });
    
    // 默认全选
    selectAllCheckbox.checked = true;
    featureCheckboxes.forEach(checkbox => {
        checkbox.checked = true;
    });
}

// 开始符号回归
async function startRegression() {
    if (!currentData) {
        showNotification('请先上传数据文件', 'warning');
        return;
    }
    
    const targetColumn = document.getElementById('target-column').value;
    const featureCheckboxes = document.querySelectorAll('#feature-columns input[type="checkbox"]:checked');
    
    if (!targetColumn) {
        showNotification('请选择目标变量', 'warning');
        return;
    }
    
    if (featureCheckboxes.length === 0) {
        showNotification('请选择至少一个特征变量', 'warning');
        return;
    }
    
    const featureColumns = Array.from(featureCheckboxes).map(cb => cb.value);
    const populationSize = parseInt(document.getElementById('population-size').value) || 100;
    const generations = parseInt(document.getElementById('generations').value) || 50;
    const testRatio = parseInt(document.getElementById('test-ratio').value) || 30;
    
    // 获取选择的运算符
    const operators = [];
    if (document.getElementById('op-add').checked) operators.push('add');
    if (document.getElementById('op-sub').checked) operators.push('sub');
    if (document.getElementById('op-mul').checked) operators.push('mul');
    if (document.getElementById('op-div').checked) operators.push('div');
    if (document.getElementById('op-pow').checked) operators.push('pow');
    if (document.getElementById('op-sqrt').checked) operators.push('sqrt');
    
    if (operators.length === 0) {
        showNotification('请至少选择一个运算符号', 'warning');
        return;
    }
    
    showLoading('正在进行符号回归分析...');
    
    try {
        const result = await performSymbolicRegression({
            data: currentData,
            targetColumn,
            featureColumns,
            populationSize,
            generations,
            testRatio,
            operators
        });
        
        // 保存模型
        regressionModels.push(result);
        updateRegressionModelList();
        
        // 显示结果
        displayRegressionResults(result);
        
        showNotification('符号回归分析完成', 'success');
        
    } catch (error) {
        showNotification('符号回归分析失败: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

// 执行符号回归分析
async function performSymbolicRegression(params) {
    try {
        const response = await fetch('http://localhost:5000/api/regression/symbolic-regression', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                data: params.data,
                target_column: params.targetColumn,
                feature_columns: params.featureColumns,
                population_size: params.populationSize,
                generations: params.generations,
                test_ratio: params.testRatio,
                operators: params.operators
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP ${response.status}`);
        }
        
        const result = await response.json();
        
        if (!result.success) {
            throw new Error(result.error || '分析失败');
        }
        
        // 转换结果格式
        return {
            id: Date.now(),
            model_id: result.result.model_id,
            expression: result.result.expression || '',
            r2: result.result.r2 || 0,
            mse: result.result.mse || 0,
            featureImportance: result.result.feature_importance || [],
            predictions: result.result.predictions || {},
            parameters: result.result.parameters || {}
        };
        
    } catch (error) {
        console.error('符号回归分析失败:', error);
        throw error;
    }
}

// 显示回归结果
function displayRegressionResults(result) {
    const container = document.getElementById('regression-results');
    const formulaDisplay = document.getElementById('formula-display');
    
    if (!container) return;
    
    // 显示基本结果
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
            <p>样本数量: ${result.predictions.actual ? result.predictions.actual.length : 0}</p>
            <button class="btn-secondary" onclick="visualizeResults(${result.id})">查看图表</button>
        </div>
    `;
    
    // 显示公式显示区域
    if (formulaDisplay) {
        formulaDisplay.style.display = 'block';
        
        // 更新LaTeX公式
        const formulaLatex = document.getElementById('formula-latex');
        if (formulaLatex) {
            formulaLatex.innerHTML = formatFormulaToLatex(result.expression);
        }
        
        // 更新性能指标
        updatePerformanceMetrics(result);
        
        // 生成公式树
        generateFormulaTree(result);
    }
}

// 格式化公式为LaTeX
function formatFormulaToLatex(expression) {
    // 简单的LaTeX格式化
    let latex = expression
        .replace(/\*/g, ' \\cdot ')
        .replace(/\//g, ' \\div ')
        .replace(/\^/g, '^')
        .replace(/sqrt/g, '\\sqrt');
    
    return `$$${latex}$$`;
}

// 更新性能指标
function updatePerformanceMetrics(result) {
    const r2Value = document.getElementById('r2-value');
    const mseValue = document.getElementById('mse-value');
    const maeValue = document.getElementById('mae-value');
    const rmseValue = document.getElementById('rmse-value');
    
    if (r2Value) r2Value.textContent = result.r2.toFixed(3);
    if (mseValue) mseValue.textContent = result.mse.toFixed(3);
    
    // 计算MAE和RMSE
    if (result.predictions.actual && result.predictions.predicted) {
        const actual = result.predictions.actual;
        const predicted = result.predictions.predicted;
        
        const mae = actual.reduce((sum, val, i) => sum + Math.abs(val - predicted[i]), 0) / actual.length;
        const rmse = Math.sqrt(result.mse);
        
        if (maeValue) maeValue.textContent = mae.toFixed(3);
        if (rmseValue) rmseValue.textContent = rmse.toFixed(3);
    }
}

// 生成公式树
function generateFormulaTree(result) {
    const treeContainer = document.getElementById('formula-tree');
    if (!treeContainer) return;
    
    // 解析表达式生成树结构
    const treeData = parseExpressionToTree(result.expression, result.featureImportance);
    
    treeContainer.innerHTML = '';
    renderTreeNodes(treeContainer, treeData);
    
    // 添加右键菜单事件
    setupContextMenu();
}

// 解析表达式为树结构
function parseExpressionToTree(expression, featureImportance) {
    // 简化的表达式解析
    const nodes = [];
    const terms = expression.split('+').map(term => term.trim());
    
    terms.forEach((term, index) => {
        const parts = term.split('*');
        if (parts.length === 2) {
            const coefficient = parseFloat(parts[0]) || 1;
            const feature = parts[1].trim();
            
            // 找到特征的重要性
            const importance = featureImportance.find(f => f.feature === feature)?.importance || 0;
            
            nodes.push({
                id: `node-${index}`,
                type: 'term',
                coefficient: coefficient,
                feature: feature,
                importance: importance,
                weight: getWeightClass(importance)
            });
        }
    });
    
    return {
        type: 'expression',
        children: nodes
    };
}

// 获取权重类别
function getWeightClass(importance) {
    if (importance > 0.5) return 'high-weight';
    if (importance > 0.2) return 'medium-weight';
    return 'low-weight';
}

// 渲染树节点
function renderTreeNodes(container, node, level = 0) {
    if (node.type === 'expression') {
        const expressionDiv = document.createElement('div');
        expressionDiv.className = 'tree-expression';
        expressionDiv.innerHTML = '<strong>药效预测公式</strong>';
        container.appendChild(expressionDiv);
        
        node.children.forEach(child => {
            renderTreeNodes(container, child, level + 1);
        });
    } else if (node.type === 'term') {
        const nodeDiv = document.createElement('div');
        nodeDiv.className = `tree-node ${node.weight}`;
        nodeDiv.setAttribute('data-node-id', node.id);
        nodeDiv.setAttribute('data-feature', node.feature);
        nodeDiv.setAttribute('data-importance', node.importance);
        
        nodeDiv.innerHTML = `
            <span class="node-coefficient">${node.coefficient > 0 ? '+' : ''}${node.coefficient.toFixed(3)}</span>
            <span class="node-feature">× ${node.feature}</span>
            <span class="node-importance">(权重: ${node.importance.toFixed(3)})</span>
        `;
        
        container.appendChild(nodeDiv);
    }
}

// 设置右键菜单
function setupContextMenu() {
    const treeNodes = document.querySelectorAll('.tree-node');
    
    treeNodes.forEach(node => {
        node.addEventListener('contextmenu', function(e) {
            e.preventDefault();
            showContextMenu(e, this);
        });
        
        node.addEventListener('click', function() {
            toggleNodeSelection(this);
        });
    });
}

// 显示右键菜单
function showContextMenu(e, node) {
    // 移除现有菜单
    const existingMenu = document.querySelector('.context-menu');
    if (existingMenu) existingMenu.remove();
    
    const menu = document.createElement('div');
    menu.className = 'context-menu';
    menu.style.left = e.pageX + 'px';
    menu.style.top = e.pageY + 'px';
    
    const feature = node.getAttribute('data-feature');
    const importance = parseFloat(node.getAttribute('data-importance'));
    
    menu.innerHTML = `
        <div class="context-menu-item">特征: ${feature}</div>
        <div class="context-menu-item">权重: ${importance.toFixed(3)}</div>
        <div class="context-menu-item danger" onclick="deleteNode('${node.getAttribute('data-node-id')}')">删除此节点</div>
        <div class="context-menu-item danger" onclick="deleteLowWeightNodes()">删除所有低权重节点</div>
    `;
    
    document.body.appendChild(menu);
    
    // 点击其他地方关闭菜单
    document.addEventListener('click', function closeMenu() {
        menu.remove();
        document.removeEventListener('click', closeMenu);
    });
}

// 切换节点选择状态
function toggleNodeSelection(node) {
    node.classList.toggle('selected');
}

// 删除节点
function deleteNode(nodeId) {
    // 这里应该重新计算回归，删除指定节点
    showNotification('节点删除功能开发中...', 'info');
}

// 删除低权重节点
function deleteLowWeightNodes() {
    // 删除所有低权重节点
    const lowWeightNodes = document.querySelectorAll('.tree-node.low-weight');
    lowWeightNodes.forEach(node => {
        node.style.opacity = '0.3';
        node.style.textDecoration = 'line-through';
    });
    showNotification('已标记低权重节点，可重新回归获得简化公式', 'info');
}

// 剪枝选中节点
function pruneSelectedNodes() {
    const selectedNodes = document.querySelectorAll('.tree-node.selected');
    if (selectedNodes.length === 0) {
        showNotification('请先选择要删除的节点', 'warning');
        return;
    }
    
    // 这里应该重新计算回归
    showNotification(`已选择 ${selectedNodes.length} 个节点进行删除`, 'info');
}

// 重置公式
function resetFormula() {
    // 重置所有节点状态
    const nodes = document.querySelectorAll('.tree-node');
    nodes.forEach(node => {
        node.classList.remove('selected');
        node.style.opacity = '1';
        node.style.textDecoration = 'none';
    });
    
    showNotification('公式已重置', 'success');
}

// 更新回归模型列表
function updateRegressionModelList() {
    const select = document.getElementById('mc-model');
    if (!select) return;
    
    select.innerHTML = '<option value="">请选择回归模型</option>';
    regressionModels.forEach(model => {
        const option = document.createElement('option');
        option.value = model.model_id || model.id;
        option.textContent = `模型 ${model.model_id || model.id} (R²=${model.r2.toFixed(3)})`;
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
            modelId,
            iterations,
            targetEfficacy,
            tolerance
        });
        
        displayMonteCarloResults(result);
        showNotification('蒙特卡罗分析完成', 'success');
        
    } catch (error) {
        showNotification('蒙特卡罗分析失败: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

// 执行蒙特卡罗分析
async function performMonteCarloAnalysis(params) {
    try {
        const response = await fetch('http://localhost:5000/api/monte-carlo/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                data: params.data,
                target_column: params.targetColumn,
                feature_columns: params.featureColumns,
                model_id: params.modelId,
                iterations: params.iterations,
                target_efficacy: params.targetEfficacy,
                tolerance: params.tolerance
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP ${response.status}`);
        }
        
        const result = await response.json();
        
        if (!result.success) {
            throw new Error(result.error || '分析失败');
        }
        
        // 转换结果格式
        const analysisResult = result.result;
        return {
            analysis_id: analysisResult.analysis_id,
            iterations: analysisResult.iterations || 0,
            targetEfficacy: analysisResult.target_efficacy || 0,
            tolerance: analysisResult.tolerance || 0,
            validSamples: analysisResult.valid_samples_count || 0,
            validRate: analysisResult.valid_rate || 0,
            componentStatistics: analysisResult.component_statistics || {},
            distributionData: analysisResult.distribution_data || {},
            sampleData: analysisResult.sample_data || {}
        };
        
    } catch (error) {
        console.error('蒙特卡罗分析失败:', error);
        throw error;
    }
}

// 显示蒙特卡罗结果
function displayMonteCarloResults(result) {
    const container = document.getElementById('monte-carlo-results');
    if (!container) return;
    
    // 转换成分统计信息为表格格式
    const optimalRanges = Object.entries(result.componentStatistics).map(([component, stats]) => ({
        component,
        min: stats.min,
        max: stats.max,
        mean: stats.mean,
        std: stats.std
    }));
    
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
            <p>有效率: ${(result.validRate * 100).toFixed(2)}%</p>
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
                        <th>标准差</th>
                    </tr>
                </thead>
                <tbody>
                    ${optimalRanges.map(range => `
                        <tr>
                            <td>${range.component}</td>
                            <td>${range.min.toFixed(3)}</td>
                            <td>${range.max.toFixed(3)}</td>
                            <td>${range.mean.toFixed(3)}</td>
                            <td>${range.std.toFixed(3)}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
        
        <div class="result-item">
            <button class="btn-secondary" onclick="exportMonteCarloResults('${result.analysis_id}')">导出结果</button>
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
            updateConnectionStatus(true);
            showNotification('后端服务启动成功', 'success');
        } else {
            updateConnectionStatus(false);
            showNotification('后端服务启动失败: ' + result.error, 'error');
        }
    } catch (error) {
        updateConnectionStatus(false);
        showNotification('后端服务启动失败: ' + error.message, 'error');
    }
}

// 测试后端连接
async function testBackendConnection() {
    try {
        const response = await fetch(`http://127.0.0.1:${currentSettings.backendPort}/api/health`, {
            method: 'GET',
            timeout: 5000
        });
        
        if (response.ok) {
            updateConnectionStatus(true);
            return true;
        } else {
            updateConnectionStatus(false);
            return false;
        }
    } catch (error) {
        updateConnectionStatus(false);
        return false;
    }
}

// 保存设置
async function saveSettings() {
    try {
        localStorage.setItem('tcm-settings', JSON.stringify(currentSettings));
        showNotification('设置已保存', 'success');
    } catch (error) {
        showNotification('设置保存失败: ' + error.message, 'error');
    }
}

// 加载设置
function loadSettings() {
    try {
        const saved = localStorage.getItem('tcm-settings');
        if (saved) {
            const settings = JSON.parse(saved);
            currentSettings = { ...currentSettings, ...settings };
        }
        
        // 更新UI
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
    saveSettings();
}

// 更新连接状态
function updateConnectionStatus(isConnected) {
    const statusElement = document.getElementById('connection-status');
    if (statusElement) {
        if (isConnected) {
            statusElement.textContent = `后端服务：已连接 (localhost:${currentSettings.backendPort})`;
            statusElement.className = 'status-connected';
        } else {
            statusElement.textContent = `后端服务：未连接 (localhost:${currentSettings.backendPort})`;
            statusElement.className = 'status-disconnected';
        }
    }
}

// 更新状态栏
function updateStatusBar() {
    const statusBar = document.getElementById('status-bar');
    if (statusBar) {
        const updateTime = () => {
            const now = new Date();
            const timeString = now.toLocaleTimeString();
            statusBar.textContent = `就绪 | ${timeString}`;
        };
        
        updateTime();
        setInterval(updateTime, 1000);
    }
}

// 显示加载状态
function showLoading(text = '正在处理...') {
    const loading = document.getElementById('loading');
    if (loading) {
        const textElement = loading.querySelector('.loading-text');
        if (textElement) {
            textElement.textContent = text;
        }
        loading.style.display = 'flex';
    }
}

// 隐藏加载状态
function hideLoading() {
    const loading = document.getElementById('loading');
    if (loading) {
        loading.style.display = 'none';
    }
}

// 显示通知
function showNotification(message, type = 'info') {
    // 移除现有通知
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(notification => {
        notification.remove();
    });
    
    // 创建新通知
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    
    notification.innerHTML = `
        <div class="notification-message">${message}</div>
        <button class="notification-close" onclick="this.parentElement.remove()">×</button>
    `;
    
    // 添加到页面
    document.body.appendChild(notification);
    
    // 自动移除通知
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

// 显示关于对话框
function showAboutDialog() {
    alert('中药多组分均化分析客户端 v1.0.0\n\n基于符号回归和蒙特卡罗模拟的中药配比优化工具');
}

// 可视化结果
function visualizeResults(modelId) {
    showNotification('图表功能开发中...', 'info');
}

// 导出蒙特卡罗结果
function exportMonteCarloResults(analysisId) {
    showNotification('导出功能开发中...', 'info');
} 