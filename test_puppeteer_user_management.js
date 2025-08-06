const puppeteer = require('puppeteer');

async function testUserManagement() {
    console.log('🚀 开始Puppeteer测试用户管理功能...');
    
    const browser = await puppeteer.launch({ 
        headless: false,
        defaultViewport: null,
        args: ['--start-maximized']
    });
    
    let page;
    
    try {
        page = await browser.newPage();
        
        // 1. 访问前端页面
        console.log('📱 访问前端页面...');
        await page.goto('http://127.0.0.1:3000/', { waitUntil: 'networkidle0' });
        
        // 2. 等待登录界面加载
        await page.waitForSelector('#login-form', { timeout: 5000 });
        console.log('✅ 登录界面已加载');
        
        // 3. 填写登录表单
        console.log('🔐 填写登录表单...');
        await page.type('#username', 'admin');
        await page.type('#password', 'admin123');
        
        // 4. 点击登录按钮
        await page.click('#login-btn');
        console.log('✅ 点击登录按钮');
        
        // 5. 等待登录完成并跳转到主界面
        await page.waitForSelector('.main-container', { timeout: 10000 });
        console.log('✅ 登录成功，进入主界面');
        
        // 6. 点击用户管理标签
        await page.waitForSelector('[data-tab="user-management"]', { timeout: 5000 });
        await page.click('[data-tab="user-management"]');
        console.log('✅ 点击用户管理标签');
        
        // 7. 等待用户管理页面加载
        await page.waitForSelector('#user-management', { timeout: 5000 });
        console.log('✅ 用户管理页面已加载');
        
        // 8. 点击添加用户按钮
        await page.waitForSelector('#add-user-btn', { timeout: 5000 });
        await page.click('#add-user-btn');
        console.log('✅ 点击添加用户按钮');
        
        // 9. 等待模态框出现
        await page.waitForSelector('#modal-overlay', { timeout: 5000 });
        console.log('✅ 添加用户模态框已显示');
        
        // 10. 填写用户信息
        console.log('📝 填写用户信息...');
        await page.type('#new-username', 'ChHsich');
        await page.type('#new-password', '123456');
        
        // 选择角色（如果需要）
        const roleSelect = await page.$('#new-role');
        if (roleSelect) {
            await page.select('#new-role', 'user');
            console.log('✅ 选择用户角色');
        }
        
        // 11. 点击确认按钮
        await page.click('#modal-confirm');
        console.log('✅ 点击确认按钮');
        
        // 12. 等待响应
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // 13. 检查是否有错误消息
        const errorElements = await page.$$('.notification.error');
        if (errorElements.length > 0) {
            const errorText = await page.evaluate(el => el.textContent, errorElements[0]);
            console.log('❌ 出现错误:', errorText);
        } else {
            console.log('✅ 没有错误消息');
        }
        
        // 14. 检查用户列表是否更新
        const userRows = await page.$$('#users-table tbody tr');
        console.log(`📋 用户列表中有 ${userRows.length} 行数据`);
        
        // 15. 检查是否包含新添加的用户
        const pageContent = await page.content();
        if (pageContent.includes('ChHsich')) {
            console.log('✅ 新用户已添加到列表中');
        } else {
            console.log('❌ 新用户未出现在列表中');
        }
        
        // 16. 截图保存
        await page.screenshot({ path: 'user_management_test.png', fullPage: true });
        console.log('📸 已保存截图: user_management_test.png');
        
    } catch (error) {
        console.error('❌ 测试失败:', error.message);
        
        // 保存错误截图
        if (page) {
            try {
                await page.screenshot({ path: 'error_screenshot.png', fullPage: true });
                console.log('📸 已保存错误截图: error_screenshot.png');
            } catch (screenshotError) {
                console.error('截图失败:', screenshotError.message);
            }
        }
    } finally {
        await browser.close();
        console.log('🔚 浏览器已关闭');
    }
}

// 运行测试
testUserManagement().catch(console.error); 