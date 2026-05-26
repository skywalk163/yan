#!/usr/bin/env python3
"""
言语言 API 文档自动生成器
"""

import os
import re
import ast
from typing import Dict, List, Tuple, Optional

class DocGenerator:
    """API 文档生成器"""
    
    def __init__(self, project_root: str = '.'):
        self.project_root = project_root
        self.modules = []
        
    def extract_docstrings(self, file_path: str) -> List[Dict]:
        """从文件中提取文档字符串"""
        docs = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        try:
            tree = ast.parse(content)
        except SyntaxError:
            print(f"警告：无法解析 {file_path}")
            return docs
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                docstring = ast.get_docstring(node)
                if docstring:
                    params = []
                    for arg in node.args.args:
                        params.append(arg.arg)
                    
                    docs.append({
                        'type': 'function',
                        'name': node.name,
                        'params': params,
                        'docstring': docstring.strip(),
                        'line': node.lineno
                    })
            
            elif isinstance(node, ast.ClassDef):
                docstring = ast.get_docstring(node)
                if docstring:
                    docs.append({
                        'type': 'class',
                        'name': node.name,
                        'docstring': docstring.strip(),
                        'line': node.lineno,
                        'methods': []
                    })
                
                # 提取类方法
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        method_doc = ast.get_docstring(item)
                        method_params = []
                        for arg in item.args.args[1:]:  # 跳过 self
                            method_params.append(arg.arg)
                        
                        if docs and docs[-1]['name'] == node.name:
                            docs[-1]['methods'].append({
                                'name': item.name,
                                'params': method_params,
                                'docstring': method_doc.strip() if method_doc else '',
                                'line': item.lineno
                            })
        
        return docs
    
    def generate_md_doc(self, module_name: str, docs: List[Dict]) -> str:
        """生成 Markdown 格式的文档"""
        lines = []
        
        lines.append(f"# {module_name} 模块 API 文档")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        for doc in docs:
            if doc['type'] == 'class':
                lines.append(f"## 类: `{doc['name']}`")
                lines.append("")
                lines.append(f"**行号**: {doc['line']}")
                lines.append("")
                lines.append("### 描述")
                lines.append("")
                for line in doc['docstring'].split('\n'):
                    lines.append(f"> {line}")
                lines.append("")
                
                if doc['methods']:
                    lines.append("### 方法")
                    lines.append("")
                    
                    for method in doc['methods']:
                        params = ', '.join(method['params'])
                        lines.append(f"#### `{method['name']}({params})`")
                        lines.append("")
                        lines.append(f"**行号**: {method['line']}")
                        lines.append("")
                        if method['docstring']:
                            for line in method['docstring'].split('\n'):
                                lines.append(f"> {line}")
                        lines.append("")
            
            elif doc['type'] == 'function':
                params = ', '.join(doc['params'])
                lines.append(f"## 函数: `{doc['name']}({params})`")
                lines.append("")
                lines.append(f"**行号**: {doc['line']}")
                lines.append("")
                lines.append("### 描述")
                lines.append("")
                for line in doc['docstring'].split('\n'):
                    lines.append(f"> {line}")
                lines.append("")
        
        return '\n'.join(lines)
    
    def generate_all_docs(self):
        """生成所有模块的文档"""
        modules = [
            ('lexer.py', '词法分析器'),
            ('parser.py', '语法分析器'),
            ('codegen.py', 'Python 代码生成器'),
            ('codegen_js.py', 'JavaScript 代码生成器'),
            ('runtime.py', '运行时系统'),
            ('optimizer/optimizer.py', '优化器'),
            ('optimizer/strategy.py', '优化策略'),
            ('module_system.py', '模块系统'),
        ]
        
        output_dir = os.path.join(self.project_root, 'docs/api')
        os.makedirs(output_dir, exist_ok=True)
        
        for file_path, module_name in modules:
            full_path = os.path.join(self.project_root, file_path)
            if os.path.exists(full_path):
                docs = self.extract_docstrings(full_path)
                if docs:
                    md_content = self.generate_md_doc(module_name, docs)
                    output_file = os.path.join(output_dir, f"{os.path.basename(file_path).replace('.py', '')}.md")
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(md_content)
                    print(f"已生成文档: {output_file}")
                else:
                    print(f"警告: {file_path} 中没有找到文档字符串")
            else:
                print(f"警告: 文件不存在: {file_path}")
    
    def generate_index(self):
        """生成文档索引页"""
        index_content = """# 言语言 API 文档

---

## 目录

### 核心模块

- [词法分析器](api/lexer.md)
- [语法分析器](api/parser.md)
- [Python 代码生成器](api/codegen.md)
- [JavaScript 代码生成器](api/codegen_js.md)
- [运行时系统](api/runtime.md)

### 优化器模块

- [优化器](api/optimizer.md)
- [优化策略](api/strategy.md)

### 扩展模块

- [模块系统](api/module_system.md)

---

**文档版本**: v1.0  
**生成日期**: 自动生成  
**项目**: 言语言 (Yán)
"""
        
        output_file = os.path.join(self.project_root, 'docs/api/index.md')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(index_content)
        print(f"已生成文档索引: {output_file}")


if __name__ == '__main__':
    generator = DocGenerator(os.path.dirname(os.path.dirname(__file__)))
    generator.generate_all_docs()
    generator.generate_index()
    print("\nAPI 文档生成完成！")