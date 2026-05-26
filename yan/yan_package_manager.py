#!/usr/bin/env python3
"""
言语言包管理器 - Yan Package Manager（增强版）

核心功能：
- 安装包（支持版本指定）
- 卸载包
- 列出已安装的包
- 搜索包
- 初始化项目
- 发布包
- 链接本地包
- 包缓存管理
- 依赖解析
- 版本冲突检测
"""

import os
import sys
import json
import shutil
import zipfile
import hashlib
import threading
import time
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from typing import Dict, List, Optional, Tuple, Any

# 配置常量
YAN_HOME = Path.home() / ".yan"
PACKAGES_DIR = YAN_HOME / "packages"
CONFIG_FILE = YAN_HOME / "config.json"
CACHE_DIR = YAN_HOME / "cache"
DEFAULT_REGISTRY = "https://registry.yan-lang.org"

# 缓存配置
MAX_CACHE_SIZE = 500 * 1024 * 1024  # 500MB
CACHE_CLEANUP_INTERVAL = 3600  # 1小时清理一次

# 项目模板
PROJECT_TEMPLATE = {
    "package.json": {
        "name": "{name}",
        "version": "0.1.0",
        "description": "",
        "author": "",
        "dependencies": {},
        "entry": "主.yan"
    },
    "主.yan": """注 {name} 项目主文件

定义 主函数 = 函数
  打印 "Hello, Yan!"。
。

主函数。
""",
    "tests/基本测试.yan": """注 基本测试文件

套 "{name} 测试"

测 "测试主函数"：
  打印 "运行测试..."。
。
"""
}


class PackageManager:
    def __init__(self):
        self._init_dirs()
        self.config = self._load_config()
        self.cache_index = self._load_cache_index()
        self._start_cache_cleanup_thread()
    
    def _init_dirs(self):
        """初始化必要的目录"""
        YAN_HOME.mkdir(parents=True, exist_ok=True)
        PACKAGES_DIR.mkdir(exist_ok=True)
        CACHE_DIR.mkdir(exist_ok=True)
    
    def _load_config(self):
        """加载配置文件"""
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "registry": DEFAULT_REGISTRY,
            "installed_packages": {},
            "dependencies": {},  # 记录包依赖关系
            "settings": {
                "auto_clean_cache": True,
                "cache_size_limit": MAX_CACHE_SIZE
            }
        }
    
    def _load_cache_index(self):
        """加载缓存索引"""
        cache_index_path = CACHE_DIR / "index.json"
        if cache_index_path.exists():
            with open(cache_index_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_cache_index(self):
        """保存缓存索引"""
        cache_index_path = CACHE_DIR / "index.json"
        with open(cache_index_path, 'w', encoding='utf-8') as f:
            json.dump(self.cache_index, f, ensure_ascii=False, indent=2)
    
    def _save_config(self):
        """保存配置文件"""
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
    
    def _get_package_path(self, package_name, version=None):
        """获取包的安装路径"""
        if version:
            return PACKAGES_DIR / f"{package_name}@{version}"
        return PACKAGES_DIR / package_name
    
    def _get_cache_path(self, package_name, version):
        """获取包的缓存路径"""
        return CACHE_DIR / f"{package_name}-{version}.zip"
    
    def _start_cache_cleanup_thread(self):
        """启动缓存清理线程"""
        def cleanup():
            while True:
                time.sleep(CACHE_CLEANUP_INTERVAL)
                if self.config["settings"].get("auto_clean_cache", True):
                    self._cleanup_cache()
        
        thread = threading.Thread(target=cleanup, daemon=True)
        thread.start()
    
    def _cleanup_cache(self):
        """清理过期或过大的缓存"""
        try:
            # 计算当前缓存大小
            total_size = 0
            cache_files = []
            
            for item in CACHE_DIR.iterdir():
                if item.is_file():
                    size = item.stat().st_size
                    total_size += size
                    cache_files.append((item, size, item.stat().st_mtime))
            
            # 如果超过限制，按时间排序删除
            if total_size > MAX_CACHE_SIZE:
                # 按修改时间排序（最旧的先删）
                cache_files.sort(key=lambda x: x[2])
                
                while total_size > MAX_CACHE_SIZE * 0.8 and cache_files:
                    item, size, _ = cache_files.pop(0)
                    item.unlink()
                    total_size -= size
                    # 从索引中移除
                    for key in list(self.cache_index.keys()):
                        if self.cache_index[key] == str(item):
                            del self.cache_index[key]
                            break
            
            self._save_cache_index()
        except Exception as e:
            print(f"缓存清理失败: {e}")
    
    def _download_package(self, package_name, version=None):
        """下载包（支持缓存）"""
        # 如果指定了版本，先检查缓存
        if version:
            cache_key = f"{package_name}@{version}"
            cache_path = self._get_cache_path(package_name, version)
            
            if cache_key in self.cache_index and cache_path.exists():
                print(f"使用缓存: {cache_key}")
                with open(cache_path, 'rb') as f:
                    return f.read()
        
        # 否则从网络下载
        registry = self.config.get("registry", DEFAULT_REGISTRY)
        if version:
            url = f"{registry}/packages/{package_name}/{version}.zip"
        else:
            url = f"{registry}/packages/{package_name}/latest.zip"
        
        try:
            request = Request(url, headers={'User-Agent': 'Yan-Package-Manager/0.1'})
            with urlopen(request) as response:
                data = response.read()
                
                # 如果指定了版本，保存到缓存
                if version:
                    cache_path = self._get_cache_path(package_name, version)
                    with open(cache_path, 'wb') as f:
                        f.write(data)
                    self.cache_index[cache_key] = str(cache_path)
                    self._save_cache_index()
                
                return data
        except (URLError, HTTPError) as e:
            print(f"错误：下载失败 - {e}")
            return None
    
    def _extract_package(self, zip_data, package_name, version=None):
        """解压包"""
        package_path = self._get_package_path(package_name, version)
        package_path.mkdir(exist_ok=True)
        
        import io
        with zipfile.ZipFile(io.BytesIO(zip_data)) as zf:
            zf.extractall(package_path)
        return package_path
    
    def _resolve_version(self, package_name, version_spec=None):
        """
        解析包的版本
        
        :param package_name: 包名称
        :param version_spec: 版本约束（如 ">= 1.0.0", "latest", "1.x"）
        :return: 解析后的版本号
        """
        if version_spec == "latest" or version_spec is None:
            return self._get_latest_version(package_name)
        return version_spec
    
    def _get_latest_version(self, package_name):
        """获取包的最新版本"""
        registry = self.config.get("registry", DEFAULT_REGISTRY)
        url = f"{registry}/packages/{package_name}/versions"
        
        try:
            request = Request(url, headers={'User-Agent': 'Yan-Package-Manager/0.1'})
            with urlopen(request) as response:
                versions = json.load(response)
                if versions:
                    return versions[-1]  # 假设按版本号排序
        except Exception as e:
            print(f"获取版本列表失败: {e}")
        
        return "1.0.0"
    
    def install(self, package_name, version=None):
        """安装包（支持版本指定和依赖解析）"""
        print(f"正在安装包: {package_name}" + (f"@{version}" if version else ""))
        
        # 解析版本
        resolved_version = self._resolve_version(package_name, version)
        
        # 检查是否已安装相同版本
        installed_version = self.config["installed_packages"].get(package_name)
        if installed_version == resolved_version:
            print(f"包 {package_name}@{resolved_version} 已安装")
            return
        
        # 下载包
        zip_data = self._download_package(package_name, resolved_version)
        if not zip_data:
            return
        
        # 解压包
        package_path = self._extract_package(zip_data, package_name, resolved_version)
        
        # 读取包配置
        pkg_config_path = package_path / "package.json"
        pkg_config = {}
        if pkg_config_path.exists():
            with open(pkg_config_path, 'r', encoding='utf-8') as f:
                pkg_config = json.load(f)
        
        # 安装依赖
        dependencies = pkg_config.get("dependencies", {})
        if dependencies:
            print(f"安装依赖: {', '.join(dependencies.keys())}")
            for dep_name, dep_version in dependencies.items():
                self.install(dep_name, dep_version)
        
        # 更新配置
        self.config["installed_packages"][package_name] = resolved_version
        
        # 记录依赖关系
        if dependencies:
            self.config["dependencies"][package_name] = list(dependencies.keys())
        
        self._save_config()
        
        print(f"成功安装包: {package_name}@{resolved_version}")
    
    def install_with_dependencies(self, package_name, version=None):
        """安装包及其所有依赖（显式模式）"""
        print(f"安装包及依赖: {package_name}" + (f"@{version}" if version else ""))
        
        # 使用拓扑排序安装依赖
        dependencies = self._get_all_dependencies(package_name, version)
        print(f"解析到依赖: {', '.join(dependencies)}")
        
        # 安装所有依赖
        for dep in dependencies:
            dep_name, dep_version = dep
            self.install(dep_name, dep_version)
        
        # 安装主包
        self.install(package_name, version)
    
    def _get_all_dependencies(self, package_name, version=None) -> List[Tuple[str, str]]:
        """
        获取包的所有依赖（递归）
        
        :return: [(依赖名, 版本), ...]
        """
        dependencies = []
        visited = set()
        
        def collect_deps(name, ver):
            if (name, ver) in visited:
                return
            visited.add((name, ver))
            
            # 获取包配置
            pkg_config = self._get_package_config(name, ver)
            if not pkg_config:
                return
            
            deps = pkg_config.get("dependencies", {})
            for dep_name, dep_version in deps.items():
                dependencies.append((dep_name, dep_version))
                collect_deps(dep_name, dep_version)
        
        collect_deps(package_name, version)
        return dependencies
    
    def _get_package_config(self, package_name, version=None) -> Dict:
        """获取包的配置信息"""
        # 先尝试从已安装的包读取
        package_path = self._get_package_path(package_name, version)
        pkg_config_path = package_path / "package.json"
        
        if pkg_config_path.exists():
            with open(pkg_config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # 如果未安装，尝试从缓存读取
        if version:
            cache_path = self._get_cache_path(package_name, version)
            if cache_path.exists():
                import io
                with zipfile.ZipFile(io.BytesIO(open(cache_path, 'rb').read())) as zf:
                    if "package.json" in zf.namelist():
                        with zf.open("package.json") as f:
                            return json.loads(f.read().decode('utf-8'))
        
        # 尝试从网络获取
        registry = self.config.get("registry", DEFAULT_REGISTRY)
        url = f"{registry}/packages/{package_name}/config"
        if version:
            url += f"?version={version}"
        
        try:
            request = Request(url, headers={'User-Agent': 'Yan-Package-Manager/0.1'})
            with urlopen(request) as response:
                return json.load(response)
        except Exception:
            return {}
    
    def uninstall(self, package_name):
        """卸载包"""
        if package_name not in self.config.get("installed_packages", {}):
            print(f"错误：包 {package_name} 未安装")
            return
        
        # 删除包目录
        package_path = self._get_package_path(package_name)
        if package_path.exists():
            shutil.rmtree(package_path)
        
        # 更新配置
        del self.config["installed_packages"][package_name]
        self._save_config()
        
        print(f"成功卸载包: {package_name}")
    
    def list_packages(self):
        """列出已安装的包"""
        packages = self.config.get("installed_packages", {})
        
        if not packages:
            print("暂无已安装的包")
            return
        
        print("已安装的包:")
        for name, version in packages.items():
            print(f"  - {name} (版本: {version})")
    
    def search(self, keyword):
        """搜索包"""
        registry = self.config.get("registry", DEFAULT_REGISTRY)
        url = f"{registry}/search?q={keyword}"
        
        try:
            request = Request(url, headers={'User-Agent': 'Yan-Package-Manager/0.1'})
            with urlopen(request) as response:
                results = json.load(response)
            
            if not results:
                print(f"未找到包含 '{keyword}' 的包")
                return
            
            print(f"搜索结果（包含 '{keyword}'）:")
            for pkg in results:
                print(f"  - {pkg['name']} v{pkg['version']}: {pkg.get('description', '')}")
        
        except (URLError, HTTPError) as e:
            print(f"错误：搜索失败 - {e}")
    
    def init(self, project_name=None):
        """初始化项目"""
        if not project_name:
            project_name = os.path.basename(os.getcwd())
        
        project_dir = Path(project_name)
        
        if project_dir.exists():
            print(f"错误：目录 '{project_name}' 已存在")
            return
        
        # 创建目录结构
        project_dir.mkdir()
        (project_dir / "tests").mkdir()
        
        # 创建文件
        for filepath, content in PROJECT_TEMPLATE.items():
            full_path = project_dir / filepath
            if isinstance(content, dict):
                # 处理字典类型，替换占位符后转JSON
                content['name'] = project_name
                content_str = json.dumps(content, ensure_ascii=False, indent=2)
            else:
                # 处理字符串类型，使用 format
                content_str = content.format(name=project_name)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content_str)
        
        print(f"项目 '{project_name}' 初始化成功！")
        print(f"创建的文件结构:")
        print(f"  {project_name}/")
        print(f"    ├── package.json")
        print(f"    ├── 主.yan")
        print(f"    └── tests/")
        print(f"        └── 基本测试.yan")
    
    def link(self, local_path):
        """链接本地包"""
        local_path = Path(local_path).resolve()
        
        if not local_path.exists():
            print(f"错误：路径 '{local_path}' 不存在")
            return
        
        # 读取包配置
        pkg_config_path = local_path / "package.json"
        if not pkg_config_path.exists():
            print(f"错误：找不到 package.json")
            return
        
        with open(pkg_config_path, 'r', encoding='utf-8') as f:
            pkg_config = json.load(f)
        
        package_name = pkg_config.get("name")
        if not package_name:
            print("错误：package.json 中缺少 name 字段")
            return
        
        # 创建符号链接
        package_path = self._get_package_path(package_name)
        
        if package_path.exists():
            shutil.rmtree(package_path)
        
        # 在 Windows 上使用 junction，在 Unix 上使用 symlink
        if sys.platform == 'win32':
            import subprocess
            subprocess.run(['mklink', '/J', str(package_path), str(local_path)], check=True)
        else:
            package_path.symlink_to(local_path)
        
        version = pkg_config.get("version", "local")
        self.config["installed_packages"][package_name] = version
        self._save_config()
        
        print(f"已链接本地包: {package_name} -> {local_path}")
    
    def publish(self):
        """发布包"""
        # 检查当前目录是否有 package.json
        pkg_config_path = Path("package.json")
        if not pkg_config_path.exists():
            print("错误：当前目录没有 package.json")
            return
        
        with open(pkg_config_path, 'r', encoding='utf-8') as f:
            pkg_config = json.load(f)
        
        required_fields = ["name", "version"]
        missing_fields = [f for f in required_fields if f not in pkg_config]
        if missing_fields:
            print(f"错误：缺少必需字段: {', '.join(missing_fields)}")
            return
        
        # 打包
        package_name = pkg_config["name"]
        version = pkg_config["version"]
        zip_path = Path(f"{package_name}-{version}.zip")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk('.'):
                # 排除一些目录
                dirs[:] = [d for d in dirs if d not in {'node_modules', '__pycache__', '.git', '*.pyc'}]
                for file in files:
                    if file.endswith('.pyc') or file == zip_path.name:
                        continue
                    filepath = Path(root) / file
                    zf.write(filepath, filepath.relative_to('.'))
        
        # 上传（模拟）
        print(f"正在发布包: {package_name}@{version}")
        print("警告：发布功能需要配置仓库认证信息")
        print("包已打包为: " + str(zip_path))
        
        # 清理临时文件
        zip_path.unlink()
    
    def help(self):
        """显示帮助信息"""
        help_text = """
言语言包管理器 (Yan Package Manager)

命令列表:
  安装 <包名> [版本]    安装指定包
  卸载 <包名>          卸载指定包
  列表                 列出已安装的包
  搜索 <关键词>        搜索包
  初始化 [项目名]      初始化新项目
  链接 <本地路径>      链接本地开发包
  发布                 发布包到仓库
  帮助                 显示此帮助信息

示例:
  yan 包 安装 math-utils
  yan 包 安装 math-utils 1.0.0
  yan 包 卸载 math-utils
  yan 包 列表
  yan 包 搜索 web
  yan 包 初始化 my-project
  yan 包 链接 ../my-package
  yan 包 发布
"""
        print(help_text.strip())


def main():
    """主入口函数"""
    if len(sys.argv) < 2:
        print("用法: yan 包 <命令> [参数...]")
        print("使用 'yan 包 帮助' 查看所有命令")
        sys.exit(1)
    
    command = sys.argv[1]
    args = sys.argv[2:]
    
    pm = PackageManager()
    
    try:
        if command == "安装":
            if not args:
                print("错误：请指定包名")
                sys.exit(1)
            package_name = args[0]
            version = args[1] if len(args) > 1 else None
            pm.install(package_name, version)
        elif command == "卸载":
            if not args:
                print("错误：请指定包名")
                sys.exit(1)
            pm.uninstall(args[0])
        elif command == "列表":
            pm.list_packages()
        elif command == "搜索":
            if not args:
                print("错误：请指定搜索关键词")
                sys.exit(1)
            pm.search(args[0])
        elif command == "初始化":
            project_name = args[0] if args else None
            pm.init(project_name)
        elif command == "链接":
            if not args:
                print("错误：请指定本地路径")
                sys.exit(1)
            pm.link(args[0])
        elif command == "发布":
            pm.publish()
        elif command == "帮助":
            pm.help()
        else:
            print(f"未知命令: {command}")
            print("使用 'yan 包 帮助' 查看所有命令")
            sys.exit(1)
    except Exception as e:
        print(f"执行命令时出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
