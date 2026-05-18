#!/usr/bin/env python3
"""
言语言包管理器 - Yan Package Manager

核心功能：
- 安装包
- 卸载包
- 列出已安装的包
- 搜索包
- 初始化项目
- 发布包
- 链接本地包
"""

import os
import sys
import json
import shutil
import zipfile
import hashlib
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

# 配置常量
YAN_HOME = Path.home() / ".yan"
PACKAGES_DIR = YAN_HOME / "packages"
CONFIG_FILE = YAN_HOME / "config.json"
DEFAULT_REGISTRY = "https://registry.yan-lang.org"

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

定 主函数 = 函
  印 "Hello, Yan!"。
。

主函数。
""",
    "tests/基本测试.yan": """注 基本测试文件

套 "{name} 测试"

测 "测试主函数"：
  印 "运行测试..."。
。
"""
}


class PackageManager:
    def __init__(self):
        self._init_dirs()
        self.config = self._load_config()
    
    def _init_dirs(self):
        """初始化必要的目录"""
        YAN_HOME.mkdir(parents=True, exist_ok=True)
        PACKAGES_DIR.mkdir(exist_ok=True)
    
    def _load_config(self):
        """加载配置文件"""
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "registry": DEFAULT_REGISTRY,
            "installed_packages": {}
        }
    
    def _save_config(self):
        """保存配置文件"""
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
    
    def _get_package_path(self, package_name):
        """获取包的安装路径"""
        return PACKAGES_DIR / package_name
    
    def _download_package(self, package_name, version=None):
        """下载包"""
        registry = self.config.get("registry", DEFAULT_REGISTRY)
        if version:
            url = f"{registry}/packages/{package_name}/{version}.zip"
        else:
            url = f"{registry}/packages/{package_name}/latest.zip"
        
        try:
            request = Request(url, headers={'User-Agent': 'Yan-Package-Manager/0.1'})
            with urlopen(request) as response:
                return response.read()
        except (URLError, HTTPError) as e:
            print(f"错误：下载失败 - {e}")
            return None
    
    def _extract_package(self, zip_data, package_name):
        """解压包"""
        package_path = self._get_package_path(package_name)
        package_path.mkdir(exist_ok=True)
        
        import io
        with zipfile.ZipFile(io.BytesIO(zip_data)) as zf:
            zf.extractall(package_path)
    
    def install(self, package_name, version=None):
        """安装包"""
        print(f"正在安装包: {package_name}" + (f"@{version}" if version else ""))
        
        # 检查是否已安装
        if package_name in self.config.get("installed_packages", {}):
            print(f"警告：包 {package_name} 已安装")
            return
        
        # 下载包
        zip_data = self._download_package(package_name, version)
        if not zip_data:
            return
        
        # 解压包
        self._extract_package(zip_data, package_name)
        
        # 读取包配置
        package_path = self._get_package_path(package_name)
        pkg_config_path = package_path / "package.json"
        
        if pkg_config_path.exists():
            with open(pkg_config_path, 'r', encoding='utf-8') as f:
                pkg_config = json.load(f)
            installed_version = pkg_config.get("version", "unknown")
        else:
            installed_version = version or "unknown"
        
        # 更新配置
        self.config["installed_packages"][package_name] = installed_version
        self._save_config()
        
        print(f"成功安装包: {package_name}@{installed_version}")
    
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
