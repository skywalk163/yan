"""
自举验证脚本 - 简化版
"""
import hashlib
import sys

def compare_files():
    """比较编译器1和编译器2"""
    with open('compiler1_from_c0.py', 'r', encoding='utf-8') as f:
        code1 = f.read()
    with open('compiler2_from_c1.py', 'r', encoding='utf-8') as f:
        code2 = f.read()
    
    hash1 = hashlib.md5(code1.encode()).hexdigest()
    hash2 = hashlib.md5(code2.encode()).hexdigest()
    
    print('=' * 60)
    print('自举验证结果')
    print('=' * 60)
    print(f'编译器1: {len(code1)} 字符')
    print(f'编译器2: {len(code2)} 字符')
    print(f'MD5 (编译器1): {hash1}')
    print(f'MD5 (编译器2): {hash2}')
    print()
    
    if code1 == code2:
        print('[SUCCESS] Bootstrap verification passed! Compiler1 and Compiler2 are identical')
        return True
    else:
        print('[FAILED] Bootstrap verification failed - Compiler1 and Compiler2 are different')
        print()
        print('差异分析:')
        print(f'  大小差异: {abs(len(code1) - len(code2))} 字符')
        print(f'  编译器1行数: {len(code1.splitlines())}')
        print(f'  编译器2行数: {len(code2.splitlines())}')
        
        # 显示前几行差异
        lines1 = code1.splitlines()
        lines2 = code2.splitlines()
        print()
        print('编译器1前10行:')
        for i, line in enumerate(lines1[:10], 1):
            print(f'  {i}: {line[:80]}')
        print()
        print('编译器2前10行:')
        for i, line in enumerate(lines2[:10], 1):
            print(f'  {i}: {line[:80]}')
        
        return False

if __name__ == '__main__':
    success = compare_files()
    sys.exit(0 if success else 1)
