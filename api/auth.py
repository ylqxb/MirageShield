# © 2026 MirageShield 团队 版权所有，侵权必究
# 本项目已申请发明专利，未经许可禁止商用
# 认证模块认证相关功能
import json
import logging
import os
import re
import bcrypt
import hashlib
from datetime import datetime, timedelta
from flask import request, jsonify, make_response
import jwt

# 配置日志
logger = logging.getLogger('api.auth')

# 密钥存储文件路径
SECRET_KEY_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'secret_key.json')

# 用户存储文件路径
USERS_FILE = os.environ.get('USERS_FILE', os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'users.json'))

# 确保数据目录存在
os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)

# 生成随机密码
def generate_random_password(length=12):
    """生成随机密码"""
    import string
    import random
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))

# 文件锁定机制
try:
    import fcntl
    has_fcntl = True
except ImportError:
    has_fcntl = False
    import logging
    logger = logging.getLogger('api.auth')
    logger.warning("fcntl模块不可用，文件锁定功能将被禁用")

# 加载用户数据
# 全局用户缓存
_users_cache = None
_cache_timestamp = 0
CACHE_TTL = 30  # 缓存有效期（秒）

def load_users():
    """从文件加载用户数据"""
    global _users_cache, _cache_timestamp
    
    # 检查缓存是否有效
    current_time = datetime.now().timestamp()
    if _users_cache and (current_time - _cache_timestamp) < CACHE_TTL:
        logger.info("使用缓存的用户数据")
        return _users_cache
    
    # 检查是否是首次运行（用户文件不存在）
    is_first_run = not os.path.exists(USERS_FILE)
    logger.info(f"load_users() 被调用，is_first_run: {is_first_run}")
    
    # 尝试从文件加载现有数据
    existing_users = {}
    if not is_first_run:
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                existing_users = json.load(f)
            logger.info(f"从文件加载用户数据成功，用户数量: {len(existing_users)}")
        except Exception as e:
            logger.error(f"加载用户数据失败: {str(e)}")
    
    # 从环境变量获取初始密码
    initial_password = os.environ.get('ADMIN_PASSWORD')
    logger.info(f"从环境变量获取初始密码: {initial_password is not None}")
    
    # 检查是否需要生成新密码
    password_changed = False
    if is_first_run:
        # 首次运行时生成随机密码
        if not initial_password:
            initial_password = generate_random_password()
            logger.warning(f"未设置ADMIN_PASSWORD环境变量，生成随机初始密码: {initial_password}")
            logger.warning("首次运行，请使用此密码登录并立即修改")
        password_changed = True
        logger.info(f"首次运行，需要生成新密码: {password_changed}")
    elif initial_password and not existing_users:
        # 只有当用户不存在时，才根据环境变量更新密码
        password_changed = True
        logger.info(f"设置了ADMIN_PASSWORD环境变量且用户不存在，更新密码: {password_changed}")
    
    # 只有在需要时才更新admin用户
    if password_changed:
        # 创建或更新管理员用户
        admin_user = {
            'admin': {
                'username': 'admin',
                'password': bcrypt.hashpw(initial_password.encode(), bcrypt.gensalt(rounds=10)).decode(),
                'role': 'admin',
                'force_password_change': True  # 标记需要强制修改密码
            }
        }
        
        # 合并现有用户数据
        if existing_users:
            existing_users.update(admin_user)
            save_users(existing_users)
            logger.info("更新现有管理员用户并保存")
        else:
            save_users(admin_user)
            logger.info("创建新的管理员用户并保存")
    
    # 从文件加载用户数据（确保返回最新数据）
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                users = json.load(f)
            logger.info(f"从文件加载最新用户数据成功，用户数量: {len(users)}")
            # 更新缓存
            _users_cache = users
            _cache_timestamp = current_time
            return users
    except Exception as e:
        logger.error(f"加载用户数据失败: {str(e)}")
    
    # 如果文件不存在，返回包含admin用户的字典
    if not existing_users and initial_password:
        logger.info("文件不存在，返回包含admin用户的字典")
        admin_data = {
            'admin': {
                'username': 'admin',
                'password': bcrypt.hashpw(initial_password.encode(), bcrypt.gensalt(rounds=10)).decode(),
                'role': 'admin',
                'force_password_change': True
            }
        }
        # 更新缓存
        _users_cache = admin_data
        _cache_timestamp = current_time
        return admin_data
    
    logger.info(f"返回现有用户数据，用户数量: {len(existing_users)}")
    # 更新缓存
    _users_cache = existing_users
    _cache_timestamp = current_time
    return existing_users

# 检查密码复杂度
def check_password_strength(password):
    """检查密码复杂度"""
    # 至少8个字符
    if len(password) < 8:
        return False, "密码长度至少为8个字符"
    # 至少包含一个大写字母
    if not re.search(r'[A-Z]', password):
        return False, "密码至少包含一个大写字母"
    # 至少包含一个小写字母
    if not re.search(r'[a-z]', password):
        return False, "密码至少包含一个小写字母"
    # 至少包含一个数字
    if not re.search(r'[0-9]', password):
        return False, "密码至少包含一个数字"
    # 至少包含一个特殊字符
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "密码至少包含一个特殊字符"
    return True, "密码强度符合要求"

# 导入备份模块
try:
    from utils.backup import backup_users_data
except ImportError:
    logger.warning("备份模块导入失败，跳过自动备份")
    backup_users_data = None

# 保存用户数据
def save_users(users_data):
    """保存用户数据到文件"""
    global _users_cache, _cache_timestamp
    try:
        # 保存前备份
        if backup_users_data:
            backup_users_data()
        
        # 确保目录存在
        os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
        logger.info(f"尝试保存用户数据到: {USERS_FILE}")
        logger.info(f"保存的用户数据: {json.dumps(users_data, indent=2, ensure_ascii=False)}")
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users_data, f, indent=2, ensure_ascii=False)
        logger.info(f"用户数据保存成功: {USERS_FILE}")
        # 清除缓存，确保下次加载时获取最新数据
        _users_cache = None
        _cache_timestamp = 0
    except Exception as e:
        logger.error(f"保存用户数据失败: {str(e)}")
        # 打印详细错误信息
        import traceback
        logger.error(f"异常堆栈: {traceback.format_exc()}")

# 认证装饰器
def require_auth(f=None, roles=None):
    """认证装饰器，支持角色验证
    
    Args:
        f: 被装饰的函数
        roles: 允许的角色列表，None表示不限制角色
    """
    def decorator(func):
        def decorated(*args, **kwargs):
            from api.app import app  # 避免循环导入
            token = request.headers.get('Authorization')
            if not token:
                return jsonify({'error': '缺少认证令牌'}), 401
            
            try:
                # 移除Bearer前缀
                if token.startswith('Bearer '):
                    token = token.split(' ')[1]
                data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
                request.user = data
            except jwt.ExpiredSignatureError:
                return jsonify({'error': '认证令牌已过期'}), 401
            except jwt.InvalidTokenError:
                return jsonify({'error': '无效的认证令牌'}), 401
            
            # 检查角色
            if roles:
                user_role = data.get('role')
                if user_role not in roles:
                    return jsonify({'error': '权限不足'}), 403
            
            return func(*args, **kwargs)
        decorated.__name__ = func.__name__
        return decorated
    
    # 支持两种调用方式：@require_auth 和 @require_auth(roles=['admin'])
    if f:
        return decorator(f)
    return decorator

# 注册认证相关接口
def register_auth_routes(app):
    """注册认证相关接口"""
    # 认证相关接口
    @app.route('/api/auth/login', methods=['POST'])
    def login():
        """用户登录"""
        try:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
            
            if not username or not password:
                return jsonify({'error': '用户名和密码不能为空'}), 400
            
            # 直接调用load_users()获取最新用户数据
            users = load_users()
            if username not in users:
                return jsonify({'error': '用户名或密码错误'}), 401
            
            user = users[username]
            if not bcrypt.checkpw(password.encode(), user['password'].encode()):
                return jsonify({'error': '用户名或密码错误'}), 401
            
            # 生成访问令牌
            access_token = jwt.encode(
                {
                    'username': user['username'],
                    'role': user['role'],
                    'exp': datetime.utcnow() + app.config['JWT_EXPIRATION_DELTA'],
                    'iat': datetime.utcnow(),  # 令牌签发时间
                    'jti': hashlib.sha256(f"{user['username']}{datetime.utcnow()}".encode()).hexdigest()  # 令牌ID
                },
                app.config['SECRET_KEY'],
                algorithm='HS256'
            )
            
            # 生成刷新令牌
            refresh_token = jwt.encode(
                {
                    'username': user['username'],
                    'role': user['role'],
                    'exp': datetime.utcnow() + app.config.get('JWT_REFRESH_EXPIRATION_DELTA', timedelta(days=7)),
                    'iat': datetime.utcnow(),  # 令牌签发时间
                    'jti': hashlib.sha256(f"refresh_{user['username']}{datetime.utcnow()}".encode()).hexdigest()  # 令牌ID
                },
                app.config['SECRET_KEY'],
                algorithm='HS256'
            )
            
            # 检查是否需要强制修改密码
            force_password_change = user.get('force_password_change', False)
            
            return jsonify({
                'success': True,
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': {
                    'username': user['username'],
                    'role': user['role'],
                    'force_password_change': force_password_change
                }
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/auth/register', methods=['POST'])
    def register():
        """用户注册"""
        try:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
            
            if not username or not password:
                return jsonify({'error': '用户名和密码不能为空'}), 400
            
            # 直接调用load_users()获取最新用户数据
            users = load_users()
            # 检查用户是否已存在
            if username in users:
                return jsonify({'error': '用户名已存在'}), 400
            
            # 检查密码复杂度
            is_valid, message = check_password_strength(password)
            if not is_valid:
                return jsonify({'error': message}), 400
            
            # 创建新用户，默认角色为user
            hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            users[username] = {
                'username': username,
                'password': hashed_password,
                'role': 'user'
            }
            
            # 保存用户数据
            save_users(users)
            
            return jsonify({'success': True, 'message': '注册成功'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/auth/me', methods=['GET'])
    @require_auth
    def get_current_user():
        """获取当前用户信息"""
        username = request.user.get('username')
        # 直接调用load_users()获取最新用户数据
        users = load_users()
        user = users.get(username)
        force_password_change = user.get('force_password_change', False) if user else False
        
        return jsonify({
            'success': True,
            'user': {
                **request.user,
                'force_password_change': force_password_change
            }
        })

    @app.route('/api/auth/change-password', methods=['POST'])
    @require_auth
    def change_password():
        """修改密码"""
        try:
            data = request.get_json()
            current_password = data.get('current_password')
            new_password = data.get('new_password')
            
            if not current_password or not new_password:
                return jsonify({'error': '当前密码和新密码不能为空'}), 400
            
            # 获取当前用户
            username = request.user.get('username')
            # 直接调用load_users()获取最新用户数据
            users = load_users()
            user = users.get(username)
            
            if not user:
                return jsonify({'error': '用户不存在'}), 404
            
            # 验证当前密码
            if not bcrypt.checkpw(current_password.encode(), user['password'].encode()):
                return jsonify({'error': '当前密码错误'}), 401
            
            # 检查新密码复杂度
            is_valid, message = check_password_strength(new_password)
            if not is_valid:
                return jsonify({'error': message}), 400
            
            # 更新密码
            user['password'] = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
            user['force_password_change'] = False  # 取消强制修改密码标记
            
            # 保存用户数据
            save_users(users)
            
            return jsonify({'success': True, 'message': '密码修改成功'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/auth/refresh', methods=['POST'])
    def refresh_token():
        """刷新令牌"""
        try:
            # 获取刷新令牌
            data = request.get_json()
            refresh_token = data.get('refresh_token')
            
            if not refresh_token:
                return jsonify({'error': '缺少刷新令牌'}), 400
            
            # 验证刷新令牌
            from api.app import app  # 避免循环导入
            try:
                data = jwt.decode(
                    refresh_token, 
                    app.config['SECRET_KEY'], 
                    algorithms=['HS256']
                )
                # 检查必要字段
                if not all(k in data for k in ['username', 'role', 'jti', 'iat']):
                    return jsonify({'error': '令牌格式无效'}), 401
                username = data.get('username')
                role = data.get('role')
            except jwt.ExpiredSignatureError:
                return jsonify({'error': '刷新令牌已过期'}), 401
            except jwt.InvalidTokenError:
                return jsonify({'error': '无效的刷新令牌'}), 401
            
            # 直接调用load_users()获取最新用户数据
            users = load_users()
            user = users.get(username)
            
            if not user:
                return jsonify({'error': '用户不存在'}), 404
            
            # 生成新的访问令牌
            access_token = jwt.encode(
                {
                    'username': username,
                    'role': role,
                    'exp': datetime.utcnow() + app.config['JWT_EXPIRATION_DELTA'],
                    'iat': datetime.utcnow(),  # 令牌签发时间
                    'jti': hashlib.sha256(f"{username}{datetime.utcnow()}".encode()).hexdigest()  # 令牌ID
                },
                app.config['SECRET_KEY'],
                algorithm='HS256'
            )
            
            # 生成新的刷新令牌
            new_refresh_token = jwt.encode(
                {
                    'username': username,
                    'role': role,
                    'exp': datetime.utcnow() + app.config.get('JWT_REFRESH_EXPIRATION_DELTA', timedelta(days=7)),
                    'iat': datetime.utcnow(),  # 令牌签发时间
                    'jti': hashlib.sha256(f"refresh_{username}{datetime.utcnow()}".encode()).hexdigest()  # 令牌ID
                },
                app.config['SECRET_KEY'],
                algorithm='HS256'
            )
            
            # 检查是否需要强制修改密码
            force_password_change = user.get('force_password_change', False)
            
            return jsonify({
                'success': True,
                'access_token': access_token,
                'refresh_token': new_refresh_token,
                'user': {
                    'username': username,
                    'role': role,
                    'force_password_change': force_password_change
                }
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
