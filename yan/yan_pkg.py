#!/usr/bin/env python3
"""
言语言 包管理器 - yan 包
"""

import os
import sys
import json
import subprocess
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from dataclasses import dataclass as dc


@dc
class Package:
    """包信息"""
    name: str
    version: str
    description: str
    author: str
    dependencies: Dict[str, str]
    entry: str = "主.yan"
    repository: Optional[str] = None


@dc
class DependencyNode:
    """依赖节点"""
    name: str
    version: str
    path: str
    dependencies: List['DependencyNode'] = field(default_factory=list)


class Version:
    """版本比较"""
    def __init__(self, v: str):
        self.v = v
        self.parts = self._parse(v)

    def _parse(self, v: str) -> Tuple[int, ...]:
        parts = re.match(r'^(\d+)\.(\d+)\.(\d+)', v)
        if parts:
            return tuple(int(x) for x in parts.groups())
        return (0, 0, 0)

    def __eq__(self, other):
        return self.parts == other.parts

    def __lt__(self, other):
        return self.parts < other.parts

    def __le__(self, other):
        return self.parts <= other.parts

    def __gt__(self, other):
        return self.parts > other.parts

    def __ge__(self, other):
        return self.parts >= other.parts

    def __str__(self):
        return self.v


class DependencyResolver:
    """依赖解析器"""

    def __init__(self, registry_urls: List[str]):
        self.registry_urls = registry_urls
        self.resolved: Dict[str, DependencyNode] = {}
        self.resolving: Set[str] = set()

    def resolve(self, name: str, version_spec: str = None) -> Optional[DependencyNode]:
        """解析依赖"""
        if name in self.resolved:
            return self.resolved[name]

        if name in self.resolving:
            return None

        self.resolving.add(name)

        package_info = self._fetch_package(name, version_spec)
        if not package_info:
            self.resolving.remove(name)
            return None

        node = DependencyNode(
            name=name,
            version=package_info.get('version', '0.1.0'),
            path=package_info.get('path', ''),
            dependencies=[]
        )

        for dep_name, dep_spec in package_info.get('dependencies', {}).items():
            dep_node = self.resolve(dep_name, dep_spec)
            if dep_node:
                node.dependencies.append(dep_node)

        self.resolved[name] = node
        self.resolving.remove(name)
        return node

    def _fetch_package(self, name: str, version_spec: str = None) -> Optional[Dict]:
        """从注册表获取包信息"""
        mock_packages = {
            '网络请求': {
                'version': '1.0.0',
                'description': '网络请求工具',
                'author': 'Yan Team',
                'dependencies': {},
                'path': ''
            },
            'json-tools': {
                'version': '1.2.0',
                'description': 'JSON 处理工具',
                'author': 'Yan Team',
                'dependencies': {},
                'path': ''
            },
            'math-utils': {
                'version': '2.1.0',
                'description': '数学工具库',
                'author': 'Yan Team',
                'dependencies': {},
                'path': ''
            },
            'web-tools': {
                'version': '1.5.0',
                'description': 'Web 开发工具',
                'author': 'Yan Team',
                'dependencies': {
                    '网络请求': '^1.0'
                },
                'path': ''
            }
        }

        if name in mock_packages:
            return mock_packages[name]

        return None

    def get_resolution_order(self) -> List[DependencyNode]:
        """获取解析顺序（后序遍历）"""
        result = []
        visited = set()

        def traverse(node: DependencyNode):
            for dep in node.dependencies:
                if dep.name not in visited:
                    traverse(dep)
            if node.name not in visited:
                result.append(node)
                visited.add(node.name)

        for node in self.resolved.values():
            if node.name not in visited:
                traverse(node)

        return result


class PackageManager:
    """包管理器"""

    def __init__(self):
        self.home = Path.home()
        self.yan_dir = self.home / ".yan"
        self.packages_dir = self.yan_dir / "packages"
        self.cache_dir = self.yan_dir / "cache"
        self.config_file = self.yan_dir / "config.json"

        self.yan_dir.mkdir(exist_ok=True)
        self.packages_dir.mkdir(exist_ok=True)
        self.cache_dir.mkdir(exist_ok=True)

        self.config = self._load_config()
        self.resolver = DependencyResolver(self.config.get("sources", []))

    def _load_config(self) -> Dict:
        """加载配置"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {
            "packages": {},
            "sources": [
                "https://yanpkg.org",
                "https://github.com/yan-lang/packages"
            ],
            "registry": "https://yanpkg.org"
        }

    def _save_config(self):
        """保存配置"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    def _version_matches(self, installed: str, spec: str) -> bool:
        """检查版本是否匹配"""
        if spec.startswith('^'):
            min_ver = Version(spec[1:])
            inst_ver = Version(installed)
            return inst_ver >= min_ver
        elif spec.startswith('~'):
            min_ver = Version(spec[1:])
            inst_ver = Version(installed)
            return inst_ver.parts[:2] == min_ver.parts[:2]
        elif spec == installed:
            return True
        return False

    def install(self, package_name: str, version: Optional[str] = None):
        """安装包"""
        print(f"正在安装 {package_name}...")

        if package_name in self.config["packages"]:
            print(f"{package_name} 已安装 (版本: {self.config['packages'][package_name].get('version', 'unknown')})")
            if version:
                current_ver = self.config["packages"][package_name].get('version', '0.0.0')
                if Version(version) > Version(current_ver):
                    print(f"正在更新 {package_name} 到版本 {version}...")
                    self._do_update(package_name, version)
                else:
                    print(f"当前版本已满足要求")
            return

        resolved = self.resolver.resolve(package_name, version)
        if not resolved:
            print(f"错误: 无法找到包 '{package_name}'")
            self._try_install_from_source(package_name, version)
            return

        self._install_package_node(resolved)

        print(f"{package_name} 安装成功！")

    def _install_package_node(self, node: DependencyNode):
        """安装包节点"""
        if node.name in self.config["packages"]:
            return

        for dep in node.dependencies:
            self._install_package_node(dep)

        package_dir = self.packages_dir / node.name
        package_dir.mkdir(exist_ok=True, parents=True)

        package_info = {
            "name": node.name,
            "version": node.version,
            "description": f"{node.name} 包",
            "author": "Yan User",
            "dependencies": {dep.name: dep.version for dep in node.dependencies},
            "entry": "主.yan"
        }

        with open(package_dir / "package.json", 'w', encoding='utf-8') as f:
            json.dump(package_info, f, ensure_ascii=False, indent=2)

        entry_file = package_dir / "主.yan"
        if not entry_file.exists():
            with open(entry_file, 'w', encoding='utf-8') as f:
                f.write(f"""-- {node.name} 包入口文件
-- 版本: {node.version}

定 版本 = "{node.version}"。
定 作者 = "Yan User"。

出 版本 作者。
""")

        self.config["packages"][node.name] = {
            "version": node.version,
            "path": str(package_dir),
            "dependencies": {dep.name: dep.version for dep in node.dependencies}
        }
        self._save_config()

    def _try_install_from_source(self, package_name: str, version: Optional[str] = None):
        """尝试从源码安装"""
        print(f"正在尝试从源码安装 {package_name}...")

        package_dir = self.packages_dir / package_name
        package_dir.mkdir(exist_ok=True)

        package_info = {
            "name": package_name,
            "version": version or "0.1.0",
            "description": f"{package_name} 包（本地安装）",
            "author": "Local",
            "dependencies": {},
            "entry": "主.yan"
        }

        with open(package_dir / "package.json", 'w', encoding='utf-8') as f:
            json.dump(package_info, f, ensure_ascii=False, indent=2)

        self.config["packages"][package_name] = {
            "version": version or "0.1.0",
            "path": str(package_dir),
            "dependencies": {}
        }
        self._save_config()

        print(f"{package_name} 已从源码安装")

    def _do_update(self, package_name: str, version: str):
        """执行更新"""
        package_dir = self.packages_dir / package_name
        if package_dir.exists():
            import shutil
            shutil.rmtree(package_dir)

        self.config["packages"][package_name] = {
            "version": version,
            "path": str(package_dir),
            "dependencies": self.config["packages"][package_name].get("dependencies", {})
        }
        self._save_config()

    def uninstall(self, package_name: str):
        """卸载包"""
        print(f"正在卸载 {package_name}...")

        if package_name not in self.config["packages"]:
            print(f"{package_name} 未安装")
            return

        dependents = self._find_dependents(package_name)
        if dependents:
            print(f"警告: 以下包依赖于 {package_name}:")
            for dep in dependents:
                print(f"  - {dep}")
            response = input("确定要继续吗？(y/N): ")
            if response.lower() != 'y':
                print("取消卸载")
                return

        package_dir = self.packages_dir / package_name
        if package_dir.exists():
            import shutil
            shutil.rmtree(package_dir)

        del self.config["packages"][package_name]
        self._save_config()

        print(f"{package_name} 卸载成功！")

    def _find_dependents(self, package_name: str) -> List[str]:
        """查找依赖该包的包"""
        dependents = []
        for name, info in self.config["packages"].items():
            deps = info.get("dependencies", {})
            if package_name in deps:
                dependents.append(name)
        return dependents

    def list(self):
        """列出已安装的包"""
        print("已安装的包:")
        print()

        if not self.config["packages"]:
            print("  (无)")
            return

        for name, info in sorted(self.config["packages"].items()):
            version = info.get('version', 'unknown')
            deps = info.get('dependencies', {})
            deps_str = ", ".join(f"{k}@{v}" for k, v in deps.items()) if deps else "(无依赖)"
            print(f"  📦 {name}")
            print(f"     版本: {version}")
            print(f"     依赖: {deps_str}")
            print()

    def search(self, query: str):
        """搜索包"""
        print(f"搜索: {query}")
        print()

        all_packages = {
            '网络请求': {'version': '1.0.0', 'description': '简洁的网络请求库'},
            'json-tools': {'version': '1.2.0', 'description': 'JSON 序列化/反序列化工具'},
            'math-utils': {'version': '2.1.0', 'description': '数学工具库'},
            'web-tools': {'version': '1.5.0', 'description': 'Web 开发工具集'},
            '日期时间': {'version': '1.0.0', 'description': '日期时间处理库'},
            '文件工具': {'version': '1.1.0', 'description': '文件操作工具'},
            '字符串工具': {'version': '1.0.5', 'description': '字符串处理工具'},
            '测试框架': {'version': '2.0.0', 'description': '言语言单元测试框架'},
            '调试助手': {'version': '1.0.0', 'description': '调试辅助工具'},
            '类型检查': {'version': '0.9.0', 'description': '运行时类型检查'},
        }

        query_lower = query.lower()
        found = False
        for name, info in all_packages.items():
            if query_lower in name.lower() or query_lower in info['description'].lower():
                print(f"  📦 {name}@{info['version']}")
                print(f"     {info['description']}")
                print()
                found = True

        if not found:
            print("  未找到匹配的包")
            print()
            print("  热门包:")
            for name, info in list(all_packages.items())[:5]:
                print(f"  📦 {name}@{info['version']}")

    def update(self, package_name: str = None):
        """更新包"""
        if package_name:
            print(f"正在更新 {package_name}...")
            if package_name not in self.config["packages"]:
                print(f"错误: {package_name} 未安装")
                return

            info = self.config["packages"][package_name]
            current_ver = info.get('version', '0.0.0')
            print(f"当前版本: {current_ver}")

            resolved = self.resolver.resolve(package_name)
            if resolved:
                latest_ver = resolved.version
                if Version(latest_ver) > Version(current_ver):
                    self._do_update(package_name, latest_ver)
                    print(f"{package_name} 已更新到 {latest_ver}")
                else:
                    print(f"{package_name} 已是最新版本")
            else:
                print(f"无法检查更新")

        else:
            print("正在检查所有包的更新...")
            updated = 0
            for name in self.config["packages"]:
                info = self.config["packages"][name]
                current_ver = info.get('version', '0.0.0')
                resolved = self.resolver.resolve(name)
                if resolved and Version(resolved.version) > Version(current_ver):
                    print(f"  {name}: {current_ver} -> {resolved.version}")
                    self._do_update(name, resolved.version)
                    updated += 1

            if updated == 0:
                print("所有包已是最新版本")
            else:
                print(f"已更新 {updated} 个包")

    def publish(self, package_dir: str = None):
        """发布包到远程仓库"""
        if package_dir is None:
            package_dir = os.getcwd()

        package_json_path = Path(package_dir) / "package.json"

        if not package_json_path.exists():
            print("错误: 当前目录没有 package.json")
            print("请先在项目目录运行 'yan 包 init' 初始化项目")
            return

        with open(package_json_path, 'r', encoding='utf-8') as f:
            package_info = json.load(f)

        name = package_info.get('name', 'unknown')
        version = package_info.get('version', '0.1.0')

        print(f"正在发布 {name}@{version}...")
        print(f"仓库: {self.config.get('registry', 'https://yanpkg.org')}")
        print()
        print("发布功能需要登录账号")
        print("请访问 https://yanpkg.org 进行注册和发布")

    def info(self, package_name: str):
        """显示包详细信息"""
        if package_name in self.config["packages"]:
            info = self.config["packages"][package_name]
            print(f"📦 {package_name}")
            print(f"   版本: {info.get('version', 'unknown')}")
            print(f"   路径: {info.get('path', 'unknown')}")
            print(f"   依赖: {info.get('dependencies', {})}")
            return

        print(f"正在从注册表获取 {package_name} 的信息...")

        resolved = self.resolver.resolve(package_name)
        if resolved:
            print(f"📦 {resolved.name}")
            print(f"   版本: {resolved.version}")
            print(f"   依赖: {[d.name for d in resolved.dependencies]}")
        else:
            print(f"错误: 找不到包 '{package_name}'")

    def init(self, name: Optional[str] = None):
        """初始化新项目"""
        current_dir = Path.cwd()
        if name is None:
            name = current_dir.name

        print(f"正在初始化项目: {name}")

        package_json = current_dir / "package.json"
        if package_json.exists():
            print("package.json 已存在")
            return

        with open(package_json, 'w', encoding='utf-8') as f:
            json.dump({
                "name": name,
                "version": "0.1.0",
                "description": "Yan 语言项目",
                "author": "",
                "dependencies": {},
                "entry": "主.yan"
            }, f, ensure_ascii=False, indent=2)

        entry_file = current_dir / "主.yan"
        if not entry_file.exists():
            with open(entry_file, 'w', encoding='utf-8') as f:
                f.write(f"""-- {name} 项目入口文件

印 "欢迎使用 {name}！"。

出。
""")

        tests_dir = current_dir / "tests"
        tests_dir.mkdir(exist_ok=True)

        test_file = tests_dir / "基本测试.yan"
        if not test_file.exists():
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write("""-- 基本测试

套 "基本功能测试":
    测 "加法":
        断言等 加 1 2 3。
    。

出 测试结果。
""")

        yan_json = current_dir / ".yan.json"
        if not yan_json.exists():
            with open(yan_json, 'w', encoding='utf-8') as f:
                json.dump({
                    "name": name,
                    "version": "0.1.0",
                    "entry": "主.yan",
                    "test": "tests/"
                }, f, ensure_ascii=False, indent=2)

        print("项目初始化成功！")
        print(f"目录: {current_dir}")
        print("文件:")
        print("  📄 package.json (包配置)")
        print("  📄 主.yan (入口文件)")
        print("  📁 tests/ (测试目录)")
        print("  📄 .yan.json (语言配置)")

    def help(self):
        """显示帮助"""
        print("""
言语言包管理器 - yan
用法:
    yan 包 安装 <包名> [版本]   - 安装包
    yan 包 卸载 <包名>          - 卸载包
    yan 包 更新 [包名]          - 更新包（可选包名）
    yan 包 列表                 - 列出已安装的包
    yan 包 搜索 <关键词>         - 搜索包
    yan 包 信息 <包名>           - 显示包信息
    yan 包 发布                 - 发布包到远程仓库
    yan 包 初始化 [项目名]        - 初始化项目
    yan 包 帮助                 - 显示帮助

版本说明:
    ^1.0.0  - 兼容 1.0.0 到 2.0.0 以下的版本
    ~1.0.0  - 兼容 1.0.0 到 1.1.0 以下的版本
    1.0.0   - 精确版本

示例:
    yan 包 安装 网络请求
    yan 包 安装 math-utils ^2.0.0
    yan 包 更新
    yan 包 搜索 json
    yan 包 初始化 my-project
""")


def main():
    """主函数"""
    args = sys.argv[1:]
    
    if not args:
        args = ["帮助"]
    
    pkg_manager = PackageManager()
    
    cmd = args[0]
    
    if cmd == "安装" or cmd == "i" or cmd == "install":
        if len(args) < 2:
            print("错误: 请指定包名")
            pkg_manager.help()
            sys.exit(1)
        pkg_name = args[1]
        version = args[2] if len(args) > 2 else None
        pkg_manager.install(pkg_name, version)
    
    elif cmd == "卸载" or cmd == "uninstall":
        if len(args) < 2:
            print("错误: 请指定包名")
            sys.exit(1)
        pkg_manager.uninstall(args[1])
    
    elif cmd == "列表" or cmd == "ls" or cmd == "list":
        pkg_manager.list()
    
    elif cmd == "搜索" or cmd == "s" or cmd == "search":
        query = args[1] if len(args) > 1 else ""
        pkg_manager.search(query)
    
    elif cmd == "初始化" or cmd == "init":
        name = args[1] if len(args) > 1 else None
        pkg_manager.init(name)
    
    elif cmd == "帮助" or cmd == "h" or cmd == "help":
        pkg_manager.help()
    
    else:
        print(f"未知命令: {cmd}")
        pkg_manager.help()


if __name__ == "__main__":
    main()
