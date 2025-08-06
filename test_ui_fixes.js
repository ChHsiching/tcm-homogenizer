const puppeteer = require('puppeteer');

async function testUIFixes() {
    console.log('🚀 开始测试UI修复效果...');
    
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
        
        // 8. 测试删除用户功能
        console.log('🗑️ 测试删除用户功能...');
        const deleteButtons = await page.$$('#users-table .btn-danger');
        if (deleteButtons.length > 0) {
            await deleteButtons[0].click();
            console.log('✅ 点击删除按钮');
            
            // 等待确认对话框出现
            await page.waitForSelector('#modal-overlay', { timeout: 5000 });
            console.log('✅ 确认对话框已显示');
            
            // 检查对话框内容
            const dialogText = await page.$eval('#modal-body', el => el.textContent);
            console.log('📝 对话框内容:', dialogText);
            
            // 点击取消按钮
            await page.click('#modal-cancel');
            console.log('✅ 点击取消按钮');
            
            // 等待对话框消失
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            // 再次点击删除按钮
            await deleteButtons[0].click();
            await page.waitForSelector('#modal-overlay', { timeout: 5000 });
            
            // 这次点击确认按钮
            await page.click('#modal-confirm');
            console.log('✅ 点击确认按钮');
            
            // 等待删除操作完成
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            // 检查通知消息
            const notifications = await page.$$('.notification');
            if (notifications.length > 0) {
                const notificationText = await page.evaluate(el => el.textContent, notifications[0]);
                console.log('📢 通知消息:', notificationText);
            }
        }
        
        // 9. 测试添加用户功能
        console.log('➕ 测试添加用户功能...');
        await page.click('#add-user-btn');
        await page.waitForSelector('#modal-overlay', { timeout: 5000 });
        
        // 填写用户信息
        await page.type('#new-username', 'UITestUser');
        await page.type('#new-password', '123456');
        
        // 点击确认按钮
        await page.click('#modal-confirm');
        console.log('✅ 点击确认按钮');
        
        // 等待添加操作完成
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // 检查通知消息
        const notifications2 = await page.$$('.notification');
        if (notifications2.length > 0) {
            const notificationText = await page.evaluate(el => el.textContent, notifications2[0]);
            console.log('📢 通知消息:', notificationText);
        }
        
        // 10. 截图保存
        await page.screenshot({ path: 'ui_fixes_test.png', fullPage: true });
        console.log('📸 已保存截图: ui_fixes_test.png');
        
    } catch (error) {
        console.error('❌ 测试失败:', error.message);
        
        // 保存错误截图
        if (page) {
            try {
                await page.screenshot({ path: 'ui_fixes_error.png', fullPage: true });
                console.log('📸 已保存错误截图: ui_fixes_error.png');
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
testUIFixes().catch(console.error); 