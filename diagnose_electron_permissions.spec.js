const { test, expect } = require('@playwright/test');

test.describe('Electron权限问题诊断', () => {
  
  test('诊断Electron会话管理问题', async ({ page }) => {
    // 模拟Electron环境
    await page.addInitScript(() => {
      // 模拟Electron的file://协议
      Object.defineProperty(window.location, 'protocol', {
        value: 'file:',
        writable: false
      });
      
      // 添加调试信息
      console.log('🔍 模拟Electron环境:', {
        protocol: window.location.protocol,
        href: window.location.href,
        userAgent: navigator.userAgent
      });
    });
    
    // 监听网络请求
    page.on('request', request => {
      console.log('🌐 请求:', request.method(), request.url());
    });
    
    page.on('response', response => {
      console.log('📡 响应:', response.status(), response.url());
    });
    
    // 访问前端页面
    await page.goto('http://127.0.0.1:3000/');
    
    // 等待登录表单
    await page.waitForSelector('#login-form');
    
    // 填写登录信息
    await page.fill('#username', 'admin');
    await page.fill('#password', 'admin123');
    
    // 点击登录按钮
    await page.click('#login-btn');
    
    // 等待主界面加载
    await page.waitForSelector('.main-container');
    
    // 点击用户管理标签
    await page.click('[data-tab="user-management"]');
    
    // 等待用户管理页面加载
    await page.waitForSelector('#user-management');
    
    // 等待用户列表加载
    await page.waitForTimeout(2000);
    
    // 检查用户列表内容
    const userTable = await page.$('#users-table');
    if (userTable) {
      const tableContent = await userTable.textContent();
      console.log('📋 用户表格内容:', tableContent.substring(0, 200) + '...');
    }
    
    // 点击添加用户按钮
    await page.click('#add-user-btn');
    
    // 等待模态框出现
    await page.waitForSelector('#modal-overlay');
    
    // 填写用户信息
    await page.fill('#new-username', 'Electron诊断用户');
    await page.fill('#new-password', '123456');
    
    // 选择用户角色
    await page.selectOption('#new-role', 'user');
    
    // 点击确认按钮
    await page.click('#modal-confirm');
    
    // 等待响应
    await page.waitForTimeout(3000);
    
    // 检查是否有错误消息
    const errorElements = await page.$$('.notification.error');
    if (errorElements.length > 0) {
      const errorText = await errorElements[0].textContent();
      console.log('❌ 出现错误:', errorText);
      
      // 保存错误截图
      await page.screenshot({ path: 'electron_diagnosis_error.png', fullPage: true });
      
      // 检查错误详情
      const errorDetails = await page.evaluate(() => {
        const errors = document.querySelectorAll('.notification.error');
        return Array.from(errors).map(el => ({
          text: el.textContent,
          className: el.className,
          style: el.style.cssText
        }));
      });
      console.log('🔍 错误详情:', errorDetails);
    } else {
      console.log('✅ 没有错误消息');
    }
    
    // 检查成功消息
    const successElements = await page.$$('.notification.success');
    if (successElements.length > 0) {
      const successText = await successElements[0].textContent();
      console.log('✅ 成功消息:', successText);
    }
    
    // 保存最终截图
    await page.screenshot({ path: 'electron_diagnosis_final.png', fullPage: true });
    
    // 检查JavaScript控制台错误
    const consoleErrors = await page.evaluate(() => {
      return window.consoleErrors || [];
    });
    if (consoleErrors.length > 0) {
      console.log('🔍 JavaScript控制台错误:', consoleErrors);
    }
  });

  test('检查Electron特定的认证机制', async ({ page }) => {
    // 模拟Electron环境并添加认证调试
    await page.addInitScript(() => {
      // 模拟Electron的file://协议
      Object.defineProperty(window.location, 'protocol', {
        value: 'file:',
        writable: false
      });
      
      // 拦截fetch请求以添加调试信息
      const originalFetch = window.fetch;
      window.fetch = function(...args) {
        console.log('🔍 Fetch请求:', args[0], args[1]);
        return originalFetch.apply(this, args);
      };
      
      // 监听认证相关的事件
      window.addEventListener('storage', (e) => {
        console.log('🔍 Storage事件:', e.key, e.newValue);
      });
    });
    
    // 访问前端页面
    await page.goto('http://127.0.0.1:3000/');
    
    // 等待登录表单
    await page.waitForSelector('#login-form');
    
    // 填写登录信息
    await page.fill('#username', 'admin');
    await page.fill('#password', 'admin123');
    
    // 点击登录按钮
    await page.click('#login-btn');
    
    // 等待主界面加载
    await page.waitForSelector('.main-container');
    
    // 检查认证状态
    const authStatus = await page.evaluate(() => {
      return {
        currentUser: window.authManager?.currentUser,
        isAuthenticated: window.authManager?.isAuthenticated,
        apiBaseUrl: window.authManager?.apiBaseUrl
      };
    });
    console.log('🔍 认证状态:', authStatus);
    
    // 点击用户管理标签
    await page.click('[data-tab="user-management"]');
    
    // 等待用户管理页面加载
    await page.waitForSelector('#user-management');
    
    // 等待用户列表加载
    await page.waitForTimeout(2000);
    
    // 检查用户列表是否加载
    const userRows = await page.$$('#users-table tbody tr');
    console.log(`📋 用户列表行数: ${userRows.length}`);
    
    if (userRows.length === 0) {
      console.log('⚠️ 用户列表为空，可能是权限问题');
      
      // 检查是否有权限不足的提示
      const permissionElements = await page.$$('*:contains("权限不足")');
      if (permissionElements.length > 0) {
        console.log('❌ 发现权限不足提示');
      }
    }
    
    await page.screenshot({ path: 'electron_auth_diagnosis.png', fullPage: true });
  });
}); 