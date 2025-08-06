const puppeteer = require('puppeteer');

async function testUserManagement() {
    console.log('🚀 开始Puppeteer用户管理测试...');
    
    const browser = await puppeteer.launch({
        headless: false, // 显示浏览器窗口
        slowMo: 1000, // 放慢操作速度，便于观察
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    try {
        const page = await browser.newPage();
        
        // 设置视口大小
        await page.setViewport({ width: 1280, height: 720 });
        
        console.log('📱 打开前端页面...');
        await page.goto('http://127.0.0.1:3000/', { waitUntil: 'networkidle0' });
        
        // 等待页面加载
        await page.waitForTimeout(2000);
        
        // 检查是否在登录页面
        const loginForm = await page.$('#login-form');
        if (loginForm) {
            console.log('✅ 检测到登录表单，开始登录...');
            
            // 填写登录表单
            await page.type('#username', 'admin');
            await page.type('#password', 'admin123');
            
            // 点击登录按钮
            await page.click('#login-btn');
            
            // 等待登录完成
            await page.waitForTimeout(3000);
            
            // 检查登录是否成功
            const userInfo = await page.$('.user-info');
            if (userInfo) {
                console.log('✅ 登录成功，用户信息显示正常');
            } else {
                console.log('❌ 登录失败，未找到用户信息');
                return;
            }
        } else {
            console.log('⚠️ 未检测到登录表单，可能已经登录');
        }
        
        // 等待导航菜单加载
        await page.waitForTimeout(1000);
        
        // 点击用户管理标签
        console.log('👥 点击用户管理标签...');
        const userManagementTab = await page.$('[data-tab="user-management"]');
        if (userManagementTab) {
            await userManagementTab.click();
            await page.waitForTimeout(2000);
        } else {
            console.log('❌ 未找到用户管理标签');
            return;
        }
        
        // 检查用户管理页面是否显示
        const userManagementContent = await page.$('#user-management');
        if (userManagementContent) {
            console.log('✅ 用户管理页面显示正常');
        } else {
            console.log('❌ 用户管理页面未显示');
            return;
        }
        
        // 检查用户列表
        const usersTable = await page.$('#users-table');
        if (usersTable) {
            console.log('✅ 用户表格容器存在');
            
            // 等待用户数据加载
            await page.waitForTimeout(2000);
            
            // 检查是否有用户数据
            const tableContent = await page.$eval('#users-table', el => el.innerHTML);
            console.log('📋 用户表格内容:', tableContent.substring(0, 200) + '...');
            
            if (tableContent.includes('table') || tableContent.includes('用户')) {
                console.log('✅ 用户数据加载正常');
            } else {
                console.log('❌ 用户数据未加载');
            }
        } else {
            console.log('❌ 用户表格容器不存在');
        }
        
        // 测试添加用户功能
        console.log('➕ 测试添加用户功能...');
        const addUserBtn = await page.$('#add-user-btn');
        if (addUserBtn) {
            console.log('✅ 找到添加用户按钮');
            await addUserBtn.click();
            await page.waitForTimeout(2000);
            
            // 检查是否出现模态框
            const modal = await page.$('#modal-overlay');
            if (modal) {
                console.log('✅ 添加用户模态框显示正常');
                
                // 填写用户信息
                await page.type('#new-username', 'testuser');
                await page.type('#new-password', 'testpass123');
                
                // 选择角色
                await page.select('#new-role', 'user');
                
                // 点击确认按钮
                const confirmBtn = await page.$('#modal-confirm');
                if (confirmBtn) {
                    console.log('✅ 找到确认按钮，点击创建用户...');
                    await confirmBtn.click();
                    await page.waitForTimeout(3000);
                    
                    // 检查是否有通知消息
                    const notifications = await page.$$('.notification');
                    if (notifications.length > 0) {
                        const notificationText = await page.$eval('.notification', el => el.textContent);
                        console.log('📢 通知消息:', notificationText);
                        
                        if (notificationText.includes('成功') || notificationText.includes('创建')) {
                            console.log('✅ 用户创建成功');
                        } else if (notificationText.includes('权限') || notificationText.includes('不足')) {
                            console.log('❌ 权限不足，无法创建用户');
                        } else {
                            console.log('⚠️ 未知的创建结果:', notificationText);
                        }
                    } else {
                        console.log('⚠️ 未找到通知消息');
                    }
                } else {
                    console.log('❌ 未找到确认按钮');
                }
            } else {
                console.log('❌ 添加用户模态框未显示');
            }
        } else {
            console.log('❌ 未找到添加用户按钮');
        }
        
        // 等待一段时间观察结果
        console.log('⏳ 等待5秒观察最终结果...');
        await page.waitForTimeout(5000);
        
        // 截图保存结果
        await page.screenshot({ path: 'user_management_test_result.png' });
        console.log('📸 已保存测试结果截图: user_management_test_result.png');
        
    } catch (error) {
        console.error('❌ 测试过程中出现错误:', error);
        await page.screenshot({ path: 'error_screenshot.png' });
        console.log('📸 已保存错误截图: error_screenshot.png');
    } finally {
        await browser.close();
        console.log('🔚 测试完成，浏览器已关闭');
    }
}

// 检查Puppeteer是否可用
async function checkPuppeteer() {
    try {
        require('puppeteer');
        console.log('✅ Puppeteer可用');
        return true;
    } catch (error) {
        console.log('❌ Puppeteer不可用，需要安装: npm install puppeteer');
        return false;
    }
}

// 主函数
async function main() {
    console.log('🔍 检查环境...');
    
    if (!await checkPuppeteer()) {
        console.log('请先安装Puppeteer: npm install puppeteer');
        return;
    }
    
    await testUserManagement();
}

main().catch(console.error); 