#!/usr/bin/env python3
"""
Playwright 测试脚本 - 测试言语言 Playground 的 Python 和 WebAssembly 模式
"""

import asyncio
from playwright.async_api import async_playwright
import sys

async def test_playground():
    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # 访问 Playground
            print("🚀 访问 Playground...")
            await page.goto("http://localhost:5000")
            await page.wait_for_selector('#editor')
            print("✅ 页面加载成功")
            
            # 获取初始代码
            initial_code = await page.locator('#editor').input_value()
            print(f"📝 初始代码:\n{initial_code[:100]}...")
            
            # 测试 Python 模式
            print("\n🔵 测试 Python 模式...")
            await page.locator('#modePython').click()
            await page.wait_for_timeout(500)
            
            # 输入测试代码
            test_code = '''印 "Hello, Python!"。
印 加 1 2。'''
            await page.locator('#editor').fill(test_code)
            
            # 点击运行
            await page.locator('#runBtn').click()
            await page.wait_for_timeout(3000)
            
            # 检查输出
            output = await page.locator('#output').inner_text()
            print(f"📊 Python 输出:\n{output}")
            
            if "Hello, Python!" in output and "3" in output:
                print("✅ Python 模式测试通过！")
            else:
                print("❌ Python 模式测试失败！")
                await browser.close()
                return False
            
            # 清理之前的输出
            await page.evaluate('document.getElementById("output").innerHTML = ""')
            await page.wait_for_timeout(300)
            
            # 测试 WebAssembly 模式
            print("\n⚡ 测试 WebAssembly 模式...")
            await page.locator('#modeWasm').click()
            await page.wait_for_timeout(500)
            
            # 输入测试代码
            wasm_test_code = '''印 "Hello, WASM!"。
定 x = 42。
印数 x。'''
            await page.locator('#editor').fill(wasm_test_code)
            
            # 点击编译运行
            await page.locator('#runBtn').click()
            await page.wait_for_timeout(3000)
            
            # 检查输出
            output = await page.locator('#output').inner_text()
            print(f"📊 WASM 输出:\n{output}")
            
            if "Hello, WASM!" in output and "42" in output:
                print("✅ WebAssembly 模式测试通过！")
            else:
                print("❌ WebAssembly 模式测试失败！")
                await browser.close()
                return False
            
            print("\n🎉 所有测试通过！")
            await browser.close()
            return True
            
        except Exception as e:
            print(f"❌ 测试过程中发生错误: {e}")
            import traceback
            traceback.print_exc()
            await browser.close()
            return False

if __name__ == "__main__":
    print("=" * 60)
    print("    言语言 Playground Playwright 测试")
    print("=" * 60)
    
    # 检查 Playwright 是否安装
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("⚠ Playwright 未安装，正在安装...")
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "playwright"], check=True)
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
        print("✅ Playwright 安装完成")
    
    # 运行测试
    success = asyncio.run(test_playground())
    
    if success:
        print("\n✅ 测试全部通过！")
        sys.exit(0)
    else:
        print("\n❌ 测试失败！")
        sys.exit(1)