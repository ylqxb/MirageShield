# © 2026 MirageShield 团队 版权所有，侵权必究
# 配置管理模块

# 配置字典
_config = {
    'use_mock_message_queue': True  # 默认使用模拟消息队列
}

def get_config(key, default=None):
    """获取配置值"""
    return _config.get(key, default)

def set_config(key, value):
    """设置配置值"""
    _config[key] = value
