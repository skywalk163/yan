"""
言语言 Markdown 执行器
执行 .ymd 文档中的代码块，生成带结果的输出
"""

import sys
import io
from typing import List, Tuple, Optional
from md_parser import (
    MDDocument, MDNode, MDText, MDHeading, 
    MDCodeBlock, MDInlineCode, MDMath
)
from main import run, run_repl


class MDExecutor:
    """Markdown 执行器"""

    def __init__(self, debug: bool = False):
        self.debug = debug
        self.results: List[Tuple[str, str]] = []  # (代码, 结果)

    def execute(self, doc: MDDocument) -> str:
        """执行文档中的代码块，生成输出"""
        output = []
        code_block_idx = 0

        for node in doc.nodes:
            if isinstance(node, MDHeading):
                output.append(self._render_heading(node))

            elif isinstance(node, MDCodeBlock):
                rendered, result = self._render_code_block(node, code_block_idx)
                output.append(rendered)
                if result is not None:
                    self.results.append((node.code, str(result)))
                code_block_idx += 1

            elif isinstance(node, MDMath):
                output.append(self._render_math(node))

            elif isinstance(node, MDInlineCode):
                output.append(self._render_inline_code(node))

            elif isinstance(node, MDText):
                output.append(node.content)

        return ''.join(output)

    def _render_heading(self, node: MDHeading) -> str:
        """渲染标题"""
        return f"{'#' * node.level} {node.content}\n\n"

    def _render_code_block(self, node: MDCodeBlock, idx: int) -> Tuple[str, Optional[str]]:
        """渲染代码块，执行 yan 代码"""
        result = None

        if node.lang == 'yan':
            # 捕获 stdout
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            
            try:
                # 执行言语言代码
                return_value = run(node.code, debug=self.debug)
                captured_output = sys.stdout.getvalue()
            finally:
                sys.stdout = old_stdout
            
            # 结果优先使用返回值，否则使用捕获的输出
            if return_value is not None:
                result = return_value
            elif captured_output.strip():
                result = captured_output.strip()

        # 渲染代码块
        output = f"```{node.lang}\n{node.code}\n```\n"

        # 如果有执行结果，添加结果块
        if result is not None:
            output += f"\n**执行结果：**\n\n```\n{result}\n```\n\n"

        return output, result

    def _render_math(self, node: MDMath) -> str:
        """渲染数学公式"""
        if node.inline:
            return f"${node.expr}$"
        else:
            return f"$$\n{node.expr}\n$$\n\n"

    def _render_inline_code(self, node: MDInlineCode) -> str:
        """渲染内联代码"""
        return f"`{node.code}`"


def run_ymd(filename: str, output_file: Optional[str] = None, debug: bool = False) -> str:
    """运行 .ymd 文件
    
    Args:
        filename: 输入文件名
        output_file: 输出文件名（可选，默认打印到控制台）
        debug: 是否显示调试信息
    
    Returns:
        生成的 Markdown 内容
    """
    # 读取文件
    with open(filename, 'r', encoding='utf-8') as f:
        source = f.read()

    # 解析
    from md_parser import parse_markdown
    doc = parse_markdown(source)

    # 执行
    executor = MDExecutor(debug=debug)
    output = executor.execute(doc)

    # 输出
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"已生成: {output_file}")
    else:
        print(output)

    return output


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法: python md_executor.py <文件.ymd> [输出文件.md]")
        sys.exit(1)

    filename = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    debug = '--debug' in sys.argv

    run_ymd(filename, output_file, debug)
