"""
语法迁移工具：将 v1 语法转换为 v2 语法
用法：python yan/syntax_migrator.py <file> [--in-place]
      python yan/syntax_migrator.py <dir>  [--in-place]
"""

import re
import sys
from pathlib import Path


# 块开始模式：以这些关键字开头且行尾有 `：` 或 `:`
BLOCK_START_PATTERN = re.compile(
    r'^\s*(定|当|遍历|试|否则|否则当|捕获|如果|若|当满足)'
)


def is_standalone_period(line):
    """判断是否只有句号的独立行（块结束符）"""
    return re.match(r'^[\s　]*[。．]$', line.strip())


def is_block_start_line(line):
    """判断是否是代码块开始行（如 定 f = 函 x：）"""
    stripped = line.strip()
    # 行尾必须要有 ：或 :
    if not (stripped.endswith('：') or stripped.endswith(':')):
        return False
    # 检查是否以块开始关键字开头
    if BLOCK_START_PATTERN.match(stripped):
        return True
    # 定 某 = 函 x： 这种模式
    if re.match(r'^定\s+.+\s*=\s*函\s', stripped):
        return True
    return False


def migrate_content(content):
    """迁移代码内容：移除代码块结束句号"""
    lines = content.split('\n')
    result = []

    for line in lines:
        stripped = line.strip()
        
        # 情况1：独立句号行（块结束符）→ 完全删除
        if is_standalone_period(line):
            continue
        
        # 情况2：注释或空行 → 原样保留
        if not stripped or stripped.startswith('--') or stripped.startswith('注'):
            result.append(line)
            continue
        
        # 计算缩进
        indent = len(line) - len(stripped)
        
        # 情况3：缩进行（在代码块内）且不是块开始行 → 移除行尾句号
        if indent > 0 and not is_block_start_line(line):
            # 移除行尾句号
            if stripped.endswith('。') or stripped.endswith('．'):
                stripped = stripped[:-1]
                result.append(line[:indent] + stripped)
            else:
                result.append(line)
        else:
            # 顶层语句或块开始行：保留原样
            result.append(line)

    return '\n'.join(result)


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