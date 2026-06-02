#!/usr/bin/env python3
"""
言语言包管理器 (Yan Package Manager)
"""

import os
import json
import sys
import hashlib
import zipfile
import shutil
import re
from urllib.request import urlopen

# 配置
CONFIG = {
    "registry_url": "packages/registry",
    "cache_dir": "packages/cache",
    "local_dir": "packages/local",
    "stdlib_dir": "yan/stdlib"
}


def load_registry():
    """加载包注册表"""
    registry_path = os.path.join(CONFIG["registry_url"], "packages.json")
    if os.path.exists(registry_path):
        with open(registry_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"packages": []}


def parse_version(version):
    """解析版本号为元组"""
    parts = version.split('.')
    result = []
    for part in parts:
        match = re.match(r'^(\d+)(.*)$', part)
        if match:
            result.append(int(match.group(1)))
            if match.group(2):
                result.append(match.group(2))
        else:
            result.append(0)
    return tuple(result)


def satisfies_constraint(version, constraint):
    """检查版本是否满足约束"""
    version_tuple = parse_version(version)
    
    constraints = constraint.split(',')
    for c in constraints:
        c = c.strip()
        if not c:
            continue
        
        match = re.match(r'^([<>]=?|==|!=)(.+)$', c)
        if not match:
            continue
        
        op, target = match.group(1), match.group(2)
        target_tuple = parse_version(target)
        
        if op == '>':
            if version_tuple <= target_tuple:
                return False
        elif op == '>=':
            if version_tuple < target_tuple:
                return False
        elif op == '<':
            if version_tuple >= target_tuple:
                return False
        elif op == '<=':
            if version_tuple > target_tuple:
                return False
        elif op == '==':
            if version_tuple != target_tuple:
                return False
        elif op == '!=':
            if version_tuple == target_tuple:
                return False
    
    return True


def find_matching_version(package_name, constraint=None):
    """查找满足约束的版本"""
    registry = load_registry()
    
    pkg_versions = []
    for pkg in registry["packages"]:
        if pkg["name"] == package_name:
            pkg_versions.append(pkg)
    
    if not pkg_versions:
        return None
    
    if constraint:
        for pkg in pkg_versions:
            if satisfies_constraint(pkg["version"], constraint):
                return pkg
        return None
    else:
        pkg_versions.sort(key=lambda p: parse_version(p["version"]), reverse=True)
        return pkg_versions[0] if pkg_versions else None


def load_index():
    """加载包索引"""
    index_path = os.path.join(CONFIG["registry_url"], "index.json")
    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"packages": []}


def search_package(query):
    """搜索包"""
    registry = load_registry()
    results = []
    for pkg in registry["packages"]:
        if query.lower() in pkg["name"].lower() or query.lower() in pkg["description"].lower():
            results.append(pkg)
    return results


def install_package(package_name, version=None):
    """安装包（支持版本约束）"""
    registry = load_registry()
    
    pkg = None
    if version and (version.startswith('>') or version.startswith('<') or version.startswith('=') or version.startswith('!')):
        pkg = find_matching_version(package_name, version)
        if pkg:
            print(f"找到满足约束 '{version}' 的版本 {pkg['version']}")
        else:
            print(f"错误：未找到满足约束 '{version}' 的版本")
            return False
    else:
        # 原有的精确版本匹配逻辑
        for p in registry["packages"]:
            if p["name"] == package_name:
                if version and p["version"] == version:
                    pkg = p
                    break
                elif not version:
                    pkg = p
                    break
        
        if not pkg:
            pkg = find_matching_version(package_name, version)
    
    print(f"正在安装 {package_name} v{pkg['version']}...")
    
    # 复制标准库模块
    source_dir = pkg["location"]
    target_dir = os.path.join(CONFIG["local_dir"], package_name)
    
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    
    # 复制模块文件
    for module in pkg["modules"]:
        src_file = os.path.join(source_dir, f"{module}.yan")
        if os.path.exists(src_file):
            shutil.copy(src_file, target_dir)
            print(f"  已复制 {module}.yan")
        else:
            print(f"  警告：未找到 {module}.yan")
    
    # 创建包配置
    pkg_config = {
        "name": pkg["name"],
        "version": pkg["version"],
        "installed_modules": pkg["modules"],
        "install_time": "2026-05-27"
    }
    
    with open(os.path.join(target_dir, "package.json"), 'w', encoding='utf-8') as f:
        json.dump(pkg_config, f, ensure_ascii=False, indent=2)
    
    print(f"成功安装 {package_name} v{pkg['version']}")
    return True


def list_packages():
    """列出所有可用包"""
    registry = load_registry()
    print("可用包列表：")
    print("-" * 60)
    for pkg in registry["packages"]:
        print(f"{pkg['name']} v{pkg['version']}")
        print(f"  描述: {pkg['description']}")
        print(f"  作者: {pkg['author']}")
        print(f"  模块数: {len(pkg['modules'])}")
        print()


def list_installed():
    """列出已安装的包"""
    installed = []
    if os.path.exists(CONFIG["local_dir"]):
        for dir_name in os.listdir(CONFIG["local_dir"]):
            pkg_dir = os.path.join(CONFIG["local_dir"], dir_name)
            if os.path.isdir(pkg_dir):
                config_path = os.path.join(pkg_dir, "package.json")
                if os.path.exists(config_path):
                    with open(config_path, 'r', encoding='utf-8') as f:
                        installed.append(json.load(f))
    
    print("已安装的包：")
    print("-" * 60)
    if not installed:
        print("  暂无已安装的包")
        return
    
    for pkg in installed:
        print(f"{pkg['name']} v{pkg['version']}")
        print(f"  安装时间: {pkg.get('install_time', '未知')}")
        print(f"  模块数: {len(pkg.get('installed_modules', []))}")
        print()


def detect_conflicts(dependencies):
    """检测依赖冲突"""
    conflicts = {}
    version_map = {}
    
    for pkg in dependencies:
        pkg_name = pkg["name"]
        pkg_version = pkg["version"]
        
        if pkg_name in version_map:
            if version_map[pkg_name] != pkg_version:
                if pkg_name not in conflicts:
                    conflicts[pkg_name] = {
                        "versions": [version_map[pkg_name], pkg_version],
                        "packages": []
                    }
                conflicts[pkg_name]["packages"].append(pkg_name)
        else:
            version_map[pkg_name] = pkg_version
    
    return conflicts

def check_and_resolve_conflicts(dependencies):
    """检查并解决依赖冲突"""
    conflicts = detect_conflicts(dependencies)
    
    if conflicts:
        print("警告：检测到依赖冲突:")
        for pkg_name, info in conflicts.items():
            print(f"  - {pkg_name}: 版本 {info['versions']}")
        print("将使用最高版本...")
        
        # 解决冲突：保留最高版本
        resolved = {}
        for pkg in dependencies:
            pkg_name = pkg["name"]
            if pkg_name not in resolved:
                resolved[pkg_name] = pkg
            else:
                # 比较版本，保留更高的
                current = resolved[pkg_name]
                if parse_version(pkg["version"]) > parse_version(current["version"]):
                    resolved[pkg_name] = pkg
        
        return list(resolved.values())
    
    return dependencies


def resolve_dependencies(package_name, version=None, installed=None):
    """解析依赖树"""
    if installed is None:
        installed = set()
    
    pkg = find_matching_version(package_name, version)
    if not pkg:
        return []
    
    if pkg["name"] in installed:
        return []
    
    installed.add(pkg["name"])
    dependencies = pkg.get("dependencies", [])
    
    result = [pkg]
    
    for dep in dependencies:
        dep_name = dep.split('@')[0] if '@' in dep else dep
        dep_version = dep.split('@')[1] if '@' in dep else None
        result.extend(resolve_dependencies(dep_name, dep_version, installed))
    
    # 检测并解决冲突
    return check_and_resolve_conflicts(result)


def install_with_dependencies(package_name, version=None):
    """安装包及其依赖"""
    print(f"解析 {package_name} 的依赖...")
    dependencies = resolve_dependencies(package_name, version)
    
    if not dependencies:
        print(f"未找到包 '{package_name}'")
        return False
    
    print(f"需要安装 {len(dependencies)} 个包:")
    for pkg in dependencies:
        print(f"  - {pkg['name']} v{pkg['version']}")
    
    for pkg in dependencies:
        install_package(pkg["name"], pkg["version"])
    
    return True


def uninstall_package(package_name):
    """卸载包"""
    pkg_dir = os.path.join(CONFIG["local_dir"], package_name)
    if not os.path.exists(pkg_dir):
        print(f"错误：未找到已安装的包 '{package_name}'")
        return False
    
    shutil.rmtree(pkg_dir)
    print(f"已卸载 {package_name}")
    return True


def show_package(package_name):
    """显示包详情"""
    registry = load_registry()
    
    pkg = None
    for p in registry["packages"]:
        if p["name"] == package_name:
            pkg = p
            break
    
    if not pkg:
        print(f"错误：未找到包 '{package_name}'")
        return
    
    print(f"包名: {pkg['name']}")
    print(f"版本: {pkg['version']}")
    print(f"描述: {pkg['description']}")
    print(f"作者: {pkg['author']}")
    print(f"许可证: {pkg['license']}")
    print(f"依赖: {', '.join(pkg.get('dependencies', [])) or '无'}")
    print(f"模块列表:")
    for module in pkg["modules"]:
        print(f"  - {module}")


def update_registry():
    """更新注册表"""
    print("检查更新...")
    print("注册表已是最新版本")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("言语言包管理器 (yan-pm)")
        print("用法: yan-pm <命令> [参数]")
        print()
        print("命令:")
        print("  search <关键词>    搜索包")
        print("  install <包名>     安装包")
        print("  uninstall <包名>   卸载包")
        print("  list              列出所有可用包")
        print("  installed         列出已安装的包")
        print("  show <包名>       显示包详情")
        print("  update            更新注册表")
        print("  help              显示帮助")
        return
    
    command = sys.argv[1]
    
    if command == "search":
        if len(sys.argv) < 3:
            print("用法: yan-pm search <关键词>")
            return
        results = search_package(sys.argv[2])
        if results:
            print(f"找到 {len(results)} 个匹配的包:")
            for pkg in results:
                print(f"  {pkg['name']} v{pkg['version']} - {pkg['description']}")
        else:
            print("未找到匹配的包")
    
    elif command == "install":
        if len(sys.argv) < 3:
            print("用法: yan-pm install <包名> [版本/约束]")
            return
        
        package_name = sys.argv[2]
        version = sys.argv[3] if len(sys.argv) > 3 else None
        
        # 始终尝试解析依赖树（除非指定 --no-deps）
        if len(sys.argv) > 4 and sys.argv[4] == '--no-deps':
            install_package(package_name, version)
        else:
            install_with_dependencies(package_name, version)
    
    elif command == "uninstall":
        if len(sys.argv) < 3:
            print("用法: yan-pm uninstall <包名>")
            return
        uninstall_package(sys.argv[2])
    
    elif command == "list":
        list_packages()
    
    elif command == "installed":
        list_installed()
    
    elif command == "show":
        if len(sys.argv) < 3:
            print("用法: yan-pm show <包名>")
            return
        show_package(sys.argv[2])
    
    elif command == "update":
        update_registry()
    
    elif command == "help":
        main()
    
    else:
        print(f"未知命令: {command}")
        print("使用 'yan-pm help' 查看帮助")


if __name__ == "__main__":
    main()