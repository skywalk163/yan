"""
言语言自举编译管线 (Bootstrap Pipeline)

自举过程：
  编译器0 (Python) = main.py + lexer.py + parser.py + codegen.py + runtime.py
  编译器1源码 = compiler.yan (用言语言编写的编译器)
  编译器1 = 编译器0(编译器1源码) → Python代码
  编译器2 = 编译器1(编译器1源码) → Python代码
  自举验证 = 编译器1 == 编译器2 (输出相同)

使用方式：
  python bootstrap.py          # 执行完整自举
  python bootstrap.py --test   # 运行测试套件
  python bootstrap.py --verify # 验证自举结果
"""
import sys
import os
import subprocess
import tempfile
import hashlib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexer import Lexer
from parser import Parser
from codegen import PythonCodeGen

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SELFHOST_DIR = BASE_DIR
COMPILER_YAN = os.path.join(BASE_DIR, 'compiler.yan')
COMPILER1_PY = os.path.join(BASE_DIR, 'compiler1_from_c0.py')
COMPILER2_PY = os.path.join(BASE_DIR, 'compiler2_from_c1.py')
TEST_SUITE = os.path.join(BASE_DIR, 'test_suite.yan')

def ensure_selfhost_dir():
    """确保 selfhost 目录存在"""
    os.makedirs(SELFHOST_DIR, exist_ok=True)

def compile_yan_to_python(yan_file: str, output_file: str) -> bool:
    """编译 Yan 文件为 Python 代码"""
    print(f'编译: {yan_file}')
    try:
        with open(yan_file, 'r', encoding='utf-8') as f:
            source = f.read()

        # 使用编译器0编译
        lexer = Lexer()
        tokens = lexer.tokenize(source)
        parser = Parser()
        ast = parser.parse(tokens)
        gen = PythonCodeGen()
        python_code = gen.generate(ast)

        if python_code:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(python_code)
            print(f'  → 已生成: {output_file} ({len(python_code)} 字符)')
            return True
        else:
            print(f'  ❌ 编译结果为空')
            return False
    except Exception as e:
        print(f'  ❌ 编译失败: {e}')
        import traceback
        traceback.print_exc()
        return False

def compile_with_compiler1(yan_file: str, compiler1_py: str, output_file: str) -> bool:
    """使用编译器1编译 Yan 文件"""
    print(f'使用编译器1编译: {yan_file}')
    try:
        # 读取编译器1的代码
        with open(compiler1_py, 'r', encoding='utf-8') as f:
            compiler_code = f.read()
        
        # 读取 Yan 源文件
        with open(yan_file, 'r', encoding='utf-8') as f:
            yan_source = f.read()
        
        # 创建执行环境
        exec_globals = {'__builtins__': __builtins__}
        
        # 执行编译器1代码并编译
        exec_code = f"""
{compiler_code}

# 编译输入的 Yan 源
RESULT = compile({repr(yan_source)})[0]
"""
        exec(exec_code, exec_globals)
        result = exec_globals.get('RESULT')
        
        if result:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result)
            print(f'  → 已生成: {output_file} ({len(result)} 字符)')
            return True
        else:
            print(f'  ❌ 编译结果为空')
            return False
    except Exception as e:
        print(f'  ❌ 编译失败: {e}')
        import traceback
        traceback.print_exc()
        return False

def verify_bootstrap():
    """验证自举：编译器1和编译器2输出是否一致"""
    print('\n' + '=' * 60)
    print('自举验证')
    print('=' * 60)
    
    if not os.path.exists(COMPILER1_PY) or not os.path.exists(COMPILER2_PY):
        print('❌ 编译器1或编译器2不存在')
        return False
    
    with open(COMPILER1_PY, 'r', encoding='utf-8') as f:
        code1 = f.read()
    with open(COMPILER2_PY, 'r', encoding='utf-8') as f:
        code2 = f.read()
    
    hash1 = hashlib.md5(code1.encode()).hexdigest()
    hash2 = hashlib.md5(code2.encode()).hexdigest()
    
    if code1 == code2:
        print(f'✓ 自举验证通过！')
        print(f'  编译器1: {len(code1)} 字符 (MD5: {hash1})')
        print(f'  编译器2: {len(code2)} 字符 (MD5: {hash2})')
        return True
    else:
        print(f'❌ 自举验证失败 - 输出不同')
        print(f'  编译器1: {len(code1)} 字符 (MD5: {hash1})')
        print(f'  编译器2: {len(code2)} 字符 (MD5: {hash2})')
        
        # 显示差异
        import difflib
        diff = difflib.unified_diff(
            code1.splitlines(True), code2.splitlines(True),
            fromfile='compiler1', tofile='compiler2'
        )
        print('\n差异:')
        for line in list(diff)[:30]:
            print(f'  {line}', end='')
        return False

def run_test_suite():
    """运行测试套件"""
    print('\n' + '=' * 60)
    print('运行测试套件')
    print('=' * 60)
    
    if not os.path.exists(TEST_SUITE):
        print(f'❌ 测试套件不存在: {TEST_SUITE}')
        return False
    
    if not os.path.exists(COMPILER1_PY):
        print('❌ 编译器1不存在，先执行自举')
        return False
    
    try:
        with open(COMPILER1_PY, 'r', encoding='utf-8') as f:
            compiler_code = f.read()
        
        with open(TEST_SUITE, 'r', encoding='utf-8') as f:
            test_source = f.read()
        
        exec_globals = {'__builtins__': __builtins__}
        
        exec_code = f"""
{compiler_code}

# 编译测试套件
test_code, errors = compile({repr(test_source)})

# 执行测试
exec(test_code, {{}}, {{}})
"""
        exec(exec_code, exec_globals)
        print('✓ 测试套件执行完成')
        return True
    except Exception as e:
        print(f'❌ 测试失败: {e}')
        import traceback
        traceback.print_exc()
        return False

def main():
    ensure_selfhost_dir()
    
    # 解析命令行参数
    args = sys.argv[1:]
    
    if '--test' in args:
        return 0 if run_test_suite() else 1
    
    if '--verify' in args:
        return 0 if verify_bootstrap() else 1
    
    # 检查编译器源文件是否存在
    if not os.path.exists(COMPILER_YAN):
        print(f'❌ 编译器源文件不存在: {COMPILER_YAN}')
        print('请先创建 compiler.yan')
        return 1
    
    # 阶段1: 编译器0 → 编译器1
    print('\n' + '=' * 60)
    print('阶段1: 编译器0 (Python) → 编译 compiler.yan → 编译器1')
    print('=' * 60)
    ok1 = compile_yan_to_python(COMPILER_YAN, COMPILER1_PY)
    if not ok1:
        print('❌ 阶段1失败')
        return 1
    
    # 阶段2: 编译器1 → 编译器2 (自举验证)
    print('\n' + '=' * 60)
    print('阶段2: 编译器1 → 编译 compiler.yan → 编译器2')
    print('=' * 60)
    ok2 = compile_with_compiler1(COMPILER_YAN, COMPILER1_PY, COMPILER2_PY)
    
    # 验证
    verify_bootstrap()
    
    # 运行测试套件
    run_test_suite()
    
    print('\n' + '=' * 60)
    print('完成')
    print('=' * 60)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
