// 认证相关功能模块
class AuthManager {
    constructor() {
        this.currentUser = null;
        this.isAuthenticated = false;
        this.isFirstRun = false;
        this.apiBaseUrl = 'http://127.0.0.1:5000/api/auth';
    }

    // 初始化认证系统
    async initialize() {
        console.log('🔐 初始化认证系统...');
        
        // 检查是否首次运行
        await this.checkFirstRun();
        
        // 检查认证状态
        await this.checkAuthStatus();
        
        // 设置事件监听器
        this.setupAuthEventListeners();
        
        console.log('✅ 认证系统初始化完成');
    }

    // 检查是否首次运行
    async checkFirstRun() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/check-admin`, {
                method: 'GET',
                credentials: 'include'
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.isFirstRun = !data.admin_created;
                
                if (this.isFirstRun) {
                    this.showFirstRunMessage();
                } else {
                    this.hideFirstRunMessage();
                }
            }
        } catch (error) {
            console.error('检查首次运行状态失败:', error);
        }
    }

    // 检查认证状态
    async checkAuthStatus() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/check-auth`, {
                method: 'GET',
                credentials: 'include'
            });
            
            const data = await response.json();
            
            if (data.success && data.authenticated) {
                this.currentUser = data.user;
                this.isAuthenticated = true;
                this.showMainInterface();
                this.updateUserInfo();
                this.updateNavigationVisibility();
                
                // 如果当前在用户管理页面，自动加载用户列表
                const activeTab = document.querySelector('.tab-content.active');
                if (activeTab && activeTab.id === 'user-management' && this.currentUser.role === 'admin') {
                    console.log('🔍 检测到在用户管理页面，自动加载用户列表');
                    setTimeout(() => {
                        this.loadUsers();
                    }, 100);
                }
            } else {
                this.showLoginInterface();
            }
        } catch (error) {
            console.error('检查认证状态失败:', error);
            this.showLoginInterface();
        }
    }

    // 设置认证相关事件监听器
    setupAuthEventListeners() {
        // 登录表单提交
        const loginForm = document.getElementById('login-form');
        if (loginForm) {
            loginForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleLogin();
            });
        }

        // 登出按钮
        const logoutBtn = document.getElementById('logout-btn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => {
                this.handleLogout();
            });
        }

        // 用户管理相关按钮
        const addUserBtn = document.getElementById('add-user-btn');
        if (addUserBtn) {
            addUserBtn.addEventListener('click', () => {
                console.log('🔍 添加用户按钮被点击');
                this.showAddUserModal();
            });
        }

        const refreshUsersBtn = document.getElementById('refresh-users-btn');
        if (refreshUsersBtn) {
            refreshUsersBtn.addEventListener('click', () => {
                console.log('🔍 刷新用户列表按钮被点击');
                this.loadUsers();
            });
        }
    }

    // 处理登录
    async handleLogin() {
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        
        if (!username || !password) {
            this.showLoginError('请输入用户名和密码');
            return;
        }

        try {
            showLoading('正在登录...');
            
            const response = await fetch(`${this.apiBaseUrl}/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'include',
                body: JSON.stringify({ username, password })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.currentUser = data.user;
                this.isAuthenticated = true;
                this.showMainInterface();
                this.updateUserInfo();
                this.updateNavigationVisibility();
                this.hideLoginError();
                showNotification('登录成功', 'success');
                
                // 清空登录表单
                document.getElementById('login-form').reset();
            } else {
                this.showLoginError(data.error || '登录失败');
            }
        } catch (error) {
            console.error('登录失败:', error);
            this.showLoginError('网络错误，请检查后端服务');
        } finally {
            hideLoading();
        }
    }

    // 处理登出
    async handleLogout() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/logout`, {
                method: 'POST',
                credentials: 'include'
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.currentUser = null;
                this.isAuthenticated = false;
                this.showLoginInterface();
                showNotification('已退出登录', 'info');
            }
        } catch (error) {
            console.error('登出失败:', error);
        }
    }

    // 创建管理员账号
    async createAdmin(password) {
        try {
            showLoading('正在创建管理员账号...');
            
            const response = await fetch(`${this.apiBaseUrl}/create-admin`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'include',
                body: JSON.stringify({ password })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.isFirstRun = false;
                this.hideFirstRunMessage();
                showNotification('管理员账号创建成功', 'success');
                return true;
            } else {
                showNotification(data.error || '创建管理员账号失败', 'error');
                return false;
            }
        } catch (error) {
            console.error('创建管理员失败:', error);
            showNotification('网络错误，请检查后端服务', 'error');
            return false;
        } finally {
            hideLoading();
        }
    }

    // 显示首次运行消息
    showFirstRunMessage() {
        const message = document.getElementById('first-run-message');
        if (message) {
            message.style.display = 'block';
        }
    }

    // 隐藏首次运行消息
    hideFirstRunMessage() {
        const message = document.getElementById('first-run-message');
        if (message) {
            message.style.display = 'none';
        }
    }

    // 显示登录界面
    showLoginInterface() {
        const loginContainer = document.getElementById('login-container');
        const mainContainer = document.getElementById('main-container');
        
        if (mainContainer) {
            // 主界面淡出
            mainContainer.style.opacity = '0';
            mainContainer.style.transform = 'translateY(-20px)';
            
            setTimeout(() => {
                if (mainContainer) mainContainer.style.display = 'none';
                if (loginContainer) {
                    loginContainer.style.display = 'flex';
                    // 登录界面淡入
                    setTimeout(() => {
                        if (loginContainer) {
                            loginContainer.style.opacity = '1';
                            loginContainer.style.transform = 'translateY(0)';
                        }
                    }, 50);
                }
            }, 300);
        } else {
            if (loginContainer) loginContainer.style.display = 'flex';
        }
    }

    // 显示主界面
    showMainInterface() {
        const loginContainer = document.getElementById('login-container');
        const mainContainer = document.getElementById('main-container');
        
        if (loginContainer) {
            // 登录界面淡出
            loginContainer.style.opacity = '0';
            loginContainer.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                if (loginContainer) loginContainer.style.display = 'none';
                if (mainContainer) {
                    mainContainer.style.display = 'block';
                    // 主界面淡入
                    setTimeout(() => {
                        if (mainContainer) {
                            mainContainer.style.opacity = '1';
                            mainContainer.style.transform = 'translateY(0)';
                            mainContainer.classList.add('loaded');
                        }
                    }, 50);
                }
            }, 300);
        } else {
            if (mainContainer) {
                mainContainer.style.display = 'block';
                mainContainer.classList.add('loaded');
            }
        }
    }

    // 显示登录错误
    showLoginError(message) {
        const errorElement = document.getElementById('login-error');
        if (errorElement) {
            errorElement.textContent = message;
            errorElement.style.display = 'block';
        }
    }

    // 隐藏登录错误
    hideLoginError() {
        const errorElement = document.getElementById('login-error');
        if (errorElement) {
            errorElement.style.display = 'none';
        }
    }

    // 更新用户信息显示
    updateUserInfo() {
        const userInfo = document.getElementById('user-info');
        const currentUserSpan = document.getElementById('current-user');
        const userRoleSpan = document.getElementById('user-role');
        
        if (this.currentUser && userInfo) {
            userInfo.textContent = `${this.currentUser.username} (${this.currentUser.role === 'admin' ? '管理员' : '用户'})`;
        }
        
        if (this.currentUser && currentUserSpan) {
            currentUserSpan.textContent = this.currentUser.username;
        }
        
        if (this.currentUser && userRoleSpan) {
            userRoleSpan.textContent = this.currentUser.role === 'admin' ? '管理员' : '普通用户';
        }
    }

    // 更新导航可见性
    updateNavigationVisibility() {
        const adminOnlyButtons = document.querySelectorAll('.nav-btn.admin-only');
        
        adminOnlyButtons.forEach(button => {
            if (this.currentUser && this.currentUser.role === 'admin') {
                button.classList.add('show');
            } else {
                button.classList.remove('show');
            }
        });
    }

    // 加载用户列表
    async loadUsers() {
        console.log('🔍 开始加载用户列表');
        console.log('当前用户:', this.currentUser);
        
        if (!this.currentUser || this.currentUser.role !== 'admin') {
            console.error('❌ 权限不足，无法加载用户列表');
            showNotification('权限不足', 'error');
            this.displayUsers([]); // 清空用户列表显示
            return;
        }

        try {
            showLoading('正在加载用户列表...');
            console.log('🔍 发送请求到:', `${this.apiBaseUrl}/users`);
            
            // 检查是否在file://协议下
            const isFileProtocol = window.location.protocol === 'file:';
            console.log('🔍 当前协议:', window.location.protocol);
            
            const fetchOptions = {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            };
            
            // 在file://协议下，通过请求头传递用户名
            if (isFileProtocol) {
                fetchOptions.headers['X-Username'] = this.currentUser.username;
            } else {
                fetchOptions.credentials = 'include';
            }
            
            const response = await fetch(`${this.apiBaseUrl}/users`, fetchOptions);
            
            console.log('🔍 响应状态:', response.status);
            const data = await response.json();
            console.log('🔍 响应数据:', data);
            
            if (data.success) {
                console.log('✅ 用户列表加载成功，用户数量:', data.users.length);
                this.displayUsers(data.users);
            } else {
                console.error('❌ 加载用户列表失败:', data.error);
                showNotification(data.error || '加载用户列表失败', 'error');
                this.displayUsers([]); // 显示空列表
            }
        } catch (error) {
            console.error('❌ 加载用户列表失败:', error);
            showNotification('网络错误', 'error');
            this.displayUsers([]); // 显示空列表
        } finally {
            hideLoading();
        }
    }

    // 显示用户列表
    displayUsers(users) {
        console.log('🔍 开始显示用户列表，用户数量:', users.length);
        console.log('🔍 用户数据:', users);
        
        const usersTable = document.getElementById('users-table');
        console.log('🔍 用户表格元素:', usersTable);
        
        if (!usersTable) {
            console.error('❌ 找不到用户表格元素');
            return;
        }
        
        if (users.length === 0) {
            console.log('📝 用户列表为空');
            usersTable.innerHTML = `
                <div class="empty-state">
                    <p>暂无用户数据</p>
                    <p>点击"添加用户"按钮创建第一个用户</p>
                </div>
            `;
            return;
        }
        
        console.log('📝 生成用户列表HTML');
        let html = `
            <table>
                <thead>
                    <tr>
                        <th>用户名</th>
                        <th>角色</th>
                        <th>创建时间</th>
                        <th>最后登录</th>
                        <th>状态</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody>
        `;
        
        users.forEach(user => {
            const createdTime = user.created_at ? new Date(user.created_at * 1000).toLocaleString() : '未知';
            const lastLogin = user.last_login ? new Date(user.last_login * 1000).toLocaleString() : '从未登录';
            const isActive = user.last_login && (Date.now() - user.last_login * 1000) < 24 * 60 * 60 * 1000; // 24小时内登录过
            const roleText = user.role === 'admin' ? '管理员' : '用户';
            const roleClass = user.role === 'admin' ? 'admin-role' : 'user-role';
            
            html += `
                <tr>
                    <td><strong>${user.username}</strong></td>
                    <td><span class="role-badge ${roleClass}">${roleText}</span></td>
                    <td>${createdTime}</td>
                    <td>${lastLogin}</td>
                    <td>
                        <div class="status-cell">
                            <span class="status-indicator ${isActive ? '' : 'inactive'}"></span>
                            <span>${isActive ? '在线' : '离线'}</span>
                        </div>
                    </td>
                    <td>
                        <button class="btn-secondary btn-sm" onclick="authManager.editUser('${user.username}')" title="编辑用户">
                            <span>编辑</span>
                        </button>
                        <button class="btn-danger btn-sm" onclick="authManager.deleteUser('${user.username}')" title="删除用户">
                            <span>删除</span>
                        </button>
                    </td>
                </tr>
            `;
        });
        
        html += '</tbody></table>';
        usersTable.innerHTML = html;
        console.log('📝 设置用户表格HTML:', html);
        console.log('✅ 用户列表显示完成');
    }

    // 显示添加用户模态框
    showAddUserModal() {
        const modalTitle = document.getElementById('modal-title');
        const modalBody = document.getElementById('modal-body');
        const modalOverlay = document.getElementById('modal-overlay');
        
        if (modalTitle) modalTitle.textContent = '添加用户';
        
        if (modalBody) {
            modalBody.innerHTML = `
                <div class="form-group">
                    <label for="new-username">用户名</label>
                    <input type="text" id="new-username" required>
                </div>
                <div class="form-group">
                    <label for="new-password">密码</label>
                    <input type="password" id="new-password" required>
                </div>
                <div class="form-group">
                    <label for="new-role">角色</label>
                    <select id="new-role">
                        <option value="user">用户</option>
                        <option value="admin">管理员</option>
                    </select>
                </div>
            `;
        }
        
        if (modalOverlay) {
            modalOverlay.style.display = 'flex';
            
            // 设置确认按钮事件
            const confirmBtn = document.getElementById('modal-confirm');
            if (confirmBtn) {
                confirmBtn.onclick = () => {
                    console.log('🔍 模态框确认按钮被点击');
                    this.createUser();
                };
            }
            
            // 设置取消按钮事件
            const cancelBtn = document.getElementById('modal-cancel');
            if (cancelBtn) {
                cancelBtn.onclick = () => {
                    console.log('🔍 模态框取消按钮被点击');
                    this.hideModal();
                };
            }
            
            // 设置关闭按钮事件
            const closeBtn = document.querySelector('.modal-close');
            if (closeBtn) {
                closeBtn.onclick = () => {
                    console.log('🔍 模态框关闭按钮被点击');
                    this.hideModal();
                };
            }
        }
    }

    // 创建用户
    async createUser() {
        const username = document.getElementById('new-username')?.value;
        const password = document.getElementById('new-password')?.value;
        const role = document.getElementById('new-role')?.value;
        
        if (!username || !password) {
            showNotification('请填写完整信息', 'error');
            return;
        }
        
        try {
            showLoading('正在创建用户...');
            
            // 检查是否在file://协议下
            const isFileProtocol = window.location.protocol === 'file:';
            console.log('🔍 创建用户 - 当前协议:', window.location.protocol);
            
            const fetchOptions = {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, password, role })
            };
            
            // 在file://协议下，通过请求头传递用户名
            if (isFileProtocol) {
                fetchOptions.headers['X-Username'] = this.currentUser.username;
            } else {
                fetchOptions.credentials = 'include';
            }
            
            const response = await fetch(`${this.apiBaseUrl}/users`, fetchOptions);
            
            const data = await response.json();
            
            if (data.success) {
                showNotification('用户创建成功', 'success');
                this.hideModal();
                this.loadUsers();
            } else {
                showNotification(data.error || '创建用户失败', 'error');
            }
        } catch (error) {
            console.error('创建用户失败:', error);
            showNotification('网络错误', 'error');
        } finally {
            hideLoading();
        }
    }

    // 编辑用户
    async editUser(username) {
        try {
            console.log('🔍 开始编辑用户:', username);
            
            // 获取用户信息
            const isFileProtocol = window.location.protocol === 'file:';
            console.log('🔍 编辑用户 - 当前协议:', window.location.protocol);
            
            const fetchOptions = {
                method: 'GET'
            };
            
            // 在file://协议下，通过请求头传递用户名
            if (isFileProtocol) {
                fetchOptions.headers = {
                    'X-Username': this.currentUser.username
                };
            } else {
                fetchOptions.credentials = 'include';
            }
            
            const response = await fetch(`${this.apiBaseUrl}/users/${username}`, fetchOptions);
            const data = await response.json();
            
            if (data.success) {
                this.showEditUserModal(data.user);
            } else {
                showNotification(data.error || '获取用户信息失败', 'error');
            }
        } catch (error) {
            console.error('获取用户信息失败:', error);
            showNotification('网络错误', 'error');
        }
    }

    // 显示编辑用户模态框
    showEditUserModal(user) {
        const modalTitle = document.getElementById('modal-title');
        const modalBody = document.getElementById('modal-body');
        const modalOverlay = document.getElementById('modal-overlay');
        
        if (modalTitle) modalTitle.textContent = '编辑用户';
        
        if (modalBody) {
            modalBody.innerHTML = `
                <div class="form-group">
                    <label for="edit-username">用户名</label>
                    <input type="text" id="edit-username" value="${user.username}" readonly>
                    <small>用户名不可修改</small>
                </div>
                <div class="form-group">
                    <label for="edit-password">新密码</label>
                    <input type="password" id="edit-password" placeholder="留空则不修改密码">
                </div>
                <div class="form-group">
                    <label for="edit-role">角色</label>
                    <select id="edit-role">
                        <option value="user" ${user.role === 'user' ? 'selected' : ''}>用户</option>
                        <option value="admin" ${user.role === 'admin' ? 'selected' : ''}>管理员</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>用户信息</label>
                    <div class="user-info-display">
                        <p><strong>创建时间:</strong> ${user.created_at ? new Date(user.created_at * 1000).toLocaleString() : '未知'}</p>
                        <p><strong>最后登录:</strong> ${user.last_login ? new Date(user.last_login * 1000).toLocaleString() : '从未登录'}</p>
                    </div>
                </div>
            `;
        }
        
        if (modalOverlay) {
            modalOverlay.style.display = 'flex';
            
            // 设置确认按钮事件
            const confirmBtn = document.getElementById('modal-confirm');
            if (confirmBtn) {
                confirmBtn.onclick = () => {
                    console.log('🔍 编辑用户模态框确认按钮被点击');
                    this.updateUser(user.username);
                };
            }
            
            // 设置取消按钮事件
            const cancelBtn = document.getElementById('modal-cancel');
            if (cancelBtn) {
                cancelBtn.onclick = () => {
                    console.log('🔍 编辑用户模态框取消按钮被点击');
                    this.hideModal();
                };
            }
            
            // 设置关闭按钮事件
            const closeBtn = document.querySelector('.modal-close');
            if (closeBtn) {
                closeBtn.onclick = () => {
                    console.log('🔍 编辑用户模态框关闭按钮被点击');
                    this.hideModal();
                };
            }
        }
    }

    // 更新用户
    async updateUser(username) {
        const password = document.getElementById('edit-password')?.value;
        const role = document.getElementById('edit-role')?.value;
        
        if (!role) {
            showNotification('请选择用户角色', 'error');
            return;
        }
        
        try {
            showLoading('正在更新用户...');
            
            // 检查是否在file://协议下
            const isFileProtocol = window.location.protocol === 'file:';
            console.log('🔍 更新用户 - 当前协议:', window.location.protocol);
            
            const updateData = { role };
            if (password) {
                updateData.password = password;
            }
            
            const fetchOptions = {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(updateData)
            };
            
            // 在file://协议下，通过请求头传递用户名
            if (isFileProtocol) {
                fetchOptions.headers['X-Username'] = this.currentUser.username;
            } else {
                fetchOptions.credentials = 'include';
            }
            
            const response = await fetch(`${this.apiBaseUrl}/users/${username}`, fetchOptions);
            
            const data = await response.json();
            
            if (data.success) {
                showNotification('用户更新成功', 'success');
                this.hideModal();
                this.loadUsers();
            } else {
                showNotification(data.error || '更新用户失败', 'error');
            }
        } catch (error) {
            console.error('更新用户失败:', error);
            showNotification('网络错误', 'error');
        } finally {
            hideLoading();
        }
    }

    // 删除用户
    async deleteUser(username) {
        // 使用自定义确认对话框替代原生confirm
        const confirmed = await this.showConfirmDialog(`确定要删除用户 ${username} 吗？`);
        if (!confirmed) {
            return;
        }
        
        try {
            showLoading('正在删除用户...');
            
            // 检查是否在file://协议下
            const isFileProtocol = window.location.protocol === 'file:';
            console.log('🔍 删除用户 - 当前协议:', window.location.protocol);
            
            const fetchOptions = {
                method: 'DELETE'
            };
            
            // 在file://协议下，通过请求头传递用户名
            if (isFileProtocol) {
                fetchOptions.headers = {
                    'X-Username': this.currentUser.username
                };
            } else {
                fetchOptions.credentials = 'include';
            }
            
            const response = await fetch(`${this.apiBaseUrl}/users/${username}`, fetchOptions);
            
            const data = await response.json();
            
            if (data.success) {
                showNotification('用户删除成功', 'success');
                this.loadUsers();
            } else {
                showNotification(data.error || '删除用户失败', 'error');
            }
        } catch (error) {
            console.error('删除用户失败:', error);
            showNotification('网络错误', 'error');
        } finally {
            hideLoading();
        }
    }

    // 显示确认对话框
    showConfirmDialog(message) {
        return new Promise((resolve) => {
            const modalTitle = document.getElementById('modal-title');
            const modalBody = document.getElementById('modal-body');
            const modalOverlay = document.getElementById('modal-overlay');
            const confirmBtn = document.getElementById('modal-confirm');
            const cancelBtn = document.getElementById('modal-cancel');
            
            if (modalTitle) modalTitle.textContent = '确认操作';
            if (modalBody) {
                modalBody.innerHTML = `
                    <div class="confirm-dialog">
                        <p>${message}</p>
                    </div>
                `;
            }
            
            if (modalOverlay) {
                modalOverlay.style.display = 'flex';
                
                // 设置确认按钮事件
                if (confirmBtn) {
                    confirmBtn.onclick = () => {
                        this.hideModal();
                        resolve(true);
                    };
                }
                
                // 设置取消按钮事件
                if (cancelBtn) {
                    cancelBtn.onclick = () => {
                        this.hideModal();
                        resolve(false);
                    };
                }
            }
        });
    }

    // 隐藏模态框
    hideModal() {
        const modalOverlay = document.getElementById('modal-overlay');
        if (modalOverlay) {
            modalOverlay.style.display = 'none';
        }
    }

    // 测试函数 - 用于调试
    testUserManagement() {
        console.log('🧪 开始用户管理功能测试');
        console.log('当前用户:', this.currentUser);
        console.log('认证状态:', this.isAuthenticated);
        
        // 测试用户表格元素是否存在
        const usersTable = document.getElementById('users-table');
        console.log('用户表格元素:', usersTable);
        
        if (usersTable) {
            console.log('用户表格内容:', usersTable.innerHTML);
        }
        
        // 测试API连接
        fetch(`${this.apiBaseUrl}/check-auth`, {
            method: 'GET',
            credentials: 'include'
        }).then(response => response.json())
        .then(data => {
            console.log('认证检查结果:', data);
        })
        .catch(error => {
            console.error('认证检查失败:', error);
        });
    }
}

// 创建全局认证管理器实例
const authManager = new AuthManager();

// 导出认证管理器
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AuthManager;
} 