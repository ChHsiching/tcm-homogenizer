// 导出蒙特卡洛 Top10 为CSV（前端导出，不入库）
function exportMonteCarloTop10Csv() {
    try {
        const res = currentMonteCarloResult;
        if (!res || !Array.isArray(res.top10) || res.top10.length === 0) {
            showNotification('暂无可导出的结果，请先完成分析', 'warning');
            return;
        }
        const targetName = (window.__mcTargetName__ || '目标');
        // 收集所有出现的变量名，保持列稳定
        const varSet = new Set();
        res.top10.forEach(item => (item.components || []).forEach(c => varSet.add(c.name)));
        const vars = Array.from(varSet);
        // CSV 头
        const headers = ['Rank', `${targetName}`].concat(vars);
        const rows = [headers.join(',')];
        // 每行按变量名顺序取值，无则留空
        res.top10.forEach(item => {
            const map = Object.create(null);
            (item.components || []).forEach(c => { map[c.name] = c.value; });
            const line = [item.rank ?? '', item.efficacy ?? ''].concat(vars.map(v => (map[v] ?? '')));
            rows.push(line.join(','));
        });
        const csv = rows.join('\n');
        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
        const ts = new Date().toISOString().slice(0,19).replace(/[:T]/g,'-');
        const fileName = `monte_carlo_top10_${ts}.csv`;
        if (window.electronAPI && window.electronAPI.saveZipFile) {
            // 复用保存API，尽量触发系统文件对话框
            blob.arrayBuffer().then(buf => window.electronAPI.saveZipFile(fileName, buf));
        } else {
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = fileName;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }
        showNotification('CSV 导出成功', 'success');
    } catch (e) {
        console.error('导出CSV失败:', e);
        showNotification('导出失败: ' + e.message, 'error');
    }
}
// 变量范围配置弹窗
async function openRangeConfigDialog() {
    try {
        // 获取所选数据模型，拉取 data_model.json
        const dataModelId = document.getElementById('mc-data-model').value;
        if (!dataModelId) {
            showNotification('请先选择数据模型', 'warning');
            return;
        }
        
        showNotification('正在加载模型信息...', 'info');
        
        const resp = await fetch(`${API_BASE_URL}/api/data-models/models/${dataModelId}`);
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        const { success, model } = await resp.json();
        if (!success) throw new Error('无法获取模型信息');
        const features = model.feature_columns || [];
        
        // 添加调试信息
        console.log('🔍 从数据模型读取的特征列:', features);
        console.log('🔍 数据模型信息:', model);
        
        // 检查特征列是否为空
        if (!features.length) {
            showNotification('警告：选择的模型没有特征列信息，将使用默认变量', 'warning');
        }

        const modalTitle = document.getElementById('modal-title');
        const modalBody = document.getElementById('modal-body');
        const modalOverlay = document.getElementById('modal-overlay');
        const confirmBtn = document.getElementById('modal-confirm');
        const cancelBtn = document.getElementById('modal-cancel');
        if (modalTitle) modalTitle.textContent = '设置变量范围';
        if (modalBody) {
            const ranges = (window.__mcRanges__ && typeof window.__mcRanges__ === 'object') ? window.__mcRanges__ : {};
            const vars = (features.length ? features : ['变量1','变量2']);
            
            // 添加调试信息
            console.log('🔍 最终使用的变量列表:', vars);
            
            // 显示数据来源信息
            const dataSourceInfo = features.length 
                ? `从数据模型 "${model.name}" 读取到 ${features.length} 个特征变量`
                : '使用默认变量（建议先选择包含特征列的数据模型）';
            
            const header = `
                <div style="margin-bottom: 15px; padding: 10px; background: var(--bg-tertiary); border-radius: 6px; font-size: 12px; color: var(--text-secondary);">
                    📊 ${dataSourceInfo}
                </div>
                <div class="range-row" style="font-weight:600;">
                    <div></div>
                    <div style="color: var(--text-secondary)">最小值</div>
                    <div style="color: var(--text-secondary)">最大值</div>
                </div>`;
            const rows = vars.map(name => {
                const prev = ranges[name] || {};
                const minVal = (prev.min !== undefined && prev.min !== null) ? String(prev.min) : '';
                const maxVal = (prev.max !== undefined && prev.max !== null) ? String(prev.max) : '';
                const cnName = (typeof getComponentChineseName === 'function') ? getComponentChineseName(name) : name;
                return `
                    <div class="range-row">
                        <div class="var-name"><span class="primary">${name}</span><span class="secondary">${cnName}</span></div>
                        <input type="number" step="0.01" placeholder="0" data-var="${name}" data-type="min" value="${minVal}">
                        <input type="number" step="0.01" placeholder="+∞" data-var="${name}" data-type="max" value="${maxVal}">
                    </div>
                `;
            }).join('');
            modalBody.innerHTML = `<div>${header}${rows}</div>`;
        }
        if (modalOverlay) {
            modalOverlay.style.display = 'flex';
        // 右上角叉号关闭（取消）
        const closeBtn = document.querySelector('.modal-close');
        if (closeBtn) closeBtn.onclick = () => authManager.hideModal();
            if (confirmBtn) {
                confirmBtn.onclick = () => {
                    const inputs = modalBody.querySelectorAll('input[data-var]');
                    const ranges = {};
                    inputs.forEach(inp => {
                        const varName = inp.getAttribute('data-var');
                        const t = inp.getAttribute('data-type');
                        ranges[varName] = ranges[varName] || { min: 0, max: null };
                        const v = inp.value.trim();
                        if (t === 'min') {
                            ranges[varName].min = (v === '') ? 0 : Number(v);
                        } else {
                            ranges[varName].max = (v === '') ? null : Number(v);
                        }
                    });
                    // 与模型ID绑定存储，避免换模型时串扰
                    window.__mcRanges__ = window.__mcRanges__ || {};
                    window.__mcRanges__.__model__ = dataModelId;
                    Object.keys(ranges).forEach(k => {
                        window.__mcRanges__[k] = ranges[k];
                    });
                    authManager.hideModal();
                    showNotification('变量范围已设置', 'success');
                };
            }
            if (cancelBtn) {
                cancelBtn.onclick = () => {
                    authManager.hideModal();
                };
            }
        }
    } catch (e) {
        console.error('打开范围配置失败:', e);
        showNotification('打开范围配置失败: ' + e.message, 'error');
    }
}
// 全局变量
let currentData = null;
let regressionModels = [];
let currentRegressionResult = null;
let currentMonteCarloResult = null; // 最近一次蒙特卡洛分析结果（用于导出）
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

// 全局函数：显示指定标签页（用于首页按钮点击）
function showTab(tabName) {
    console.log(`🔄 切换到标签页: ${tabName}`);
    switchTab(tabName);
}

// DOM 加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// 应用初始化
async function initializeApp() {
    console.log('🚀 初始化本草智配客户端...');
    
    // 初始化认证系统
    await authManager.initialize();
    
    // 设置事件监听器
    setupEventListeners();
    
    // 设置数据管理事件监听器
    setupDataManagementListeners();
    
    // 加载设置
    loadSettings();
    
    // 更新状态栏
    updateStatusBar();
    
    // 立即更新连接状态为检查中
    updateConnectionStatus('检查中...');
    
    // 测试后端连接
    await testBackendConnection();
    
    // 显示欢迎通知
    showNotification('欢迎使用本草智配客户端', 'success');
    
    // 测试用户管理功能
    if (authManager) {
        setTimeout(() => {
            authManager.testUserManagement();
        }, 2000);
    }
    
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
    // 下拉菜单项事件
    const dropdownItems = document.querySelectorAll('.dropdown-item');
    dropdownItems.forEach(item => {
        item.addEventListener('click', function() {
            const tabName = this.getAttribute('data-tab');
            switchTab(tabName);
        });
    });
    
    // 文件输入事件
    const regressionDataInput = document.getElementById('regression-data');
    if (regressionDataInput) {
        regressionDataInput.addEventListener('change', handleFileUpload);
    }
    
    // 开始分析按钮事件
    const startRegressionBtn = document.getElementById('start-regression');
    if (startRegressionBtn) {
        startRegressionBtn.addEventListener('click', startRegression);
    }
    
    // 导出模型按钮事件
    const exportModelBtn = document.getElementById('export-model');
    if (exportModelBtn) {
        exportModelBtn.addEventListener('click', exportModel);
    }
    
    const startMonteCarloBtn = document.getElementById('start-monte-carlo');
    if (startMonteCarloBtn) {
        startMonteCarloBtn.addEventListener('click', startMonteCarlo);
    }
    // 变量范围配置按钮
    const openRangeBtn = document.getElementById('open-range-config');
    if (openRangeBtn) {
        openRangeBtn.addEventListener('click', openRangeConfigDialog);
    }
    
    // 表达式语法选择checkbox事件处理
    setupGrammarCheckboxEvents();
    
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

    // 随机种子相关事件
    setupSeedControls();
}

// 切换标签页
function switchTab(tabName) {
    // 获取当前激活的标签页
    const currentActiveTab = document.querySelector('.tab-content.active');
    const targetTab = document.getElementById(tabName);
    
    if (!targetTab) {
        console.error('❌ 找不到目标标签页:', tabName);
        return;
    }
    
    // 如果点击的是当前激活的标签页，不做任何操作
    if (currentActiveTab === targetTab) {
        return;
    }
    
    // 创建页面切换指示器
    let transitionIndicator = document.querySelector('.page-transition-indicator');
    if (!transitionIndicator) {
        transitionIndicator = document.createElement('div');
        transitionIndicator.className = 'page-transition-indicator';
        document.body.appendChild(transitionIndicator);
    }
    
    // 显示页面切换指示器
    transitionIndicator.classList.add('active');
    
    // 移除所有导航按钮的激活状态
    const navButtons = document.querySelectorAll('.nav-btn');
    navButtons.forEach(button => {
        button.classList.remove('active');
    });
    
    // 激活对应的导航按钮（表达式树属于符号回归的二级页，仍高亮主按钮）
    let navHighlightTabName = tabName;
    if (tabName === 'expression-tree') {
        navHighlightTabName = 'regression';
    }
    const targetButton = document.querySelector(`.nav-btn[data-tab="${navHighlightTabName}"]`);
    if (targetButton) {
        targetButton.classList.add('active');
    }
    
    // 更丝滑的页面切换动画
    if (currentActiveTab) {
        // 为当前页面添加过渡状态
        currentActiveTab.classList.add('transitioning');
        
        // 当前页面淡出 - 使用更长的动画时间
        currentActiveTab.classList.add('fade-out');
        
        // 延迟显示目标页面，确保过渡更丝滑
        setTimeout(() => {
            // 隐藏当前页面
            currentActiveTab.classList.remove('active', 'fade-out', 'transitioning');
            
            // 显示目标页面并淡入
            targetTab.classList.add('active', 'fade-in');
            
            // 移除过渡状态
            targetTab.classList.remove('transitioning');
            
            // 移除淡入类，保持激活状态
            setTimeout(() => {
                targetTab.classList.remove('fade-in');
                
                // 隐藏页面切换指示器
                transitionIndicator.classList.remove('active');
                
                // 延迟移除指示器元素
                setTimeout(() => {
                    if (transitionIndicator.parentElement) {
                        transitionIndicator.remove();
                    }
                }, 300);
                
                // 在页面切换完成后重新设置checkbox事件
                if (tabName === 'regression') {
                    setupGrammarCheckboxEvents();
                    // 切换到符号回归页时同步种子可用状态
                    setupSeedControls();
                }
                
            }, 500); // 增加动画时间
            
        }, 300); // 增加延迟时间，让过渡更丝滑
    } else {
        // 如果没有当前激活的页面，直接显示目标页面
        targetTab.classList.add('active');
        
        // 隐藏页面切换指示器
        setTimeout(() => {
            transitionIndicator.classList.remove('active');
            setTimeout(() => {
                if (transitionIndicator.parentElement) {
                    transitionIndicator.remove();
                }
            }, 300);
        }, 200);
    }
    
    // 特殊处理：用户管理页面自动加载用户列表
    if (tabName === 'user-management') {
        console.log('🔍 切换到用户管理页面');
        if (authManager && authManager.currentUser && authManager.currentUser.role === 'admin') {
            console.log('🔍 用户是管理员，自动加载用户列表');
            setTimeout(() => {
                authManager.loadUsers();
            }, 800); // 延迟到动画完成后执行
        } else {
            console.log('🔍 用户不是管理员，显示权限不足');
            const usersTable = document.getElementById('users-table');
            if (usersTable) {
                usersTable.innerHTML = '<p>权限不足，只有管理员可以查看用户列表</p>';
            }
        }
    }
    
    // 特殊处理：数据管理页面自动加载数据模型列表
    if (tabName === 'data-management') {
        console.log('🔍 切换到数据管理页面');
        if (authManager && authManager.currentUser && authManager.currentUser.role === 'admin') {
            console.log('🔍 用户是管理员，自动加载数据模型列表');
            setTimeout(() => {
                loadDataModels();
            }, 800); // 延迟到动画完成后执行
        } else {
            console.log('🔍 用户不是管理员，显示权限不足');
            const dataPreview = document.getElementById('data-preview');
            if (dataPreview) {
                dataPreview.innerHTML = '<p>权限不足，只有管理员可以查看数据模型</p>';
            }
        }
    }
    
    // 特殊处理：蒙特卡洛采样页面自动加载数据模型列表
    if (tabName === 'monte-carlo') {
        console.log('🔍 切换到蒙特卡洛采样页面');
        setTimeout(() => {
            loadDataModelsForMonteCarlo();
        }, 800); // 延迟到动画完成后执行
    }
    // 特殊处理：切换到 符号表达式树 页面时渲染左侧概览
    if (tabName === 'expression-tree') {
        console.log('🔍 切换到符号表达式树页面');
        setTimeout(() => {
            renderExpressionTreePage();
        }, 600);
    }
    
    // 更新状态栏
    updateStatusBar();
    
    // 滚动到页面顶部，确保良好的用户体验
    setTimeout(() => {
        const mainContent = document.querySelector('.main-content');
        if (mainContent) {
            mainContent.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        }
    }, 100);
}

// 渲染"符号表达式树"页面（按专用布局分别填充左右区域）
async function renderExpressionTreePage() {
    const perfContainer = document.getElementById('expr-performance-container');
    const detailedContainer = document.getElementById('expr-detailed-container');
    const formulaContainer = document.getElementById('expr-formula-container');
    const featureContainer = document.getElementById('expr-feature-container');
    if (!perfContainer || !detailedContainer || !formulaContainer || !featureContainer) return;

    try {
        perfContainer.innerHTML = '<p>正在加载模型信息...</p>';
        detailedContainer.innerHTML = '';
        formulaContainer.innerHTML = '';
        featureContainer.innerHTML = '';
        // 优先使用最新一次回归结果；否则直接从数据库获取最新数据
        let summary = null;
        if (window.currentRegressionResult) {
            // 统一改为：即使有当前回归结果，也从数据库取回归文件，保证与数据库一致
            try {
                const modelId = window.currentRegressionResult.data_model_id;
                if (modelId) {
                    const regResp = await fetch(`${API_BASE_URL}/api/data-models/models/${modelId}/files/regression_model`);
                    if (regResp.ok) {
                        const regJson = await regResp.json();
                        if (regJson && regJson.success && regJson.content) {
                            const reg = JSON.parse(regJson.content);
                            summary = {
                                id: modelId,
                                data_model_id: modelId,
                                expression: reg.expression_text || reg.expression || '0',
                                expression_latex: reg.expression_latex || '',
                                target_variable: reg.target_variable || 'HDL',
                                constants: reg.constants || {},
                                pearson_r_test: reg.detailed_metrics?.pearson_r_test || 0,
                                pearson_r_training: reg.detailed_metrics?.pearson_r_training || 0,
                                feature_importance: reg.feature_importance || [],
                                impact_tree: reg.impact_tree || null,
                                detailed_metrics: reg.detailed_metrics || {},
                                created_at: reg.created_at || Date.now()
                            };
                            console.log('🔍 构造的 summary 对象（当前回归结果）:', summary);
                            console.log('🔍 reg.impact_tree（当前回归结果）:', reg.impact_tree);
                            console.log('✅ 从数据库获取到当前回归结果的模型数据:', modelId);
                        }
                    }
                }
            } catch (err) {
                console.error('从数据库加载当前回归结果模型失败:', err);
            }
        } else {
            // 没有当前回归结果，直接从数据库获取最新数据
            try {
                const resp = await fetch(`${API_BASE_URL}/api/data-models/models`);
                if (resp.ok) {
                    const listJson = await resp.json();
                    if (listJson && listJson.success && Array.isArray(listJson.models) && listJson.models.length > 0) {
                        const latest = listJson.models[0];
                        const modelId = latest.id;
                        // 直接从数据库获取回归模型文件内容
                        const regResp = await fetch(`${API_BASE_URL}/api/data-models/models/${modelId}/files/regression_model`);
                        if (regResp.ok) {
                            const regJson = await regResp.json();
                            if (regJson && regJson.success && regJson.content) {
                                const reg = JSON.parse(regJson.content);
                                // 构造完整的摘要数据
                                summary = {
                                    id: modelId,
                                    data_model_id: modelId,
                                    expression: reg.expression_text || reg.expression || '0',
                                    expression_latex: reg.expression_latex || '',
                                    target_variable: reg.target_variable || 'HDL',
                                    constants: reg.constants || {},
                                    pearson_r_test: reg.detailed_metrics?.pearson_r_test || 0,
                                    pearson_r_training: reg.detailed_metrics?.pearson_r_training || 0,
                                    feature_importance: reg.feature_importance || [],
                                    impact_tree: reg.impact_tree || null,
                                    detailed_metrics: reg.detailed_metrics || {},
                                    created_at: reg.created_at || Date.now()
                                };
                                console.log('🔍 构造的 summary 对象:', summary);
                                console.log('🔍 reg.impact_tree:', reg.impact_tree);
                                console.log('✅ 从数据库获取到最新数据:', modelId);
                            }
                        }
                    }
                }
            } catch (error) {
                console.error('从数据库获取数据失败:', error);
            }
        }
        // 兜底：如果从数据库没有获取到数据，才使用后端模拟数据
        if (!summary) {
            console.warn('⚠️ 数据库中没有找到任何符号回归模型，无法渲染表达式树');
            showNotification('数据库中没有找到符号回归模型，请先在"符号回归"页面完成一次分析', 'warning');
            perfContainer.innerHTML = '<p class="text-muted">暂无模型</p>';
            detailedContainer.innerHTML = '<p class="text-muted">暂无</p>';
            formulaContainer.innerHTML = '<p class="text-muted">暂无公式</p>';
            featureContainer.innerHTML = '<p class="text-muted">暂无特征影响力</p>';
            return;
        }
        // 确保数据完整性：验证expression字段
        if (!summary.expression || summary.expression === '0') {
            console.warn('⚠️ 数据不完整，尝试重新获取');
            // 如果有模型ID，尝试重新获取数据
            if (summary.id || summary.data_model_id) {
                try {
                    const modelId = summary.id || summary.data_model_id;
                    const regResp = await fetch(`${API_BASE_URL}/api/data-models/models/${modelId}/files/regression_model`);
                    if (regResp.ok) {
                        const regJson = await regResp.json();
                        if (regJson && regJson.success && regJson.content) {
                            const reg = JSON.parse(regJson.content);
                            summary.expression = reg.expression_text || reg.expression || summary.expression;
                            console.log('✅ 重新获取到表达式数据:', summary.expression);
                        }
                    }
                } catch (error) {
                    console.error('重新获取数据失败:', error);
                }
            }
        }
        // 统一使用数据库中的 MathJax 作为单一真源来驱动 SVG：将 LaTeX 转为中缀
        if (summary.expression_latex) {
            const normalized = latexToInfix(summary.expression_latex, summary.constants);
            if (normalized) summary.expression = normalized;
        }
        // 显示摘要信息
        displayExpressionTreeSummary(summary);
        // 渲染表达式树
        try {
            await renderExpressionTreeSVG(summary);
        } catch (e) {
            const canvas = document.getElementById('expression-tree-canvas');
            if (canvas) canvas.innerHTML = `<p class="text-muted">表达式树渲染失败：${e.message}</p>`;
        }
        // 添加自动刷新功能：每5分钟自动刷新一次数据
        if (window.__exprTreeAutoRefreshTimer__) {
            clearInterval(window.__exprTreeAutoRefreshTimer__);
        }
        window.__exprTreeAutoRefreshTimer__ = setInterval(async () => {
            console.log('🔄 自动刷新表达式树数据...');
            try {
                await renderExpressionTreePage();
                showNotification('表达式树数据已自动刷新', 'info');
            } catch (error) {
                console.error('自动刷新失败:', error);
            }
        }, 5 * 60 * 1000); // 5分钟
    } catch (e) {
        console.error('表达式树概览加载失败', e);
        perfContainer.innerHTML = `<p class="text-muted">加载失败：${e.message}</p>`;
        showNotification('表达式树概览加载失败: ' + e.message, 'error');
    }
}
// LaTeX 转中缀表达式（全局复用，保持 SVG 与上方公式同源）
function latexToInfix(latex, constantsMap) {
  if (!latex || typeof latex !== 'string') return '';
  let s = String(latex);
  s = s.replace(/\r?\n/g, ' ');
  const endIdx = s.indexOf('\\end{align*}');
  if (endIdx !== -1) s = s.slice(0, endIdx);
  const eqMatch = s.match(/&\s*=\s*(.*)$/) || s.match(/&=\s*(.*)$/);
  if (eqMatch) s = eqMatch[1];
  s = s.replace(/\\begin\{align\*\}/g, '')
       .replace(/\\nonumber/g, '')
       .replace(/\\;/g, ' ')
       .trim();
  function findMatchingBrace(str, startIdx) {
    let depth = 0;
    for (let i = startIdx; i < str.length; i++) {
      const ch = str[i];
      if (ch === '{') depth++;
      else if (ch === '}') {
        depth--;
        if (depth === 0) return i;
      }
    }
    return -1;
  }
  function replaceFirstCfrac(str) {
    const tag = '\\cfrac';
    const i = str.indexOf(tag);
    if (i === -1) return str;
    const aStart = str.indexOf('{', i + tag.length);
    if (aStart === -1) return str;
    const aEnd = findMatchingBrace(str, aStart);
    if (aEnd === -1) return str;
    const bStart = str.indexOf('{', aEnd + 1);
    if (bStart === -1) return str;
    const bEnd = findMatchingBrace(str, bStart);
    if (bEnd === -1) return str;
    const num = str.slice(aStart + 1, aEnd);
    const den = str.slice(bStart + 1, bEnd);
    const before = str.slice(0, i);
    const after = str.slice(bEnd + 1);
    return before + '(' + num + ')/(' + den + ')' + after;
  }
  while (s.includes('\\cfrac')) s = replaceFirstCfrac(s);
  s = s.replace(/\\left\s*/g, '')
       .replace(/\\right\s*/g, '')
       .replace(/\\cdot/g, '*')
       .replace(/\\times/g, '*')
       .replace(/\\,/g, ' ')
       .replace(/\\!/g, ' ');
  s = s.replace(/\\text\{([^}]*)\}/g, '$1');
  const idxToVal = new Map();
  try {
    const entries = Object.entries(constantsMap || {});
    for (const [k, v] of entries) {
      const m = String(k).match(/^c(?:[_{]?)(\d+)\}?$/i);
      if (m) idxToVal.set(m[1], v);
    }
  } catch (_) {}
  function replaceConstByIndex(match, p1) {
    if (idxToVal.has(p1)) return String(idxToVal.get(p1));
    return match;
  }
  s = s.replace(/c_\{\s*(\d+)\s*\}/g, replaceConstByIndex)
       .replace(/c\{\s*(\d+)\s*\}/g, replaceConstByIndex)
       .replace(/c_(\d+)/g, replaceConstByIndex)
       .replace(/\bc(\d+)\b/g, replaceConstByIndex);
  s = s.replace(/\s+/g, ' ').trim();
  return s;
}

async function renderExpressionTreeSVG(summary) {
    const canvas = document.getElementById('expression-tree-canvas');
    if (!canvas) return;
    const inner = canvas.querySelector('.expr-tree-inner') || canvas;
    const expression = (summary && summary.expression) || '0';
    inner.innerHTML = '';
    
    // 调试信息：显示summary对象的内容
    console.log('🔍 renderExpressionTreeSVG 接收到的 summary:', summary);
    console.log('🔍 summary.impact_tree:', summary?.impact_tree);
    
    // 使用后端返回的 impact_tree 作为唯一来源（不再从 /docs 读取）
    try {
        if (summary && summary.impact_tree) {
            window.TREE_IMPACT_DATA = summary.impact_tree;
            console.log('✅ 已从回归模型数据加载影响力数据 (impact_tree)');
            console.log('🔍 完整的 impact_tree 数据结构:', JSON.stringify(summary.impact_tree, null, 2));
            console.log('🔍 impact_tree 的键:', Object.keys(summary.impact_tree));
        } else {
            // 若本次摘要未包含，则保留内存中的旧值，避免置空导致白色
            if (!window.TREE_IMPACT_DATA) {
                console.warn('⚠️ 本次摘要未包含 impact_tree 且内存无缓存，无法着色');
            } else {
                console.log('ℹ️ 本次摘要未包含 impact_tree，沿用内存中的影响力数据');
            }
        }
    } catch (error) {
        console.warn('⚠️ 影响力数据装载失败:', error);
    }
    
    try {
        const exprPreview = String(expression).slice(0, 120);
        console.log('[ExprTree] 使用表达式（已规范化）来源:', summary?.id || summary?.data_model_id || 'unknown', '| 预览:', exprPreview);
    } catch (_) {}
    let ast = ExprTree.normalizeAst(ExprTree.parseExpressionToAst(expression));
    window.currentExpressionAst = ast;
    window.__exprTreeUndo__ = [];
    window.__currentModelId__ = summary.id || summary.data_model_id;
    ExprTree.computeWeights(ast, { mode: 'coef' });
    const rect = canvas.getBoundingClientRect();
    const layoutInfo = ExprTree.layoutTree(ast, Math.max(rect.width, 900), { siblingGap: 24, vGap: 120, drawScale: 1.5 });
    const svg = ExprTree.renderSvgTree(inner, ast, { width: layoutInfo.width, config: layoutInfo.config, bounds: layoutInfo.bounds });
    wireToolbarActions(inner, () => svg);
    // 树绘制后，若数据库未提供 feature_importance，则用前端计算并刷新右下卡片
    try {
        if (!Array.isArray(summary.feature_importance) || summary.feature_importance.length === 0) {
            summary.feature_importance = ExprTree.computeFeatureImportance(ast);
            displayExpressionTreeSummary(summary);
        }
    } catch (_) {}
}

function wireToolbarActions(container, getSvg) {
    const btnDel = container.parentElement.querySelector('#btn-delete');
    const btnUndo = container.parentElement.querySelector('#btn-undo');
    const btnSimplify = container.parentElement.querySelector('#btn-simplify');
    const btnOptimize = container.parentElement.querySelector('#btn-optimize');
    // 推断数据模型ID（用于写回）
    const modelId = (window.currentRegressionResult && window.currentRegressionResult.data_model_id) || null;
    const getSelectedId = () => {
        const svg = getSvg();
        const sel = svg && svg.querySelector('[data-selected="true"]');
        return sel ? sel.getAttribute('data-node-id') : null;
    };
    const rerender = async (ast, action = 'apply') => {
        const canvas = document.getElementById('expression-tree-canvas');
        const inner = canvas.querySelector('.expr-tree-inner') || canvas;
        inner.innerHTML = '';
        ExprTree.computeWeights(ast, { mode: 'coef' });
        const rect = canvas.getBoundingClientRect();
        const layoutInfo = ExprTree.layoutTree(ast, Math.max(rect.width, 900), { siblingGap: 24, vGap: 120, drawScale: 1.5 });
        const svg = ExprTree.renderSvgTree(inner, ast, { width: layoutInfo.width, config: layoutInfo.config, bounds: layoutInfo.bounds });
        wireToolbarActions(inner, () => svg);
        
        // 从AST中提取常量信息，保持常量模块显示
        const extractConstantsFromAst = (node) => {
            // 使用与generateLatexFormula完全相同的逻辑：按照数值在表达式中出现的顺序分配常量代号
            const constants = {};
            const usedNumbers = new Set();
            
            // 首先将AST转换为表达式字符串，然后按照数字出现的顺序分配常量代号
            const expressionStr = ExprTree.astToExpression(node);
            
            // 使用与generateLatexFormula相同的数字匹配逻辑
            const numberPattern = /-?\d+\.?\d*/g;
            const numbers = expressionStr.match(numberPattern) || [];
            
            numbers.forEach((num) => {
                const numValue = parseFloat(num);
                if (!usedNumbers.has(numValue)) {
                    const index = Object.keys(constants).length;
                    const key = `c_${index}`;
                    constants[key] = numValue;
                    usedNumbers.add(numValue);
                }
            });
            
            return constants;
        };
        
        const constants = extractConstantsFromAst(ast);
        
        // 生成LaTeX公式，保持常量模块显示
        const expressionStr = ExprTree.astToLatexWithConstants(ast, 'HDL', constants);
        const formulaContainer = document.getElementById('expr-formula-container');
        if (formulaContainer) {
            // 保持与displayExpressionTreeSummary完全一致的渲染逻辑
            const formatConstantsForDisplay = (consts) => {
                const entries = Object.entries(consts || {}).map(([k, v]) => {
                    const m = String(k).match(/^c(?:_|\{)?(\d+)\}?$/i);
                    const idx = m ? parseInt(m[1], 10) : Number.MAX_SAFE_INTEGER;
                    const latexKey = m ? `c_{${m[1]}}` : String(k);
                    return { idx, key: latexKey, value: v };
                });
                entries.sort((a, b) => a.idx - b.idx);
                return entries;
            };
            
            // 完全复制displayExpressionTreeSummary的HTML结构
            formulaContainer.innerHTML = `
                <div class="regression-formula-container">
                    <div class="regression-formula">$${expressionStr}$</div>
                    ${Object.keys(constants).length ? `
                    <div class="regression-constants">
                        <h5>常数定义</h5>
                        <div class="constant-list">
                            ${formatConstantsForDisplay(constants).map(item => `<div class="constant-item">$${item.key} = ${item.value}$</div>`).join('')}
                        </div>
                    </div>` : ''}
                </div>
                <div class="result-actions" style="margin-top: 10px;">
                    <button class="btn-secondary" onclick="switchTab('regression')">返回回归</button>
                    <button class="btn-primary" onclick="refreshExpressionTreeData()" style="margin-left: 10px;">
                        刷新数据
                    </button>
                </div>
            `;
            
            // 确保MathJax渲染，包括常量模块
            if (window.MathJax && window.MathJax.typesetPromise) {
                MathJax.typesetPromise([formulaContainer]).catch(()=>{});
            }
        }
        
        // 写回数据库：同步更新到后端（包含表达式树操作类型以驱动后端指标轮换/撤销）
        const modelId = window.__currentModelId__;
        if (modelId) {
            try {
                // 1. 更新主数据模型
                const mainModelResp = await fetch(`${API_BASE_URL}/api/data-models/models/${modelId}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        symbolic_regression: {
                            expression_latex: expressionStr,
                            impact_tree: window.TREE_IMPACT_DATA,
                            updated_at: Date.now()
                        },
                        feature_importance: ExprTree.computeFeatureImportance(ast),
                        expr_tree_action: action
                    })
                });
                
                if (!mainModelResp.ok) {
                    throw new Error(`主数据模型更新失败: ${mainModelResp.status}`);
                }
                
                // 2. 更新回归模型文件（由后端据 action 更新 detailed_metrics 与元数据）
                const regModelResp = await fetch(`${API_BASE_URL}/api/data-models/models/${modelId}/files/regression_model`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        expression_latex: expressionStr,
                        expression: expressionStr,
                        constants: constants, // 添加常量信息
                        feature_importance: ExprTree.computeFeatureImportance(ast),
                        impact_tree: window.TREE_IMPACT_DATA,
                        updated_at: Date.now(),
                        expr_tree_action: action
                    })
                });
                
                if (!regModelResp.ok) {
                    throw new Error(`回归模型文件更新失败: ${regModelResp.status}`);
                }
                
                // 3. 读取最新摘要以刷新左侧性能与详细指标
                try {
                    const updated = await fetchExpressionTreeSummary({ model_id: modelId });
                    if (updated) {
                        displayExpressionTreeSummary(updated);
                    }
                } catch (e) {
                    console.warn('刷新表达式树摘要失败（将继续显示旧指标）:', e);
                }

                console.log('✅ 表达式树修改已同步到数据库并刷新指标');
                showNotification('表达式树修改已同步到数据库并刷新指标', 'success');
                
            } catch (error) {
                console.error('❌ 数据库同步失败:', error);
                showNotification('数据库同步失败: ' + error.message, 'error');
            }
        } else {
            console.warn('⚠️ 无法获取模型ID，跳过数据库同步');
        }
    };

    if (btnDel) btnDel.onclick = () => {
        const id = getSelectedId();
        if (!id) return;
        window.__exprTreeUndo__.push(ExprTree.cloneAst(window.currentExpressionAst));
        const next = ExprTree.deleteNodeById(window.currentExpressionAst, id);
        window.currentExpressionAst = ExprTree.simplifyAst(next);
        showNotification('正在删除节点/子树...', 'info');
        if (typeof window.__updateExprOpCounter__ === 'function') window.__updateExprOpCounter__(+1);
        rerender(window.currentExpressionAst, 'delete');
    };
    if (btnUndo) btnUndo.onclick = () => {
        if (!window.__exprTreeUndo__ || window.__exprTreeUndo__.length === 0) return;
        const prev = window.__exprTreeUndo__.pop();
        window.currentExpressionAst = prev;
        showNotification('正在撤销操作...', 'info');
        if (typeof window.__updateExprOpCounter__ === 'function') window.__updateExprOpCounter__(-1);
        rerender(window.currentExpressionAst, 'undo');
    };
    if (btnSimplify) btnSimplify.onclick = () => {
        window.__exprTreeUndo__.push(ExprTree.cloneAst(window.currentExpressionAst));
        window.currentExpressionAst = ExprTree.simplifyAst(window.currentExpressionAst);
        showNotification('正在简化表达式...', 'info');
        if (typeof window.__updateExprOpCounter__ === 'function') window.__updateExprOpCounter__(+1);
        rerender(window.currentExpressionAst, 'simplify');
    };
    if (btnOptimize) btnOptimize.onclick = () => {
        window.__exprTreeUndo__.push(ExprTree.cloneAst(window.currentExpressionAst));
        window.currentExpressionAst = ExprTree.simplifyAst(window.currentExpressionAst);
        showNotification('正在优化表达式...', 'info');
        if (typeof window.__updateExprOpCounter__ === 'function') window.__updateExprOpCounter__(+1);
        rerender(window.currentExpressionAst, 'optimize');
    };
}

// 获取表达式树页面左侧所需摘要（空壳API）
async function fetchExpressionTreeSummary(payload) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/regression/expression-tree/summary`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload || {})
        });
        if (!response.ok) {
            const err = await response.json().catch(() => ({}));
            throw new Error(err.message || `HTTP ${response.status}`);
        }
        const json = await response.json();
        if (!json.success) throw new Error(json.message || '接口返回失败');
        return json.result;
    } catch (err) {
        throw err;
    }
}

// 渲染左/右区域摘要（公式、性能、详细指标、特征影响力）
function displayExpressionTreeSummary(result) {
    const perfContainer = document.getElementById('expr-performance-container');
    const detailedContainer = document.getElementById('expr-detailed-container');
    const formulaContainer = document.getElementById('expr-formula-container');
    const featureContainer = document.getElementById('expr-feature-container');
    if (!perfContainer || !detailedContainer || !formulaContainer || !featureContainer) return;

    const expression = result.expression || '';
    const targetVariable = result.target_variable || 'Y';
    const constants = result.constants || {};
    // 若后端提供了 LaTeX 公式，则直接使用；否则由表达式生成
    const latexFormula = result.expression_latex
        ? result.expression_latex
        : generateLatexFormula(expression, targetVariable, constants);
    const detailed = result.detailed_metrics || {};

    // 帮助：常数排序与 LaTeX 格式化
    const formatConstantsForDisplay = (consts) => {
        const entries = Object.entries(consts || {}).map(([k, v]) => {
            const m = String(k).match(/^c(?:_|\{)?(\d+)\}?$/i);
            const idx = m ? parseInt(m[1], 10) : Number.MAX_SAFE_INTEGER;
            const latexKey = m ? `c_{${m[1]}}` : String(k);
            return { idx, key: latexKey, value: v };
        });
        entries.sort((a, b) => a.idx - b.idx);
        return entries;
    };

    // 右上：公式
    formulaContainer.innerHTML = `
        <div class="regression-formula-container">
            <div class="regression-formula">$${latexFormula}$</div>
            ${Object.keys(constants).length ? `
            <div class="regression-constants">
                <h5>常数定义</h5>
                <div class="constant-list">
                    ${formatConstantsForDisplay(constants).map(item => `<div class="constant-item">$${item.key} = ${item.value}$</div>`).join('')}
                </div>
            </div>` : ''}
        </div>
        <div class="result-actions" style="margin-top: 10px;">
            <button class="btn-secondary" onclick="switchTab('regression')">返回回归</button>
            <button class="btn-primary" onclick="refreshExpressionTreeData()" style="margin-left: 10px;">
                刷新数据
            </button>
        </div>
    `;

    // 左侧：性能
    perfContainer.innerHTML = `
        <div class="performance-metrics">
            <div class="performance-metric">
                <div class="metric-label">皮尔逊相关系数</div>
                <div class="metric-value">${(result.pearson_r_test ?? 0).toFixed(3)}<span class="metric-raw">${typeof result.pearson_r_test === 'number' ? ` (${result.pearson_r_test})` : ''}</span></div>
                <div class="metric-unit">(测试)</div>
            </div>
            <div class="performance-metric">
                <div class="metric-label">皮尔逊相关系数</div>
                <div class="metric-value">${(result.pearson_r_training ?? 0).toFixed(3)}<span class="metric-raw">${typeof result.pearson_r_training === 'number' ? ` (${result.pearson_r_training})` : ''}</span></div>
                <div class="metric-unit">(训练)</div>
            </div>
        </div>
    `;

    // 左侧：详细指标
    if (result.detailed_metrics) {
        detailedContainer.innerHTML = `
            <div class="metrics-grid">
                    <div class="metric-section">
                        <h6>误差指标</h6>
                        <div class="metric-list">
                            <div class="metric-item"><div class="metric-name-container"><span class="metric-name-cn">平均相对误差</span><span class="metric-name-en">Average relative error</span><span class="metric-dataset">(测试)</span></div><span class="metric-value">${detailed.average_relative_error_test}%</span></div>
                            <div class="metric-item"><div class="metric-name-container"><span class="metric-name-cn">平均相对误差</span><span class="metric-name-en">Average relative error</span><span class="metric-dataset">(训练)</span></div><span class="metric-value">${detailed.average_relative_error_training}%</span></div>
                            <div class="metric-item"><div class="metric-name-container"><span class="metric-name-cn">平均绝对误差</span><span class="metric-name-en">Mean absolute error</span><span class="metric-dataset">(测试)</span></div><span class="metric-value">${detailed.mean_absolute_error_test}</span></div>
                            <div class="metric-item"><div class="metric-name-container"><span class="metric-name-cn">平均绝对误差</span><span class="metric-name-en">Mean absolute error</span><span class="metric-dataset">(训练)</span></div><span class="metric-value">${detailed.mean_absolute_error_training}</span></div>
                            <div class="metric-item"><div class="metric-name-container"><span class="metric-name-cn">均方误差</span><span class="metric-name-en">Mean squared error</span><span class="metric-dataset">(测试)</span></div><span class="metric-value">${detailed.mean_squared_error_test}</span></div>
                            <div class="metric-item"><div class="metric-name-container"><span class="metric-name-cn">均方误差</span><span class="metric-name-en">Mean squared error</span><span class="metric-dataset">(训练)</span></div><span class="metric-value">${detailed.mean_squared_error_training}</span></div>
                            <div class="metric-item"><div class="metric-name-container"><span class="metric-name-cn">归一化均方误差</span><span class="metric-name-en">Normalized MSE</span><span class="metric-dataset">(测试)</span></div><span class="metric-value">${detailed.normalized_mean_squared_error_test}</span></div>
                            <div class="metric-item"><div class="metric-name-container"><span class="metric-name-cn">归一化均方误差</span><span class="metric-name-en">Normalized MSE</span><span class="metric-dataset">(训练)</span></div><span class="metric-value">${detailed.normalized_mean_squared_error_training}</span></div>
                            <div class="metric-item"><div class="metric-name-container"><span class="metric-name-cn">均方根误差</span><span class="metric-name-en">Root MSE</span><span class="metric-dataset">(测试)</span></div><span class="metric-value">${detailed.root_mean_squared_error_test}</span></div>
                            <div class="metric-item"><div class="metric-name-container"><span class="metric-name-cn">均方根误差</span><span class="metric-name-en">Root MSE</span><span class="metric-dataset">(训练)</span></div><span class="metric-value">${detailed.root_mean_squared_error_training}</span></div>
                        </div>
                    </div>

                    <div class="metric-section">
                        <h6>模型结构</h6>
                        <div class="metric-list">
                            <div class="metric-item"><div class="metric-name-container"><span class="metric-name-cn">模型深度</span><span class="metric-name-en">Model Depth</span></div><span class="metric-value">${detailed.model_depth}</span></div>
                            <div class="metric-item"><div class="metric-name-container"><span class="metric-name-cn">模型长度</span><span class="metric-name-en">Model Length</span></div><span class="metric-value">${detailed.model_length}</span></div>
                        </div>
                    </div>
            </div>
        `;
    } else {
        detailedContainer.innerHTML = '<p class="text-muted">无</p>';
    }

    // 右下：特征影响力
    // 构造中文名映射（无外部函数时降级使用英文名）
    const getCn = (name) => {
        try {
            if (typeof getComponentChineseName === 'function') {
                return getComponentChineseName(name);
            }
        } catch (_) {}
        return name || '';
    };
    featureContainer.innerHTML = `
        <div class="feature-importance">
            ${(result.feature_importance || []).map(f => `
                <div class="feature-importance-item">
                    <div class="feature-name-container">
                        <div class="feature-name-en">${f.feature ?? ''}</div>
                        <div class="feature-name-cn">${getCn(f.feature ?? '')}</div>
                    </div>
                    <div class="importance-bar"><div class="importance-fill" style="width: ${(Number(f.importance||0)*100).toFixed(1)}%"></div></div>
                    <div class="importance-value">${(Number(f.importance)||0).toFixed(3)}</div>
                </div>
            `).join('')}
        </div>
    `;

    // 只对右上公式区做 MathJax 渲染（带兜底重试，确保切页后首次也能渲染）
    if (window.MathJax && window.MathJax.typesetPromise) {
        MathJax.typesetPromise([formulaContainer]).catch(err => console.error('MathJax渲染错误:', err));
    } else {
        const retryTypeset = () => {
            if (window.MathJax && window.MathJax.typesetPromise) {
                MathJax.typesetPromise([formulaContainer]).catch(err => console.error('MathJax渲染错误:', err));
            } else {
                setTimeout(retryTypeset, 100);
            }
        };
        setTimeout(retryTypeset, 100);
    }
}

// 生成Python可存储的随机整数（32位有符号范围内）
function generateRandomSeed() {
    const min = 1; // 避免0
    const max = 2147483647; // 2^31 - 1
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

// 根据模式更新Seed输入框状态，并提供重新生成逻辑
function setupSeedControls() {
    const modeSelect = document.getElementById('set-seed-randomly');
    const seedInput = document.getElementById('seed');
    const regenBtn = document.getElementById('regenerate-seed');

    if (!modeSelect || !seedInput) return;

    const applyState = () => {
        const isRandom = modeSelect.value === 'true';
        if (isRandom) {
            // 随机模式：生成随机种子；输入框不变灰但不可编辑；刷新按钮启用
            const newSeed = generateRandomSeed();
            seedInput.value = String(newSeed);
            seedInput.readOnly = true;
            seedInput.classList.add('readonly-not-allowed');
            if (regenBtn) regenBtn.disabled = false;
        } else {
            // 固定模式：可编辑，并自动重置为42；刷新按钮禁用且灰色
            seedInput.readOnly = false;
            seedInput.classList.remove('readonly-not-allowed');
            seedInput.value = '42';
            if (regenBtn) regenBtn.disabled = true;
        }
    };

    // 初始应用一次
    applyState();

    // 监听模式切换（避免重复绑定）
    if (modeSelect.dataset.seedBound !== '1') {
        modeSelect.addEventListener('change', applyState);
        modeSelect.dataset.seedBound = '1';
    }

    // 监听重新生成
    if (regenBtn) {
        if (regenBtn.dataset.seedBound !== '1') {
            regenBtn.addEventListener('click', (e) => {
                e.preventDefault();
                const newSeed = generateRandomSeed();
                seedInput.value = String(newSeed);
            });
            regenBtn.dataset.seedBound = '1';
        }
    }
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
            data: result.result.full_data || result.result.data_preview,
            headers: result.result.columns_list,
            rows: result.result.rows,
            columns: result.result.columns,
            filename: result.result.filename,
            server_csv_filename: result.result.server_csv_filename
        };
        
        // 更新目标列选择
        updateTargetColumnSelect(result.result.columns_list);
        
        // 更新特征列复选框
        updateFeatureColumnsCheckboxes(result.result.columns_list);

        // 渲染预览表格
        renderRegressionPreviewTable(currentData.headers, currentData.data);
        
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

// 解析CSV行，处理引号内的逗号
function parseCSVLine(line) {
    const result = [];
    let current = '';
    let inQuotes = false;
    
    for (let i = 0; i < line.length; i++) {
        const char = line[i];
        
        if (char === '"') {
            inQuotes = !inQuotes;
        } else if (char === ',' && !inQuotes) {
            result.push(current);
            current = '';
        } else {
            current += char;
        }
    }
    
    result.push(current);
    return result;
}

// 解析CSV内容
function parseCSV(content) {
    const lines = content.trim().split('\n');
    if (lines.length === 0) {
        throw new Error('CSV文件为空');
    }
    
    // 解析表头
    const headerLine = lines[0];
    const headers = parseCSVLine(headerLine).map(h => h.trim());
    
    if (headers.length === 0) {
        throw new Error('CSV文件没有有效的表头');
    }
    
    const data = [];
    
    // 解析数据行
    for (let i = 1; i < lines.length; i++) {
        const line = lines[i].trim();
        if (line === '') continue; // 跳过空行
        
        const values = parseCSVLine(line);
        const row = {};
        
        headers.forEach((header, index) => {
            const value = values[index] ? values[index].trim() : '';
            // 尝试转换为数字，如果失败则保持字符串
            const numValue = parseFloat(value);
            row[header] = isNaN(numValue) ? value : numValue;
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

// 设置表达式语法选择checkbox事件
function setupGrammarCheckboxEvents() {
    const grammarCheckboxes = document.querySelectorAll('input[id^="grammar-"]');
    grammarCheckboxes.forEach(checkbox => {
        const checkboxItem = checkbox.closest('.checkbox-item');
        if (checkboxItem) {
            checkboxItem.addEventListener('click', function(e) {
                // 如果点击的不是复选框本身，则切换复选框状态
                if (e.target.type !== 'checkbox') {
                    const checkbox = this.querySelector('input[type="checkbox"]');
                    checkbox.checked = !checkbox.checked;
                }
            });
        }
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
        
        // 添加点击事件，让整个区域可点击
        div.addEventListener('click', function(e) {
            // 如果点击的不是复选框本身，则切换复选框状态
            if (e.target.type !== 'checkbox') {
                const checkbox = this.querySelector('input[type="checkbox"]');
                checkbox.checked = !checkbox.checked;
            }
        });
        
        container.appendChild(div);
    });
}

// 生成带行列号的表格HTML
function generateTableWithCoordinates(headers, rows, title = '') {
    if (!headers || !rows || rows.length === 0) {
        return '<p>暂无数据</p>';
    }
    
    // 生成行号
    const rowNumbers = rows.map((_, index) => `<div class="row-number" data-row="${index + 1}">${index + 1}</div>`).join('');
    
    // 生成列号
    const columnNumbers = headers.map((_, index) => `<div class="column-number" data-col="${String.fromCharCode(65 + index)}">${String.fromCharCode(65 + index)}</div>`).join('');
    
    // 生成表格内容
    const thead = `<thead><tr>${headers.map(h=>`<th>${h}</th>`).join('')}</tr></thead>`;
    const tbody = `<tbody>${rows.map(r=>`<tr>${headers.map(h=>`<td>${r[h] ?? ''}</td>`).join('')}</tr>`).join('')}</tbody>`;
    
    let html = `<div class="table-with-coordinates">`;
    if (title) {
        html += `<h4>${title}</h4>`;
    }
    html += `<div class="table-wrapper">`;
    html += `<div class="corner-cell"></div>`;
    html += `<div class="row-numbers">${rowNumbers}</div>`;
    html += `<div class="column-numbers">${columnNumbers}</div>`;
    html += `<div class="table-content">`;
    html += `<table>${thead}${tbody}</table>`;
    html += `</div>`;
    html += `</div>`;
    html += `</div>`;
    
    return html;
}

// 对齐行列号到表格单元格
function alignCoordinatesToTable(container) {
    if (!container) return;
    
    const table = container.querySelector('.table-content table');
    const rowNumbers = container.querySelectorAll('.row-number');
    const columnNumbers = container.querySelectorAll('.column-number');
    
    if (!table || rowNumbers.length === 0 || columnNumbers.length === 0) return;
    
            // 对齐行号
        const tableRows = table.querySelectorAll('tbody tr');
        const rowHeightOffset = tableRows[0] ? tableRows[0].getBoundingClientRect().height : 32;
        tableRows.forEach((row, index) => {
            if (rowNumbers[index]) {
                const rowRect = row.getBoundingClientRect();
                const rowNumber = rowNumbers[index];
                const containerRect = container.getBoundingClientRect();
                const tableContent = container.querySelector('.table-content');
                const tableContentRect = tableContent.getBoundingClientRect();
                
                // 计算行号应该的位置，居中对齐到单元格中心
                // 需要考虑表格内容的偏移量
                const top = rowRect.top - tableContentRect.top + (rowRect.height / 2) - 16 + rowHeightOffset; // 整体向下偏移一个单元格高度
                rowNumber.style.top = `${top}px`;
                
                console.log(`行号 ${index + 1}: top = ${top}px, row height = ${rowRect.height}px`);
            }
        });
        
                    // 对齐列号
            const tableHeaders = table.querySelectorAll('thead th');
            tableHeaders.forEach((header, index) => {
                if (columnNumbers[index]) {
                    const headerRect = header.getBoundingClientRect();
                    const columnNumber = columnNumbers[index];
                    const containerRect = container.getBoundingClientRect();
                    const tableContent = container.querySelector('.table-content');
                    const tableContentRect = tableContent.getBoundingClientRect();
                    
                    // 计算列号应该的位置，居中对齐到单元格中心
                    // 需要考虑表格内容的偏移量，以及行号列的宽度
                    // 由于表格内容有30px的左边距，列号需要相应调整
                    const left = headerRect.left - tableContentRect.left + (headerRect.width / 2) - 40 + 30; // 40px是列号宽度的一半，+30px是表格内容的左边距
                    columnNumber.style.left = `${left}px`;
                    
                    console.log(`列号 ${String.fromCharCode(65 + index)}: left = ${left}px, width = ${headerRect.width}px, header left = ${headerRect.left}, tableContent left = ${tableContentRect.left}`);
                }
            });
}

// 渲染数据预览表格
function renderRegressionPreviewTable(headers, rows) {
    const host = document.getElementById('regression-data-preview');
    if (!host) return;
    if (!headers || !rows || rows.length === 0) {
        host.innerHTML = '<p>暂无数据</p>';
        return;
    }
    
    const html = generateTableWithCoordinates(headers, rows, `数据预览 (共${rows.length}行数据)`);
    host.innerHTML = html;
    
    // 等待DOM渲染完成后对齐行列号
    setTimeout(() => {
        const container = host.querySelector('.table-with-coordinates');
        if (container) {
            alignCoordinatesToTable(container);
        }
    }, 100);
}

// 隐藏数据预览
function hideDataPreview() {
    const host = document.getElementById('regression-data-preview');
    if (!host) return;
    
    host.innerHTML = `
        <div class="data-preview-collapsed">
            <p>数据预览已隐藏</p>
            <button class="btn btn-secondary" onclick="showDataPreview()">重新展开数据预览</button>
        </div>
    `;
}

// 显示数据预览
function showDataPreview() {
    if (!currentData) return;
    
    renderRegressionPreviewTable(currentData.headers, currentData.data);
}

// 训练/测试滑块联动
document.addEventListener('input', (e) => {
    if (e.target && e.target.id === 'train-ratio') {
        const train = Number(e.target.value);
        const test = 100 - train;
        const trainLabel = document.getElementById('train-ratio-label');
        const testLabel = document.getElementById('test-ratio-label');
        if (trainLabel) trainLabel.textContent = `${train}%`;
        if (testLabel) testLabel.textContent = `${test}%`;
    }
});

// 开始符号回归分析
async function startRegression() {
    console.log('🔍 开始符号回归分析...');
    
    const targetColumn = document.getElementById('target-column').value;
    const featureCheckboxes = document.querySelectorAll('#feature-columns input[type="checkbox"]:checked');
    const populationSize = parseInt(document.getElementById('population-size').value) || 100;
    const generations = parseInt(document.getElementById('generations').value) || 50;
    const maxTreeDepth = parseInt(document.getElementById('max-tree-depth').value) || 35;
    const maxTreeLength = parseInt(document.getElementById('max-tree-length').value) || 35;
    
    // 收集语法选择参数
    const grammarCheckboxes = document.querySelectorAll('input[id^="grammar-"]:checked');
    const selectedGrammar = Array.from(grammarCheckboxes).map(cb => cb.value);
    
    // 收集训练集占比和随机种子参数
    const trainRatio = parseInt(document.getElementById('train-ratio').value) || 80;
    const setSeedRandomly = document.getElementById('set-seed-randomly').value === 'true';
    const seedValue = parseInt(document.getElementById('seed')?.value) || 42;
    
    console.log('📊 分析参数:', {
        targetColumn,
        featureCount: featureCheckboxes.length,
        populationSize,
        generations,
        maxTreeDepth,
        maxTreeLength,
        selectedGrammar,
        hasData: !!currentData
    });
    
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
            generations: generations,
            max_tree_depth: maxTreeDepth,
            max_tree_length: maxTreeLength,
            symbolic_expression_grammar: selectedGrammar,
            train_ratio: trainRatio,
            set_seed_randomly: setSeedRandomly,
            seed: seedValue,
            data_source: currentData.filename || "数据源",
            server_csv_filename: currentData.server_csv_filename || null
        });
        
        // 保存当前回归结果
        currentRegressionResult = result;
        
        // 保存模型到列表
        regressionModels.push(result);
        updateRegressionModelList();
        
        // 隐藏数据预览，显示分析结果
        hideDataPreview();
        displayRegressionResults(result);
        showNotification('符号回归分析完成', 'success');
        
        // 如果返回了数据模型ID，显示提示
        if (result.data_model_id) {
            showNotification(`数据模型已自动创建: ${result.data_model_id}`, 'info');
        }
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
    
    // 解析表达式，提取目标变量、特征变量和常数
    const expression = result.expression || '';
    const targetVariable = result.target_variable || 'Y';
    const constants = result.constants || {};
    
    // 生成LaTeX公式（若后端已提供 expression_latex 则直接使用）
    const latexFormula = result.expression_latex
        ? result.expression_latex
        : generateLatexFormula(expression, targetVariable, constants);
    
    // 常数排序（与表达式树页面一致）
    const formatConstantsForDisplay = (consts) => {
        const entries = Object.entries(consts || {}).map(([k, v]) => {
            const m = String(k).match(/^c(?:_|\{)?(\d+)\}?$/i);
            const idx = m ? parseInt(m[1], 10) : Number.MAX_SAFE_INTEGER;
            const latexKey = m ? `c_{${m[1]}}` : String(k);
            return { idx, key: latexKey, value: v };
        });
        entries.sort((a, b) => a.idx - b.idx);
        return entries;
    };

    container.innerHTML = `
        <div class="result-item">
            <h4>回归表达式</h4>
            <div class="regression-formula-container">
                <div class="regression-formula">
                    $${latexFormula}$
                </div>
                ${Object.keys(constants).length > 0 ? `
                <div class="regression-constants">
                    <h5>常数定义</h5>
                    <div class="constant-list">
                        ${formatConstantsForDisplay(constants).map(item =>
                            `<div class="constant-item">$${item.key} = ${item.value}$</div>`
                        ).join('')}
                    </div>
                </div>
                ` : ''}
            </div>
                <div class="result-actions" style="margin-top: 10px;">
                    <button class="btn-secondary" id="edit-model-btn" onclick="switchTab('expression-tree')">修改模型</button>
                    <button class="btn-secondary" id="export-model-db-btn" onclick="exportRegressionModelDb()">导出模型</button>
                </div>
        </div>
        
        <div class="result-item">
            <h4>模型性能</h4>
            <div class="performance-metrics">
                <div class="performance-metric">
                    <div class="metric-label">皮尔逊相关系数</div>
                        <div class="metric-value">${result.detailed_metrics.pearson_r_test.toFixed(3)}<span class="metric-raw">${typeof result.detailed_metrics.pearson_r_test === 'number' ? ` (${result.detailed_metrics.pearson_r_test})` : ''}</span></div>
                    <div class="metric-unit">(测试)</div>
                </div>
                <div class="performance-metric">
                    <div class="metric-label">皮尔逊相关系数</div>
                        <div class="metric-value">${result.detailed_metrics.pearson_r_training.toFixed(3)}<span class="metric-raw">${typeof result.detailed_metrics.pearson_r_training === 'number' ? ` (${result.detailed_metrics.pearson_r_training})` : ''}</span></div>
                    <div class="metric-unit">(训练)</div>
                </div>
            </div>
            
            ${result.detailed_metrics ? `
            <div class="detailed-metrics">
                <h5>详细指标</h5>
                <div class="metrics-grid">
                    <div class="metric-section">
                        <h6>误差指标</h6>
                        <div class="metric-list">
                            <div class="metric-item">
                                <div class="metric-name-container">
                                    <span class="metric-name-cn">平均相对误差</span>
                                    <span class="metric-name-en">Average relative error</span>
                                    <span class="metric-dataset">(测试)</span>
                                </div>
                                <span class="metric-value">${result.detailed_metrics.average_relative_error_test}%</span>
                            </div>
                            <div class="metric-item">
                                <div class="metric-name-container">
                                    <span class="metric-name-cn">平均相对误差</span>
                                    <span class="metric-name-en">Average relative error</span>
                                    <span class="metric-dataset">(训练)</span>
                                </div>
                                <span class="metric-value">${result.detailed_metrics.average_relative_error_training}%</span>
                            </div>
                            <div class="metric-item">
                                <div class="metric-name-container">
                                    <span class="metric-name-cn">平均绝对误差</span>
                                    <span class="metric-name-en">Mean absolute error</span>
                                    <span class="metric-dataset">(测试)</span>
                                </div>
                                <span class="metric-value">${result.detailed_metrics.mean_absolute_error_test}</span>
                            </div>
                            <div class="metric-item">
                                <div class="metric-name-container">
                                    <span class="metric-name-cn">平均绝对误差</span>
                                    <span class="metric-name-en">Mean absolute error</span>
                                    <span class="metric-dataset">(训练)</span>
                                </div>
                                <span class="metric-value">${result.detailed_metrics.mean_absolute_error_training}</span>
                            </div>
                            <div class="metric-item">
                                <div class="metric-name-container">
                                    <span class="metric-name-cn">均方误差</span>
                                    <span class="metric-name-en">Mean squared error</span>
                                    <span class="metric-dataset">(测试)</span>
                                </div>
                                <span class="metric-value">${result.detailed_metrics.mean_squared_error_test}</span>
                            </div>
                            <div class="metric-item">
                                <div class="metric-name-container">
                                    <span class="metric-name-cn">均方误差</span>
                                    <span class="metric-name-en">Mean squared error</span>
                                    <span class="metric-dataset">(训练)</span>
                                </div>
                                <span class="metric-value">${result.detailed_metrics.mean_squared_error_training}</span>
                            </div>
                            <div class="metric-item">
                                <div class="metric-name-container">
                                    <span class="metric-name-cn">归一化均方误差</span>
                                    <span class="metric-name-en">Normalized MSE</span>
                                    <span class="metric-dataset">(测试)</span>
                                </div>
                                <span class="metric-value">${result.detailed_metrics.normalized_mean_squared_error_test}</span>
                            </div>
                            <div class="metric-item">
                                <div class="metric-name-container">
                                    <span class="metric-name-cn">归一化均方误差</span>
                                    <span class="metric-name-en">Normalized MSE</span>
                                    <span class="metric-dataset">(训练)</span>
                                </div>
                                <span class="metric-value">${result.detailed_metrics.normalized_mean_squared_error_training}</span>
                            </div>
                            <div class="metric-item">
                                <div class="metric-name-container">
                                    <span class="metric-name-cn">均方根误差</span>
                                    <span class="metric-name-en">Root MSE</span>
                                    <span class="metric-dataset">(测试)</span>
                                </div>
                                <span class="metric-value">${result.detailed_metrics.root_mean_squared_error_test}</span>
                            </div>
                            <div class="metric-item">
                                <div class="metric-name-container">
                                    <span class="metric-name-cn">均方根误差</span>
                                    <span class="metric-name-en">Root MSE</span>
                                    <span class="metric-dataset">(训练)</span>
                                </div>
                                <span class="metric-value">${result.detailed_metrics.root_mean_squared_error_training}</span>
                            </div>
                        </div>
                    </div>
                    

                    
                    <div class="metric-section">
                        <h6>模型结构</h6>
                        <div class="metric-list">
                            <div class="metric-item">
                                <div class="metric-name-container">
                                    <span class="metric-name-cn">模型深度</span>
                                    <span class="metric-name-en">Model Depth</span>
                                </div>
                                <span class="metric-value">${result.detailed_metrics.model_depth}</span>
                            </div>
                            <div class="metric-item">
                                <div class="metric-name-container">
                                    <span class="metric-name-cn">模型长度</span>
                                    <span class="metric-name-en">Model Length</span>
                                </div>
                                <span class="metric-value">${result.detailed_metrics.model_length}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            ` : ''}
        </div>
        
        <div class="result-item">
            <h4>特征影响力</h4>
            <div class="feature-importance">
                ${result.feature_importance.map(f => `
                    <div class="feature-importance-item">
                        <div class="feature-name-container">
                            <div class="feature-name-en">${f.feature}</div>
                            <div class="feature-name-cn">${getComponentChineseName(f.feature)}</div>
                        </div>
                        <div class="importance-bar">
                            <div class="importance-fill" style="width: ${f.importance * 100}%"></div>
                        </div>
                        <div class="importance-value">${f.importance.toFixed(3)}</div>
                    </div>
                `).join('')}
            </div>
        </div>
        
        
    `;
    
    // 重新渲染MathJax
    if (window.MathJax && window.MathJax.typesetPromise) {
        console.log('开始渲染MathJax公式:', latexFormula);
        MathJax.typesetPromise([container]).then(() => {
            console.log('MathJax渲染完成');
        }).catch((err) => console.error('MathJax渲染错误:', err));
    } else {
        // 如果MathJax还没加载完成，等待加载
        console.log('MathJax未加载，等待加载...');
        const checkMathJax = () => {
            if (window.MathJax && window.MathJax.typesetPromise) {
                console.log('MathJax已加载，开始渲染:', latexFormula);
                MathJax.typesetPromise([container]).then(() => {
                    console.log('MathJax渲染完成');
                }).catch((err) => console.error('MathJax渲染错误:', err));
            } else {
                setTimeout(checkMathJax, 100);
            }
        };
        checkMathJax();
    }
    
    // 启用导出模型按钮
    const exportModelBtn = document.getElementById('export-model');
    if (exportModelBtn) {
        exportModelBtn.disabled = false;
    }
}

// 从数据库/文件系统导出最新创建的数据模型对应的回归模型文件
async function exportRegressionModelDb() {
    try {
        // 优先使用后端返回的数据模型ID
        const modelId = currentRegressionResult?.data_model_id;
        if (!modelId) {
            showNotification('未找到数据模型ID，请先完成一次分析', 'warning');
            return;
        }
        
        // 获取并下载数据包（包含CSV、回归JSON、蒙特卡洛JSON[如有]）
        const resp = await fetch(`${API_BASE_URL}/api/data-models/models/${modelId}/files/all_as_zip`);
        if (!resp.ok) {
            throw new Error(`HTTP ${resp.status}`);
        }
        const blob = await resp.blob();
        // 从响应头中尝试获取文件名
        let fileName = `${modelId}.zip`;
        const disposition = resp.headers.get('Content-Disposition') || resp.headers.get('content-disposition');
        if (disposition) {
            const match = disposition.match(/filename\*=UTF-8''([^;]+)|filename=\"?([^;\"]+)\"?/i);
            const name = match?.[1] || match?.[2];
            if (name) fileName = decodeURIComponent(name);
        }
        // 优先使用 Electron 保存对话框
        if (window.electronAPI && window.electronAPI.saveZipFile) {
            const arrayBuffer = await blob.arrayBuffer();
            const result = await window.electronAPI.saveZipFile(fileName, arrayBuffer);
            if (!result?.success) {
                // 回退到浏览器下载
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = fileName;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
            }
        } else {
            // 回退到浏览器下载
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = fileName;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }
        
        showNotification(`数据包已导出: ${fileName}`, 'success');
    } catch (err) {
        console.error('导出模型失败:', err);
        showNotification('导出模型失败: ' + err.message, 'error');
    }
}

// 生成LaTeX公式的函数
function generateLatexFormula(expression, targetVariable, constants) {
    if (!expression) return `${targetVariable} = 0`;
    let processedExpression = expression;
    // 简化的数字匹配，避免使用不兼容的负向后行断言
    const numberPattern = /-?\d+\.?\d*/g;
    const numbers = expression.match(numberPattern) || [];
    const constantMap = {};
    const usedNumbers = new Set();
    numbers.forEach((num) => {
        if (!usedNumbers.has(num)) {
            const index = Object.keys(constantMap).length;
            const constantName = `c_{${index}}`;
            constantMap[constantName] = parseFloat(num);
            usedNumbers.add(num);
            const regex = new RegExp(`\\b${num.replace(/\./g, '\\.')}\\b`, 'g');
            processedExpression = processedExpression.replace(regex, constantName);
        }
    });
    Object.keys(constants).forEach(key => delete constants[key]);
    Object.assign(constants, constantMap);
    let latex = processedExpression
        .replace(/\*/g, '\\cdot ')
        .replace(/\//g, '\\frac{')
        .replace(/\^/g, '^')
        .replace(/\(/g, '\\left(')
        .replace(/\)/g, '\\right)');
    if (latex.includes('\\frac{')) {
        // 修正 \\frac{num}/den → \\frac{num}{den}
        latex = latex.replace(/\\frac\{([^}]+)\}\/([^\s]+)/g, function(_, a, b){ return `\\frac{${a}}{${b}}`; });
    }
    return `${targetVariable} = ${latex}`;
}

// 导出模型（与数据管理保持一致：标准ZIP包）
async function exportModel() {
    return exportRegressionModelDb();
}

// 更新回归模型列表
function updateRegressionModelList() {
    const select = document.getElementById('mc-data-model');
    if (!select) return;
    
    select.innerHTML = '<option value="">请选择数据模型</option>';
    regressionModels.forEach(model => {
        const option = document.createElement('option');
        // 这里用于联动蒙特卡洛页的数据模型选择，本地回归结果没有数据模型ID，仅展示表达式模型ID
        option.value = model.data_model_id || model.id;
        const pearsonText = (typeof model.detailed_metrics?.pearson_r_test === 'number') ? model.detailed_metrics.pearson_r_test.toFixed(3) : (model.detailed_metrics?.pearson_r_test || 'N/A');
        option.textContent = `模型 ${model.data_model_id || model.id} (R=${pearsonText})`;
        select.appendChild(option);
    });
}

// 开始蒙特卡洛采样分析
async function startMonteCarlo() {
    const dataModelId = document.getElementById('mc-data-model').value;
    const iterations = parseInt(document.getElementById('mc-iterations').value);
    const targetEfficacy = parseFloat(document.getElementById('target-efficacy').value);
    const tolerance = parseFloat(document.getElementById('tolerance').value);
    
    if (!dataModelId) {
        showNotification('请选择数据模型', 'warning');
        return;
    }
    
    if (!targetEfficacy) {
        showNotification('请输入目标药效值', 'warning');
        return;
    }
    
    showLoading('正在进行蒙特卡洛采样分析...');
    
    try {
        // 读取模型信息以获取目标变量名（例如 HDL）
        try {
            const modelResp = await fetch(`${API_BASE_URL}/api/data-models/models/${dataModelId}`);
            if (modelResp.ok) {
                const modelJson = await modelResp.json();
                if (modelJson && modelJson.success && modelJson.model) {
                    window.__mcTargetName__ = modelJson.model.target_column || '药效';
                }
            }
        } catch (_) {}
        const payload = {
            model_id: dataModelId,
            iterations,
            target_efficacy: targetEfficacy,
            tolerance,
            component_ranges: (window.__mcRanges__ && window.__mcRanges__.__model__ === dataModelId)
                ? Object.fromEntries(Object.entries(window.__mcRanges__).filter(([k]) => !k.startsWith('__'))) : {}
        };
        const result = await performMonteCarloAnalysis(payload);
        
        currentMonteCarloResult = result;
        displayMonteCarloResults(result);
        showNotification('蒙特卡洛采样分析完成', 'success');
        
        // 如果返回了数据模型ID，显示提示
        if (result.data_model_id) {
            showNotification(`数据模型已更新: ${result.data_model_id}`, 'info');
        }
        
        // 重新加载数据模型列表
        setTimeout(() => {
            loadDataModels();
        }, 1000);
    } catch (error) {
        showNotification('蒙特卡洛采样分析失败: ' + error.message, 'error');
        console.error('❌ 蒙特卡洛采样分析错误:', error);
    } finally {
        hideLoading();
    }
}

// 执行蒙特卡洛采样分析（真实API调用）
async function performMonteCarloAnalysis(params) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/monte-carlo-sampling/analyze`, {
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

// 显示蒙特卡洛采样结果（重构UI）
function displayMonteCarloResults(result) {
    const container = document.getElementById('monte-carlo-results');
    if (!container) return;
    
    // 参数视图
    const params = [
        { name: '模拟次数', value: result.iterations },
        { name: '目标药效', value: result.target_efficacy },
        { name: '容差', value: result.tolerance },
        { name: '分析时间(秒)', value: result.analysis_time }
    ];
    const paramsHtml = params.map(p => `
        <div class="param-card"><div class="param-name">${p.name}</div><div class="param-value">${p.value}</div></div>
    `).join('');
    
    // 汇总视图
    const summary = [
        { name: '有效样本数', value: result.valid_samples },
        { name: '成功率', value: `${(result.success_rate * 100).toFixed(1)}%` }
    ];
    const summaryHtml = summary.map(s => `
        <div class="summary-card"><div class="summary-name">${s.name}</div><div class="summary-value">${s.value}</div></div>
    `).join('');
    
    // Top10（若后端不提供，则从 result.distribution 构造示例）
    const top10 = (result.top10 && Array.isArray(result.top10)) ? result.top10 : [];
    const topTitle = (window.__mcTargetName__ ? `${window.__mcTargetName__} 值` : '目标值');
    // 组装表格
    const varSet = new Set();
    top10.forEach(it => (it.components || []).forEach(c => varSet.add(c.name)));
    const vars = Array.from(varSet);
    const headerRow = ['Rank', topTitle].concat(vars).map(h => `<th>${h}</th>`).join('');
    const bodyRows = top10.map(it => {
        const map = {}; (it.components || []).forEach(c => { map[c.name] = c.value; });
        const cols = [it.rank ?? '', it.efficacy ?? ''].concat(vars.map(v => map[v] ?? ''));
        return `<tr>${cols.map(c => `<td>${c}</td>`).join('')}</tr>`;
    }).join('');
    const top10TableHtml = `
        <div class="csv-table-container mc-top10-container">
            <table class="csv-table mc-top-table">
                <thead><tr>${headerRow}</tr></thead>
                <tbody>${bodyRows}</tbody>
            </table>
        </div>`;
    
    container.innerHTML = `
        <div class="result-item">
            <h4>分析参数</h4>
            <div id="mc-params-view" class="params-grid">${paramsHtml}</div>
        </div>
        <div class="result-item">
            <h4>分析结果</h4>
            <div id="mc-summary-view" class="summary-grid">${summaryHtml}</div>
        </div>
        <div class="result-item">
            <h4>最佳药效（前10条）</h4>
            <div id="mc-top10-view">${top10TableHtml}</div>
        </div>
        <div class="result-item">
            <div class="button-group">
                <button class="btn-secondary" onclick="exportMonteCarloTop10Csv()">导出结果</button>
            </div>
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
    try {
        const response = await fetch(`${API_BASE_URL}/api/health`);
        if (response.ok) {
            const data = await response.json();
            updateConnectionStatus('已连接');
            showNotification(`后端连接正常: ${data.service}`, 'success');
            return true;
        } else {
            updateConnectionStatus('连接失败');
            showNotification('后端连接失败', 'error');
            return false;
        }
    } catch (error) {
        updateConnectionStatus('连接失败');
        showNotification('后端连接测试失败: ' + error.message, 'error');
        return false;
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
    const footerElement = document.getElementById('connection-status-footer');
    
    if (element) {
        element.textContent = `后端服务：${status}`;
    }
    
    if (footerElement) {
        footerElement.textContent = `后端服务：${status}`;
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
    const notificationContainer = document.getElementById('notification-container');
    if (!notificationContainer) {
        console.error('找不到通知容器');
        return;
    }
    
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <span class="notification-message">${message}</span>
        <button class="notification-close" onclick="this.parentElement.remove()">×</button>
    `;
    
    // 添加到通知容器
    notificationContainer.appendChild(notification);
    
    // 添加进入动画
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);
    
    // 自动移除
    setTimeout(() => {
        if (notification.parentElement) {
            notification.classList.remove('show');
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.remove();
                }
            }, 300);
        }
    }, 5000);
}

// 显示关于对话框
function showAboutDialog() {
    alert('本草智配客户端 v1.0.0\n\n基于Electron + Flask的跨平台桌面应用');
}

// 可视化结果
// visualizeResults 功能不再需要，保留空实现以免引用残留
function visualizeResults() {}

// 导出蒙特卡洛采样结果
function exportMonteCarloResults(iterations) {
    showNotification('导出功能开发中...', 'info');
}

// 数据管理相关函数
async function loadDataModels() {
    console.log('📊 加载数据模型列表...');
    const dataPreview = document.getElementById('data-preview');
    
    if (!dataPreview) {
        console.error('找不到数据预览容器');
        return;
    }
    
    try {
        showLoading('正在加载数据模型...');
        
        const response = await fetch(`${API_BASE_URL}/api/data-models/models`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-Username': authManager.currentUser.username
            }
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (!result.success) {
            throw new Error(result.message || '加载数据模型失败');
        }
        
        displayDataModels(result.models);
        showNotification(`成功加载 ${result.models.length} 个数据模型`, 'success');
        
    } catch (error) {
        console.error('❌ 加载数据模型失败:', error);
        showNotification('加载数据模型失败: ' + error.message, 'error');
        dataPreview.innerHTML = `<p>加载失败: ${error.message}</p>`;
    } finally {
        hideLoading();
    }
}

function displayDataModels(models) {
    const dataPreview = document.getElementById('data-preview');
    
    if (!dataPreview) {
        console.error('找不到数据预览容器');
        return;
    }
    
    if (!models || models.length === 0) {
        dataPreview.innerHTML = '<p>暂无数据模型</p>';
        return;
    }
    
    // 创建表格
    const table = document.createElement('table');
    table.innerHTML = `
        <thead>
            <tr>
                <th>模型名称</th>
                <th>模型描述</th>
                <th>主要指标</th>
                <th>创建时间</th>
                <th>文件状态</th>
                <th>操作</th>
            </tr>
        </thead>
        <tbody>
        </tbody>
    `;
    
    const tbody = table.querySelector('tbody');
    
    models.forEach(model => {
        const row = document.createElement('tr');
        const createdDate = new Date(model.created_at * 1000).toLocaleString('zh-CN');
        
        // 生成文件状态显示
        const fileStatus = generateFileStatus(model.metadata);
        
        // 生成主要指标显示
        const mainMetrics = generateMainMetrics(model);
        
        row.innerHTML = `
            <td><strong>${model.name}</strong></td>
            <td>${model.description || '暂无描述'}</td>
            <td>${mainMetrics}</td>
            <td>${createdDate}</td>
            <td>${fileStatus}</td>
            <td>
                <button class="btn-sm btn-primary" onclick="viewDataModel('${model.id}')">查看</button>
                <button class="btn-sm btn-secondary" onclick="exportDataModelZip('${model.id}')">导出</button>
                <button class="btn-sm btn-danger" onclick="deleteDataModel('${model.id}')">删除</button>
            </td>
        `;
        
        tbody.appendChild(row);
    });
    
    dataPreview.innerHTML = '';
    dataPreview.appendChild(table);
}

function generateMainMetrics(model) {
    if (!model.metadata) return '<span class="text-muted">无指标</span>';
    
    // 从metadata中获取指标
    const pearsonTest = model.metadata.pearson_r_test;
    const pearsonTraining = model.metadata.pearson_r_training;
    
    if (pearsonTest !== undefined && pearsonTraining !== undefined) {
        return `<div class="metrics-summary">
            <div class="metric-item">
                <span class="metric-label">R(测试):</span>
                <span class="metric-value">${pearsonTest.toFixed(3)}</span>
            </div>
            <div class="metric-item">
                <span class="metric-label">R(训练):</span>
                <span class="metric-value">${pearsonTraining.toFixed(3)}</span>
            </div>
        </div>`;
    }
    
    return '<span class="text-muted">无指标</span>';
}

function generateFileStatus(metadata) {
    if (!metadata) return '<span class="status-unknown">未知</span>';
    // 强制转为布尔，避免字符串 'false' 或 null 被当作真
    const hasCsv = Boolean(metadata.has_csv_data);
    const hasReg = Boolean(metadata.has_regression_model);
    const hasMc = Boolean(metadata.has_monte_carlo_results);

    const status = [];
    status.push(hasCsv ? '<span class="status-ok">📊 CSV</span>' : '<span class="status-missing">❌ CSV</span>');
    status.push(hasReg ? '<span class="status-ok">📈 回归</span>' : '<span class="status-missing">❌ 回归</span>');
    status.push(hasMc ? '<span class="status-ok">🎲 蒙特卡洛</span>' : '<span class="status-missing">❌ 蒙特卡洛</span>');
    return status.join(' ');
}

// 导出数据模型的ZIP（CSV + 回归JSON + 蒙特卡洛JSON[如有]）
async function exportDataModelZip(modelId) {
    try {
        if (!modelId) {
            showNotification('无效的模型ID', 'warning');
            return;
        }
        const resp = await fetch(`${API_BASE_URL}/api/data-models/models/${modelId}/files/all_as_zip`);
        if (!resp.ok) {
            throw new Error(`HTTP ${resp.status}`);
        }
        const blob = await resp.blob();
        let fileName = `${modelId}.zip`;
        const disposition = resp.headers.get('Content-Disposition') || resp.headers.get('content-disposition');
        if (disposition) {
            const match = disposition.match(/filename\*=UTF-8''([^;]+)|filename=\"?([^;\"]+)\"?/i);
            const name = match?.[1] || match?.[2];
            if (name) fileName = decodeURIComponent(name);
        }
        if (window.electronAPI && window.electronAPI.saveZipFile) {
            const arrayBuffer = await blob.arrayBuffer();
            const result = await window.electronAPI.saveZipFile(fileName, arrayBuffer);
            if (!result?.success) {
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = fileName;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
            }
        } else {
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = fileName;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }
        showNotification(`数据包已导出: ${fileName}`, 'success');
    } catch (err) {
        console.error('导出ZIP失败:', err);
        showNotification('导出失败: ' + err.message, 'error');
    }
}

// 动态加载 JSZip（兼容 ESM 与 UMD）
async function loadJSZip() {
    // 如果全局已有，直接返回
    if (window.JSZip) return window.JSZip;
    // 优先尝试 UMD 版本
    await new Promise((resolve, reject) => {
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/jszip@3.10.1/dist/jszip.min.js';
        script.onload = () => resolve();
        script.onerror = () => reject(new Error('JSZip加载失败'));
        document.head.appendChild(script);
    });
    if (window.JSZip) return window.JSZip;
    // 兜底尝试 ESM 导入
    try {
        const mod = await import('https://cdn.jsdelivr.net/npm/jszip@3.10.1/dist/jszip.min.js');
        return mod && (mod.default || mod.JSZip || mod);
    } catch (e) {
        throw new Error('无法加载JSZip');
    }
}

// 为蒙特卡洛采样加载数据模型列表
async function loadDataModelsForMonteCarlo() {
    console.log('📊 为蒙特卡洛采样加载数据模型列表...');
    const dataModelSelect = document.getElementById('mc-data-model');
    
    if (!dataModelSelect) {
        console.error('找不到数据模型选择框');
        return;
    }
    
    // 显示加载状态
    dataModelSelect.innerHTML = '<option value="">正在加载数据模型...</option>';
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/data-models/models`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-Username': authManager.currentUser.username
            }
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (!result.success) {
            throw new Error(result.message || '加载数据模型失败');
        }
        
        console.log('🔍 从API获取到的原始数据模型列表:', result.models);
        
        // 过滤出有符号回归模型的数据模型
        const modelsWithRegression = result.models.filter(model => 
            model.metadata && model.metadata.has_regression_model
        );
        
        console.log('🔍 过滤后有符号回归模型的数据模型:', modelsWithRegression);
        
        // 更新选择框
        dataModelSelect.innerHTML = '<option value="">请选择数据模型</option>';
        modelsWithRegression.forEach(model => {
            const option = document.createElement('option');
            option.value = model.id;
            const featureCount = model.feature_columns ? model.feature_columns.length : 0;
            option.textContent = `${model.name} (${model.target_column}, ${featureCount}个特征)`;
            dataModelSelect.appendChild(option);
        });
        
        console.log(`✅ 加载了 ${modelsWithRegression.length} 个可用的数据模型`);
        
        // 如果没有可用的模型，显示提示
        if (modelsWithRegression.length === 0) {
            dataModelSelect.innerHTML = '<option value="">没有可用的数据模型</option>';
            showNotification('没有找到包含符号回归模型的数据模型，请先进行符号回归分析', 'warning');
        } else {
            showNotification(`成功加载 ${modelsWithRegression.length} 个数据模型`, 'success');
        }
        
    } catch (error) {
        console.error('❌ 加载数据模型失败:', error);
        showNotification('加载数据模型失败: ' + error.message, 'error');
        dataModelSelect.innerHTML = '<option value="">加载失败</option>';
    }
}

async function viewDataModel(modelId) {
    console.log(`📊 查看数据模型: ${modelId}`);
    
    try {
        showLoading('正在加载模型详情...');
        
        const response = await fetch(`${API_BASE_URL}/api/data-models/models/${modelId}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-Username': authManager.currentUser.username
            }
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (!result.success) {
            throw new Error(result.message || '加载模型详情失败');
        }
        
        showDataModelDetails(result.model);
        
    } catch (error) {
        console.error('❌ 查看数据模型失败:', error);
        showNotification('查看数据模型失败: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

function showDataModelDetails(model) {
    // 创建模态框显示模型详情（美化版，仅作用于本弹窗）
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    const featureTags = (model.feature_columns && model.feature_columns.length)
        ? model.feature_columns.map(col => `<span class="tag">${col}</span>`).join('')
        : '<span class="text-muted">无</span>';
    const csvStatus = model.metadata && model.metadata.has_csv_data ? '<span class="status-ok">📊 CSV</span>' : '<span class="status-missing">❌ CSV</span>';
    const regStatus = model.metadata && model.metadata.has_regression_model ? '<span class="status-ok">📈 回归</span>' : '<span class="status-missing">❌ 回归</span>';
    const mcStatus = model.metadata && model.metadata.has_monte_carlo_results ? '<span class="status-ok">🎲 蒙特卡洛</span>' : '<span class="status-missing">❌ 蒙特卡洛</span>';
    
    modal.innerHTML = `
        <div class="modal-content model-details">
            <div class="modal-header">
                <h3>数据模型详情</h3>
                <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">×</button>
            </div>
            <div class="modal-body">
                <section class="details-section">
                    <div class="section-title">基本信息</div>
                    <div class="info-grid">
                        <div class="info-item"><div class="info-label">名称</div><div class="info-value">${model.name}</div></div>
                        <div class="info-item"><div class="info-label">目标变量</div><div class="info-value">${model.target_column || '-'}</div></div>
                        <div class="info-item info-span-2"><div class="info-label">描述</div><div class="info-value">${model.description || '-'}</div></div>
                        <div class="info-item info-span-2"><div class="info-label">特征变量</div><div class="info-value tag-list">${featureTags}</div></div>
                        <div class="info-item"><div class="info-label">创建时间</div><div class="info-value">${model.created_at ? new Date(model.created_at * 1000).toLocaleString('zh-CN') : '-'}</div></div>
                        <div class="info-item"><div class="info-label">状态</div><div class="info-value">${model.status === 'active' ? '活跃' : '非活跃'}</div></div>
                    </div>
                </section>
                
                <section class="details-section">
                    <div class="section-title">分析参数</div>
                    <div class="info-grid">
                        <div class="info-item"><div class="info-label">配比方案数量</div><div class="info-value">${model.analysis_params?.population_size || '-'}</div></div>
                        <div class="info-item"><div class="info-label">优化轮次</div><div class="info-value">${model.analysis_params?.generations || '-'}</div></div>
                        <div class="info-item"><div class="info-label">最大表达式树深度</div><div class="info-value">${model.analysis_params?.max_tree_depth || '-'}</div></div>
                        <div class="info-item"><div class="info-label">最大表达式树长度</div><div class="info-value">${model.analysis_params?.max_tree_length || '-'}</div></div>
                        <div class="info-item"><div class="info-label">表达式语法</div><div class="info-value">${formatGrammarDisplay(model.analysis_params?.symbolic_expression_grammar)}</div></div>
                        <div class="info-item"><div class="info-label">训练/测试集占比</div><div class="info-value">${model.analysis_params?.train_ratio ? `${model.analysis_params.train_ratio}%/${100-model.analysis_params.train_ratio}%` : '-'}</div></div>
                         <div class="info-item"><div class="info-label">随机种子随机化</div><div class="info-value">${model.analysis_params?.set_seed_randomly ? '是（结果不可重复）' : '否（结果可重复）'}</div></div>
                         <div class="info-item"><div class="info-label">Seed模式</div><div class="info-value">${model.analysis_params?.seed_mode || (model.analysis_params?.set_seed_randomly ? '随机' : '固定')}</div></div>
                         <div class="info-item"><div class="info-label">Seed数值</div><div class="info-value">${model.analysis_params?.seed ?? '-'}</div></div>
                    </div>
                </section>
                
                <section class="details-section">
                    <div class="section-title">文件状态</div>
                    <div class="status-chips">
                        ${csvStatus} ${regStatus} ${mcStatus}
                    </div>
                    <div class="file-actions">
                        ${model.metadata && model.metadata.has_csv_data 
                            ? `<button class="btn-sm btn-primary" onclick="viewDataModelFile('${model.id}', 'csv_data')">查看CSV数据</button>` 
                            : '<span class="text-muted">CSV数据文件不存在</span>'}
                        ${model.metadata && model.metadata.has_regression_model 
                            ? `<button class="btn-sm btn-primary" onclick="viewDataModelFile('${model.id}', 'regression_model')">查看回归模型</button>` 
                            : '<span class="text-muted">回归模型文件不存在</span>'}
                        ${model.metadata && model.metadata.has_monte_carlo_results 
                            ? `<button class="btn-sm btn-primary" onclick="viewDataModelFile('${model.id}', 'monte_carlo_results')">查看蒙特卡洛结果</button>` 
                            : '<span class="text-muted">蒙特卡洛结果文件不存在</span>'}
                    </div>
                </section>
                
                <section class="details-section advanced-info">
                    <div class="section-title-row">
                        <div class="section-title">高级信息</div>
                        <button class="btn-secondary btn-compact section-collapse-btn" data-collapsed="true">展开</button>
                    </div>
                    <div class="advanced-content" style="display:none;">
                        <div class="info-grid">
                            ${model.data_source ? `<div class="info-item"><div class="info-label">数据来源</div><div class="info-value">${model.data_source}</div></div>` : ''}
                            ${model.analysis_type ? `<div class="info-item"><div class="info-label">分析类型</div><div class="info-value">${model.analysis_type}</div></div>` : ''}
                            ${model.created_by ? `<div class="info-item"><div class="info-label">创建人</div><div class="info-value">${model.created_by}</div></div>` : ''}
                            ${model.updated_at ? `<div class="info-item"><div class="info-label">更新时间</div><div class="info-value">${new Date(model.updated_at * 1000).toLocaleString('zh-CN')}</div></div>` : ''}
                            ${model.data_files && model.data_files.csv_data ? `<div class="info-item info-span-2"><div class="info-label">CSV文件</div><div class="info-value">${model.data_files.csv_data}</div></div>` : ''}
                            ${model.data_files && model.data_files.regression_model ? `<div class="info-item info-span-2"><div class="info-label">回归模型文件</div><div class="info-value">${model.data_files.regression_model}</div></div>` : ''}
                            ${model.data_files && model.data_files.monte_carlo_results ? `<div class="info-item info-span-2"><div class="info-label">蒙特卡洛结果文件</div><div class="info-value">${model.data_files.monte_carlo_results}</div></div>` : ''}
                        </div>
                        <div class="raw-toggle">
                            <button class="btn-secondary btn-compact raw-json-toggle" data-mode="hidden">显示原始数据</button>
                            <button class="btn-secondary btn-compact copy-json-btn">复制JSON</button>
                        </div>
                        <div class="meta-box raw-json" style="display:none;"><pre>${JSON.stringify({
                            id: model.id,
                            data_source: model.data_source,
                            analysis_type: model.analysis_type,
                            created_by: model.created_by,
                            created_at: model.created_at,
                            updated_at: model.updated_at,
                            data_files: model.data_files || {},
                            metadata: model.metadata || {}
                        }, null, 2)}</pre></div>
                    </div>
                </section>
            </div>
            <div class="modal-footer">
                <button class="btn-secondary" onclick="this.closest('.modal-overlay').remove()">关闭</button>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    // 高级信息折叠/展开与原始JSON切换
    const collapseBtn = modal.querySelector('.section-collapse-btn');
    const advContent = modal.querySelector('.advanced-content');
    const rawToggleBtn = modal.querySelector('.raw-json-toggle');
    const rawBox = modal.querySelector('.raw-json');
    const copyBtn = modal.querySelector('.copy-json-btn');
    
    collapseBtn?.addEventListener('click', () => {
        const collapsed = collapseBtn.getAttribute('data-collapsed') === 'true';
        if (collapsed) {
            advContent.style.display = '';
            collapseBtn.textContent = '收起';
            collapseBtn.setAttribute('data-collapsed', 'false');
        } else {
            advContent.style.display = 'none';
            collapseBtn.textContent = '展开';
            collapseBtn.setAttribute('data-collapsed', 'true');
        }
    });
    
    rawToggleBtn?.addEventListener('click', () => {
        const mode = rawToggleBtn.getAttribute('data-mode') || 'hidden';
        if (mode === 'hidden') {
            rawBox.style.display = '';
            rawToggleBtn.textContent = '隐藏原始数据';
            rawToggleBtn.setAttribute('data-mode', 'shown');
        } else {
            rawBox.style.display = 'none';
            rawToggleBtn.textContent = '显示原始数据';
            rawToggleBtn.setAttribute('data-mode', 'hidden');
        }
    });
    
    copyBtn?.addEventListener('click', async () => {
        try {
            const text = rawBox?.innerText || '';
            if (navigator.clipboard && text) {
                await navigator.clipboard.writeText(text);
                showNotification('已复制到剪贴板', 'success');
            } else {
                throw new Error('Clipboard API 不可用');
            }
        } catch (e) {
            showNotification('复制失败，请手动选择文本复制', 'warning');
        }
    });
}

async function deleteDataModel(modelId) {
    console.log(`🗑️ 删除数据模型: ${modelId}`);
    
    // 使用统一的主题化确认弹窗
    if (!(await authManager.showConfirmDialog('确定要删除这个数据模型吗？此操作不可撤销。'))) {
        return;
    }
    
    try {
        showLoading('正在删除数据模型...');
        
        const response = await fetch(`${API_BASE_URL}/api/data-models/models/${modelId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-Username': authManager.currentUser.username
            }
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (!result.success) {
            throw new Error(result.message || '删除数据模型失败');
        }
        
        showNotification('数据模型删除成功', 'success');
        
        // 重新加载数据模型列表
        setTimeout(() => {
            loadDataModels();
        }, 500);
        
    } catch (error) {
        console.error('❌ 删除数据模型失败:', error);
        showNotification('删除数据模型失败: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

// 查看数据模型文件
async function viewDataModelFile(modelId, fileType) {
    console.log(`📄 查看数据模型文件: ${modelId}, 类型: ${fileType}`);
    
    try {
        showLoading('正在加载文件内容...');
        
        const response = await fetch(`${API_BASE_URL}/api/data-models/models/${modelId}/files/${fileType}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-Username': authManager.currentUser.username
            }
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (!result.success) {
            throw new Error(result.message || '加载文件失败');
        }
        
        showFileContent(result.content, result.filename, fileType);
        
    } catch (error) {
        console.error('❌ 查看数据模型文件失败:', error);
        showNotification('查看文件失败: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

// 显示文件内容（支持"美化视图/原始内容"切换）
function showFileContent(content, filename, fileType) {
    const fileTypeNames = {
        'csv_data': 'CSV数据文件',
        'regression_model': '符号回归模型',
        'monte_carlo_results': '蒙特卡洛分析结果'
    };

    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal-content modal-large">
            <div class="modal-header">
                <h3>${fileTypeNames[fileType] || '文件内容'}</h3>
                <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">×</button>
            </div>
            <div class="modal-body">
                <div class="file-info">
                    <p><strong>文件名:</strong> ${filename}</p>
                    <p><strong>文件类型:</strong> ${fileTypeNames[fileType] || '-'}</p>
                </div>
                <div class="view-toggle">
                    <button class="btn-secondary toggle-view-btn" data-mode="beautified">切换为原始内容</button>
                </div>
                <div class="beautified-view"></div>
                <div class="file-content raw-view" style="display:none;">
                    <pre>${content}</pre>
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn-secondary" onclick="this.closest('.modal-overlay').remove()">关闭</button>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    // 渲染美化视图
    try {
        renderBeautifiedFileContent(modal.querySelector('.beautified-view'), content, filename, fileType);
    } catch (e) {
        // 解析失败则默认显示原始内容
        const toggleBtn = modal.querySelector('.toggle-view-btn');
        const beautified = modal.querySelector('.beautified-view');
        const raw = modal.querySelector('.raw-view');
        if (beautified) beautified.style.display = 'none';
        if (raw) raw.style.display = '';
        if (toggleBtn) toggleBtn.textContent = '切换为概览视图';
        if (toggleBtn) toggleBtn.dataset.mode = 'raw';
    }

    // 切换按钮事件
    const toggleBtn = modal.querySelector('.toggle-view-btn');
    toggleBtn?.addEventListener('click', () => {
        const mode = toggleBtn.dataset.mode || 'beautified';
        const beautified = modal.querySelector('.beautified-view');
        const raw = modal.querySelector('.raw-view');
        if (mode === 'beautified') {
            // 切换到原始
            if (beautified) beautified.style.display = 'none';
            if (raw) raw.style.display = '';
            toggleBtn.textContent = '切换为概览视图';
            toggleBtn.dataset.mode = 'raw';
        } else {
            // 切换到美化
            if (beautified && beautified.children.length === 0) {
                // 再次渲染兜底
                try { renderBeautifiedFileContent(beautified, content, filename, fileType); } catch (_) {}
            }
            if (beautified) beautified.style.display = '';
            if (raw) raw.style.display = 'none';
            toggleBtn.textContent = '切换为原始内容';
            toggleBtn.dataset.mode = 'beautified';
        }
    });
}

// 渲染美化视图
function renderBeautifiedFileContent(container, content, filename, fileType) {
    if (!container) return;
    if (fileType === 'csv_data') {
        // CSV 美化：展示基础统计与完整数据
        const parsed = parseCSV(content || '');
        const headers = parsed.headers || [];
        const rows = parsed.data || [];
        const tableHtml = generateTableWithCoordinates(headers, rows, `CSV数据预览 (共${rows.length}行数据)`);
        const html = `
            <div class="beautified-csv">
                <div class="metric-cards">
                    <div class="metric-card"><div class="metric-label">文件名</div><div class="metric-value">${filename || '-'}</div></div>
                    <div class="metric-card"><div class="metric-label">行数</div><div class="metric-value">${parsed.rows || 0}</div></div>
                    <div class="metric-card"><div class="metric-label">列数</div><div class="metric-value">${parsed.columns || 0}</div></div>
                </div>
                <div class="csv-table-container">
                    ${tableHtml}
                </div>
                <div class="csv-info">完整显示 ${rows.length} 行数据</div>
            </div>
        `;
        container.innerHTML = html;
        
        // 等待DOM渲染完成后对齐行列号
        setTimeout(() => {
            const tableContainer = container.querySelector('.table-with-coordinates');
            if (tableContainer) {
                alignCoordinatesToTable(tableContainer);
            }
        }, 100);
        
        return;
    }

    if (fileType === 'regression_model') {
        const json = JSON.parse(content || '{}');
        const dm = json.detailed_metrics || {};
        const featureImportance = Array.isArray(json.feature_importance) ? json.feature_importance.slice() : [];
        featureImportance.sort((a, b) => (b.importance || 0) - (a.importance || 0));

        const fmt = (v) => (v === 0 || typeof v === 'number') ? (Math.abs(v) < 1e-4 ? v.toExponential(2) : Number(v).toFixed(3)) : (v ?? '-');

        const html = `
            <div class="beautified-json">
                <div class="metric-cards">
                    <div class="metric-card"><div class="metric-label">目标变量</div><div class="metric-value">${json.target_column || '-'}</div></div>
                    <div class="metric-card"><div class="metric-label">皮尔逊相关系数(测试)</div><div class="metric-value">${dm.pearson_r_test ?? '-'}</div></div>
                    <div class="metric-card"><div class="metric-label">皮尔逊相关系数(训练)</div><div class="metric-value">${dm.pearson_r_training ?? '-'}</div></div>
                    <div class="metric-card"><div class="metric-label">复杂度</div><div class="metric-value">${json.model_complexity ?? '-'}</div></div>
                </div>
                ${json.expression_latex ? `<div class="expression-box"><div class="expression-label">模型表达式（MathJax）</div><div class="expression-value">$${json.expression_latex}$</div></div>` : (json.expression ? `<div class="expression-box"><div class="expression-label">模型表达式（MathJax）</div><div class="expression-value">$${json.expression}$</div></div>` : (json.expression_text ? `<div class="expression-box"><div class="expression-label">模型表达式（文本）</div><div class="expression-value">${json.expression_text}</div></div>` : ''))}

                <div class="section-subtitle">详细指标</div>
                <div class="metrics-grid">
                    <div class="metric-section">
                        <h6>误差指标</h6>
                        <div class="metric-list">
                            <div class="metric-item"><div class="metric-name-container"><span class="metric-name-cn">平均相对误差</span><span class="metric-name-en">Average relative error</span><span class="metric-dataset">(测试)</span></div><span class="metric-value">${dm.average_relative_error_test != null ? dm.average_relative_error_test + '%' : '-'}</span></div>
                            <div class="metric-item"><div class="metric-name-container"><span class="metric-name-cn">平均相对误差</span><span class="metric-name-en">Average relative error</span><span class="metric-dataset">(训练)</span></div><span class="metric-value">${dm.average_relative_error_training != null ? dm.average_relative_error_training + '%' : '-'}</span></div>
                            <div class="metric-item"><div class="metric-name-container"><span class="metric-name-cn">平均绝对误差</span><span class="metric-name-en">Mean absolute error</span><span class="metric-dataset">(测试)</span></div><span class="metric-value">${fmt(dm.mean_absolute_error_test)}</span></div>
                            <div class="metric-item"><div class="metric-name-container"><span class="metric-name-cn">平均绝对误差</span><span class="metric-name-en">Mean absolute error</span><span class="metric-dataset">(训练)</span></div><span class="metric-value">${fmt(dm.mean_absolute_error_training)}</span></div>
                            <div class="metric-item"><div class="metric-name-container"><span class="metric-name-cn">均方误差</span><span class="metric-name-en">Mean squared error</span><span class="metric-dataset">(测试)</span></div><span class="metric-value">${fmt(dm.mean_squared_error_test)}</span></div>
                            <div class="metric-item"><div class="metric-name-container"><span class="metric-name-cn">均方误差</span><span class="metric-name-en">Mean squared error</span><span class="metric-dataset">(训练)</span></div><span class="metric-value">${fmt(dm.mean_squared_error_training)}</span></div>
                            <div class="metric-item"><div class="metric-name-container"><span class="metric-name-cn">归一化均方误差</span><span class="metric-name-en">Normalized MSE</span><span class="metric-dataset">(测试)</span></div><span class="metric-value">${fmt(dm.normalized_mean_squared_error_test)}</span></div>
                            <div class="metric-item"><div class="metric-name-container"><span class="metric-name-cn">归一化均方误差</span><span class="metric-name-en">Normalized MSE</span><span class="metric-dataset">(训练)</span></div><span class="metric-value">${fmt(dm.normalized_mean_squared_error_training)}</span></div>
                            <div class="metric-item"><div class="metric-name-container"><span class="metric-name-cn">均方根误差</span><span class="metric-name-en">Root MSE</span><span class="metric-dataset">(测试)</span></div><span class="metric-value">${fmt(dm.root_mean_squared_error_test)}</span></div>
                            <div class="metric-item"><div class="metric-name-container"><span class="metric-name-cn">均方根误差</span><span class="metric-name-en">Root MSE</span><span class="metric-dataset">(训练)</span></div><span class="metric-value">${fmt(dm.root_mean_squared_error_training)}</span></div>
                        </div>
                    </div>

                    <div class="metric-section">
                        <h6>模型结构</h6>
                        <div class="metric-list">
                            <div class="metric-item"><div class="metric-name-container"><span class="metric-name-cn">模型深度</span><span class="metric-name-en">Model Depth</span></div><span class="metric-value">${dm.model_depth ?? '-'}</span></div>
                            <div class="metric-item"><div class="metric-name-container"><span class="metric-name-cn">模型长度</span><span class="metric-name-en">Model Length</span></div><span class="metric-value">${dm.model_length ?? '-'}</span></div>
                        </div>
                    </div>
                </div>

                ${featureImportance.length ? `
                <div class="section-subtitle">特征重要性</div>
                <div class="importance-table">
                    ${featureImportance.map(item => `
                        <div class="importance-row">
                            <div class="imp-name">${item.feature}</div>
                            <div class="imp-bar"><span style="width:${Math.min(100, Math.round((item.importance || 0) * 100))}%"></span></div>
                            <div class="imp-value">${(item.importance ?? 0).toFixed(3)}</div>
                        </div>
                    `).join('')}
                </div>` : ''}
            </div>
        `;
        container.innerHTML = html;
        // 对 MathJax 公式进行渲染（无论是 expression_latex 还是 expression）
        if ((json.expression_latex || json.expression) && window.MathJax && window.MathJax.typesetPromise) {
            // 等待 DOM 渲染完成后执行 MathJax
            setTimeout(() => {
                MathJax.typesetPromise([container]).catch(()=>{});
            }, 100);
        }
        return;
    }

    if (fileType === 'monte_carlo_results') {
        // 既支持 JSON，也支持 .txt 文本报告
        let json = null;
        try { json = JSON.parse(content || '{}'); } catch (_) { json = null; }

        // 新格式（包含 top10）
        if (json && Array.isArray(json.top10)) {
            const targetName = json.target_name || '目标';
            // 汇总卡片
            const summaryCards = `
                <div class="metric-cards">
                    <div class="metric-card"><div class="metric-label">模拟次数</div><div class="metric-value">${json.iterations ?? '-'}</div></div>
                    <div class="metric-card"><div class="metric-label">成功率</div><div class="metric-value">${json.success_rate != null ? (json.success_rate*100).toFixed(1)+'%' : '-'}</div></div>
                    <div class="metric-card"><div class="metric-label">有效样本</div><div class="metric-value">${json.valid_samples ?? '-'}</div></div>
                    <div class="metric-card"><div class="metric-label">分析时间(秒)</div><div class="metric-value">${json.analysis_time ?? '-'}</div></div>
                </div>`;
            // Top10 表格
            const varSet = new Set();
            json.top10.forEach(it => (it.components||[]).forEach(c => varSet.add(c.name)));
            const vars = Array.from(varSet);
            const header = ['Rank', targetName].concat(vars).map(h=>`<th>${h}</th>`).join('');
            const body = json.top10.map(it => {
                const map = {}; (it.components||[]).forEach(c=>map[c.name]=c.value);
                const cols = [it.rank ?? '', it.efficacy ?? ''].concat(vars.map(v=>map[v] ?? ''));
                return `<tr>${cols.map(c=>`<td>${c}</td>`).join('')}</tr>`;
            }).join('');
            const table = `
                <div class="section-subtitle">最佳药效（前10条）</div>
                <div class="csv-table-container">
                  <table class="csv-table"><thead><tr>${header}</tr></thead><tbody>${body}</tbody></table>
                </div>`;
            container.innerHTML = `<div class="beautified-json">${summaryCards}${table}</div>`;
            return;
        }

        // 旧格式（统计/重要性/样本）
        if (json && (json.target_statistics || json.feature_importance || json.simulations)) {
            const stats = json.target_statistics || {};
            const cis = json.confidence_intervals || {};
            const fi = Array.isArray(json.feature_importance) ? json.feature_importance.slice() : [];
            fi.sort((a, b) => (b.importance || 0) - (a.importance || 0));
            const top = fi.slice(0, 10);
            const sims = Array.isArray(json.simulations) ? json.simulations : [];
            const html = `
                <div class="beautified-json">
                    <div class="metric-cards">
                        <div class="metric-card"><div class="metric-label">均值</div><div class="metric-value">${fmtNum(stats.mean)}</div></div>
                        <div class="metric-card"><div class="metric-label">标准差</div><div class="metric-value">${fmtNum(stats.std)}</div></div>
                        <div class="metric-card"><div class="metric-label">最小值</div><div class="metric-value">${fmtNum(stats.min)}</div></div>
                        <div class="metric-card"><div class="metric-label">最大值</div><div class="metric-value">${fmtNum(stats.max)}</div></div>
                    </div>
                    <div class="section-subtitle">置信区间</div>
                    <div class="ci-grid">
                        ${Object.keys(cis).map(k => {
                            const c = cis[k] || {}; return `<div class=\"ci-item\"><div class=\"ci-label\">${k.toUpperCase()}</div><div class=\"ci-value\">${fmtNum(c.lower)} ~ ${fmtNum(c.upper)}</div></div>`;
                        }).join('')}
                    </div>
                    ${top.length ? `
                    <div class="section-subtitle">特征重要性（Top ${top.length}）</div>
                    <div class="importance-table">
                        ${top.map(item => `
                            <div class="importance-row">
                                <div class="imp-name">${item.feature}</div>
                                <div class="imp-bar"><span style="width:${Math.min(100, Math.round((item.importance || 0) * 100))}%"></span></div>
                                <div class="imp-value">${(item.importance ?? 0).toFixed(3)}</div>
                            </div>
                        `).join('')}
                    </div>` : ''}
                    ${sims.length ? `
                    <div class="section-subtitle">模拟样本（前5条）</div>
                    <div class="csv-table-container">
                        <table class="csv-table">
                            <thead><tr><th>#</th><th>特征维度</th><th>目标值</th></tr></thead>
                            <tbody>
                                ${sims.slice(0, 5).map(s => `<tr><td>${s.iteration ?? '-'}</td><td>${Array.isArray(s.features) ? s.features.length : '-'}</td><td>${fmtNum(s.target)}</td></tr>`).join('')}
                            </tbody>
                        </table>
                    </div>` : ''}
                </div>
            `;
            container.innerHTML = html;
            return;
        }

        // 文本报告解析
        const parsed = parseMonteCarloText(content || '');
        if (parsed) {
            const html = `
                <div class="beautified-json">
                    <div class="metric-cards">
                        ${parsed.target !== undefined ? `<div class=\"metric-card\"><div class=\"metric-label\">目标药效</div><div class=\"metric-value\">${parsed.target}</div></div>` : ''}
                        ${parsed.samples !== undefined ? `<div class=\"metric-card\"><div class=\"metric-label\">采样次数</div><div class=\"metric-value\">${parsed.samples}</div></div>` : ''}
                        ${parsed.valid !== undefined ? `<div class=\"metric-card\"><div class=\"metric-label\">有效样本</div><div class=\"metric-value\">${parsed.valid}</div></div>` : ''}
                        ${parsed.successRate !== undefined ? `<div class=\"metric-card\"><div class=\"metric-label\">成功率</div><div class=\"metric-value\">${parsed.successRate}%</div></div>` : ''}
                    </div>
                    ${parsed.recommendations && parsed.recommendations.length ? `
                    <div class="section-subtitle">推荐方案（前${Math.min(10, parsed.recommendations.length)}条）</div>
                    <div class="csv-table-container">
                        <table class="csv-table">
                            <thead><tr><th>#</th><th>预期药效</th><th>配比方案</th></tr></thead>
                            <tbody>
                                ${parsed.recommendations.slice(0, 10).map((r, idx) => `<tr><td>${idx + 1}</td><td>${r.effect}</td><td>${r.recipe}</td></tr>`).join('')}
                            </tbody>
                        </table>
                    </div>` : ''}
                </div>
            `;
            container.innerHTML = html;
            return;
        }

        // 若无法解析，则抛出以触发原始内容回退
        throw new Error('Unsupported monte carlo text format');
    }

    // 默认：没有美化
    container.innerHTML = `<div class="text-muted">该文件类型暂不支持美化视图，可切换查看原始内容</div>`;
}

function fmtNum(v) {
    if (typeof v !== 'number') return '-';
    const s = Math.abs(v) >= 1000 ? v.toFixed(0) : Math.abs(v) >= 1 ? v.toFixed(3) : v.toPrecision(3);
    return s;
}

// 解析蒙特卡洛 .txt 文本报告，返回简要结构
function parseMonteCarloText(text) {
    if (!text || typeof text !== 'string') return null;
    const clean = text.replace(/\r/g, '');
    const lines = clean.split('\n').map(l => l.trim()).filter(Boolean);
    if (!lines.length) return null;

    const result = {};
    // 目标药效、采样次数、有效样本、成功率
    const targetMatch = clean.match(/目标药效[:：]\s*([\d.]+)/);
    if (targetMatch) result.target = Number(targetMatch[1]);
    const samplesMatch = clean.match(/采样次数[:：]\s*([\d,]+)/);
    if (samplesMatch) result.samples = Number(samplesMatch[1].replace(/,/g, ''));
    const validMatch = clean.match(/有效样本[:：]\s*([\d,]+)/);
    if (validMatch) result.valid = Number(validMatch[1].replace(/,/g, ''));
    const successMatch = clean.match(/成功率[:：]\s*([\d.]+)%/);
    if (successMatch) result.successRate = Number(successMatch[1]);

    // 推荐方案（"推荐方案 1: ...，预期药效: 22.5"风格）
    const recs = [];
    const recRe = /推荐方案\s*\d+\s*[:：]\s*([^，,]+(?:[，,].*?)?)\s*[，,]\s*预期药效[:：]\s*([\d.]+)/g;
    let m;
    while ((m = recRe.exec(clean)) !== null) {
        const recipe = (m[1] || '').trim();
        const effect = Number(m[2]);
        if (recipe) recs.push({ recipe, effect });
    }
    if (recs.length) result.recommendations = recs;

    // 如果至少解析出一项关键数据，则认为有效
    if (result.target !== undefined || result.samples !== undefined || (result.recommendations && result.recommendations.length)) {
        return result;
    }
    return null;
}

// 数据管理页面事件监听器
function setupDataManagementListeners() {
    const importDataBtn = document.getElementById('import-data-btn');
    const exportDataBtn = document.getElementById('export-data-btn');
    const clearDataBtn = document.getElementById('clear-data-btn');
    
    if (importDataBtn) {
        importDataBtn.addEventListener('click', async () => {
            // 弹出文件选择（支持单个ZIP）
            const input = document.createElement('input');
            input.type = 'file';
            input.accept = '.zip';
            input.onchange = async (e) => {
                const file = e.target.files[0];
                if (!file) return;
                try {
                    showLoading('正在导入数据包...');
                    const formData = new FormData();
                    formData.append('file', file);
                    const resp = await fetch(`${API_BASE_URL}/api/data-models/import`, {
                        method: 'POST',
                        body: formData
                    });
                    if (!resp.ok) {
                        const ejson = await resp.json().catch(() => ({}));
                        throw new Error(ejson.message || `HTTP ${resp.status}`);
                    }
                    const data = await resp.json();
                    if (!data.success) throw new Error(data.message || '导入失败');
                    showNotification(`导入成功，共 ${data.count} 个模型`, 'success');
                    loadDataModels();
                } catch (err) {
                    console.error('导入失败:', err);
                    showNotification('导入失败: ' + err.message, 'error');
                } finally {
                    hideLoading();
                }
            };
            input.click();
        });
    }
    
    if (exportDataBtn) {
        exportDataBtn.addEventListener('click', async () => {
            try {
                showLoading('正在导出全部数据模型...');
                // 后端尚未提供"一键导出全部"端点，此处采用客户端合并方案：
                // 1) 获取模型列表；2) 逐个拉取单模型ZIP；3) 合并为总ZIP；4) 触发保存
                const listResp = await fetch(`${API_BASE_URL}/api/data-models/models`);
                if (!listResp.ok) throw new Error(`HTTP ${listResp.status}`);
                const listJson = await listResp.json();
                if (!listJson.success) throw new Error(listJson.message || '无法获取模型列表');
                const models = listJson.models || [];
                if (!models.length) {
                    showNotification('没有可导出的模型', 'info');
                    return;
                }
                // 并行获取所有单模型ZIP
                const blobs = await Promise.all(models.map(async (m) => {
                    const r = await fetch(`${API_BASE_URL}/api/data-models/models/${m.id}/files/all_as_zip`);
                    if (!r.ok) throw new Error(`获取模型 ${m.id} 失败: HTTP ${r.status}`);
                    return await r.blob();
                }));
                // 合并为总ZIP（仅打包子ZIP原样，保持"原封不动"）
                const JSZip = await loadJSZip();
                const zip = new JSZip();
                blobs.forEach((blob, idx) => {
                    zip.file(`${models[idx].id}.zip`, blob);
                });
                const content = await zip.generateAsync({ type: 'blob' });
                const fileName = `all_models_${new Date().toISOString().slice(0,19).replace(/[:T]/g,'-')}.zip`;
                if (window.electronAPI && window.electronAPI.saveZipFile) {
                    const arrayBuffer = await content.arrayBuffer();
                    await window.electronAPI.saveZipFile(fileName, arrayBuffer);
                } else {
                    const url = URL.createObjectURL(content);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = fileName;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    URL.revokeObjectURL(url);
                }
                showNotification('全部模型已导出', 'success');
            } catch (err) {
                console.error('导出失败:', err);
                showNotification('导出失败: ' + err.message, 'error');
            } finally {
                hideLoading();
            }
        });
    }
    
    if (clearDataBtn) {
        clearDataBtn.addEventListener('click', async () => {
            const confirmed = await authManager.showConfirmDialog('确定要清空所有数据模型吗？此操作不可撤销。');
            if (!confirmed) return;
            fetch(`${API_BASE_URL}/api/data-models/clear`, { method: 'POST' })
                .then(async (resp) => {
                    if (!resp.ok) {
                        const e = await resp.json().catch(() => ({}));
                        throw new Error(e.message || `HTTP ${resp.status}`);
                    }
                    return resp.json();
                })
                .then(() => {
                    showNotification('已清空所有数据', 'success');
                    loadDataModels();
                })
                .catch(err => {
                    console.error('清空失败:', err);
                    showNotification('清空失败: ' + err.message, 'error');
                });
        });
    }
}

// 格式化语法显示
function formatGrammarDisplay(grammar) {
    if (!grammar || !Array.isArray(grammar) || grammar.length === 0) {
        return '未设置';
    }
    
    const grammarMap = {
        'addition': '加法 (+)',
        'subtraction': '减法 (-)',
        'multiplication': '乘法 (×)',
        'division': '除法 (÷)'
    };
    
    return grammar.map(g => grammarMap[g] || g).join(', ');
}

// 全局函数（供HTML调用）
window.switchTab = switchTab;
window.startRegression = startRegression;
window.startMonteCarlo = startMonteCarlo;
window.importData = importData;
window.exportResults = exportResults;
window.testBackendConnection = testBackendConnection;
window.saveSettings = saveSettings;
window.loadDataModels = loadDataModels;
window.viewDataModel = viewDataModel;
window.deleteDataModel = deleteDataModel; 
window.viewDataModelFile = viewDataModelFile;
window.exportMonteCarloTop10Csv = exportMonteCarloTop10Csv;

// 刷新表达式树数据（供HTML调用）
window.refreshExpressionTreeData = async function() {
    try {
        showNotification('正在刷新数据...', 'info');
        await renderExpressionTreePage();
        showNotification('数据刷新完成', 'success');
    } catch (error) {
        console.error('刷新数据失败:', error);
        showNotification('刷新数据失败: ' + error.message, 'error');
    }
};