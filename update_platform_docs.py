import sys

def update_platform_docs():
    content = '''
## 平台特定模块说明

### Unix/Linux 特定模块

以下模块仅在 Unix/Linux 系统上可用：

| 中文名称 | 英文名称 | 说明 |
|---------|---------|------|
| 资源 | resource | 资源限制管理 |
| 文件控制 | fcntl | 文件描述符控制 |
| 终端IO | termios | 终端属性控制 |
| 终端 | tty | TTY控制功能 |
| 伪终端 | pty | 伪终端创建 |
| 组 | grp | 组账户信息 |
| 密码 | pwd | 用户密码数据库 |
| 阴影密码 | spwd | 阴影密码数据库 |
| POSIX | posix | POSIX系统接口 |

#### 资源模块 (resource)
提供对系统资源使用的控制和查询功能：
- `获取限制(resource.getrlimit)` - 获取资源限制
- `设置限制(resource.setrlimit)` - 设置资源限制
- `资源类型(resource.RLIMIT_*)` - 资源类型常量

#### 文件控制模块 (fcntl)
提供文件描述符的控制操作：
- `文件控制(fcntl.fcntl)` - 文件控制操作
- `锁文件(fcntl.flock)` - 文件锁操作
- `获取记录锁(fcntl.fcntl)` - 记录锁操作

#### 终端IO模块 (termios)
提供终端属性的控制：
- `获取属性(termios.tcgetattr)` - 获取终端属性
- `设置属性(termios.tcsetattr)` - 设置终端属性
- `终端属性常量(termios.*)` - 终端控制常量

#### 终端模块 (tty)
提供TTY控制功能：
- `设置行模式(tty.setraw)` - 设置原始模式
- `设置规范模式(tty.setcbreak)` - 设置cbreak模式

#### 伪终端模块 (pty)
提供伪终端创建功能：
- `打开伪终端(pty.openpty)` - 创建伪终端对
- `派生伪终端(pty.fork)` - 创建子进程并连接到伪终端

#### 组模块 (grp)
提供组账户信息查询：
- `获取组信息(grp.getgrnam)` - 按名称获取组信息
- `获取组ID信息(grp.getgrgid)` - 按ID获取组信息
- `枚举组(grp.getgrall)` - 获取所有组信息

#### 密码模块 (pwd)
提供用户密码数据库访问：
- `获取用户信息(pwd.getpwnam)` - 按名称获取用户信息
- `获取用户ID信息(pwd.getpwuid)` - 按ID获取用户信息
- `枚举用户(pwd.getpwall)` - 获取所有用户信息

#### 阴影密码模块 (spwd)
提供阴影密码数据库访问：
- `获取阴影密码(spwd.getspnam)` - 按名称获取阴影密码
- `获取阴影密码ID(spwd.getspuid)` - 按ID获取阴影密码

### Windows 特定模块

以下模块仅在 Windows 系统上可用：

| 中文名称 | 英文名称 | 说明 |
|---------|---------|------|
| Win32API | win32api | Windows API访问 |
| Win32进程 | win32process | 进程管理 |
| Win32服务 | win32service | Windows服务管理 |
| Win32安全 | win32security | Windows安全 |
| 注册表 | winreg | Windows注册表访问 |

#### 注册表模块 (winreg)
提供Windows注册表访问：
- `打开键(winreg.OpenKey)` - 打开注册表键
- `创建键(winreg.CreateKey)` - 创建注册表键
- `删除键(winreg.DeleteKey)` - 删除注册表键
- `设置值(winreg.SetValue)` - 设置注册表值
- `获取值(winreg.QueryValue)` - 获取注册表值

### macOS 特定模块

以下模块主要在 macOS 上使用：

| 中文名称 | 英文名称 | 说明 |
|---------|---------|------|
| 属性列表 | plistlib | macOS属性列表处理 |

#### 属性列表模块 (plistlib)
提供macOS属性列表(plist)处理：
- `加载plist(plistlib.load)` - 加载plist文件
- `转储plist(plistlib.dump)` - 保存plist文件
- `解析字符串(plistlib.loads)` - 解析plist字符串
- `生成字符串(plistlib.dumps)` - 生成plist字符串

### 跨平台兼容性建议

#### 1. 使用平台检测
```yan
定义 平台名称 等于 平台.系统()

如果 平台名称 等于 "Windows" 那么:
    打印("运行在Windows上")
否则如果 平台名称 等于 "Linux" 那么:
    打印("运行在Linux上")
否则如果 平台名称 等于 "Darwin" 那么:
    打印("运行在macOS上")
否则:
    打印("未知平台")
```

#### 2. 条件导入平台特定模块
```yan
-- 尝试导入平台特定模块
定义 资源模块 等于 空

尝试:
    资源模块 = 资源
除:
    打印("资源模块不可用")
```

#### 3. 使用跨平台替代方案

| 功能 | 跨平台方案 | 平台特定方案 |
|------|-----------|-------------|
| 文件路径 | pathlib | os.path |
| 进程管理 | subprocess | multiprocessing |
| 线程同步 | threading | threading |
| 网络通信 | socket | socket |

### 平台兼容性注意事项

1. **路径分隔符**: Windows使用 `\`，Unix使用 `/`
2. **行结束符**: Windows使用 `\r\n`，Unix使用 `\n`
3. **文件权限**: Unix有复杂的权限系统，Windows权限模型不同
4. **进程ID**: Windows的PID与Unix的PID含义不同
5. **环境变量**: Windows使用 `%VAR%`，Unix使用 `$VAR`

### 推荐实践

1. **优先使用跨平台API**: 如 `pathlib`, `subprocess`, `socket`
2. **避免直接使用平台特定代码**: 除非必要
3. **提供优雅降级**: 当平台特定功能不可用时提供替代方案
4. **测试多个平台**: 确保代码在目标平台上都能正常工作

'''

    # 读取现有文档
    with open('g:/dumategithub/newlisp/.worktrees/v2-syntax/V2_STATUS.md', 'r', encoding='utf-8') as f:
        docs = f.read()

    # 找到待办事项部分并替换
    todo_section = '''## 待办事项

- [ ] 添加更多中文属性映射
- [ ] 完善平台特定模块文档
- [ ] 添加更多测试用例
- [ ] 优化错误处理和提示'''

    new_todo = '''## 平台特定模块文档

### Unix/Linux 特定模块

以下模块仅在 Unix/Linux 系统上可用：

| 中文名称 | 英文名称 | 说明 |
|---------|---------|------|
| 资源 | resource | 资源限制管理 |
| 文件控制 | fcntl | 文件描述符控制 |
| 终端IO | termios | 终端属性控制 |
| 终端 | tty | TTY控制功能 |
| 伪终端 | pty | 伪终端创建 |
| 组 | grp | 组账户信息 |
| 密码 | pwd | 用户密码数据库 |
| 阴影密码 | spwd | 阴影密码数据库 |
| POSIX | posix | POSIX系统接口 |

#### 资源模块 (resource)
提供对系统资源使用的控制和查询功能：
- `获取限制(resource.getrlimit)` - 获取资源限制
- `设置限制(resource.setrlimit)` - 设置资源限制
- `资源类型(resource.RLIMIT_*)` - 资源类型常量

#### 文件控制模块 (fcntl)
提供文件描述符的控制操作：
- `文件控制(fcntl.fcntl)` - 文件控制操作
- `锁文件(fcntl.flock)` - 文件锁操作

#### 终端IO模块 (termios)
提供终端属性的控制：
- `获取属性(termios.tcgetattr)` - 获取终端属性
- `设置属性(termios.tcsetattr)` - 设置终端属性

#### 终端模块 (tty)
提供TTY控制功能：
- `设置行模式(tty.setraw)` - 设置原始模式
- `设置规范模式(tty.setcbreak)` - 设置cbreak模式

#### 伪终端模块 (pty)
提供伪终端创建功能：
- `打开伪终端(pty.openpty)` - 创建伪终端对
- `派生伪终端(pty.fork)` - 创建子进程并连接到伪终端

#### 组模块 (grp)
提供组账户信息查询：
- `获取组信息(grp.getgrnam)` - 按名称获取组信息
- `获取组ID信息(grp.getgrgid)` - 按ID获取组信息

#### 密码模块 (pwd)
提供用户密码数据库访问：
- `获取用户信息(pwd.getpwnam)` - 按名称获取用户信息
- `获取用户ID信息(pwd.getpwuid)` - 按ID获取用户信息

### Windows 特定模块

以下模块仅在 Windows 系统上可用：

| 中文名称 | 英文名称 | 说明 |
|---------|---------|------|
| 注册表 | winreg | Windows注册表访问 |

#### 注册表模块 (winreg)
提供Windows注册表访问：
- `打开键(winreg.OpenKey)` - 打开注册表键
- `创建键(winreg.CreateKey)` - 创建注册表键
- `设置值(winreg.SetValue)` - 设置注册表值
- `获取值(winreg.QueryValue)` - 获取注册表值

### macOS 特定模块

以下模块主要在 macOS 上使用：

| 中文名称 | 英文名称 | 说明 |
|---------|---------|------|
| 属性列表 | plistlib | macOS属性列表处理 |

#### 属性列表模块 (plistlib)
提供macOS属性列表(plist)处理：
- `加载plist(plistlib.load)` - 加载plist文件
- `转储plist(plistlib.dump)` - 保存plist文件

### 跨平台兼容性建议

#### 1. 使用平台检测
```yan
定义 平台名称 等于 平台.系统()

如果 平台名称 等于 "Windows" 那么:
    打印("运行在Windows上")
否则如果 平台名称 等于 "Linux" 那么:
    打印("运行在Linux上")
否则如果 平台名称 等于 "Darwin" 那么:
    打印("运行在macOS上")
```

#### 2. 条件导入平台特定模块
```yan
-- 尝试导入平台特定模块
定义 资源模块 等于 空

尝试:
    资源模块 = 资源
除:
    打印("资源模块不可用")
```

## 待办事项

- [x] 添加更多中文属性映射 ✓
- [x] 完善平台特定模块文档 ✓
- [ ] 添加更多测试用例
- [ ] 优化错误处理和提示'''

    updated_docs = docs.replace(todo_section, new_todo)

    with open('g:/dumategithub/newlisp/.worktrees/v2-syntax/V2_STATUS.md', 'w', encoding='utf-8') as f:
        f.write(updated_docs)

    print("平台特定模块文档更新完成")

if __name__ == "__main__":
    update_platform_docs()
