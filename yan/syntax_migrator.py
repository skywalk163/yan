"""
语法迁移工具：将 v1 语法转换为 v2 语法
用法：python yan/syntax_migrator.py <file> [--in-place]
"""

import re
import sys
from pathlib import Path


# 控制结构关键字，进入代码块
BLOCK_STARTS = ['当', '遍历', '当满足', '定', '试', '否则', '否则当', '捕获']


def migrate_file(filepath, in_place=False):
    """迁移单个文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    migrated = migrate_content(content)
    
    if in_place:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(migrated)
        print(f"已迁移: {filepath}")
    else:
        print(migrated)


def migrate_content(content):
    """迁移代码内容"""
    lines = content.split('\n')
    result = []
    
    # 追踪是否在代码块内
    in_block = False
    # 缩进栈，用于追踪嵌套级别
    indent_stack = []
    # 上一行的缩进级别
    prev_level = 0
    
    for line in lines:
        stripped = line.strip()
        indent = len(line) - len(stripped)
        current_level = indent // 2  # 假设 2 空格 = 1 级
        
        # 判断当前行是否结束代码块
        if current_level < prev_level:
            # 缩进减少，结束代码块
            in_block = False
            # 出栈直到回到当前级别
            while indent_stack and indent_stack[-1] >= current_level:
                indent_stack.pop()
        
        # 清理句号
        processed = remove_period(stripped, in_block, current_level, indent_stack)
        
        # 重建行（保留原始缩进）
        if processed:
            result.append(line[:len(line) - len(stripped.lstrip())] + processed)
        else:
            result.append('')
        
        # 判断当前行是否开始新的代码块
        if stripped and current_level > prev_level:
            # 进入更深缩进，开始代码块
            indent_stack.append(current_level)
            in_block = True
        elif stripped and current_level == prev_level and prev_level > 0:
            # 同级缩进且在代码块内，继续
            pass
        elif stripped:
            # 顶层语句，可能结束代码块
            if current_level == 0:
                in_block = False
                indent_stack = []
        
        # 更新上一级缩进级别
        if stripped:
            prev_level = current_level
    
    return '\n'.join(result)


def remove_period(line, in_block, current_level, indent_stack):
    """移除句号"""
    stripped = line.strip()
    
    # 情况1：独立句号行（只有句号）
    if stripped == '。' or stripped == '．':
        return ''
    
    # 情况2：只有空白和句号的行
    if re.match(r'^[\s　]*[。．]$', stripped):
        return ''
    
    # 情况3：如果在代码块内，移除行尾句号
    if in_block and (stripped.endswith('。') or stripped.endswith('．')):
        # 检查是否是块开始语句（定 x = 函: 这种）
        if is_block_start(stripped):
            # 块开始语句保留句号作为结束标记
            return stripped
        # 否则移除句号
        return stripped[:-1]
    
    return stripped


def is_block_start(line):
    """判断这行是否是代码块的开始（如 定 f = 函:）"""
    stripped = line.strip()
    
    # 定 某 = 函: 这种模式
    if re.match(r'^定\s+.+\s*=\s*函\s*[:：]', stripped):
        return True
    
    # 当 xxx: 这种模式
    if re.match(r'^当\s+.+[:：]', stripped):
        return True
    
    # 遍历 x 于 y: 这种模式
    if re.match(r'^遍历\s+.+[:：]', stripped):
        return True
    
    return False


def migrate_directory(dirpath, pattern='*.yan', in_place=False):
    """迁移目录下所有匹配的文件"""
    path = Path(dirpath)
    
    if not path.is_dir():
        print(f"错误: {dirpath} 不是有效的目录")
        return
    
    files = list(path.glob(pattern))
    
    if not files:
        print(f"在 {dirpath} 中没有找到匹配 {pattern} 的文件")
        return
    
    print(f"找到 {len(files)} 个文件需要迁移")
    
    for filepath in files:
        migrate_file(str(filepath), in_place)


def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  python yan/syntax_migrator.py <file>              # 打印迁移结果")
        print("  python yan/syntax_migrator.py <file> --in-place   # 直接迁移文件")
        print("  python yan/syntax_migrator.py <dir>  --in-place   # 迁移目录下所有 .yan 文件")
        sys.exit(1)
    
    target = sys.argv[1]
    in_place = '--in-place' in sys.argv
    
    if Path(target).is_dir():
        migrate_directory(target, '*.yan', in_place)
    else:
        migrate_file(target, in_place)


if __name__ == '__main__':
    main()
