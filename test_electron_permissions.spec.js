const { test, expect } = require('@playwright/test');

test.describe('Electron权限问题测试', () => {
  
  test('测试浏览器中的用户管理功能', async ({ page }) => {
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
    
    // 点击添加用户按钮
    await page.click('#add-user-btn');
    
    // 等待模态框出现
    await page.waitForSelector('#modal-overlay');
    
    // 填写用户信息
    await page.fill('#new-username', '测试用户');
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
      console.log('❌ 浏览器中出现错误:', errorText);
      await page.screenshot({ path: 'browser_error.png', fullPage: true });
    } else {
      console.log('✅ 浏览器中没有错误消息');
    }
    
    // 检查用户列表
    const userRows = await page.$$('#users-table tbody tr');
    console.log(`📋 浏览器中用户列表有 ${userRows.length} 行数据`);
    
    await page.screenshot({ path: 'browser_result.png', fullPage: true });
  });

  test('测试后端API权限', async ({ request }) => {
    // 创建新的上下文
    const context = await request.newContext();
    
    // 登录
    const loginResponse = await context.post('http://127.0.0.1:5000/api/auth/login', {
      data: {
        username: 'admin',
        password: 'admin123'
      }
    });
    
    expect(loginResponse.ok()).toBeTruthy();
    const loginData = await loginResponse.json();
    console.log('登录响应:', loginData);
    
    // 获取用户列表
    const usersResponse = await context.get('http://127.0.0.1:5000/api/auth/users');
    expect(usersResponse.ok()).toBeTruthy();
    const usersData = await usersResponse.json();
    console.log('用户列表响应:', usersData);
    
    // 创建新用户
    const createUserResponse = await context.post('http://127.0.0.1:5000/api/auth/users', {
      data: {
        username: '测试用户',
        password: '123456',
        role: 'user'
      }
    });
    
    const createUserData = await createUserResponse.json();
    console.log('创建用户响应:', createUserData);
    
    if (createUserResponse.ok()) {
      console.log('✅ 后端API创建用户成功');
    } else {
      console.log('❌ 后端API创建用户失败:', createUserData);
    }
  });

  test('测试Electron会话问题', async ({ page }) => {
    // 模拟Electron环境
    await page.addInitScript(() => {
      // 模拟Electron的file://协议
      Object.defineProperty(window.location, 'protocol', {
        value: 'file:',
        writable: false
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
    
    // 点击用户管理标签
    await page.click('[data-tab="user-management"]');
    
    // 等待用户管理页面加载
    await page.waitForSelector('#user-management');
    
    // 点击添加用户按钮
    await page.click('#add-user-btn');
    
    // 等待模态框出现
    await page.waitForSelector('#modal-overlay');
    
    // 填写用户信息
    await page.fill('#new-username', 'Electron测试用户');
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
      console.log('❌ 模拟Electron环境中出现错误:', errorText);
      await page.screenshot({ path: 'electron_simulated_error.png', fullPage: true });
    } else {
      console.log('✅ 模拟Electron环境中没有错误消息');
    }
    
    await page.screenshot({ path: 'electron_simulated_result.png', fullPage: true });
  });
}); 