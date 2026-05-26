#!/usr/bin/env python3
"""
使用 Playwright 测试 Playground 问题
"""

import asyncio
from playwright.async_api import async_playwright
import sys


async def test_playground():
    """测试 Playground"""
    print("启动 Playwright 测试...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # headless=False 可以看到浏览器
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # 1. 测试访问首页
            print("\n[1] 测试访问首页...")
            response = await page.goto("http://127.0.0.1:5000", wait_until='domcontentloaded', timeout=10000)
            print(f"    状态码: {response.status}")
            
            if response.status != 200:
                print("    ❌ 首页访问失败")
                return False
            
            print("    ✅ 首页访问成功")
            
            # 等待页面加载
            await page.wait_for_selector('#editor', timeout=5000)
            print("    ✅ 编辑器加载完成")
            
            # 2. 测试输入代码
            print("\n[2] 测试输入代码...")
            await page.fill('#editor', '印 "你好，言语言！"。')
            editor_content = await page.input_value('#editor')
            print(f"    编辑器内容: {editor_content[:30]}...")
            
            # 3. 测试运行代码（这个步骤可能会卡住）
            print("\n[3] 测试运行代码...")
            print("    ⚠️  点击运行按钮...")
            
            # 点击运行按钮
            await page.click('button:has-text("运行代码")')
            
            # 等待输出，最多等15秒
            print("    ⏳ 等待执行结果（最多15秒）...")
            try:
                # 等待输出面板内容变化
                await page.wait_for_function(
                    """() => {
                        const output = document.getElementById('output');
                        const loading = document.getElementById('loading');
                        return output && output.innerText.includes('执行') || 
                               output.innerText.includes('完成') ||
                               output.innerText.includes('错误') ||
                               output.innerText.includes('你好');
                    }""",
                    timeout=15000
                )
                
                # 获取输出内容
                output_text = await page.inner_text('#output')
                print(f"    ✅ 执行完成，输出: {output_text[:100]}...")
                
            except Exception as e:
                print(f"    ❌ 执行超时或失败: {e}")
                
                # 尝试获取页面状态
                try:
                    output_text = await page.inner_text('#output')
                    loading_class = await page.get_attribute('#loading', 'class')
                    print(f"    当前输出: {output_text[:100]}...")
                    print(f"    Loading 状态: {loading_class}")
                except:
                    pass
                
                return False
            
            # 4. 测试多次执行
            print("\n[4] 测试多次执行...")
            for i in range(3):
                print(f"    第 {i+1} 次执行...")
                await page.click('button:has-text("运行代码")')
                await asyncio.sleep(2)  # 等待2秒
            
            print("    ✅ 多次执行完成")
            
            return True
            
        except Exception as e:
            print(f"\n❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False
            
        finally:
            await browser.close()


if __name__ == "__main__":
    result = asyncio.run(test_playground())
    sys.exit(0 if result else 1)
