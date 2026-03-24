# © 2026 MirageShield 团队 版权所有，侵权必究
# 本项目已申请发明专利，未经许可禁止商用
# 缓存模块缓存工具模块
import hashlib
import threading
from datetime import datetime, timedelta

# 缓存存储
_cache = {}
_cache_expiry = {}
_cache_lock = threading.RLock()
_cache_size_limit = 10000  # 缓存大小限制

# 定期清理过期缓存
def cleanup_expired_cache():
    """清理过期的缓存"""
    now = datetime.now()
    expired_keys = []
    with _cache_lock:
        # 清理过期缓存
        expired_keys = [key for key, expiry in _cache_expiry.items() if now > expiry]
        for key in expired_keys:
            if key in _cache:
                del _cache[key]
            if key in _cache_expiry:
                del _cache_expiry[key]
        
        # 检查缓存大小，超过限制时清理最旧的缓存
        if len(_cache) > _cache_size_limit:
            # 按过期时间排序，删除最旧的缓存
            sorted_keys = sorted(_cache_expiry.items(), key=lambda x: x[1])
            keys_to_remove = [key for key, _ in sorted_keys[:len(_cache) - _cache_size_limit]]
            for key in keys_to_remove:
                if key in _cache:
                    del _cache[key]
                if key in _cache_expiry:
                    del _cache_expiry[key]

# 清除指定模式的缓存
def clear_cache(patterns):
    """清除指定模式的缓存"""
    with _cache_lock:
        keys_to_remove = []
        for key in _cache:
            for pattern in patterns:
                if pattern in key:
                    keys_to_remove.append(key)
                    break
        for key in keys_to_remove:
            if key in _cache:
                del _cache[key]
            if key in _cache_expiry:
                del _cache_expiry[key]

# 缓存装饰器
def cached(timeout=30):
    def decorator(func):
        func_name = func.__name__
        
        def wrapper(*args, **kwargs):
            # 生成缓存键
            args_str = "_".join(str(arg) for arg in args)
            kwargs_str = "_".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
            params_str = f"{args_str}:{kwargs_str}"
            
            # 使用SHA256哈希生成缓存键
            key_hash = hashlib.sha256(params_str.encode('utf-8')).hexdigest()
            key = f"{func_name}:{key_hash}"
            
            # 检查缓存是否有效（加锁）
            now = datetime.now()
            with _cache_lock:
                if key in _cache and key in _cache_expiry and now < _cache_expiry[key]:
                    return _cache[key]
            
            # 执行函数
            result = func(*args, **kwargs)
            
            # 更新缓存（加锁）
            with _cache_lock:
                _cache[key] = result
                _cache_expiry[key] = now + timedelta(seconds=timeout)
            
            return result
        # 保留原始函数的名称，避免Flask端点冲突
        wrapper.__name__ = func_name
        wrapper.__doc__ = func.__doc__
        return wrapper
    return decorator
