# © 2026 MirageShield 团队 版权所有，侵权必究
# 统一配置管理模块
import json
import logging
import os
from typing import Dict, Any, Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s:%(funcName)s:%(lineno)d - %(message)s'
)
logger = logging.getLogger('utils.config_manager')

class ConfigManager:
    """统一配置管理器"""
    def __init__(self, config_dir: str = None):
        """初始化配置管理器
        
        Args:
            config_dir: 配置文件目录
        """
        if config_dir is None:
            # 默认配置目录
            config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config')
        self.config_dir = config_dir
        self.configs: Dict[str, Any] = {}
        self.defaults = {
            'api': {
                'ip_whitelist': [
                    '192.168.0.0/16',
                    '10.0.0.0/8',
                    '172.16.0.0/12'
                ],
                'rate_limit': {
                    'max_connections': 5,
                    'window_seconds': 60
                }
            },
            'security': {
                'jwt_expiration_hours': 1,
                'jwt_refresh_days': 7
            },
            'performance': {
                'cache_cleanup_interval': 300,
                'max_cache_size': 10000
            }
        }
        self._load_configs()
    
    def _load_configs(self):
        """加载所有配置文件"""
        try:
            # 确保配置目录存在
            os.makedirs(self.config_dir, exist_ok=True)
            
            # 加载 API 配置
            api_config_file = os.path.join(self.config_dir, 'api_config.json')
            if os.path.exists(api_config_file):
                with open(api_config_file, 'r', encoding='utf-8') as f:
                    self.configs['api'] = json.load(f)
                logger.info("加载 API 配置成功")
            else:
                self.configs['api'] = self.defaults['api']
                logger.warning("API 配置文件不存在，使用默认配置")
            
            # 加载安全配置
            security_config_file = os.path.join(self.config_dir, 'security_config.json')
            if os.path.exists(security_config_file):
                with open(security_config_file, 'r', encoding='utf-8') as f:
                    self.configs['security'] = json.load(f)
                logger.info("加载安全配置成功")
            else:
                self.configs['security'] = self.defaults['security']
                logger.warning("安全配置文件不存在，使用默认配置")
            
            # 加载性能配置
            performance_config_file = os.path.join(self.config_dir, 'performance_config.json')
            if os.path.exists(performance_config_file):
                with open(performance_config_file, 'r', encoding='utf-8') as f:
                    self.configs['performance'] = json.load(f)
                logger.info("加载性能配置成功")
            else:
                self.configs['performance'] = self.defaults['performance']
                logger.warning("性能配置文件不存在，使用默认配置")
            
            # 验证配置
            self._validate_configs()
            logger.info("配置加载完成")
        except Exception as e:
            logger.error(f"加载配置失败: {str(e)}")
            # 使用默认配置
            self.configs = self.defaults.copy()
            logger.info("使用默认配置")
    
    def _validate_configs(self):
        """验证配置"""
        # 验证 API 配置
        if 'api' not in self.configs:
            self.configs['api'] = self.defaults['api']
        else:
            # 确保必要的字段存在
            if 'ip_whitelist' not in self.configs['api']:
                self.configs['api']['ip_whitelist'] = self.defaults['api']['ip_whitelist']
            if 'rate_limit' not in self.configs['api']:
                self.configs['api']['rate_limit'] = self.defaults['api']['rate_limit']
            else:
                if 'max_connections' not in self.configs['api']['rate_limit']:
                    self.configs['api']['rate_limit']['max_connections'] = self.defaults['api']['rate_limit']['max_connections']
                if 'window_seconds' not in self.configs['api']['rate_limit']:
                    self.configs['api']['rate_limit']['window_seconds'] = self.defaults['api']['rate_limit']['window_seconds']
        
        # 验证安全配置
        if 'security' not in self.configs:
            self.configs['security'] = self.defaults['security']
        else:
            if 'jwt_expiration_hours' not in self.configs['security']:
                self.configs['security']['jwt_expiration_hours'] = self.defaults['security']['jwt_expiration_hours']
            if 'jwt_refresh_days' not in self.configs['security']:
                self.configs['security']['jwt_refresh_days'] = self.defaults['security']['jwt_refresh_days']
        
        # 验证性能配置
        if 'performance' not in self.configs:
            self.configs['performance'] = self.defaults['performance']
        else:
            if 'cache_cleanup_interval' not in self.configs['performance']:
                self.configs['performance']['cache_cleanup_interval'] = self.defaults['performance']['cache_cleanup_interval']
            if 'max_cache_size' not in self.configs['performance']:
                self.configs['performance']['max_cache_size'] = self.defaults['performance']['max_cache_size']
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值
        
        Args:
            key: 配置键，使用点分隔，如 'api.ip_whitelist'
            default: 默认值
        
        Returns:
            配置值
        """
        keys = key.split('.')
        value = self.configs
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key: str, value: Any):
        """设置配置值
        
        Args:
            key: 配置键，使用点分隔，如 'api.ip_whitelist'
            value: 配置值
        """
        keys = key.split('.')
        config = self.configs
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
    
    def save(self, config_name: str):
        """保存配置到文件
        
        Args:
            config_name: 配置名称，如 'api', 'security', 'performance'
        """
        if config_name in self.configs:
            config_file = os.path.join(self.config_dir, f'{config_name}_config.json')
            try:
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(self.configs[config_name], f, indent=2, ensure_ascii=False)
                logger.info(f"保存 {config_name} 配置成功")
            except Exception as e:
                logger.error(f"保存 {config_name} 配置失败: {str(e)}")
        else:
            logger.error(f"配置 {config_name} 不存在")
    
    def reload(self):
        """重新加载配置"""
        self._load_configs()

# 全局配置管理器实例
config_manager = ConfigManager()
