#!/usr/bin/env python3
"""使用 Playwright 测试 Playground - 不等待网络空闲"""

import asyncio
from playwright.async_api import async_playwright

async def test_playground():
    """测试 Playground"""
    print("启动 Playwright...")
    
    async with async_playwright() as p:
        print("启动浏览器...")
        browser = await p.chromium.launch(headless=False)  # 显示浏览器窗口
        page = await browser.new_page()
        
        try:
            # 1. 访问首页
            print("\n[1] 访问 http://localhost:5000...")
            await page.goto("http://localhost:5000", wait_until='commit', timeout=15000)
            print("✅ 页面加载中...")
            
            # 等待页面元素出现
            await page.wait_for_selector('#editor', timeout=10000)
            print("✅ 编辑器加载完成")
            
            # 2. 输入代码
            print("\n[2] 输入代码...")
            await page.fill('#editor', '印 "你好，言语言！"。')
            print("✅ 代码已输入")
            
            # 3. 点击运行
            print("\n[3] 点击运行...")
            await page.click('button:has-text("运行代码")')
            print("✅ 已点击，等待结果...")
            
            # 等待输出变化
            await asyncio.sleep(3)
            
            # 4. 获取输出
            print("\n[4] 获取输出...")
            output = await page.inner_text('#output')
            print(f"输出内容:\n{output}")
            
            if "你好" in output or "Hello" in output:
                print("\n✅ 测试成功！")
                return True
            else:
                print("\n⚠️  输出未包含预期内容")
                return False
            
        except Exception as e:
            print(f"\n❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            input("\n按回车键关闭浏览器...")
            await browser.close()

if __name__ == "__main__":
    result = asyncio.run(test_playground())
    exit(0 if result else 1)
