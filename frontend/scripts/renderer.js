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
            model_id: result.result.id || Date.now(),
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
    console.log('displayRegressionResults called with:', result);
    
    const container = document.getElementById('regression-results');
    const formulaDisplay = document.getElementById('formula-display');
    
    console.log('container:', container);
    console.log('formulaDisplay:', formulaDisplay);
    
    if (!container) {
        console.error('regression-results container not found');
        return;
    }
    
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
        console.log('Showing formula display');
        formulaDisplay.style.display = 'block';
        
        // 更新LaTeX公式
        renderLatexFormula(result.expression, document.getElementById('target-column').value);
        
        // 更新性能指标
        updatePerformanceMetrics(result);
        
        // 生成公式树
        generateFormulaTree(result);
    } else {
        console.error('formula-display not found');
    }
    
    // 显示结果区域
    const resultSection = document.getElementById('regression-result');
    if (resultSection) {
        resultSection.style.display = 'block';
    }
}

// 格式化公式为LaTeX（支持分段渲染）
function formatFormulaToLatex(expression, targetColumn) {
    // 清理表达式
    let cleaned = expression
        .replace(/\+\s*\+/g, '+')
        .replace(/\+\s*-/g, '-')
        .replace(/\s+/g, ' ')
        .trim();
    
    // 分割各项
    const terms = cleaned.split(/(?=[+-])/).filter(term => term.trim());
    
    // 格式化各项
    const formattedTerms = terms.map(term => {
        term = term.trim();
        if (term.startsWith('+')) {
            term = term.substring(1);
        }
        
        // 处理系数和变量
        const parts = term.split('*');
        if (parts.length === 2) {
            const coefficient = parseFloat(parts[0].trim());
            const variable = parts[1].trim();
            
            if (coefficient === 0) return '';
            if (coefficient === 1) return variable;
            if (coefficient === -1) return `-${variable}`;
            
            return `${coefficient.toFixed(3)} \\cdot ${variable}`;
        }
        
        return term;
    }).filter(term => term !== '');
    
    // 组合公式
    let latex = formattedTerms.join(' + ');
    
    // 处理特殊情况
    if (latex === '') latex = '0';
    if (latex.startsWith('+ ')) latex = latex.substring(2);
    
    // 添加等号和目标变量
    return `${targetColumn} = ${latex}`;
}

// 渲染LaTeX公式（统一背景，分段渲染）
function renderLatexFormula(expression, targetColumn) {
    const formulaContainer = document.getElementById('formula-latex');
    if (!formulaContainer) {
        console.error('formula-latex container not found');
        return;
    }
    
    console.log('Rendering LaTeX formula:', expression, targetColumn);
    
    // 格式化LaTeX公式
    const latexFormula = formatFormulaToLatex(expression, targetColumn);
    
    // 清空容器
    formulaContainer.innerHTML = '';
    
    // 创建统一的背景容器
    const backgroundContainer = document.createElement('div');
    backgroundContainer.className = 'formula-background';
    backgroundContainer.style.cssText = `
        padding: 20px;
        background: #2a2a2a;
        border-radius: 8px;
        margin: 10px 0;
        text-align: center;
        overflow-x: auto;
        word-wrap: break-word;
        overflow-wrap: break-word;
        max-width: 100%;
    `;
    
    // 分段渲染：每6项为一段（增加每段项数，减少换行）
    const terms = latexFormula.split(' + ');
    const maxTermsPerSegment = 6; // 从3增加到6
    const segments = [];
    
    for (let i = 0; i < terms.length; i += maxTermsPerSegment) {
        const segment = terms.slice(i, i + maxTermsPerSegment).join(' + ');
        segments.push(segment);
    }
    
    // 在统一背景内创建分段
    segments.forEach((segment, index) => {
        const segmentElement = document.createElement('div');
        segmentElement.className = 'formula-segment';
        segmentElement.style.cssText = `
            margin: 8px 0;
            font-size: 16px;
            line-height: 1.5;
            color: #4a9eff;
            white-space: nowrap; /* 防止内部换行 */
            overflow-x: auto; /* 允许水平滚动 */
        `;
        
        // 如果是第一段，包含等号
        const formulaText = index === 0 ? segment : segment;
        
        // 添加到背景容器
        backgroundContainer.appendChild(segmentElement);
        
        // 先设置内容，再触发MathJax渲染
        segmentElement.innerHTML = `$$${formulaText}$$`;
        
        // 触发MathJax重新渲染
        if (window.MathJax && window.MathJax.typesetPromise) {
            console.log('Using MathJax to render segment:', index);
            MathJax.typesetPromise([segmentElement]).then(() => {
                console.log('MathJax rendering completed for segment:', index);
            }).catch((err) => {
                console.error('MathJax rendering failed for segment:', index, err);
                // 降级到普通文本显示
                segmentElement.innerHTML = `<code style="color: #4a9eff; font-size: 16px; white-space: pre-wrap;">${formulaText}</code>`;
            });
        } else {
            console.log('MathJax not available, using fallback for segment:', index);
            // 如果MathJax不可用，使用普通文本
            segmentElement.innerHTML = `<code style="color: #4a9eff; font-size: 16px; white-space: pre-wrap;">${formulaText}</code>`;
        }
    });
    
    // 将背景容器添加到主容器
    formulaContainer.appendChild(backgroundContainer);
}

// 检测树的有效状态
function checkTreeValidity(tree) {
    if (!tree) return false;
    
    // 检查节点是否有效
    if (tree.type === 'variable') {
        return tree.name && tree.coefficient !== undefined;
    } else if (tree.type === 'operator') {
        return tree.children && tree.children.length === 2;
    }
    
    return false;
}

// 更新性能指标（实时）
function updatePerformanceMetrics(result) {
    const r2Element = document.getElementById('r2-value');
    const mseElement = document.getElementById('mse-value');
    const maeElement = document.getElementById('mae-value');
    const rmseElement = document.getElementById('rmse-value');
    
    if (r2Element) r2Element.textContent = (result.r2 || 0).toFixed(3);
    if (mseElement) mseElement.textContent = (result.mse || 0).toFixed(3);
    if (maeElement) maeElement.textContent = (result.mae || 0).toFixed(3);
    if (rmseElement) rmseElement.textContent = (result.rmse || 0).toFixed(3);
    
    console.log('Updated performance metrics:', result);
}

// 解析表达式为真正的语法树（参考HeuristicLab实现）
function parseExpressionToSyntaxTree(expression, featureImportance) {
    console.log('Parsing expression:', expression);
    
    if (!expression) {
        console.error('Expression is empty');
        return null;
    }
    
    try {
        // 移除等号和目标变量
        let cleanExpression = expression;
        if (cleanExpression.includes('=')) {
            cleanExpression = cleanExpression.split('=')[1].trim();
        }
        
        // 解析表达式，支持加减乘除
        const terms = cleanExpression.split(/(?=[+-])/).filter(term => term.trim());
        console.log('Parsed terms:', terms);
        
        if (terms.length === 0) {
            console.error('No terms found in expression');
            return null;
        }
        
        // 创建真正的二叉树结构（参考HeuristicLab）
        const createBinaryTree = (terms, start, end) => {
            if (start === end) {
                // 单个项
                const term = terms[start].trim();
                const parts = term.split('*');
                if (parts.length === 2) {
                    const coefficient = parseFloat(parts[0].trim());
                    const variable = parts[1].trim();
                    const importance = featureImportance[variable] || 0.1;
                    
                    return {
                        id: `term_${start}`,
                        name: variable,
                        type: 'variable',
                        coefficient: coefficient,
                        importance: importance,
                        weight: getWeightClass(importance),
                        children: []
                    };
                }
            }
            
            if (end - start === 1) {
                // 两个项，创建加法节点
                const left = createBinaryTree(terms, start, start);
                const right = createBinaryTree(terms, end, end);
                
                return {
                    id: `op_${start}_${end}`,
                    name: 'Addition',
                    type: 'operator',
                    operator: '+',
                    importance: 1.0,
                    weight: 'weight-9',
                    children: [left, right]
                };
            }
            
            // 多个项，递归创建二叉树
            const mid = Math.floor((start + end) / 2);
            const left = createBinaryTree(terms, start, mid);
            const right = createBinaryTree(terms, mid + 1, end);
            
            return {
                id: `op_${start}_${end}`,
                name: 'Addition',
                type: 'operator',
                operator: '+',
                importance: 1.0,
                weight: 'weight-9',
                children: [left, right]
            };
        };
        
        // 处理各项，确保格式正确
        const processedTerms = terms.map(term => {
            term = term.trim();
            if (term.startsWith('+')) {
                term = term.substring(1);
            }
            return term;
        }).filter(term => term !== '');
        
        // 创建根节点
        const rootNode = createBinaryTree(processedTerms, 0, processedTerms.length - 1);
        
        console.log('Parsed tree:', rootNode);
        return rootNode;
        
    } catch (error) {
        console.error('Error parsing expression to syntax tree:', error);
        return null;
    }
}

// 使用D3.js生成真正的树形图
function generateFormulaTree(result) {
    const treeContainer = document.getElementById('formula-tree');
    if (!treeContainer) {
        console.error('formula-tree container not found');
        return;
    }
    
    console.log('Generating formula tree for result:', result);
    
    // 检查D3.js是否可用
    if (typeof d3 === 'undefined') {
        console.error('D3.js not available');
        treeContainer.innerHTML = '<p style="color: #ef4444;">D3.js库未加载，无法显示公式树</p>';
        return;
    }
    
    // 清空容器
    treeContainer.innerHTML = '';
    
    // 解析表达式生成语法树
    const syntaxTree = parseExpressionToSyntaxTree(result.expression, result.featureImportance);
    
    // 获取容器实际尺寸，确保不超出窗口
    const containerWidth = treeContainer.clientWidth || 800;
    const containerHeight = treeContainer.clientHeight || 600;
    
    // 设置树形图尺寸，确保不超出容器
    const width = Math.min(containerWidth - 40, 1000); // 留出边距
    const height = Math.min(containerHeight - 40, 700);
    
    try {
        // 创建SVG容器
        const svg = d3.select(treeContainer)
            .append('svg')
            .attr('width', width)
            .attr('height', height)
            .style('border', '1px solid #333')
            .style('background', '#1a1a1a')
            .style('max-width', '100%') // 确保不超出容器
            .style('overflow', 'visible');
        
        // 创建树形布局，使用水平布局避免节点重叠
        const treeLayout = d3.tree()
            .size([width - 100, height - 100])
            .separation((a, b) => (a.parent === b.parent ? 1.2 : 1.5)); // 减少节点间距
        
        // 创建层次结构
        const root = d3.hierarchy(syntaxTree);
        
        // 计算树形布局
        treeLayout(root);
        
        // 绘制连接线
        const links = svg.selectAll('.link')
            .data(root.links())
            .enter()
            .append('path')
            .attr('class', 'link')
            .attr('d', d3.linkVertical()
                .x(d => d.x + 50)
                .y(d => d.y + 50))
            .style('fill', 'none')
            .style('stroke', '#666')
            .style('stroke-width', '2');
        
        // 创建节点组
        const nodes = svg.selectAll('.node')
            .data(root.descendants())
            .enter()
            .append('g')
            .attr('class', 'node')
            .attr('transform', d => `translate(${d.x + 50},${d.y + 50})`);
        
        // 绘制圆角矩形节点
        nodes.append('rect')
            .attr('width', d => d.data.type === 'operator' ? 70 : 60)
            .attr('height', d => d.data.type === 'operator' ? 40 : 35)
            .attr('rx', 8) // 圆角半径
            .attr('ry', 8)
            .style('fill', d => {
                if (d.data.type === 'operator') {
                    // 运算符节点使用灰阶色调
                    return '#6b7280';
                }
                // 根据权重返回颜色
                const weightClass = d.data.weight || 'weight-5';
                const colors = {
                    'weight-1': '#ef4444', 'weight-2': '#f56565', 'weight-3': '#f97316',
                    'weight-4': '#eab308', 'weight-5': '#84cc16', 'weight-6': '#22c55e',
                    'weight-7': '#16a34a', 'weight-8': '#15803d', 'weight-9': '#166534'
                };
                return colors[weightClass] || '#84cc16';
            })
            .style('stroke', '#333')
            .style('stroke-width', '2')
            .style('cursor', 'pointer')
            .on('click', function(event, d) {
                showNodeInfo(event, d);
            })
            .on('contextmenu', function(event, d) {
                event.preventDefault();
                showContextMenu(event, d);
            });
        
        // 添加节点文本（主文本）
        nodes.append('text')
            .attr('x', d => d.data.type === 'operator' ? 35 : 30)
            .attr('y', '15')
            .attr('text-anchor', 'middle')
            .style('fill', 'white')
            .style('font-size', '12px')
            .style('font-weight', 'bold')
            .style('text-shadow', '1px 1px 2px rgba(0,0,0,0.8)')
            .text(d => {
                if (d.data.type === 'operator') {
                    // 运算符节点显示英文名称
                    return d.data.name || 'Addition';
                } else {
                    return d.data.name;
                }
            });
        
        // 添加运算符符号（小字）
        nodes.filter(d => d.data.type === 'operator')
            .append('text')
            .attr('x', 35)
            .attr('y', '30')
            .attr('text-anchor', 'middle')
            .style('fill', '#ccc')
            .style('font-size', '10px')
            .style('text-shadow', '1px 1px 2px rgba(0,0,0,0.8)')
            .text(d => d.data.operator || '+');
        
        // 添加系数标签（对于变量节点）
        nodes.filter(d => d.data.type === 'variable')
            .append('text')
            .attr('x', 30)
            .attr('y', '30')
            .attr('text-anchor', 'middle')
            .style('fill', '#fff')
            .style('font-size', '10px')
            .style('font-weight', 'bold')
            .style('text-shadow', '1px 1px 2px rgba(0,0,0,0.8)')
            .text(d => d.data.coefficient.toFixed(3));
        
        console.log('Formula tree generated successfully');
        
    } catch (error) {
        console.error('Error generating formula tree:', error);
        treeContainer.innerHTML = `<p style="color: #ef4444;">生成公式树时出错: ${error.message}</p>`;
    }
}

// 显示节点信息
function showNodeInfo(event, node) {
    const info = {
        name: node.data.name,
        type: node.data.type,
        coefficient: node.data.coefficient,
        importance: node.data.importance
    };
    
    showNotification(`节点信息: ${info.name}, 类型: ${info.type}, 系数: ${info.coefficient}, 重要性: ${info.importance.toFixed(3)}`, 'info');
}

// 获取权重颜色类（负相关到正相关的渐变）
function getWeightClass(importance) {
    // 将重要性值映射到颜色类
    // 负相关：红色系 (weight-1 到 weight-3)
    // 中性：白色系 (weight-4 到 weight-6)  
    // 正相关：绿色系 (weight-7 到 weight-9)
    
    if (importance <= 0.1) return 'weight-1';      // 深红
    if (importance <= 0.2) return 'weight-2';      // 红色
    if (importance <= 0.3) return 'weight-3';      // 浅红
    if (importance <= 0.4) return 'weight-4';      // 白色
    if (importance <= 0.5) return 'weight-5';      // 浅白
    if (importance <= 0.6) return 'weight-6';      // 白色
    if (importance <= 0.7) return 'weight-7';      // 浅绿
    if (importance <= 0.8) return 'weight-8';      // 绿色
    if (importance <= 1.0) return 'weight-9';      // 深绿
    
    return 'weight-5'; // 默认中性
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
function showContextMenu(event, node) {
    // 移除现有菜单
    const existingMenu = document.querySelector('.context-menu');
    if (existingMenu) existingMenu.remove();
    
    const menu = document.createElement('div');
    menu.className = 'context-menu';
    menu.style.left = event.pageX + 'px';
    menu.style.top = event.pageY + 'px';
    
    const info = {
        name: node.data.name,
        type: node.data.type,
        coefficient: node.data.coefficient,
        importance: node.data.importance
    };
    
    menu.innerHTML = `
        <div class="context-menu-item">节点: ${info.name}</div>
        <div class="context-menu-item">类型: ${info.type}</div>
        <div class="context-menu-item">系数: ${info.coefficient}</div>
        <div class="context-menu-item">重要性: ${info.importance.toFixed(3)}</div>
        <div class="context-menu-item danger" onclick="deleteNode('${node.data.id}')">删除此节点</div>
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
    console.log('Deleting node:', nodeId);
    
    // 添加到删除列表
    if (!window.deletedNodes) window.deletedNodes = [];
    window.deletedNodes.push(nodeId);
    
    // 更新树显示
    updateTreeDisplay();
    
    // 更新树状态
    updateTreeStatus();
}

// 删除低权重节点
function deleteLowWeightNodes() {
    const lowWeightNodes = document.querySelectorAll('.tree-node.weight-1, .tree-node.weight-2, .tree-node.weight-3');
    const deletedFeatures = [];
    
    lowWeightNodes.forEach(node => {
        node.style.opacity = '0.3';
        node.style.textDecoration = 'line-through';
        node.classList.add('deleted');
        
        const feature = node.getAttribute('data-feature');
        deletedFeatures.push(feature);
    });
    
    window.deletedFeatures = deletedFeatures;
    showNotification(`已标记删除 ${deletedFeatures.length} 个低权重特征`, 'info');
}

// 剪枝选中节点
function pruneSelectedNodes() {
    const selectedNodes = document.querySelectorAll('.tree-node.selected');
    if (selectedNodes.length === 0) {
        showNotification('请先选择要删除的节点', 'warning');
        return;
    }
    
    const deletedFeatures = [];
    selectedNodes.forEach(node => {
        node.style.opacity = '0.3';
        node.style.textDecoration = 'line-through';
        node.classList.add('deleted');
        
        const feature = node.getAttribute('data-feature');
        deletedFeatures.push(feature);
    });
    
    window.deletedFeatures = deletedFeatures;
    showNotification(`已标记删除 ${deletedFeatures.length} 个选中特征`, 'info');
}

// 重新计算回归（排除删除的特征）
async function recalculateRegression() {
    console.log('Recalculating regression after node deletion');
    
    // 获取当前数据
    const currentData = window.currentRegressionData;
    if (!currentData) {
        showNotification('没有可用的回归数据', 'error');
        return;
    }
    
    // 获取删除的节点
    const deletedNodes = window.deletedNodes || [];
    
    // 从特征中移除删除的节点
    const filteredFeatures = currentData.features.filter(feature => 
        !deletedNodes.includes(feature)
    );
    
    // 重新构建数据
    const filteredData = {
        ...currentData,
        features: filteredFeatures,
        data: currentData.data.filter((_, index) => 
            !deletedNodes.includes(currentData.features[index])
        )
    };
    
    // 调用后端重新计算
    performSymbolicRegression(filteredData);
}

// 重置公式
function resetFormula() {
    // 重置所有节点状态
    const nodes = document.querySelectorAll('.tree-node');
    nodes.forEach(node => {
        node.classList.remove('selected', 'deleted');
        node.style.opacity = '1';
        node.style.textDecoration = 'none';
    });
    
    // 清除删除的特征记录
    window.deletedFeatures = [];
    
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