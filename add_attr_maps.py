import sys

def add_more_attr_maps():
    # 读取原始文件
    with open('g:/dumategithub/newlisp/.worktrees/v2-syntax/yan/v2/codegen.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # 找到 attr_map 的位置
    attr_map_start = content.find("attr_map = {")
    attr_map_end = content.find("}", attr_map_start) + 1
    
    # 新的属性映射
    new_attrs = """
            # 数学库扩展
            '反正切2': 'atan2', '双曲正弦': 'sinh', '双曲余弦': 'cosh', '双曲正切': 'tanh',
            '反双曲正弦': 'asinh', '反双曲余弦': 'acosh', '反双曲正切': 'atanh',
            '阶乘函数': 'gamma', '误差函数': 'erf', '余误差函数': 'erfc',
            '正弦积分': 'sinint', '余弦积分': 'cosint', '指数积分': 'expint',
            '贝塞尔函数J': 'besselj', '贝塞尔函数Y': 'bessely',
            '修正贝塞尔I': 'besseli', '修正贝塞尔K': 'besselk',
            '椭圆积分第一类': 'ellipk', '椭圆积分第二类': 'ellipe',
            '伽马函数对数': 'lgamma', '阶乘对数': 'loggamma',
            '弧度转角度': 'degrees', '角度转弧度': 'radians',
            '取模': 'fmod', '余数': 'remainder', '模运算': 'modf',
            '符号函数': 'copysign', '绝对值浮点': 'fabs', '整数截断': 'trunc',
            '无限大': 'inf', '非数字': 'nan', '非数字判断': 'isnan', '无限判断': 'isinf',
            
            # 随机库扩展
            '随机种子': 'seed', '随机状态': 'getstate', '设置状态': 'setstate',
            '泊松分布': 'poissonvariate', '指数分布': 'expovariate',
            '伽马分布': 'gammavariate', '贝塔分布': 'betavariate',
            '正态分布': 'normalvariate', '对数正态分布': 'lognormvariate',
            '冯米塞斯分布': 'vonmisesvariate', '帕累托分布': 'paretovariate',
            '威布尔分布': 'weibullvariate', '三角分布': 'triangular',
            '均匀整数范围': 'randrange', '随机字节': 'getrandbits',
            
            # 时间库扩展
            '时区偏移': 'altzone', '夏令时': 'daylight', '时区名称': 'tzname',
            '格式化UTC': 'strftime', '解析UTC': 'strptime',
            '时间元组': 'struct_time', '时钟精度': 'clock_getres',
            
            # 操作系统库扩展
            '环境变量': 'environ', '改变目录': 'chdir', '创建目录': 'mkdir',
            '创建多级目录': 'makedirs', '删除目录': 'rmdir', '删除多级目录': 'removedirs',
            '列出目录': 'listdir', '移除文件': 'remove', '重命名': 'rename',
            '系统命令': 'system', '路径连接': 'path.join', '路径分割': 'path.split',
            '路径目录': 'path.dirname', '路径文件名': 'path.basename', '路径扩展': 'path.splitext',
            '存在': 'path.exists', '是文件': 'path.isfile', '是目录': 'path.isdir',
            '获取大小': 'path.getsize', '获取修改时间': 'path.getmtime', '获取访问时间': 'path.getatime',
            '获取创建时间': 'path.getctime', '统计信息': 'stat', '访问时间': 'utime',
            '权限': 'chmod', '所有者': 'chown', '硬链接': 'link', '符号链接': 'symlink',
            '读取链接': 'readlink', '真实路径': 'realpath', '管道': 'pipe',
            '设备号': 'makedev', '主设备号': 'major', '次设备号': 'minor',
            'CPU数量': 'cpu_count', '终止进程': 'kill', '等待进程': 'wait',
            '执行权限': 'access', '文件描述符': 'open', '关闭': 'close', '读取': 'read',
            '写入': 'write', '文件位置': 'lseek', '同步': 'sync', '复制文件描述符': 'dup',
            '复制文件描述符2': 'dup2', '锁文件': 'flock', '修改权限掩码': 'umask',
            '用户ID': 'getuid', '组ID': 'getgid', '设置用户ID': 'setuid', '设置组ID': 'setgid',
            '进程ID': 'getpid', '父进程ID': 'getppid', '有效用户ID': 'geteuid', '有效组ID': 'getegid',
            
            # 系统库扩展
            '递归限制': 'getrecursionlimit', '设置递归限制': 'setrecursionlimit',
            '字节序': 'byteorder', '模块搜索路径': 'path', '内置模块': 'builtin_module_names',
            '缓存字节码': 'dont_write_bytecode', '警告选项': 'warnoptions',
            '执行文件': 'executable', '前缀': 'prefix', '基础前缀': 'base_prefix',
            '执行前缀': 'exec_prefix', '基础执行前缀': 'base_exec_prefix',
            '版权': 'copyright', '许可证': 'license', '命令行参数': 'argv',
            '命令行选项': 'flags', '显示追踪': 'tracebacklimit', '异常钩子': 'excepthook',
            
            # 正则库扩展
            '完整匹配': 'fullmatch', '查找迭代': 'finditer', '替换函数': 'subn',
            '转义': 'escape', 'ASCII模式': 'ASCII', '忽略大小写': 'IGNORECASE',
            '多行模式': 'MULTILINE', '点号匹配换行': 'DOTALL', '扩展模式': 'VERBOSE',
            '匹配对象': 'Match', '模式对象': 'Pattern',
            
            # 集合库扩展
            '计数器': 'Counter', '默认字典': 'defaultdict', '有序字典': 'OrderedDict',
            '命名元组': 'namedtuple', '双端队列': 'deque', '链映射': 'ChainMap',
            '用户列表': 'UserList', '用户字典': 'UserDict', '用户字符串': 'UserString',
            
            # 哈希库扩展
            'MD5': 'md5', 'SHA1': 'sha1', 'SHA224': 'sha224', 'SHA256': 'sha256',
            'SHA384': 'sha384', 'SHA512': 'sha512', 'SHA3_224': 'sha3_224',
            'SHA3_256': 'sha3_256', 'SHA3_384': 'sha3_384', 'SHA3_512': 'sha3_512',
            'BLAKE2b': 'blake2b', 'BLAKE2s': 'blake2s',
            
            # HMAC扩展
            'HMAC': 'new', '摘要': 'digest', '十六进制摘要': 'hexdigest', '复制': 'copy',
            
            # Base64扩展
            'URL安全编码': 'urlsafe_b64encode', 'URL安全解码': 'urlsafe_b64decode',
            '标准编码': 'standard_b64encode', '标准解码': 'standard_b64decode',
            
            # 压缩扩展
            '压缩级别': 'Z_DEFAULT_COMPRESSION', '最大压缩级别': 'Z_BEST_COMPRESSION',
            '最快压缩': 'Z_BEST_SPEED', '无压缩': 'Z_NO_COMPRESSION',
            
            # 日期时间扩展
            '时区': 'timezone', 'UTC现在': 'utcnow', 'UTC从时间戳': 'utcfromtimestamp',
            '星期几': 'weekday', 'ISO星期几': 'isoweekday', 'ISO日历': 'isocalendar',
            'ISO格式': 'isoformat', '替换': 'replace',
            
            # 线程扩展
            '互斥锁': 'RLock', '条件': 'Condition', '事件': 'Event', '信号量': 'Semaphore',
            '定时器': 'Timer', '本地': 'local', '屏障': 'Barrier',
            '当前线程': 'current_thread', '活跃线程': 'active_count', '枚举线程': 'enumerate',
            '主线程': 'main_thread', '守护线程': 'daemon',
            
            # 进程扩展
            '队列': 'Queue', '管道': 'Pipe', '锁': 'Lock', '信号量': 'Semaphore',
            '事件': 'Event', '条件': 'Condition', '值': 'Value', '数组': 'Array',
            '管理器': 'Manager', '池': 'Pool', '当前进程': 'current_process',
            '活跃子进程': 'active_children', 'CPU数量': 'cpu_count', '冻结支持': 'freeze_support',
            
            # 并发扩展
            '线程池执行器': 'ThreadPoolExecutor', '进程池执行器': 'ProcessPoolExecutor',
            '等待': 'wait', '等待全部': 'gather', '完成': 'as_completed',
            '未来': 'Future', '取消': 'cancel', '已取消': 'cancelled', '已完成': 'done',
            
            # 子进程扩展
            '运行': 'run', '调用': 'call', '检查输出': 'check_output', '检查调用': 'check_call',
            '管道': 'PIPE', '标准输出': 'STDOUT', '错误输出': 'stderr',
            '进程': 'Popen', '通信': 'communicate', '等待': 'wait', '轮询': 'poll',
            '发送信号': 'send_signal', '终止': 'terminate', '杀死': 'kill',
            
            # 文件工具扩展
            '复制': 'copy', '复制文件': 'copy2', '复制目录': 'copytree', '移动': 'move',
            '删除': 'rmtree', '归档': 'make_archive', '解归档': 'unpack_archive',
            '忽略模式': 'ignore_patterns', '磁盘使用': 'disk_usage',
            
            # 路径扩展
            '当前': 'cwd', '家目录': 'home', '解析': 'resolve', '绝对路径': 'absolute',
            '相对路径': 'relative_to', '父目录': 'parent', '父目录们': 'parents',
            '名称': 'name', '后缀': 'suffix', '后缀们': 'suffixes', '茎': 'stem',
            '驱动': 'drive', '根': 'root', '锚': 'anchor', '连接': 'joinpath',
            '匹配': 'match', '通配符匹配': 'glob', '递归通配符': 'rglob',
            '创建目录': 'mkdir', '创建多级目录': 'mkdir', '移除': 'rmdir', '触摸': 'touch',
            '删除': 'unlink', '重命名': 'rename', '替换': 'replace', '打开': 'open',
            '读取': 'read_text', '写入': 'write_text', '读取字节': 'read_bytes',
            '写入字节': 'write_bytes', '大小': 'stat', '修改时间': 'stat().st_mtime',
            '存在': 'exists', '是文件': 'is_file', '是目录': 'is_dir', '是符号链接': 'is_symlink',
            
            # 日志扩展
            '获取日志器': 'getLogger', '调试': 'DEBUG', '信息': 'INFO', '警告': 'WARNING',
            '错误': 'ERROR', '严重错误': 'CRITICAL', '基本配置': 'basicConfig',
            '格式化器': 'Formatter', '处理器': 'Handler', '流处理器': 'StreamHandler',
            '文件处理器': 'FileHandler', '旋转文件处理器': 'RotatingFileHandler',
            '时间旋转处理器': 'TimedRotatingFileHandler', '过滤器': 'Filter',
            '设置级别': 'setLevel', '添加处理器': 'addHandler', '移除处理器': 'removeHandler',
            '添加过滤器': 'addFilter', '移除过滤器': 'removeFilter',
            '日志记录': 'log', '调试记录': 'debug', '信息记录': 'info', '警告记录': 'warning',
            '错误记录': 'error', '严重错误记录': 'critical',
            
            # 配置扩展
            '配置解析器': 'ConfigParser', '读取': 'read', '获取': 'get', '设置': 'set',
            '添加节': 'add_section', '有节': 'has_section', '有选项': 'has_option',
            '移除节': 'remove_section', '移除选项': 'remove_option', '节们': 'sections',
            '选项们': 'options', '项目们': 'items', '默认值': 'defaults',
            '写入': 'write', '读取字符串': 'read_string', '读取文件': 'read_file',
            
            # URL扩展
            '打开': 'urlopen', '请求': 'Request', '解析': 'urlparse', '拆分': 'urlsplit',
            '合并': 'urlunsplit', '编码': 'urlencode', '解码': 'parse_qs', '解析列表': 'parse_qsl',
            '引用': 'quote', '取消引用': 'unquote', '引用加号': 'quote_plus',
            '取消引用加号': 'unquote_plus', 'URL连接': 'urljoin',
            
            # 套接字扩展
            '套接字': 'socket', 'AF_INET': 'AF_INET', 'AF_INET6': 'AF_INET6',
            'AF_UNIX': 'AF_UNIX', 'SOCK_STREAM': 'SOCK_STREAM', 'SOCK_DGRAM': 'SOCK_DGRAM',
            'SOCK_RAW': 'SOCK_RAW', '绑定': 'bind', '监听': 'listen', '接受': 'accept',
            '连接': 'connect', '连接ex': 'connect_ex', '发送': 'send', '发送到': 'sendto',
            '接收': 'recv', '接收从': 'recvfrom', '关闭': 'close', '设置选项': 'setsockopt',
            '获取选项': 'getsockopt', '设置阻塞': 'setblocking', '设置超时': 'settimeout',
            '获取超时': 'gettimeout', '获取peername': 'getpeername', '获取sockname': 'getsockname',
            'shutdown': 'shutdown', '选择': 'select', '轮询': 'poll',
            
            # 迭代工具扩展
            '计数': 'count', '循环': 'cycle', '重复': 'repeat', '链': 'chain',
            '组合': 'combinations', '排列': 'permutations', '笛卡尔积': 'product',
            '分组': 'groupby', '累积': 'accumulate', '无限迭代': 'islice',
            '压缩': 'compress', '丢弃': 'dropwhile', '获取直到': 'takewhile',
            '过滤假值': 'filterfalse', '交错': 'zip_longest', '成对': 'pairwise',
            '星号': 'starmap', 'tee': 'tee',
            
            # 函数工具扩展
            '装饰器': 'wraps', '部分应用': 'partial', '组合函数': 'compose',
            '缓存': 'lru_cache', '单例': 'singledispatch', '单例方法': 'singledispatchmethod',
            '归约': 'reduce', '总数排序': 'total_ordering', '更新包装': 'update_wrapper',
            '缓存信息': 'cache_info', '清除缓存': 'cache_clear',
            
            # IO扩展
            '字符串IO': 'StringIO', '字节IO': 'BytesIO', '缓冲区大小': 'DEFAULT_BUFFER_SIZE',
            '文本包装器': 'TextIOWrapper', '缓冲阅读器': 'BufferedReader',
            '缓冲写入器': 'BufferedWriter', '缓冲随机': 'BufferedRandom',
            '文件IO': 'FileIO', '打开': 'open',
            
            # 反射扩展
            '获取成员': 'getmembers', '签名': 'signature', '参数': 'Parameter',
            '返回注解': 'Return', '模块': 'module', '类': 'class', '函数': 'function',
            '方法': 'method', '实例方法': 'method_descriptor', '包装': 'wrapper_descriptor',
            '属性': 'property', '生成器': 'generator', '协程': 'coroutine',
            '异步生成器': 'async_generator', '异步函数': 'async_function',
            '获取源文件': 'getsourcefile', '获取源码': 'getsource', '获取文件': 'getfile',
            '栈': 'stack', '帧': 'frame', '跟踪': 'trace', '检查签名': 'signature',
            
            # 上下文扩展
            '上下文管理器': 'contextmanager', '抑制': 'suppress', '空上下文': 'nullcontext',
            '关闭': 'closing', '退出栈': 'ExitStack', '重定向标准输出': 'redirect_stdout',
            '重定向标准错误': 'redirect_stderr',
            
            # 数据类扩展
            '数据类': 'dataclass', '字段': 'field', '初始化后': 'post_init',
            '装饰器': 'dataclass', '数据类装饰器': 'dataclass', '字段默认值': 'MISSING',
            '冻结': 'frozen', '匹配参数': 'match_args', '排序': 'order',
            
            # 枚举扩展
            '枚举': 'Enum', '唯一枚举': 'unique', '自动枚举': 'auto', 'IntEnum': 'IntEnum',
            'IntFlag': 'IntFlag', 'Flag': 'Flag',
            
            # 类型扩展
            '任意': 'Any', '无': 'None', '布尔': 'bool', '整数': 'int', '浮点数': 'float',
            '字符串': 'str', '字节': 'bytes', '列表': 'list', '字典': 'dict', '集合': 'set',
            '元组': 'tuple', '可调用': 'Callable', '可迭代': 'Iterable', '迭代器': 'Iterator',
            '生成器': 'Generator', '序列': 'Sequence', '映射': 'Mapping', '类型变量': 'TypeVar',
            '泛型': 'Generic', '联合': 'Union', '可选': 'Optional', '无返回': 'NoReturn',
            '协议': 'Protocol', '运行时检查协议': 'runtime_checkable', '最终': 'Final',
            '字面量': 'Literal', 'TypedDict': 'TypedDict', 'NamedTuple': 'NamedTuple',
            '冻结集合': 'FrozenSet', '字节数组': 'Bytearray', '复杂': 'Complex',
            
            # 异步扩展
            '运行': 'run', '创建任务': 'create_task', '睡眠': 'sleep', '等待': 'wait',
            '等待全部': 'gather', '屏蔽': 'shield', '超时': 'wait_for',
            '事件循环': 'get_event_loop', '新事件循环': 'new_event_loop',
            '设置事件循环': 'set_event_loop', '关闭事件循环': 'close', '运行直到完成': 'run_until_complete',
            '调用很快': 'call_soon', '调用延迟': 'call_later', '调用在': 'call_at',
            '创建子进程': 'create_subprocess_exec', '创建子进程shell': 'create_subprocess_shell',
            '打开连接': 'open_connection', '启动服务器': 'start_server',
            
            # 平台扩展
            '系统': 'system', '节点': 'node', '版本': 'version', '机器': 'machine',
            '处理器': 'processor', 'Python版本': 'python_version', 'Python构建': 'python_build',
            'Python编译器': 'python_compiler', 'Python分支': 'python_branch',
            'Python实现': 'python_implementation', '平台': 'platform',
            '架构': 'architecture', 'uname': 'uname', 'libc_ver': 'libc_ver',
            
            # 信号扩展
            '信号': 'signal', '默认处理': 'default_int_handler', '忽略': 'SIG_IGN',
            '默认': 'SIG_DFL', '中断': 'SIGINT', '终止': 'SIGTERM', '杀死': 'SIGKILL',
            '挂起': 'SIGSTOP', '继续': 'SIGCONT', '段错误': 'SIGSEGV', '管道': 'SIGPIPE',
            '警报': 'SIGALRM', '用户定义1': 'SIGUSR1', '用户定义2': 'SIGUSR2',
            '设置信号处理': 'signal', '获取信号处理': 'getsignal',
            
            # 警告扩展
            '警告': 'warn', '过滤器': 'filterwarnings', '简单过滤器': 'simplefilter',
            '重置过滤器': 'resetwarnings', '格式警告': 'formatwarning',
            '显示警告': 'showwarning',
            
            # 追踪扩展
            '打印异常': 'print_exc', '格式化异常': 'format_exc', '提取堆栈': 'extract_stack',
            '打印堆栈': 'print_stack', '格式化堆栈': 'format_stack', '提取异常': 'extract_tb',
            '格式化异常追踪': 'format_tb', '清除缓存': 'clear_frames',
            
            # Unicode扩展
            '名称': 'name', '十进制': 'decimal', '数字': 'digit', '数值': 'numeric',
            '类别': 'category', '双向': 'bidirectional', '组合类': 'combining',
            '镜像': 'mirrored', '规范化': 'normalize', '分解': 'decompose',
            '组合': 'compose', '大写': 'upper', '小写': 'lower', '标题': 'title',
            '大小写折叠': 'casefold', '交换大小写': 'swapcase',
            
            # 编解码扩展
            '编码': 'encode', '解码': 'decode', '查找编解码器': 'lookup', '注册': 'register',
            '编解码器信息': 'CodecInfo', '增量编码器': 'IncrementalEncoder',
            '增量解码器': 'IncrementalDecoder', '流阅读器': 'StreamReader',
            '流写入器': 'StreamWriter',
            
            # 结构体扩展
            '打包': 'pack', '解包': 'unpack', '打包进缓冲区': 'pack_into',
            '从缓冲区解包': 'unpack_from', '大小': 'calcsize',
            
            # 数组扩展
            '数组': 'array', '类型代码': 'typecode', '项大小': 'itemsize', '缓冲区': 'buffer_info',
            '字节序': 'byteorder', '追加': 'append', '扩展': 'extend', '插入': 'insert',
            '移除': 'remove', '弹出': 'pop', '索引': 'index', '计数': 'count',
            '反转': 'reverse', '排序': 'sort', '转置': 'tofile', '从文件': 'fromfile',
            '转列表': 'tolist', '从列表': 'fromlist', '复制': 'copy',
            
            # 弱引用扩展
            '弱引用': 'ref', '代理': 'proxy', '弱键字典': 'WeakKeyDictionary',
            '弱值字典': 'WeakValueDictionary', '弱集合': 'WeakSet', '回调': 'callback',
            '清除': 'clear',
            
            # 垃圾回收扩展
            '启用': 'enable', '禁用': 'disable', '收集': 'collect', '设置阈值': 'set_threshold',
            '获取阈值': 'get_threshold', '垃圾回收对象': 'garbage', '获取对象': 'get_objects',
            '调试': 'debug', '冻结': 'freeze', '解冻': 'unfreeze',
            
            # C类型扩展
            '整型': 'c_int', '长整型': 'c_long', '短整型': 'c_short', '无符号整型': 'c_uint',
            '无符号长整型': 'c_ulong', '无符号短整型': 'c_ushort', '浮点': 'c_float',
            '双精度': 'c_double', '字符': 'c_char', '字节': 'c_byte', '无符号字节': 'c_ubyte',
            '指针': 'POINTER', '结构体': 'Structure', '联合': 'Union', '数组': 'Array',
            '函数指针': 'CFUNCTYPE', '回调函数': 'WINFUNCTYPE', '地址': 'addressof',
            '指针类型': 'pointer', '引用': 'byref', '字符串': 'create_string_buffer',
            '宽字符串': 'create_unicode_buffer', '大小': 'sizeof', '对齐': 'alignment',
            
            # 选择扩展
            '选择': 'select', '轮询': 'poll', '轮询IN': 'POLLIN', '轮询OUT': 'POLLOUT',
            '轮询ERR': 'POLLERR', '轮询HUP': 'POLLHUP', '轮询NVAL': 'POLLNVAL',
            
            # 选择器扩展
            '选择器': 'DefaultSelector', 'EPoll选择器': 'EpollSelector',
            'KQueue选择器': 'KqueueSelector', '选择器键': 'SelectorKey',
            '注册': 'register', '注销': 'unregister', '选择': 'select',
            '修改': 'modify',
            
            # 内存映射扩展
            '内存映射': 'mmap', '访问只读': 'ACCESS_READ', '访问写入': 'ACCESS_WRITE',
            '访问拷贝': 'ACCESS_COPY', '页大小': 'PAGESIZE', '分配': 'ALLOCATIONGRANULARITY',
            '长度': 'length', '偏移': 'offset', '标记': 'flags', '映射': 'map',
            '取消映射': 'unmap', '同步': 'flush', '锁定': 'lock', '解锁': 'unlock',
            
            # SQLite3扩展
            '连接': 'connect', '光标': 'Cursor', '执行': 'execute', '执行许多': 'executemany',
            '获取': 'fetchone', '获取全部': 'fetchall', '获取许多': 'fetchmany',
            '提交': 'commit', '回滚': 'rollback', '关闭': 'close', '行工厂': 'row_factory',
            '文本工厂': 'text_factory', '隔离级别': 'isolation_level',
            '完整结果': 'complete_statement', '版本': 'version', '线程安全': 'threadsafety',
            
            # UUID扩展
            'UUID': 'UUID', '生成1': 'uuid1', '生成3': 'uuid3', '生成4': 'uuid4', '生成5': 'uuid5',
            '空': 'nil', '十六进制': 'hex', '字符串': 'str', '字节': 'bytes', '字段': 'fields',
            '时间戳': 'timestamp', '时钟序列': 'clock_seq', '节点': 'node', 'URN': 'urn',
            '变体': 'variant', '版本': 'version',
            
            # 队列扩展
            '队列': 'Queue', '后进先出队列': 'LifoQueue', '优先级队列': 'PriorityQueue',
            '简单队列': 'SimpleQueue', '放入': 'put', '获取': 'get', '空': 'empty',
            '满': 'full', '任务完成': 'task_done', '加入': 'join', '大小': 'qsize',
            
            # 调度扩展
            '调度器': 'scheduler', '进入': 'enter', '进入绝对': 'enterabs',
            '取消': 'cancel', '空': 'empty', '运行': 'run', '队列': 'queue',
            
            # 运算符扩展
            '添加': 'add', '减法': 'sub', '乘法': 'mul', '除法': 'truediv', '整除': 'floordiv',
            '取余': 'mod', '幂': 'pow', '负数': 'neg', '正数': 'pos', '取反': 'not_',
            '绝对值': 'abs', '索引': 'index', '切片': 'getitem', '设置切片': 'setitem',
            '删除切片': 'delitem', '长度': 'len', '反转': 'reverse', '包含': 'contains',
            '相等': 'eq', '不等': 'ne', '小于': 'lt', '小于等于': 'le', '大于': 'gt',
            '大于等于': 'ge', '逻辑与': 'and_', '逻辑或': 'or_', '异或': 'xor',
            '位与': 'and_', '位或': 'or_', '位异或': 'xor', '位取反': 'invert',
            '左移': 'lshift', '右移': 'rshift',
            
            # 堆队列扩展
            '堆化': 'heapify', '弹出': 'heappop', '推入': 'heappush', '弹出推入': 'heapreplace',
            '推入弹出': 'heappushpop', '合并': 'merge', 'n最小': 'nsmallest', 'n最大': 'nlargest',
            
            # 二分查找扩展
            '二分查找': 'bisect', '二分查找左': 'bisect_left', '二分查找右': 'bisect_right',
            '插入': 'insort', '插入左': 'insort_left', '插入右': 'insort_right',
            
            # 复制扩展
            '复制': 'copy', '深复制': 'deepcopy',
            
            # 格式化打印扩展
            '打印': 'pprint', '格式化': 'pformat', '打印对象': 'pprint',
            '格式化对象': 'pformat', '安全表示': 'safe_repr', '排序字典': 'sorted',
            
            # 表示库扩展
            '表示': 'repr', '表示对象': 'repr', '最大字符串': 'MAXSTRING', '最大列表': 'MAXLIST',
            '最大集合': 'MAXSET', '最大字典': 'MAXDICT', '最大元组': 'MAXTUPLE',
            
            # 退出处理扩展
            '注册': 'register', '注销': 'unregister',
            
            # 文件名匹配扩展
            '匹配': 'fnmatch', '匹配大小写': 'fnmatchcase', '转换': 'translate',
            
            # 行缓存扩展
            '获取行': 'getline', '清除缓存': 'clearcache', '检查缓存': 'checkcache',
            '更新缓存': 'updatecache',
            
            # 运行模块扩展
            '运行模块': 'run_module', '运行路径': 'run_path',
            
            # 导入库扩展
            '导入模块': 'import_module', '重新加载': 'reload', '查找加载器': 'find_loader',
            '查找规范': 'find_spec', '导入': 'import_', '懒加载': 'lazy_load',
            '资源读取': 'resources', '文件读取': 'read_text', '二进制读取': 'read_binary',
            '路径': 'path', '文件': 'files',
            
            # 包工具扩展
            '迭代包': 'iter_modules', '迭代导入': 'walk_packages', '获取加载器': 'get_loader',
            '获取规范': 'get_spec', '资源字符串': 'get_resource_string',
            '资源文件名': 'get_resource_filename',
            
            # 统计扩展
            '均值': 'mean', '中位数': 'median', '中位数低': 'median_low',
            '中位数高': 'median_high', '中位数组': 'median_grouped', '模式': 'mode',
            '多模式': 'multimode', '方差': 'variance', '标准差': 'stdev',
            '总体方差': 'pvariance', '总体标准差': 'pstdev', '谐波均值': 'harmonic_mean',
            '几何均值': 'geometric_mean',
            
            # 文本包装扩展
            '包装': 'wrap', '填充': 'fill', '缩短': 'shorten', '文本包装器': 'TextWrapper',
            '宽度': 'width', '缩进': 'initial_indent', '后续缩进': 'subsequent_indent',
            '展开制表符': 'expand_tabs', '替换空白': 'replace_whitespace',
            '固定宽度': 'fix_sentence_endings', '分词': 'break_long_words',
            
            # 日历扩展
            '日历': 'calendar', '月历': 'month', '年历': 'year', '星期几': 'weekday',
            'ISO星期几': 'isoweekday', 'ISO日历': 'isocalendar', 'ISO周数': 'isoweeknum',
            '闰年': 'isleap', '闰年数': 'leapdays', '星期名称': 'day_name',
            '缩写星期名称': 'day_abbr', '月份名称': 'month_name', '缩写月份名称': 'month_abbr',
            '设置第一年': 'setfirstweekday', '获取第一年': 'firstweekday',
            '格式化月份': 'formatmonth', '格式化年份': 'formatyear',
            
            # 十进制扩展
            '十进制': 'Decimal', '上下文': 'getcontext', '设置上下文': 'setcontext',
            '本地上下文': 'localcontext', '无穷': 'Infinity', '负无穷': '-Infinity',
            '不是数字': 'NaN', '最大值': 'MAX_EMAX', '最小值': 'MIN_EMIN',
            '精度': 'precision', '四舍五入': 'rounding', '运算精度': 'prec',
            
            # 分数扩展
            '分数': 'Fraction', '分子': 'numerator', '分母': 'denominator',
            '限制分母': 'limit_denominator', '近似': 'from_float', '转换': 'to_float',
            
            # 差异比较扩展
            '差异': 'differ', '比较文件': 'compare', '统一差异': 'unified_diff',
            '上下文差异': 'context_diff', 'Html差异': 'HtmlDiff', '序列匹配': 'SequenceMatcher',
            '查找最佳匹配': 'get_close_matches', '.ndiff': 'ndiff', '恢复': 'restore',
            
            # 命令行选项扩展
            '获取选项': 'getopt', '长选项': 'gnu_getopt', '错误': 'GetoptError',
            
            # 获取密码扩展
            '获取密码': 'getpass', '获取用户名': 'getuser',
            
            # 命令行接口扩展
            '命令': 'Cmd', 'onecmd': 'onecmd', 'onecmd_plus_hooks': 'onecmd_plus_hooks',
            'emptyline': 'emptyline', 'default': 'default', 'completedefault': 'completedefault',
            'complete': 'complete', 'completenames': 'completenames',
            'help_command': 'help_command', 'do_help': 'do_help', 'do_quit': 'do_quit',
            'do_exit': 'do_exit', 'postloop': 'postloop', 'preloop': 'preloop',
            
            # 代码执行扩展
            '交互式控制台': 'InteractiveConsole', '交互式解释器': 'InteractiveInterpreter',
            '编译命令': 'compile_command', '运行代码': 'runcode', '交互': 'interact',
            
            # 代码操作扩展
            '编译': 'compile', '编译命令': 'compile_command',
            
            # 命令行解析扩展
            '分割': 'split', '引用': 'quote', '连接': 'join', '替换变量': 'substitute',
            '分割命令': 'split_command',
            
            # 性能分析扩展
            '运行': 'run', 'Profile': 'Profile', 'Stats': 'Stats', 'dump_stats': 'dump_stats',
            'load_stats': 'load_stats', '添加': 'add', '排序': 'sort_stats',
            '打印统计': 'print_stats', '打印调用者': 'print_callers', '打印被调用者': 'print_callees',
            
            # 计时扩展
            '时间': 'timeit', '重复': 'repeat', '默认计时器': 'default_timer',
            
            # 文档测试扩展
            '测试文档': 'testmod', '测试文件': 'testfile', '调试': 'debug',
            '报告失败': 'reportfailure', '结果': 'TestResults',
            
            # 单元测试扩展
            '测试用例': 'TestCase', '测试套件': 'TestSuite', '测试加载器': 'TestLoader',
            '测试运行器': 'TextTestRunner', '跳过': 'skip', '跳过如果': 'skipIf',
            '跳过除非': 'skipUnless', '预期失败': 'expectedFailure',
            '参数化': 'parameterized.expand', '子测试': 'subTest',
            '断言相等': 'assertEqual', '断言不相等': 'assertNotEqual',
            '断言真': 'assertTrue', '断言假': 'assertFalse',
            '断言几乎相等': 'assertAlmostEqual', '断言不几乎相等': 'assertNotAlmostEqual',
            '断言在': 'assertIn', '断言不在': 'assertNotIn',
            '断言是': 'assertIs', '断言不是': 'assertIsNot',
            '断言是无': 'assertIsNone', '断言不是无': 'assertIsNotNone',
            '断言调用': 'assertRaises', '断言调用匹配': 'assertRaisesRegex',
            '断言警告': 'assertWarns', '断言警告匹配': 'assertWarnsRegex',
            
            # 反汇编扩展
            '反汇编': 'dis', '反汇编字节码': 'disassemble', '反汇编函数': 'distb',
            '获取指令': 'get_instructions', '显示代码': 'show_code', '格式化指令': 'format_instructions',
            
            # AST扩展
            '解析': 'parse', '转储': 'dump', '固定位置': 'fix_missing_locations',
            '增量解析': 'incremental_parse', '编译': 'compile',
            
            # 抽象基类扩展
            '抽象方法': 'abstractmethod', '抽象属性': 'abstractproperty',
            'ABCMeta': 'ABCMeta', 'ABC': 'ABC',
            
            # 数字扩展
            '数字': 'Number', '复数': 'Complex', '实数': 'Real', '有理数': 'Rational',
            '整数': 'Integral',
            
            # SSL扩展
            '包装套接字': 'wrap_socket', 'SSL上下文': 'SSLContext', 'PROTOCOL_TLS': 'PROTOCOL_TLS',
            'PROTOCOL_TLS_CLIENT': 'PROTOCOL_TLS_CLIENT', 'PROTOCOL_TLS_SERVER': 'PROTOCOL_TLS_SERVER',
            '加载证书文件': 'load_cert_chain', '加载默认证书': 'load_default_certs',
            '设置密码': 'set_ciphers', '会话': 'session', '验证模式': 'verify_mode',
            '检查主机名': 'check_hostname', '服务器名称': 'server_hostname',
            
            # 邮件扩展
            '消息': 'Message', '邮箱地址': 'Address', '解析地址': 'parseaddr',
            '格式化地址': 'formataddr', '策略': 'policy', '默认策略': 'default_policy',
            '解析': 'message_from_string', '解析文件': 'message_from_file',
            '解析字节': 'message_from_bytes', '生成器': 'Generator', '序列化': 'serialize',
            
            # HTTP客户端扩展
            'HTTP连接': 'HTTPConnection', 'HTTPS连接': 'HTTPSConnection',
            '请求': 'request', '获取响应': 'getresponse', '连接': 'connect',
            '关闭': 'close', '设置超时': 'settimeout', '发送': 'send',
            
            # HTTP服务器扩展
            'HTTP服务器': 'HTTPServer', 'HTTP请求处理器': 'BaseHTTPRequestHandler',
            'SimpleHTTP请求处理器': 'SimpleHTTPRequestHandler',
            'CGIHTTP请求处理器': 'CGIHTTPRequestHandler',
            '端口': 'port', '主机': 'server_address', '请求队列大小': 'request_queue_size',
            '超时': 'timeout', '开启': 'serve_forever', '处理请求': 'handle_request',
        """

    # 替换旧的 attr_map
    new_attr_map = "        attr_map = {" + new_attrs + "\n        }"
    new_content = content[:attr_map_start] + new_attr_map + content[attr_map_end:]

    # 写回文件
    with open('g:/dumategithub/newlisp/.worktrees/v2-syntax/yan/v2/codegen.py', 'w', encoding='utf-8') as f:
        f.write(new_content)

    print("属性映射扩展完成")

if __name__ == "__main__":
    add_more_attr_maps()
