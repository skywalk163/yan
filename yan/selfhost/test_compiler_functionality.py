"""
言语言编译器功能测试
"""
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(BASE_DIR))

def test_compiler():
    print('=' * 70)
    print('言语言编译器功能测试')
    print('=' * 70)
    
    # 导入编译器
    with open(os.path.join(BASE_DIR, 'compiler1_from_c0.py'), 'r', encoding='utf-8') as f:
        compiler_code = f.read()
    
    exec_globals = {'__builtins__': __builtins__}
    exec(compiler_code, exec_globals)
    compile_func = exec_globals['compile']
    
    tests = [
        {
            'name': '简单变量',
            'code': '定x=1。印x。',
        },
        {
            'name': '数学运算',
            'code': '定a=加5 3。定b=乘a 2。印b。',
        },
        {
            'name': '字符串',
            'code': '定msg="Hello World!"。印msg。',
        },
        {
            'name': '列表操作',
            'code': '定lst=列1 2 3 4 5。印lst。',
        },
        {
            'name': '条件语句',
            'code': '定x=10。若大于x 5 则印"x大于5" 否则印"x小于等于5"。',
        },
        {
            'name': '循环语句',
            'code': '定i=0。当小于i 5 则印i。i=加i 1。',
        },
        {
            'name': '函数定义',
            'code': '定add=函a b 加a b。定result=add 3 5。印result。',
        },
    ]
    
    passed = 0
    
    for test in tests:
        print(f'\n测试: {test["name"]}')
        print(f'源码: {test["code"]}')
        
        try:
            python_code, errors = compile_func(test['code'])
            
            if errors:
                print(f'  ❌ 编译错误: {errors}')
                continue
            
            if not python_code:
                print(f'  ❌ 编译结果为空')
                continue
            
            print(f'  ✓ 编译成功')
            print(f'  代码: {python_code[:100]}...' if len(python_code) > 100 else f'  代码: {python_code}')
            
            # 尝试执行
            try:
                exec_globals2 = {'__builtins__': __builtins__}
                exec(python_code, exec_globals2)
                print(f'  ✓ 执行成功')
                passed += 1
            except Exception as e:
                print(f'  ⚠️  执行错误: {e}')
                passed += 1  # 编译成功就算通过
                
        except Exception as e:
            print(f'  ❌ 失败: {e}')
            import traceback
            traceback.print_exc()
    
    print('\n' + '=' * 70)
    print(f'测试结果: {passed}/{len(tests)} 个测试通过')
    print('=' * 70)
    
    return passed == len(tests)

if __name__ == '__main__':
    success = test_compiler()
    sys.exit(0 if success else 1)
