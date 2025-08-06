const puppeteer = require('puppeteer');

async function testUserManagement() {
    console.log('🚀 开始Puppeteer测试...');
    
    const browser = await puppeteer.launch({
        headless: false, // 显示浏览器窗口，方便调试
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
        
        console.log('🔍 获取用户管理页面内容...');
        
        // 获取用户表格内容
        const usersTableContent = await page.evaluate(() => {
            const usersTable = document.getElementById('users-table');
            if (usersTable) {
                return usersTable.innerHTML;
            }
            return '找不到用户表格元素';
        });
        
        console.log('📊 用户表格内容:');
        console.log(usersTableContent);
        
        // 检查是否包含张三、李四
        const hasZhangsan = usersTableContent.includes('张三');
        const hasLisi = usersTableContent.includes('李四');
        const hasNoUsers = usersTableContent.includes('暂无用户');
        const hasLoading = usersTableContent.includes('加载中');
        
        console.log('\n🔍 检查结果:');
        console.log(`包含张三: ${hasZhangsan}`);
        console.log(`包含李四: ${hasLisi}`);
        console.log(`包含暂无用户: ${hasNoUsers}`);
        console.log(`包含加载中: ${hasLoading}`);
        
        // 获取页面完整HTML用于调试
        const fullPageContent = await page.content();
        
        // 保存页面内容到文件
        const fs = require('fs');
        fs.writeFileSync('debug_page.html', fullPageContent);
        console.log('💾 页面内容已保存到 debug_page.html');
        
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
testUserManagement().catch(console.error); 