# © 2026 MirageShield 团队 版权所有，侵权必究
# 本项目已申请发明专利，未经许可禁止商用
# API接口
import json
import logging
import os
import sys
import threading
import time
import hashlib
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from functools import lru_cache
import jwt

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入日志管理蓝图
from api.logs import logs_bp
# 导入监控管理蓝图
from api.monitoring import monitoring_bp

# 输入验证函数
def validate_input(data, schema):
    """验证输入数据是否符合schema
    
    Args:
        data: 输入数据
        schema: 验证规则，格式为 {field: (required, type, max_length, min_value, max_value)}
            - required: 是否必填
            - type: 数据类型
            - max_length: 最大长度（适用于字符串、列表、字典）
            - min_value: 最小值（适用于数字类型，可选）
            - max_value: 最大值（适用于数字类型，可选）
    
    Returns:
        (valid, errors): (是否有效, 错误信息列表)
    """
    errors = []
    
    for field, schema_values in schema.items():
        # 兼容旧的schema格式
        if len(schema_values) == 3:
            required, field_type, max_length = schema_values
            min_value = None
            max_value = None
        else:
            required, field_type, max_length, min_value, max_value = schema_values
        
        value = data.get(field)
        
        # 检查是否必填
        if required and value is None:
            errors.append(f"{field} 是必填项")
            continue
        
        # 检查类型
        # 注意：isinstance函数支持元组作为第二个参数，表示检查value是否是元组中任一类型的实例
        if value is not None and not isinstance(value, field_type):
            # 构建期望类型的描述
            if isinstance(field_type, tuple):
                expected_types = ', '.join(t.__name__ for t in field_type)
            else:
                expected_types = field_type.__name__
            errors.append(f"{field} 类型错误，期望 {expected_types}")
            continue
        
        # 检查长度（包括嵌套结构）
        if max_length is not None:
            def get_depth(obj, current_depth=0):
                if isinstance(obj, (list, dict)):
                    if current_depth >= max_length:
                        return current_depth
                    if isinstance(obj, list):
                        return max(get_depth(item, current_depth + 1) for item in obj) if obj else current_depth
                    else:
                        return max(get_depth(v, current_depth + 1) for v in obj.values()) if obj else current_depth
                return current_depth
            
            depth = get_depth(value)
            if depth > max_length:
                errors.append(f"{field} 深度不能超过 {max_length}")
        
        # 检查数字范围
        if value is not None and isinstance(value, (int, float)):
            if min_value is not None and value < min_value:
                errors.append(f"{field} 不能小于 {min_value}")
            if max_value is not None and value > max_value:
                errors.append(f"{field} 不能大于 {max_value}")
    
    return len(errors) == 0, errors

# 重试装饰器
def retry(max_attempts=3, delay=1, backoff=2, exceptions=(Exception,), timeout=None):
    """重试装饰器
    
    Args:
        max_attempts: 最大重试次数
        delay: 初始延迟时间（秒）
        backoff: 延迟倍数
        exceptions: 重试的异常类型
        timeout: 单次调用的最大时间（秒）
    
    Returns:
        装饰后的函数
    """
    def decorator(func):
        import asyncio
        import concurrent.futures
        import functools
        
        # 检查函数是否为异步函数
        is_async = asyncio.iscoroutinefunction(func)
        
        if is_async:
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                attempts = 0
                current_delay = delay
                while attempts < max_attempts:
                    try:
                        if timeout:
                            # 使用asyncio.wait_for实现超时控制
                            return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout)
                        else:
                            # 无超时控制
                            return await func(*args, **kwargs)
                    except exceptions as e:
                        attempts += 1
                        if attempts == max_attempts:
                            logger.error(f"函数 {func.__name__} 重试 {max_attempts} 次后失败: {str(e)}")
                            raise
                        logger.warning(f"函数 {func.__name__} 执行失败，{current_delay} 秒后重试: {str(e)}")
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                attempts = 0
                current_delay = delay
                while attempts < max_attempts:
                    try:
                        if timeout:
                            # 使用ThreadPoolExecutor实现超时控制
                            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                                future = executor.submit(func, *args, **kwargs)
                                try:
                                    return future.result(timeout=timeout)
                                except concurrent.futures.TimeoutError:
                                    raise TimeoutError(f"函数 {func.__name__} 执行超时")
                        else:
                            # 无超时控制
                            return func(*args, **kwargs)
                    except exceptions as e:
                        attempts += 1
                        if attempts == max_attempts:
                            logger.error(f"函数 {func.__name__} 重试 {max_attempts} 次后失败: {str(e)}")
                            raise
                        logger.warning(f"函数 {func.__name__} 执行失败，{current_delay} 秒后重试: {str(e)}")
                        import time
                        time.sleep(current_delay)
                        current_delay *= backoff
            return sync_wrapper
    return decorator

# 导入消息队列管理器
from utils.message_queue import message_queue_manager, MockMessageQueueManager

# 配置日志
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'mirageshield.log')

# 异步日志处理器
class AsyncRotatingFileHandler(logging.Handler):
    """异步日志处理器，使用线程池处理日志写入"""
    def __init__(self, filename, maxBytes=0, backupCount=0, encoding=None, delay=False, queue_size=1000):
        super().__init__()
        self.filename = filename
        self.maxBytes = maxBytes
        self.backupCount = backupCount
        self.encoding = encoding
        self.delay = delay
        self.queue_size = queue_size
        self.file_handler = RotatingFileHandler(
            filename, maxBytes=maxBytes, backupCount=backupCount, encoding=encoding, delay=delay
        )
        # 创建队列和线程池
        import queue
        import concurrent.futures
        self.log_queue = queue.Queue(maxsize=queue_size)
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        # 启动日志处理线程
        self._running = True
        self.executor.submit(self._process_logs)
    
    def setFormatter(self, fmt):
        super().setFormatter(fmt)
        self.file_handler.setFormatter(fmt)
    
    def setLevel(self, level):
        super().setLevel(level)
        self.file_handler.setLevel(level)
    
    def _process_logs(self):
        """处理队列中的日志"""
        while self._running:
            try:
                # 从队列中获取日志，超时1秒
                record = self.log_queue.get(timeout=1)
                if record is None:
                    break
                try:
                    self.file_handler.emit(record)
                except Exception:
                    self.handleError(record)
                finally:
                    self.log_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"处理日志时出错: {str(e)}")
    
    def emit(self, record):
        """异步发送日志记录"""
        try:
            # 尝试将日志放入队列，队列满时使用阻塞策略
            self.log_queue.put(record, block=True, timeout=1)
        except queue.Full:
            # 队列满时，直接同步写入
            try:
                self.file_handler.emit(record)
            except Exception:
                self.handleError(record)
    
    def close(self):
        """关闭处理器"""
        try:
            # 停止日志处理
            self._running = False
            # 向队列中添加None作为结束信号
            self.log_queue.put(None, block=True, timeout=1)
            # 等待队列处理完成
            self.log_queue.join()
        except Exception as e:
            logger.error(f"关闭日志队列时出错: {str(e)}")
        
        try:
            if hasattr(self, 'executor') and self.executor:
                self.executor.shutdown(wait=True, cancel_futures=True)
                logger.info("异步日志处理器线程池已关闭")
        except Exception as e:
            logger.error(f"关闭异步日志处理器线程池时出错: {str(e)}")
        
        try:
            if hasattr(self, 'file_handler') and self.file_handler:
                self.file_handler.close()
                logger.info("日志文件处理器已关闭")
        except Exception as e:
            logger.error(f"关闭日志文件处理器时出错: {str(e)}")
        
        super().close()

# 配置根日志记录器
root_logger = logging.getLogger()
# 根据环境设置日志级别
flask_env = os.environ.get('FLASK_ENV', 'development')
if flask_env == 'production':
    root_logger.setLevel(logging.WARNING)
else:
    root_logger.setLevel(logging.INFO)

# 控制台处理器
console_handler = logging.StreamHandler()
if flask_env == 'production':
    console_handler.setLevel(logging.WARNING)
else:
    console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(name)s:%(funcName)s:%(lineno)d - %(message)s')
console_handler.setFormatter(console_formatter)

# 异步文件处理器
from logging.handlers import RotatingFileHandler
file_handler = AsyncRotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8')
if flask_env == 'production':
    file_handler.setLevel(logging.WARNING)
else:
    file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(name)s:%(funcName)s:%(lineno)d - %(message)s')
file_handler.setFormatter(file_formatter)

# 清除现有处理器并添加新处理器
root_logger.handlers = []
root_logger.addHandler(console_handler)
root_logger.addHandler(file_handler)

logger = logging.getLogger('api.app')

# 创建Flask应用
app = Flask(__name__, static_folder='../ui', static_url_path='/ui')

# 确保Flask应用支持异步路由
app.config['DEBUG'] = False

# 启用CORS
CORS(app)

# 认证相关配置
# 获取环境变量
flask_env = os.environ.get('FLASK_ENV', 'development')
secret_key = os.environ.get('SECRET_KEY')

# 密钥存储文件路径
SECRET_KEY_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'secret_key.json')

# 加载保存的密钥
if not secret_key and os.path.exists(SECRET_KEY_FILE):
    try:
        with open(SECRET_KEY_FILE, 'r', encoding='utf-8') as f:
            secret_data = json.load(f)
            secret_key = secret_data.get('secret_key')
    except Exception as e:
        logger.error(f"加载密钥文件失败: {str(e)}")

# 生产环境强制要求设置SECRET_KEY
if flask_env == 'production':
    if not secret_key:
        logger.error('生产环境必须设置SECRET_KEY环境变量')
        raise ValueError('生产环境必须设置SECRET_KEY环境变量')
    # 检查密钥长度
    if len(secret_key) < 32:
        logger.error('生产环境SECRET_KEY长度必须至少为32个字符')
        raise ValueError('生产环境SECRET_KEY长度必须至少为32个字符')
else:
    # 开发环境使用随机生成的密钥
    if not secret_key:
        import secrets
        secret_key = secrets.token_urlsafe(32)
        logger.warning('未设置SECRET_KEY环境变量，使用随机生成的开发环境密钥。生产环境请设置环境变量。')
        # 保存密钥到文件
        try:
            with open(SECRET_KEY_FILE, 'w', encoding='utf-8') as f:
                json.dump({'secret_key': secret_key, 'generated_at': datetime.utcnow().isoformat()}, f, indent=2)
        except Exception as e:
            logger.error(f"保存密钥文件失败: {str(e)}")

app.config['SECRET_KEY'] = secret_key
app.config['JWT_EXPIRATION_DELTA'] = timedelta(hours=1)  # 缩短访问令牌有效期，提高安全性
app.config['JWT_REFRESH_EXPIRATION_DELTA'] = timedelta(days=7)  # 刷新令牌有效期

# 导入认证模块
from api.auth import register_auth_routes, require_auth
# 注册认证相关接口
register_auth_routes(app)

# 注册日志管理蓝图
app.register_blueprint(logs_bp)
# 注册监控管理蓝图
app.register_blueprint(monitoring_bp)
# 注册硬件管理蓝图
from api.hardware import hardware_bp
app.register_blueprint(hardware_bp)

# 应用初始化标志
_executor_initialized = False
_cache_cleanup_started = False
_message_queue_started = False

# 消息队列线程相关变量
_message_queue_thread = None
_message_queue_lock = threading.Lock()  # 使用Lock避免重入问题
_message_queue_initialized = threading.Event()  # 使用Event确保线程安全
# 使用Event实现更健壮的同步机制，避免潜在死锁
_message_queue_ready = threading.Event()  # 消息队列线程初始化完成标志

# 初始化应用组件
def initialize_app():
    """初始化应用组件"""
    global _executor_initialized, _cache_cleanup_started, _message_queue_started, _message_queue_thread
    
    # 初始化线程池
    if not _executor_initialized:
        init_executor()
        _executor_initialized = True
        logger.info("应用启动时线程池初始化完成")
    
    # 启动缓存清理任务
    if not _cache_cleanup_started:
        start_cache_cleanup_task()
        _cache_cleanup_started = True
    
    # 初始化消息队列
    if not _message_queue_initialized.is_set():
        with _message_queue_lock:
            if not _message_queue_initialized.is_set():
                # 声明全局变量
                global message_queue_manager
                
                # 注册智能体到消息队列
                message_queue_manager.register_agent('prober')
                message_queue_manager.register_agent('baiter')
                message_queue_manager.register_agent('watcher')
                
                # 线程初始化状态
                init_success = False
                
                # 启动消息处理（在单独的线程中运行）
                def start_message_queue():
                    nonlocal init_success
                    import asyncio
                    import traceback
                    loop = None
                    try:
                        # 在新线程中创建并运行事件循环
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        # 运行消息队列处理
                        loop.run_until_complete(message_queue_manager.start_processing())
                        logger.info("消息队列线程初始化完成")
                        init_success = True
                    except Exception as e:
                        logger.error(f"消息队列启动失败: {str(e)}")
                        logger.error(f"异常堆栈: {traceback.format_exc()}")
                        init_success = False
                    finally:
                        # 标记消息队列初始化完成
                        _message_queue_ready.set()
                        # 清理事件循环
                        if loop:
                            try:
                                loop.close()
                            except Exception as close_error:
                                logger.error(f"关闭事件循环时出错: {str(close_error)}")
                        logger.info("消息队列线程初始化流程完成")
                
                # 重置事件状态
                _message_queue_ready.clear()
                
                # 创建并启动消息队列线程
                _message_queue_thread = threading.Thread(target=start_message_queue, daemon=True)
                _message_queue_thread.start()
                
                # 等待消息队列线程初始化完成，最多等待5秒
                if _message_queue_ready.wait(timeout=5.0):
                    if init_success:
                        logger.info("消息队列初始化完成")
                        _message_queue_initialized.set()  # 标记消息队列已初始化
                        _message_queue_started = True
                        logger.info("消息队列管理器初始化完成并开始处理消息")
                    else:
                        logger.warning("消息队列初始化失败，继续启动应用")
                        _message_queue_started = False
                        # 消息队列初始化失败时，创建一个模拟的消息队列管理器
                        message_queue_manager = MockMessageQueueManager()
                        logger.info("已创建模拟消息队列管理器")
                else:
                    logger.warning("消息队列初始化超时，继续启动应用")
                    _message_queue_started = False
                    # 消息队列初始化超时时，创建一个模拟的消息队列管理器
                    message_queue_manager = MockMessageQueueManager()
                    logger.info("已创建模拟消息队列管理器")

# 定义降级类
class MockLANDiscovery:
    def start(self):
        logger.warning("使用模拟LANDiscovery")
    def stop(self):
        pass
    def get_nodes(self):
        return []
    def get_node_by_ip(self, ip):
        return None
    def clear_nodes(self):
        pass

class MockSecureCommunication:
    def start_server(self):
        logger.warning("使用模拟SecureCommunication")
    def stop_server(self):
        pass
    def connect_to_node(self, ip, port):
        return None
    def get_connections(self):
        return []
    def send_message(self, client_id, message):
        return False

class MockDataTransferManager:
    def send_data(self, target_node, data_id, data, chunk_size=1024 * 1024):
        return None
    def get_transfer_status(self, transfer_id):
        return None
    def get_all_transfers(self):
        return []
    def pause_transfer(self, transfer_id):
        return False
    def resume_transfer(self, transfer_id):
        return False
    def cancel_transfer(self, transfer_id):
        return False
    def get_transfer_statistics(self):
        return {}

# 导入缓存工具
from utils.cache import cached, clear_cache, cleanup_expired_cache

# 导入系统组件
try:
    from control_plane.strategy_engine import StrategyEngine
    from control_plane.security_assessment import SecurityAssessmentModule
    from control_plane.layered_defense import layered_defense_manager
    from data_plane.real_data_pool import RealDataPool
    from data_plane.decoy_data_pool import DecoyDataPool
    from data_plane.virtual_network_layer import VirtualNetworkLayer
    from community.joint_defense_interface import CommunityDefenseInterface
    from agents.ai1.explorer import ProberAgent
    from agents.ai2.baiter import BaiterAgent
    from agents.ai3.watcher import WatcherAgent
    
    # 导入网络模块，添加异常处理
    try:
        from network.lan_discovery import LANDiscovery
        from network.secure_communication import SecureCommunication
        from network.data_transfer import DataTransferManager
        network_modules_available = True
    except ImportError as e:
        logger.warning(f"网络模块导入失败: {str(e)}")
        LANDiscovery = MockLANDiscovery
        SecureCommunication = MockSecureCommunication
        DataTransferManager = MockDataTransferManager
        network_modules_available = False
        logger.warning("网络模块不可用，使用降级方案")
    
    # 加载配置文件
    config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config')
    
    with open(os.path.join(config_dir, 'prober_config.json'), 'r', encoding='utf-8') as f:
        prober_config = json.load(f)
    
    with open(os.path.join(config_dir, 'baiter_config.json'), 'r', encoding='utf-8') as f:
        baiter_config = json.load(f)
    
    with open(os.path.join(config_dir, 'watcher_config.json'), 'r', encoding='utf-8') as f:
        watcher_config = json.load(f)
    
    # 初始化系统组件
    strategy_engine = StrategyEngine()
    security_assessment = SecurityAssessmentModule()
    real_data_pool = RealDataPool()
    decoy_data_pool = DecoyDataPool()
    virtual_network = VirtualNetworkLayer()
    community_interface = CommunityDefenseInterface()
    
    # 初始化局域网相关组件
    try:
        lan_discovery = LANDiscovery()
        secure_communication = SecureCommunication()
        data_transfer_manager = DataTransferManager(secure_communication)

        # 启动局域网发现和安全通信服务
        lan_discovery.start()
        secure_communication.start_server()
        logger.info("局域网相关组件初始化和启动成功")
    except Exception as e:
        logger.error(f"局域网相关组件初始化或启动失败: {str(e)}")
        # 使用全局降级类
        lan_discovery = MockLANDiscovery()
        secure_communication = MockSecureCommunication()
        data_transfer_manager = MockDataTransferManager()
        logger.warning("网络服务启动失败，使用降级方案")

    # 初始化智能体
    prober_agent = ProberAgent(prober_config)
    baiter_agent = BaiterAgent(baiter_config)
    watcher_agent = WatcherAgent(os.path.join(config_dir, 'watcher_config.json'))
    
    logger.info("系统组件初始化完成")
    
except Exception as e:
    logger.error(f"系统组件初始化失败: {str(e)}")
    raise

# 缓存清理定时任务
_cache_cleanup_interval = 300  # 每5分钟清理一次，优化清理间隔
_cache_cleanup_thread = None
_cache_cleanup_running = False

# 启动缓存清理定时任务
def start_cache_cleanup_task():
    """启动缓存清理定时任务"""
    global _cache_cleanup_thread, _cache_cleanup_running
    _cache_cleanup_running = True
    
    def cleanup_task():
        """缓存清理任务"""
        while _cache_cleanup_running:
            try:
                cleanup_expired_cache()
                # 等待指定的时间间隔
                import time
                time.sleep(_cache_cleanup_interval)
            except Exception as e:
                logger.error(f"缓存清理任务出错: {str(e)}")
    
    _cache_cleanup_thread = threading.Thread(target=cleanup_task, daemon=True)
    _cache_cleanup_thread.start()
    logger.info(f"缓存清理定时任务已启动，每 {_cache_cleanup_interval} 秒执行一次")

# 停止缓存清理定时任务
def stop_cache_cleanup_task():
    """停止缓存清理定时任务"""
    global _cache_cleanup_running, _cache_cleanup_thread
    if _cache_cleanup_running:
        _cache_cleanup_running = False
        if _cache_cleanup_thread:
            _cache_cleanup_thread.join(timeout=5)
        logger.info("缓存清理定时任务已停止")

# 健康检查
@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "MirageShield API"
    })

# 全局线程池变量
executor = None
_executor_max_workers = 0

# 任务优先级枚举
class TaskPriority:
    HIGH = 0
    MEDIUM = 1
    LOW = 2

# 带优先级的任务类
class PriorityTask:
    def __init__(self, priority, func, *args, **kwargs):
        self.priority = priority
        self.func = func
        self.args = args
        self.kwargs = kwargs
    
    def __lt__(self, other):
        return self.priority > other.priority

# 初始化线程池
def init_executor():
    """初始化线程池"""
    global executor, _executor_max_workers
    if not executor:
        logger.info("初始化线程池...")
        
        # 初始化线程池，根据CPU核心数设置线程数
        import concurrent.futures
        import os
        import threading
        import queue
        
        # 动态计算线程池大小
        cpu_count = os.cpu_count() or 4
        # 根据系统负载动态调整线程数
        try:
            import psutil
            try:
                cpu_percent = psutil.cpu_percent(interval=1)
                if cpu_percent > 70:
                    # 高负载时减少线程数
                    max_workers = max(1, cpu_count * 2)
                else:
                    # 正常负载时使用默认线程数
                    max_workers = cpu_count * 3
            except Exception as e:
                logger.warning(f"获取系统负载失败: {str(e)}，使用默认线程数")
                max_workers = cpu_count * 3
        except ImportError:
            logger.warning("psutil模块未安装，使用默认线程数")
            max_workers = cpu_count * 3
        
        _executor_max_workers = max_workers
        executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=max_workers, 
            thread_name_prefix='strategy_update'
        )
        logger.info(f"线程池初始化完成，最大工作线程数: {max_workers}")

# 优先级任务队列
import queue
import threading
priority_task_queue = queue.PriorityQueue()
dead_letter_queue = queue.Queue()  # 死信队列，用于存储失败的任务
priority_task_thread = None
priority_task_running = False
priority_task_stop_event = threading.Event()  # 用于控制任务线程优雅退出

# 处理优先级任务的线程函数
def process_priority_tasks():
    """处理优先级任务"""
    global priority_task_queue, priority_task_running, executor
    priority_task_running = True
    priority_task_stop_event.clear()  # 重置停止事件
    logger.info("优先级任务处理线程已启动")
    
    while not priority_task_stop_event.is_set():
        task = None
        try:
            # 从队列中获取任务，超时1秒
            task = priority_task_queue.get(timeout=1)
            if task is None:
                break
            
            # 确保线程池已初始化
            if not executor:
                init_executor()
            
            # 添加重试逻辑
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries and not priority_task_stop_event.is_set():
                try:
                    # 提交任务到线程池
                    future = executor.submit(task.func, *task.args, **task.kwargs)
                    # 等待任务完成，获取结果
                    future.result()
                    # 任务成功完成
                    priority_task_queue.task_done()
                    break
                except Exception as e:
                    retry_count += 1
                    logger.error(f"处理优先级任务时出错 (尝试 {retry_count}/{max_retries}): {str(e)}")
                    if retry_count < max_retries:
                        # 等待一段时间后重试
                        import time
                        time.sleep(1 * retry_count)  # 指数退避
                    else:
                        # 达到最大重试次数，将任务放入死信队列
                        logger.error(f"任务达到最大重试次数，放入死信队列")
                        dead_letter_queue.put((task, e))
                        priority_task_queue.task_done()
        except queue.Empty:
            continue
        except Exception as e:
            logger.error(f"处理优先级任务队列时出错: {str(e)}")
        finally:
            # 确保在任务被取出的情况下调用task_done()
            if task is not None:
                try:
                    priority_task_queue.task_done()
                except ValueError:
                    # 避免重复调用task_done()
                    pass
    
    # 处理完所有剩余任务
    logger.info("开始处理剩余任务...")
    while not priority_task_queue.empty() and not priority_task_stop_event.is_set():
        try:
            task = priority_task_queue.get(timeout=1)
            if task is None:
                break
            
            # 确保线程池已初始化
            if not executor:
                init_executor()
            
            # 提交任务到线程池
            future = executor.submit(task.func, *task.args, **task.kwargs)
            # 等待任务完成，获取结果
            future.result()
            # 任务成功完成
            priority_task_queue.task_done()
        except queue.Empty:
            break
        except Exception as e:
            logger.error(f"处理剩余任务时出错: {str(e)}")
            # 标记任务为完成，避免队列阻塞
            try:
                priority_task_queue.task_done()
            except:
                pass
    
    priority_task_running = False
    logger.info("优先级任务处理线程已停止")

# 停止优先级任务处理线程
def stop_priority_task_thread():
    """停止优先级任务处理线程"""
    global priority_task_stop_event, priority_task_running
    if priority_task_running:
        logger.info("停止优先级任务处理线程...")
        priority_task_stop_event.set()
        # 等待线程结束
        if priority_task_thread:
            priority_task_thread.join(timeout=5)
        logger.info("优先级任务处理线程已停止")

# 启动优先级任务处理线程
def start_priority_task_thread():
    """启动优先级任务处理线程"""
    global priority_task_thread, priority_task_running
    if not priority_task_running:
        import threading
        priority_task_thread = threading.Thread(target=process_priority_tasks, daemon=True)
        priority_task_thread.start()
        logger.info("优先级任务处理线程已启动")

# 提交优先级任务
def submit_priority_task(priority, func, *args, **kwargs):
    """提交带优先级的任务"""
    # 启动优先级任务处理线程
    start_priority_task_thread()
    
    # 创建优先级任务
    task = PriorityTask(priority, func, *args, **kwargs)
    # 将任务添加到优先级队列
    priority_task_queue.put(task)
    logger.debug(f"提交优先级任务，优先级: {priority}")
    return task

# 应用启动时执行初始化
logger.info("应用启动时开始初始化组件...")
initialize_app()
# 初始化用户数据，生成管理员密码
logger.info("初始化用户数据...")
from api.auth import load_users
load_users()

# 连接频率限制相关变量
connection_rate_limit = {}
connection_rate_limit_lock = threading.Lock()
# 连接频率限制存储文件
CONNECTION_RATE_LIMIT_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'connection_rate_limit.json')
# 连接频率限制文件锁
connection_rate_limit_file_lock = threading.Lock()

# 保存连接频率限制
def save_connection_rate_limit():
    """保存连接频率限制数据"""
    try:
        # 确保数据目录存在
        os.makedirs(os.path.dirname(CONNECTION_RATE_LIMIT_FILE), exist_ok=True)
        # 清理过期数据后保存
        current_time = time.time()
        data_to_save = {}
        with connection_rate_limit_lock:
            for ip, timestamps in connection_rate_limit.items():
                # 只保存1分钟内的记录
                recent_timestamps = [ts for ts in timestamps if current_time - ts < 60]
                if recent_timestamps:
                    data_to_save[ip] = recent_timestamps
        # 保存到文件
        with connection_rate_limit_file_lock:
            with open(CONNECTION_RATE_LIMIT_FILE, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, indent=2)
        logger.info(f"保存连接频率限制数据成功，共 {len(data_to_save)} 条记录")
    except Exception as e:
        logger.error(f"保存连接频率限制数据失败: {str(e)}")

# 定期保存连接频率限制的任务
def start_connection_rate_limit_save_task():
    """启动定期保存连接频率限制的任务"""
    def save_task():
        while True:
            try:
                save_connection_rate_limit()
                # 每30秒保存一次
                time.sleep(30)
            except Exception as e:
                logger.error(f"保存连接频率限制任务出错: {str(e)}")
                time.sleep(30)
    
    # 启动保存任务线程
    save_thread = threading.Thread(target=save_task, daemon=True)
    save_thread.start()
    logger.info("定期保存连接频率限制的任务已启动")

# 定义加载连接频率限制函数
def load_connection_rate_limit():
    """加载连接频率限制数据"""
    global connection_rate_limit
    try:
        if os.path.exists(CONNECTION_RATE_LIMIT_FILE):
            with connection_rate_limit_file_lock:
                with open(CONNECTION_RATE_LIMIT_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 转换时间戳字符串为浮点数
                    with connection_rate_limit_lock:
                        for ip, timestamps in data.items():
                            connection_rate_limit[ip] = [float(ts) for ts in timestamps]
            logger.info(f"加载连接频率限制数据成功，共 {len(connection_rate_limit)} 条记录")
    except Exception as e:
        logger.error(f"加载连接频率限制数据失败: {str(e)}")

# 加载连接频率限制数据
logger.info("加载连接频率限制数据...")
load_connection_rate_limit()
# 启动定期保存连接频率限制的任务
logger.info("启动定期保存连接频率限制的任务...")
start_connection_rate_limit_save_task()
logger.info("应用组件初始化完成")

# 应用启动钩子（仅用于确保初始化）
@app.before_request
def ensure_initialization():
    """确保应用组件已初始化"""
    global _executor_initialized, _cache_cleanup_started, _message_queue_started
    if not _executor_initialized or not _cache_cleanup_started or not _message_queue_started:
        initialize_app()



# 根路径重定向到UI
@app.route('/')
def index():
    """根路径重定向到UI"""
    return app.send_static_file('index.html')

# 智能体相关接口
@app.route('/api/agents', methods=['GET'])
@require_auth
@cached(timeout=300)  # 缓存5分钟，智能体列表不常变化
def get_agents():
    """获取智能体列表"""

    agents = [
        {
            "name": "prober",
            "type": "AI-1",
            "description": "负责数据采集和安全传输"
        },
        {
            "name": "baiter",
            "type": "AI-2",
            "description": "负责假数据生成和蜜罐管理"
        },
        {
            "name": "watcher",
            "type": "AI-3",
            "description": "负责监控和分析"
        }
    ]
    return jsonify(agents)

@app.route('/api/agents/<agent_name>/status', methods=['GET'])
@require_auth
@cached(timeout=30)  # 缓存30秒，智能体状态可能会变化

def get_agent_status(agent_name):
    """获取智能体状态"""

    try:
        status = strategy_engine.get_agent_states().get(agent_name, {})
        return jsonify(status)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 策略相关接口
@app.route('/api/strategy', methods=['GET'])
@require_auth
@cached(timeout=30)  # 缓存30秒，策略可能会变化

def get_strategy():
    """获取当前策略"""
    try:
        strategy = strategy_engine.get_current_strategy()
        return jsonify(strategy)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/strategy', methods=['POST'])
@require_auth
def update_strategy():
    """更新策略"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "请求数据不能为空"}), 400
        
        # 验证输入数据
        schema = {
            'threat_assessment': (True, dict, 10000)
        }
        valid, errors = validate_input(data, schema)
        if not valid:
            return jsonify({"error": "输入验证失败", "errors": errors}), 400
        
        threat_assessment = data.get('threat_assessment', {})
        strategy = strategy_engine.update_strategy(threat_assessment)
        # 清除相关缓存
        clear_cache(['get_strategy', 'get_system_status'])
        return jsonify(strategy)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 安全评估相关接口
@app.route('/api/assessment', methods=['POST'])
@require_auth
def assess_threat():
    """评估威胁"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "请求数据不能为空"}), 400
        
        # 验证输入数据
        schema = {
            'attacker_info': (True, dict, 10000)
        }
        valid, errors = validate_input(data, schema)
        if not valid:
            return jsonify({"error": "输入验证失败", "errors": errors}), 400
        
        attacker_info = data.get('attacker_info', {})
        assessment = security_assessment.assess_threat(attacker_info)
        
        # 异步更新策略
        def update_strategy_async():
            try:
                strategy_engine.update_strategy(assessment)
                # 清除相关缓存
                clear_cache(['get_strategy', 'get_system_status'])
                logger.info("策略更新成功")
                return True
            except Exception as e:
                logger.error(f"策略更新失败: {str(e)}")
                raise
        
        # 使用优先级任务提交
        future = submit_priority_task(TaskPriority.HIGH, update_strategy_async)
        
        def handle_future_result(future):
            try:
                future.result()  # 触发异常
            except Exception as e:
                logger.error(f"线程池任务执行异常: {str(e)}")
        
        future.add_done_callback(handle_future_result)
        
        # 返回评估结果
        return jsonify(assessment)
    except Exception as e:
        logger.error(f"评估或策略更新失败: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/assessment/history', methods=['GET'])
@require_auth
def get_assessment_history():
    """获取评估历史"""
    try:
        history = security_assessment.get_assessment_history()
        return jsonify(history)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 数据存储相关接口
@app.route('/api/data/real', methods=['POST'])
@require_auth
def store_real_data():
    """存储真实数据"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "请求数据不能为空"}), 400
        
        # 验证输入数据
        schema = {
            'data': (True, (dict, list), 100000),
            'data_type': (False, str, 100),
            'agent_name': (False, str, 100)
        }
        valid, errors = validate_input(data, schema)
        if not valid:
            return jsonify({"error": "输入验证失败", "errors": errors}), 400
        
        data_content = data.get('data', {})
        data_type = data.get('data_type', 'unknown')
        agent_name = data.get('agent_name', 'prober')
        
        data_id = real_data_pool.store_data(data_content, data_type, agent_name)
        return jsonify({"data_id": data_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/data/real/<data_id>', methods=['GET'])
@require_auth
def get_real_data(data_id):
    """获取真实数据"""
    try:
        agent_name = request.args.get('agent_name', 'prober')
        data = real_data_pool.retrieve_data(data_id, agent_name)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/data/decoy', methods=['POST'])
@require_auth
def store_decoy_data():
    """存储诱饵数据"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "请求数据不能为空"}), 400
        
        # 验证输入数据
        schema = {
            'data': (True, (dict, list), 100000),
            'data_type': (False, str, 100),
            'agent_name': (False, str, 100),
            'watermark': (False, str, 1000)
        }
        valid, errors = validate_input(data, schema)
        if not valid:
            return jsonify({"error": "输入验证失败", "errors": errors}), 400
        
        data_content = data.get('data', {})
        data_type = data.get('data_type', 'unknown')
        agent_name = data.get('agent_name', 'baiter')
        watermark = data.get('watermark')
        
        data_id = decoy_data_pool.store_data(data_content, data_type, agent_name, watermark)
        return jsonify({"data_id": data_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/data/decoy/<data_id>', methods=['GET'])
@require_auth
def get_decoy_data(data_id):
    """获取诱饵数据"""
    try:
        agent_name = request.args.get('agent_name', 'baiter')
        data = decoy_data_pool.retrieve_data(data_id, agent_name)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 网络相关接口
@app.route('/api/network/topology', methods=['GET'])
@require_auth
@cached(timeout=60)  # 缓存1分钟，网络拓扑不常变化

def get_network_topology():
    """获取网络拓扑"""

    try:
        topology = virtual_network.get_network_topology()
        return jsonify(topology)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/network/health', methods=['GET'])
@require_auth
@cached(timeout=30)  # 缓存30秒，网络健康状态可能会变化

def get_network_health():
    """获取网络健康状态"""
    try:
        health = virtual_network.check_network_health()
        return jsonify(health)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/network/rotate_ips', methods=['POST'])
@require_auth
def rotate_ips():
    """执行IP轮换"""
    try:
        result = virtual_network.rotate_ips()
        # 清除相关缓存
        clear_cache(['get_network', 'get_system_status'])
        return jsonify({"success": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/network/reconstruct', methods=['POST'])
@require_auth
def reconstruct_network():
    """执行网络整建迁移"""
    try:
        result = virtual_network.reconstruct_network()
        # 清除相关缓存
        clear_cache(['get_network', 'get_system_status'])
        return jsonify({"success": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 社区联防相关接口
@app.route('/api/community/sync', methods=['POST'])
@require_auth
@retry(max_attempts=3, delay=2, backoff=2, exceptions=(Exception,))
def sync_with_community():
    """与社区同步"""
    try:
        # 验证请求数据
        data = request.get_json(force=True, silent=True) or {}
        logger.info(f"开始与社区同步，请求数据: {data}")
        
        # 直接调用同步方法，避免异步调用的复杂性
        result = community_interface.sync_with_community()
        
        # 清除相关缓存
        clear_cache(['get_blacklist', 'get_threat_intel', 'get_system_status'])
        
        logger.info(f"与社区同步成功: {result}")
        return jsonify({"success": result})
    except Exception as e:
        # 处理所有异常
        error_msg = f"与社区同步失败: {str(e)}"
        logger.error(error_msg, exc_info=True)  # 记录完整的异常堆栈
        return jsonify({"error": error_msg}), 500  # 500 Internal Server Error

@app.route('/api/community/blacklist', methods=['GET'])
@require_auth
@cached(timeout=300)  # 缓存5分钟，黑名单不常变化

def get_blacklist():
    """获取黑名单"""
    try:
        blacklist = community_interface.get_blacklist()
        return jsonify(blacklist)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/community/threats', methods=['GET'])
@require_auth
@cached(timeout=300)  # 缓存5分钟，威胁情报不常变化

def get_threat_intel():
    """获取威胁情报"""
    try:
        threat_intel = community_interface.get_threat_intel()
        return jsonify(threat_intel)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 系统状态接口
@app.route('/api/system/status', methods=['GET'])
@require_auth
@cached(timeout=30)  # 缓存30秒，系统状态可能会变化

def get_system_status():
    """获取系统状态"""
    try:
        # 定义异步函数处理并行任务
        import asyncio
        async def get_status():
            # 并行获取各组件状态
            loop = asyncio.get_event_loop()
            
            # 提交并行任务
            network_health_task = loop.run_in_executor(None, virtual_network.check_network_health)
            sync_status_task = loop.run_in_executor(None, community_interface.get_sync_status)
            agent_states_task = loop.run_in_executor(None, strategy_engine.get_agent_states)
            current_strategy_task = loop.run_in_executor(None, strategy_engine.get_current_strategy)
            
            # 等待所有任务完成，使用return_exceptions=True确保部分失败不影响整体
            results = await asyncio.gather(
                network_health_task,
                sync_status_task,
                agent_states_task,
                current_strategy_task,
                return_exceptions=True
            )
            
            # 处理任务结果，即使部分任务失败
            network_health = results[0] if not isinstance(results[0], Exception) else {"error": str(results[0])}
            sync_status = results[1] if not isinstance(results[1], Exception) else {"error": str(results[1])}
            agent_states = results[2] if not isinstance(results[2], Exception) else {"error": str(results[2])}
            current_strategy = results[3] if not isinstance(results[3], Exception) else {"error": str(results[3])}
            
            return network_health, sync_status, agent_states, current_strategy
        
        # 使用asyncio.run处理异步调用，在Flask同步环境中保持简单一致的模式
        import asyncio
        try:
            # 在同步环境中直接使用asyncio.run
            network_health, sync_status, agent_states, current_strategy = asyncio.run(get_status())
        except Exception as e:
            # 处理异常
            logger.error(f"获取系统状态失败: {str(e)}")
            # 返回默认值
            network_health = {"error": str(e)}
            sync_status = {"error": str(e)}
            agent_states = {"error": str(e)}
            current_strategy = {"error": str(e)}
        
        # 根据当前策略计算防护级别
        bait_ratio = current_strategy.get('bait_ratio', 0.5)
        path_complexity = current_strategy.get('path_complexity', 3)
        psychological_level = current_strategy.get('psychological_warfare_level', 1)
        
        # 计算防护级别
        if bait_ratio >= 0.9 and path_complexity >= 5 and psychological_level >= 4:
            protection_level = 4  # 全面防护
        elif bait_ratio >= 0.7 and path_complexity >= 4 and psychological_level >= 3:
            protection_level = 3  # 高级防护
        elif bait_ratio >= 0.5 and path_complexity >= 3 and psychological_level >= 2:
            protection_level = 2  # 标准防护
        elif bait_ratio >= 0.3 and path_complexity >= 2 and psychological_level >= 1:
            protection_level = 1  # 基础防护
        else:
            protection_level = 0  # 关闭防护
        
        status = {
            "timestamp": datetime.now().isoformat(),
            "network_health": network_health,
            "community_sync": sync_status,
            "agent_states": agent_states,
            "current_strategy": current_strategy,
            "protection_level": protection_level,
            "system_status": "operational"
        }
        
        return jsonify(status)
    except Exception as e:
        logger.error(f"获取系统状态失败: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 防护级别设置接口
@app.route('/api/system/protection_level', methods=['POST'])
@require_auth
def set_protection_level():
    """设置防护级别"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "请求数据不能为空"}), 400
        
        # 验证输入数据
        schema = {
            'level': (True, int, None)
        }
        valid, errors = validate_input(data, schema)
        if not valid:
            return jsonify({"error": "输入验证失败", "errors": errors}), 400
        
        level = data.get('level', 1)  # 默认基础防护
        
        # 验证防护级别范围
        if level < 0 or level > 4:
            return jsonify({"error": "防护级别必须在0-4之间"}), 400
        
        # 根据防护级别调整系统策略
        if level == 0:
            # 关闭防护
            strategy = {
                "bait_ratio": 0.0,
                "path_complexity": 1,
                "psychological_warfare_level": 0
            }
        elif level == 1:
            # 基础防护
            strategy = {
                "bait_ratio": 0.3,
                "path_complexity": 2,
                "psychological_warfare_level": 1
            }
        elif level == 2:
            # 标准防护
            strategy = {
                "bait_ratio": 0.5,
                "path_complexity": 3,
                "psychological_warfare_level": 2
            }
        elif level == 3:
            # 高级防护
            strategy = {
                "bait_ratio": 0.7,
                "path_complexity": 4,
                "psychological_warfare_level": 3
            }
        elif level == 4:
            # 全面防护
            strategy = {
                "bait_ratio": 0.9,
                "path_complexity": 5,
                "psychological_warfare_level": 4
            }
        
        # 更新策略
        updated_strategy = strategy_engine.set_strategy(strategy)
        
        # 清除相关缓存
        clear_cache(['get_strategy', 'get_system_status'])
        
        logger.info(f"防护级别已设置为: {level}")
        return jsonify({"success": True, "level": level, "strategy": updated_strategy})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 分层防御相关接口
@app.route('/api/defense/layers', methods=['GET'])
@require_auth
@cached(timeout=300)  # 缓存5分钟，防御层配置不常变化

def get_defense_layers():
    """获取所有防御层"""
    try:
        layers = layered_defense_manager.get_defense_layers()
        return jsonify(layers)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/defense/status', methods=['GET'])
@require_auth
@cached(timeout=30)  # 缓存30秒，防御状态可能会变化

def get_defense_status():
    """获取各层防御状态"""
    try:
        status = layered_defense_manager.get_layer_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/defense/layer/<layer_name>/activate', methods=['POST'])
@require_auth
def activate_defense_layer(layer_name):
    """激活防御层"""
    try:
        layered_defense_manager.activate_layer(layer_name)
        # 清除相关缓存
        clear_cache(['get_defense_status'])
        return jsonify({"success": True, "message": f"防御层 {layer_name} 已激活"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/defense/layer/<layer_name>/deactivate', methods=['POST'])
@require_auth
def deactivate_defense_layer(layer_name):
    """停用防御层"""
    try:
        layered_defense_manager.deactivate_layer(layer_name)
        # 清除相关缓存
        clear_cache(['get_defense_status'])
        return jsonify({"success": True, "message": f"防御层 {layer_name} 已停用"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/defense/history', methods=['GET'])
@require_auth
def get_defense_history():
    """获取防御事件历史"""
    try:
        limit = int(request.args.get('limit', 50))
        history = layered_defense_manager.get_defense_history(limit)
        return jsonify(history)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/defense/statistics', methods=['GET'])
@require_auth
@cached(timeout=300)  # 缓存5分钟，统计信息不常变化

def get_defense_statistics():
    """获取防御统计信息"""
    try:
        statistics = layered_defense_manager.get_defense_statistics()
        return jsonify(statistics)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 局域网节点管理接口
@app.route('/api/lan/nodes', methods=['GET'])
@require_auth
@cached(timeout=10)  # 缓存10秒
def get_lan_nodes():
    """获取局域网节点列表"""
    try:
        nodes = lan_discovery.get_nodes()
        return jsonify({"nodes": nodes})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 连接频率限制存储
connection_rate_limit = {}
connection_rate_limit_lock = threading.Lock()
# 连接频率限制存储文件
CONNECTION_RATE_LIMIT_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'connection_rate_limit.json')
# 连接频率限制文件锁
connection_rate_limit_file_lock = threading.Lock()

# IP白名单
IP_WHITELIST = set()

# 加载配置管理器
from utils.config_manager import config_manager



# 保存连接频率限制
def save_connection_rate_limit():
    """保存连接频率限制数据"""
    try:
        # 确保数据目录存在
        os.makedirs(os.path.dirname(CONNECTION_RATE_LIMIT_FILE), exist_ok=True)
        # 清理过期数据后保存
        current_time = time.time()
        data_to_save = {}
        with connection_rate_limit_lock:
            for ip, timestamps in connection_rate_limit.items():
                # 只保存1分钟内的记录
                recent_timestamps = [ts for ts in timestamps if current_time - ts < 60]
                if recent_timestamps:
                    data_to_save[ip] = recent_timestamps
        # 保存到文件
        with connection_rate_limit_file_lock:
            with open(CONNECTION_RATE_LIMIT_FILE, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, indent=2)
        logger.info(f"保存连接频率限制数据成功，共 {len(data_to_save)} 条记录")
    except Exception as e:
        logger.error(f"保存连接频率限制数据失败: {str(e)}")

# 定期保存连接频率限制的任务
def start_connection_rate_limit_save_task():
    """启动定期保存连接频率限制的任务"""
    def save_task():
        while True:
            try:
                save_connection_rate_limit()
                # 每30秒保存一次
                time.sleep(30)
            except Exception as e:
                logger.error(f"保存连接频率限制任务出错: {str(e)}")
                time.sleep(30)
    
    import threading
    save_thread = threading.Thread(target=save_task, daemon=True)
    save_thread.start()
    logger.info("定期保存连接频率限制的任务已启动")

# 检查IP是否在白名单中
def is_ip_whitelisted(ip):
    """检查IP是否在白名单中"""
    import ipaddress
    try:
        ip_obj = ipaddress.IPv4Address(ip)
        for network in IP_WHITELIST:
            if ip_obj in ipaddress.IPv4Network(network):
                return True
        return False
    except ValueError:
        return False

# 检查连接频率
def check_rate_limit(client_ip):
    """检查连接频率限制"""
    with connection_rate_limit_lock:
        current_time = time.time()
        if client_ip not in connection_rate_limit:
            connection_rate_limit[client_ip] = []
        
        # 从配置中获取频率限制参数
        max_connections = config_manager.get('api.rate_limit.max_connections', 5)
        window_seconds = config_manager.get('api.rate_limit.window_seconds', 60)
        
        # 清理过期的记录
        connection_rate_limit[client_ip] = [t for t in connection_rate_limit[client_ip] if current_time - t < window_seconds]
        
        # 检查时间窗口内的连接次数
        if len(connection_rate_limit[client_ip]) >= max_connections:  # 时间窗口内最多max_connections次连接
            return False
        
        # 记录本次连接
        connection_rate_limit[client_ip].append(current_time)
        
        # 确保列表不会无限增长，最多保留2倍max_connections条记录
        if len(connection_rate_limit[client_ip]) > max_connections * 2:
            connection_rate_limit[client_ip] = connection_rate_limit[client_ip][-max_connections*2:]
        
        return True

@app.route('/api/lan/connect', methods=['POST'])
@require_auth
@retry(max_attempts=3, delay=1, backoff=2, exceptions=(Exception,))
def connect_to_lan_node():
    """连接到局域网节点"""
    try:
        # 获取客户端IP
        client_ip = request.remote_addr
        
        # 检查连接频率限制
        if not check_rate_limit(client_ip):
            return jsonify({"error": "连接频率过高，请稍后再试"}), 429
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "请求数据不能为空"}), 400
        
        ip = data.get('ip')
        port = data.get('port', 5001)
        
        if not ip:
            return jsonify({"error": "缺少IP地址"}), 400
        
        # 检查目标IP是否在白名单中
        if not is_ip_whitelisted(ip):
            return jsonify({"error": "目标IP不在白名单中"}), 403
        
        # 检查端口范围
        if port < 1 or port > 65535:
            return jsonify({"error": "端口号无效"}), 400
        
        connection_id = secure_communication.connect_to_node(ip, port)
        if connection_id:
            return jsonify({"success": True, "connection_id": connection_id})
        else:
            return jsonify({"error": "连接失败"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 数据传输接口
@app.route('/api/data/send', methods=['POST'])
@require_auth
@retry(max_attempts=3, delay=1, backoff=2, exceptions=(Exception,))
def send_data():
    """发送数据到目标节点"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "请求数据不能为空"}), 400
        
        # 验证输入数据
        schema = {
            'target_node': (True, str, 100),
            'data_id': (True, str, 100),
            'data': (True, (dict, list, str), 1000000),
            'chunk_size': (False, int, None)
        }
        valid, errors = validate_input(data, schema)
        if not valid:
            return jsonify({"error": "输入验证失败", "errors": errors}), 400
        
        target_node = data.get('target_node')
        data_id = data.get('data_id')
        data_content = data.get('data')
        chunk_size = data.get('chunk_size', 1024 * 1024)
        
        transfer_id = data_transfer_manager.send_data(target_node, data_id, data_content, chunk_size)
        if transfer_id:
            return jsonify({"transfer_id": transfer_id})
        else:
            return jsonify({"error": "发送失败"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/data/transfer/<transfer_id>', methods=['GET'])
@require_auth
def get_transfer_status(transfer_id):
    """获取传输状态"""
    try:
        status = data_transfer_manager.get_transfer_status(transfer_id)
        if status:
            return jsonify(status)
        else:
            return jsonify({"error": "传输不存在"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/data/transfer/<transfer_id>/pause', methods=['POST'])
@require_auth
def pause_transfer(transfer_id):
    """暂停传输"""
    try:
        success = data_transfer_manager.pause_transfer(transfer_id)
        return jsonify({"success": success})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/data/transfer/<transfer_id>/resume', methods=['POST'])
@require_auth
def resume_transfer(transfer_id):
    """恢复传输"""
    try:
        success = data_transfer_manager.resume_transfer(transfer_id)
        return jsonify({"success": success})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/data/transfer/<transfer_id>/cancel', methods=['POST'])
@require_auth
def cancel_transfer(transfer_id):
    """取消传输"""
    try:
        success = data_transfer_manager.cancel_transfer(transfer_id)
        return jsonify({"success": success})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/data/transfers', methods=['GET'])
@require_auth
def get_all_transfers():
    """获取所有传输"""
    try:
        transfers = data_transfer_manager.get_all_transfers()
        return jsonify({"transfers": transfers})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/data/transfer/statistics', methods=['GET'])
@require_auth
def get_transfer_statistics():
    """获取传输统计信息"""
    try:
        statistics = data_transfer_manager.get_transfer_statistics()
        return jsonify(statistics)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

import atexit

# 安全事件监控
class SecurityEventMonitor:
    def __init__(self):
        """初始化安全事件监控"""
        self.events_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'security_events.json')
        os.makedirs(os.path.dirname(self.events_file), exist_ok=True)
        self.events = self._load_events()
    
    def _load_events(self):
        """加载安全事件"""
        if os.path.exists(self.events_file):
            try:
                with open(self.events_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"加载安全事件失败: {str(e)}")
        return []
    
    def _save_events(self):
        """保存安全事件"""
        try:
            with open(self.events_file, 'w', encoding='utf-8') as f:
                json.dump(self.events, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"保存安全事件失败: {str(e)}")
    
    def log_event(self, event_type, severity, source, message, details=None):
        """记录安全事件"""
        event = {
            "event_id": hashlib.md5(f"{datetime.now().isoformat()}{event_type}{source}".encode('utf-8')).hexdigest(),
            "event_type": event_type,
            "severity": severity,
            "source": source,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        
        self.events.append(event)
        
        # 限制事件数量，只保留最近10000条
        if len(self.events) > 10000:
            self.events = self.events[-10000:]
        
        self._save_events()
        
        # 同时记录到日志
        log_level = {
            "critical": logging.CRITICAL,
            "high": logging.ERROR,
            "medium": logging.WARNING,
            "low": logging.INFO
        }.get(severity, logging.INFO)
        
        logger.log(log_level, f"安全事件: {event_type} - {message} - 来源: {source}")
        
        return event
    
    def get_events(self, event_type=None, severity=None, start_time=None, limit=100):
        """获取安全事件"""
        filtered_events = self.events
        
        if event_type:
            filtered_events = [e for e in filtered_events if e["event_type"] == event_type]
        
        if severity:
            filtered_events = [e for e in filtered_events if e["severity"] == severity]
        
        if start_time:
            start_time_obj = datetime.fromisoformat(start_time)
            filtered_events = [e for e in filtered_events if datetime.fromisoformat(e["timestamp"]) >= start_time_obj]
        
        # 按时间倒序排序
        filtered_events.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # 限制数量
        return filtered_events[:limit]
    
    def get_event_statistics(self, hours=24):
        """获取安全事件统计信息"""
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        recent_events = [e for e in self.events if datetime.fromisoformat(e["timestamp"]) >= start_time]
        
        stats = {
            "total": len(recent_events),
            "by_type": {},
            "by_severity": {},
            "time_range": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat()
            }
        }
        
        for event in recent_events:
            event_type = event["event_type"]
            severity = event["severity"]
            
            if event_type not in stats["by_type"]:
                stats["by_type"][event_type] = 0
            stats["by_type"][event_type] += 1
            
            if severity not in stats["by_severity"]:
                stats["by_severity"][severity] = 0
            stats["by_severity"][severity] += 1
        
        return stats

# 初始化安全事件监控
security_event_monitor = SecurityEventMonitor()

# 安全事件相关接口
@app.route('/api/security/events', methods=['GET'])
@require_auth
def get_security_events():
    """获取安全事件"""
    try:
        event_type = request.args.get('event_type')
        severity = request.args.get('severity')
        start_time = request.args.get('start_time')
        limit = int(request.args.get('limit', 100))
        
        events = security_event_monitor.get_events(event_type, severity, start_time, limit)
        return jsonify(events)
    except Exception as e:
        logger.error(f"获取安全事件失败: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/security/events/stats', methods=['GET'])
@require_auth
def get_security_event_stats():
    """获取安全事件统计信息"""
    try:
        hours = int(request.args.get('hours', 24))
        stats = security_event_monitor.get_event_statistics(hours)
        return jsonify(stats)
    except Exception as e:
        logger.error(f"获取安全事件统计失败: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 消息队列监控接口
@app.route('/api/message-queue/status', methods=['GET'])
@require_auth
def get_message_queue_status():
    """获取消息队列状态"""
    try:
        status = message_queue_manager.get_queue_status()
        return jsonify(status)
    except Exception as e:
        logger.error(f"获取消息队列状态失败: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/message-queue/stats', methods=['GET'])
@require_auth
def get_message_queue_stats():
    """获取消息队列统计信息"""
    try:
        stats = message_queue_manager.get_message_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"获取消息队列统计失败: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/message-queue/health', methods=['GET'])
@require_auth
def get_message_queue_health():
    """获取消息队列健康状态"""
    try:
        health = message_queue_manager.get_health_status()
        return jsonify(health)
    except Exception as e:
        logger.error(f"获取消息队列健康状态失败: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 应用退出时清理资源
def cleanup_resources():
    """应用退出时清理资源"""
    # 清理局域网相关组件
    try:
        logger.info("关闭局域网发现服务...")
        lan_discovery.stop()
        logger.info("局域网发现服务已关闭")
    except Exception as e:
        logger.warning(f"关闭局域网发现服务时出错: {str(e)}")
    
    try:
        logger.info("关闭安全通信服务器...")
        secure_communication.stop_server()
        logger.info("安全通信服务器已关闭")
    except Exception as e:
        logger.warning(f"关闭安全通信服务器时出错: {str(e)}")
    
    # 清理线程池
    global executor
    if executor:
        logger.info("关闭线程池...")
        # 检查Python版本，cancel_futures参数在Python 3.9+中可用
        import sys
        try:
            if sys.version_info >= (3, 9):
                executor.shutdown(wait=True, cancel_futures=True)
            else:
                # Python 3.9以下版本，先尝试正常关闭
                executor.shutdown(wait=True)
        except Exception as e:
            # 异常情况下强制关闭
            try:
                if sys.version_info >= (3, 9):
                    executor.shutdown(wait=False, cancel_futures=True)
                else:
                    executor.shutdown(wait=False)
            except:
                pass
        logger.info("线程池已关闭")
    
    # 停止缓存清理任务
    stop_cache_cleanup_task()
    
    # 停止优先级任务处理线程
    stop_priority_task_thread()
    
    # 清理消息队列
    try:
        logger.info("清理消息队列...")
        # 尝试停止消息队列处理
        if message_queue_manager:
            try:
                import asyncio
                
                # 定义异步函数
                async def stop_message_queue():
                    await message_queue_manager.stop_processing()
                
                # 在同步环境中安全调用异步函数
                asyncio.run(stop_message_queue())
                logger.info("消息队列处理已停止")
            except Exception as e:
                logger.warning(f"停止消息队列处理时出错: {str(e)}")
        logger.info("消息队列已清理")
    except Exception as e:
        logger.warning(f"清理消息队列时出错: {str(e)}")
    
    # 关闭日志处理器
    try:
        logger.info("关闭日志处理器...")
        for handler in root_logger.handlers:
            if hasattr(handler, 'close'):
                handler.close()
        logger.info("日志处理器已关闭")
    except Exception as e:
        print(f"关闭日志处理器时出错: {str(e)}")

# 注册退出处理函数
atexit.register(cleanup_resources)

if __name__ == '__main__':
    # 运行API服务
    app.run(host='0.0.0.0', port=5000, debug=True)
