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

# 导入消息队列管理器
from utils.message_queue import message_queue_manager

# 配置日志
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'mirageshield.log')

# 配置根日志记录器
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# 控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(name)s:%(funcName)s:%(lineno)d - %(message)s')
console_handler.setFormatter(console_formatter)

# 文件处理器 (使用RotatingFileHandler限制日志大小)
from logging.handlers import RotatingFileHandler
file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8')
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
app.config['JWT_EXPIRATION_DELTA'] = timedelta(hours=24)

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
                else:
                    logger.warning("消息队列初始化超时，继续启动应用")
                    _message_queue_started = False

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
    from community.联防接口 import CommunityDefenseInterface
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
_cache_cleanup_interval = 30  # 每30秒清理一次，缩短清理间隔
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

# 初始化线程池
def init_executor():
    """初始化线程池"""
    global executor
    if not executor:
        logger.info("初始化线程池...")
        
        # 初始化线程池，根据CPU核心数设置线程数
        import concurrent.futures
        import os
        cpu_count = os.cpu_count() or 4
        max_workers = cpu_count * 3  # CPU核心数的3倍
        
        executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=max_workers, 
            thread_name_prefix='strategy_update'
        )
        logger.info(f"线程池初始化完成，最大工作线程数: {max_workers}")

# 应用启动时执行初始化
logger.info("应用启动时开始初始化组件...")
initialize_app()
# 初始化用户数据，生成管理员密码
logger.info("初始化用户数据...")
from api.auth import load_users
load_users()
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
@cached(timeout=60)  # 缓存60秒
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
@cached(timeout=10)  # 缓存10秒
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
@cached(timeout=10)  # 缓存10秒
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
        
        # 使用线程池提交任务并添加异常处理回调
        future = executor.submit(update_strategy_async)
        
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
@cached(timeout=30)  # 缓存30秒
def get_network_topology():
    """获取网络拓扑"""
    try:
        topology = virtual_network.get_network_topology()
        return jsonify(topology)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/network/health', methods=['GET'])
@require_auth
@cached(timeout=10)  # 缓存10秒
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
@cached(timeout=60)  # 缓存60秒
def get_blacklist():
    """获取黑名单"""
    try:
        blacklist = community_interface.get_blacklist()
        return jsonify(blacklist)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/community/threats', methods=['GET'])
@require_auth
@cached(timeout=60)  # 缓存60秒
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
@cached(timeout=10)  # 缓存10秒
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
@cached(timeout=60)  # 缓存60秒
def get_defense_layers():
    """获取所有防御层"""
    try:
        layers = layered_defense_manager.get_defense_layers()
        return jsonify(layers)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/defense/status', methods=['GET'])
@require_auth
@cached(timeout=10)  # 缓存10秒
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
@cached(timeout=60)  # 缓存60秒
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

# IP白名单
IP_WHITELIST = set()

# 加载API配置
try:
    config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config')
    with open(os.path.join(config_dir, 'api_config.json'), 'r', encoding='utf-8') as f:
        api_config = json.load(f)
    IP_WHITELIST = set(api_config.get('api', {}).get('ip_whitelist', []))
except Exception as e:
    logger.warning(f"加载API配置失败: {e}，使用默认IP白名单")
    IP_WHITELIST = {
        '192.168.0.0/16',
        '10.0.0.0/8',
        '172.16.0.0/12'
    }

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
        
        # 清理1分钟前的记录
        connection_rate_limit[client_ip] = [t for t in connection_rate_limit[client_ip] if current_time - t < 60]
        
        # 检查1分钟内的连接次数
        if len(connection_rate_limit[client_ip]) >= 5:  # 每分钟最多5次连接
            return False
        
        # 记录本次连接
        connection_rate_limit[client_ip].append(current_time)
        
        # 确保列表不会无限增长，最多保留10条记录
        if len(connection_rate_limit[client_ip]) > 10:
            connection_rate_limit[client_ip] = connection_rate_limit[client_ip][-10:]
        
        return True

@app.route('/api/lan/connect', methods=['POST'])
@require_auth
def connect_to_lan_node():
    """连接到局域网节点"""
    try:
        # 获取客户端IP
        client_ip = request.remote_addr
        
        # 检查连接频率限制
        if not check_rate_limit(client_ip):
            return jsonify({"error": "连接频率过高，请稍后再试"}), 429
        
        data = request.get_json()
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
def send_data():
    """发送数据到目标节点"""
    try:
        data = request.get_json()
        target_node = data.get('target_node')
        data_id = data.get('data_id')
        data_content = data.get('data')
        chunk_size = data.get('chunk_size', 1024 * 1024)
        
        if not target_node or not data_id or data_content is None:
            return jsonify({"error": "缺少必要参数"}), 400
        
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
        try:
            executor.shutdown(wait=True)
            logger.info("线程池已关闭")
        except Exception as e:
            logger.warning(f"线程池关闭异常: {str(e)}")
            executor.shutdown(wait=False)
            logger.info("线程池已强制关闭")
    
    # 停止缓存清理任务
    stop_cache_cleanup_task()

# 注册退出处理函数
atexit.register(cleanup_resources)

if __name__ == '__main__':
    # 运行API服务
    app.run(host='0.0.0.0', port=5000, debug=True)
