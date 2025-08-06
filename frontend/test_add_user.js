const puppeteer = require('puppeteer');

async function testAddUser() {
    console.log('🚀 开始测试添加用户功能...');
    
    const browser = await puppeteer.launch({
        headless: false,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    try {
        const page = await browser.newPage();
        
        // 设置视口
        await page.setViewport({ width: 1200, height: 800 });
        
        console.log('📄 访问前端页面...');
        await page.goto('http://127.0.0.1:3000/', { waitUntil: 'networkidle0' });
        
        // 等待页面加载完成
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        console.log('🔐 开始登录...');
        
        // 等待登录表单加载
        await page.waitForSelector('#username');
        await page.waitForSelector('#password');
        await page.waitForSelector('#login-btn');
        
        // 填写登录表单
        await page.type('#username', 'admin');
        await page.type('#password', 'admin123');
        
        // 点击登录按钮
        await page.click('#login-btn');
        
        // 等待登录完成
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        console.log('👥 切换到用户管理页面...');
        
        // 等待用户管理标签出现
        await page.waitForSelector('[data-tab="user-management"]');
        
        // 点击用户管理标签
        await page.click('[data-tab="user-management"]');
        
        // 等待页面切换完成
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        console.log('➕ 测试添加用户功能...');
        
        // 等待添加用户按钮出现
        await page.waitForSelector('#add-user-btn');
        
        // 点击添加用户按钮
        await page.click('#add-user-btn');
        
        // 等待模态框出现
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        console.log('📝 填写用户信息...');
        
        // 填写新用户信息
        await page.type('#new-username', '王五');
        await page.type('#new-password', 'user123');
        
        // 选择角色
        await page.select('#new-role', 'user');
        
        console.log('✅ 点击确认按钮...');
        
        // 点击确认按钮
        await page.click('#modal-confirm');
        
        // 等待操作完成
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        console.log('🔍 检查用户列表是否更新...');
        
        // 获取更新后的用户表格内容
        const updatedUsersTableContent = await page.evaluate(() => {
            const usersTable = document.getElementById('users-table');
            if (usersTable) {
                return usersTable.innerHTML;
            }
            return '找不到用户表格元素';
        });
        
        console.log('📊 更新后的用户表格内容:');
        console.log(updatedUsersTableContent);
        
        // 检查是否包含新添加的用户
        const hasWangwu = updatedUsersTableContent.includes('王五');
        const hasZhangsan = updatedUsersTableContent.includes('张三');
        const hasLisi = updatedUsersTableContent.includes('李四');
        
        console.log('\n🔍 检查结果:');
        console.log(`包含王五: ${hasWangwu}`);
        console.log(`包含张三: ${hasZhangsan}`);
        console.log(`包含李四: ${hasLisi}`);
        
        // 保存页面内容到文件
        const fs = require('fs');
        const fullPageContent = await page.content();
        fs.writeFileSync('debug_add_user.html', fullPageContent);
        console.log('💾 页面内容已保存到 debug_add_user.html');
        
        // 等待一段时间以便观察
        await new Promise(resolve => setTimeout(resolve, 5000));
        
    } catch (error) {
        console.error('❌ 测试失败:', error);
    } finally {
        await browser.close();
        console.log('✅ 测试完成');
    }
}

// 运行测试
testAddUser().catch(console.error); 