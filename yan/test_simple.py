#!/usr/bin/env python3
"""最简单的 Playwright 测试"""

import asyncio
from playwright.async_api import async_playwright

async def simple_test():
    print("启动 Playwright...")
    
    async with async_playwright() as p:
        print("启动浏览器...")
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            print("尝试访问 localhost:5000...")
            # 不等待 load 事件
            await page.goto("http://127.0.0.1:5000", wait_until='commit', timeout=15000)
            print("✅ 页面已加载")
            
            # 获取标题
            title = await page.title()
            print(f"页面标题: {title}")
            
            # 获取 HTML 内容的前200个字符
            html = await page.content()
            print(f"HTML 长度: {len(html)}")
            print(f"HTML 前200字符: {html[:200]}")
            
            return True
            
        except Exception as e:
            print(f"❌ 错误: {e}")
            import traceback
            traceback.print_exc()
            return False
            
        finally:
            await browser.close()

if __name__ == "__main__":
    result = asyncio.run(simple_test())
    exit(0 if result else 1)
