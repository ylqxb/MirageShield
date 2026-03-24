# © 2026 MirageShield 团队 版权所有，侵权必究
# 本项目已申请发明专利，未经许可禁止商用
# 真实数据池
import json
import logging
import os
import hashlib
import base64
import secrets
import threading
from collections import OrderedDict
from datetime import datetime
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s:%(funcName)s:%(lineno)d - %(message)s'
)
logger = logging.getLogger('data_plane.real_data_pool')

class RealDataPool:
    def __init__(self, data_dir='data/real', encryption_key=None):
        """初始化真实数据池"""
        try:
            # 创建数据目录
            self.data_dir = data_dir
            os.makedirs(self.data_dir, exist_ok=True)
            
            # 加密密钥
            if encryption_key:
                self.encryption_key = encryption_key.encode('utf-8')
            else:
                # 从环境变量获取密钥，若不存在则生成随机密钥
                env_key = os.environ.get('CHIMERA_ENCRYPTION_KEY')
                if env_key:
                    self.encryption_key = env_key.encode('utf-8')
                else:
                    # 生成随机密钥
                    self.encryption_key = secrets.token_bytes(32)
            
            # 确保密钥长度正确
            if len(self.encryption_key) < 32:
                self.encryption_key = self.encryption_key.ljust(32, b'0')[:32]
            
            # 数据索引
            self.index_file = os.path.join(self.data_dir, 'index.json')
            # 添加线程锁，避免文件锁竞争
            self.lock = threading.RLock()
            self.index = self._load_index()
            
            # 内存缓存，使用有序字典管理访问顺序
            self.memory_cache = OrderedDict()
            self.cache_size = 100  # 缓存大小限制
            
            # 访问控制
            self.roles = {
                'admin': {'store_data': True, 'retrieve_data': True, 'delete_data': True, 'list_data': True},
                'prober': {'store_data': True, 'retrieve_data': True, 'delete_data': False, 'list_data': True},
                'watcher': {'store_data': False, 'retrieve_data': False, 'delete_data': False, 'list_data': True}
            }
            self.agent_roles = {
                'prober': 'prober',
                'watcher': 'watcher',
                'admin': 'admin'
            }
            
            logger.info("真实数据池初始化完成")
            
        except Exception as e:
            logger.error(f"初始化失败: {str(e)}")
            raise
    
    def _load_index(self):
        """加载数据索引"""
        with self.lock:
            if os.path.exists(self.index_file):
                try:
                    with open(self.index_file, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except Exception as e:
                    logger.error(f"加载索引失败: {str(e)}")
                    return {}
            return {}
    
    def _save_index(self):
        """保存数据索引"""
        with self.lock:
            try:
                with open(self.index_file, 'w', encoding='utf-8') as f:
                    json.dump(self.index, f, indent=2, ensure_ascii=False)
            except Exception as e:
                logger.error(f"保存索引失败: {str(e)}")
    
    def _encrypt_data(self, data):
        """加密数据"""
        try:
            # 生成随机IV
            iv = os.urandom(16)
            
            # 创建加密器
            cipher = Cipher(
                algorithms.AES(self.encryption_key),
                modes.CBC(iv),
                backend=default_backend()
            )
            encryptor = cipher.encryptor()
            
            # 填充数据
            data_str = json.dumps(data, ensure_ascii=False)
            data_bytes = data_str.encode('utf-8')
            padding_length = 16 - (len(data_bytes) % 16)
            padded_data = data_bytes + (b' ' * padding_length)
            
            # 加密
            ciphertext = encryptor.update(padded_data) + encryptor.finalize()
            
            # 返回IV和密文
            return base64.b64encode(iv + ciphertext).decode('utf-8')
        except Exception as e:
            logger.error(f"加密数据失败: {str(e)}")
            raise
    
    def _decrypt_data(self, encrypted_data):
        """解密数据"""
        try:
            # 解码base64
            data = base64.b64decode(encrypted_data.encode('utf-8'))
            
            # 提取IV和密文
            iv = data[:16]
            ciphertext = data[16:]
            
            # 创建解密器
            cipher = Cipher(
                algorithms.AES(self.encryption_key),
                modes.CBC(iv),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            
            # 解密
            plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            
            # 去除填充
            plaintext = plaintext.rstrip(b' ')
            
            # 解析JSON
            return json.loads(plaintext.decode('utf-8'))
        except Exception as e:
            logger.error(f"解密数据失败: {str(e)}")
            raise
    
    def store_data(self, data, data_type, agent_name):
        """存储数据"""
        if agent_name not in self.agent_roles:
            logger.error(f"Agent {agent_name} 不存在")
            return None
        
        role = self.agent_roles[agent_name]
        if not self.roles[role].get('store_data', False):
            logger.error(f"Agent {agent_name} 无权限存储数据")
            return None
        
        try:
            with self.lock:
                # 生成数据ID
                data_id = hashlib.md5(f"{datetime.now().isoformat()}{str(data)}".encode('utf-8')).hexdigest()
                
                # 加密数据
                encrypted_data = self._encrypt_data(data)
                
                # 存储数据
                data_file = os.path.join(self.data_dir, f"{data_id}.enc")
                with open(data_file, 'w', encoding='utf-8') as f:
                    f.write(encrypted_data)
                
                # 更新索引
                self.index[data_id] = {
                    "data_type": data_type,
                    "agent_name": agent_name,
                    "stored_at": datetime.now().isoformat(),
                    "size": len(encrypted_data),
                    "access_count": 0
                }
                self._save_index()
                
                # 放入内存缓存
                if len(self.memory_cache) >= self.cache_size:
                    # 清理最早的缓存项（LRU策略，移除最久未使用的项）
                    oldest_key, _ = self.memory_cache.popitem(last=False)
                    logger.debug(f"清理缓存项: {oldest_key}")
                
                # 将新数据放入缓存，自动移到字典末尾（LRU策略）
                self.memory_cache[data_id] = data
                logger.debug(f"新数据放入缓存: {data_id}")
            
            logger.info(f"数据存储成功: {data_id}")
            return data_id
        except Exception as e:
            logger.error(f"存储数据失败: {str(e)}")
            return None
    
    def retrieve_data(self, data_id, agent_name):
        """检索数据"""
        if agent_name not in self.agent_roles:
            logger.error(f"Agent {agent_name} 不存在")
            return None
        
        role = self.agent_roles[agent_name]
        if not self.roles[role].get('retrieve_data', False):
            logger.error(f"Agent {agent_name} 无权限检索数据")
            return None
        
        try:
            data = None
            with self.lock:
                # 检查数据是否存在
                if data_id not in self.index:
                    logger.error(f"数据不存在: {data_id}")
                    return None
                
                # 检查内存缓存
                if data_id in self.memory_cache:
                    logger.debug(f"从缓存中获取数据: {data_id}")
                    # 将访问的项移到字典末尾，实现LRU策略
                    data = self.memory_cache.pop(data_id)
                    self.memory_cache[data_id] = data
                else:
                    # 从文件读取数据
                    data_file = os.path.join(self.data_dir, f"{data_id}.enc")
                    if not os.path.exists(data_file):
                        logger.error(f"数据文件不存在: {data_file}")
                        return None
                    
                    with open(data_file, 'r', encoding='utf-8') as f:
                        encrypted_data = f.read()
                    
                    # 解密数据
                    data = self._decrypt_data(encrypted_data)
                    
                    # 放入内存缓存
                    if len(self.memory_cache) >= self.cache_size:
                        # 清理最早的缓存项（LRU策略，移除最久未使用的项）
                        oldest_key, _ = self.memory_cache.popitem(last=False)
                        logger.debug(f"清理缓存项: {oldest_key}")
                    
                    self.memory_cache[data_id] = data
                    logger.debug(f"数据放入缓存: {data_id}")
                
                # 更新访问计数
                self.index[data_id]["access_count"] += 1
                self.index[data_id]["last_accessed"] = datetime.now().isoformat()
                self._save_index()
            
            logger.info(f"数据检索成功: {data_id}")
            return data
        except Exception as e:
            logger.error(f"检索数据失败: {str(e)}")
            return None
    
    def slice_data(self, data_id, slice_size=1024, agent_name=None):
        """数据切片"""
        if agent_name:
            if agent_name not in self.agent_roles:
                logger.error(f"Agent {agent_name} 不存在")
                return []
            
            role = self.agent_roles[agent_name]
            if not self.roles[role].get('retrieve_data', False):
                logger.error(f"Agent {agent_name} 无权限切片数据")
                return []
        
        try:
            # 检索数据
            data = self.retrieve_data(data_id, agent_name or 'prober')
            if not data:
                return []
            
            # 转换为字符串
            data_str = json.dumps(data, ensure_ascii=False)
            
            # 切片
            slices = []
            for i in range(0, len(data_str), slice_size):
                slice_data = data_str[i:i+slice_size]
                slices.append({
                    "slice_id": f"{data_id}_slice_{i//slice_size}",
                    "data": slice_data,
                    "sequence": i//slice_size,
                    "total_slices": (len(data_str) + slice_size - 1) // slice_size
                })
            
            logger.info(f"数据切片成功: {data_id}, 共 {len(slices)} 片")
            return slices
        except Exception as e:
            logger.error(f"数据切片失败: {str(e)}")
            return []
    
    def delete_data(self, data_id, agent_name):
        """删除数据"""
        if agent_name not in self.agent_roles:
            logger.error(f"Agent {agent_name} 不存在")
            return False
        
        role = self.agent_roles[agent_name]
        if not self.roles[role].get('delete_data', False):
            logger.error(f"Agent {agent_name} 无权限删除数据")
            return False
        
        try:
            with self.lock:
                # 检查数据是否存在
                if data_id not in self.index:
                    logger.error(f"数据不存在: {data_id}")
                    return False
                
                # 删除数据文件
                data_file = os.path.join(self.data_dir, f"{data_id}.enc")
                if os.path.exists(data_file):
                    os.remove(data_file)
                
                # 从内存缓存中删除
                if data_id in self.memory_cache:
                    del self.memory_cache[data_id]
                    logger.debug(f"从缓存中删除数据: {data_id}")
                
                # 从索引中删除
                del self.index[data_id]
                self._save_index()
            
            logger.info(f"数据删除成功: {data_id}")
            return True
        except Exception as e:
            logger.error(f"删除数据失败: {str(e)}")
            return False
    
    def list_data(self, data_type=None, agent_name=None):
        """列出数据"""
        if agent_name:
            if agent_name not in self.agent_roles:
                logger.error(f"Agent {agent_name} 不存在")
                return []
            
            role = self.agent_roles[agent_name]
            if not self.roles[role].get('list_data', False):
                logger.error(f"Agent {agent_name} 无权限列出数据")
                return []
        
        try:
            data_list = []
            with self.lock:
                for data_id, info in self.index.items():
                    if data_type and info["data_type"] != data_type:
                        continue
                    data_list.append({
                        "data_id": data_id,
                        "data_type": info["data_type"],
                        "stored_at": info["stored_at"],
                        "access_count": info.get("access_count", 0),
                        "last_accessed": info.get("last_accessed", "N/A")
                    })
            
            # 按存储时间排序
            data_list.sort(key=lambda x: x["stored_at"], reverse=True)
            
            return data_list
        except Exception as e:
            logger.error(f"列出数据失败: {str(e)}")
            return []
    
    def get_data_info(self, data_id, agent_name=None):
        """获取数据信息"""
        if agent_name:
            if agent_name not in self.agent_roles:
                logger.error(f"Agent {agent_name} 不存在")
                return None
            
            role = self.agent_roles[agent_name]
            if not self.roles[role].get('list_data', False):
                logger.error(f"Agent {agent_name} 无权限获取数据信息")
                return None
        
        with self.lock:
            return self.index.get(data_id)
    
    def clear_expired_data(self, days=7, agent_name=None):
        """清理过期数据"""
        if agent_name:
            if agent_name not in self.agent_roles:
                logger.error(f"Agent {agent_name} 不存在")
                return 0
            
            role = self.agent_roles[agent_name]
            if not self.roles[role].get('delete_data', False):
                logger.error(f"Agent {agent_name} 无权限清理过期数据")
                return 0
        
        try:
            expired_count = 0
            current_time = datetime.now()
            
            # 找出过期数据
            expired_ids = []
            with self.lock:
                for data_id, info in self.index.items():
                    stored_time = datetime.fromisoformat(info["stored_at"])
                    if (current_time - stored_time).days > days:
                        expired_ids.append(data_id)
            
            # 删除过期数据
            for data_id in expired_ids:
                if self.delete_data(data_id, agent_name or 'prober'):
                    expired_count += 1
            
            logger.info(f"清理过期数据完成，共删除 {expired_count} 条数据")
            return expired_count
        except Exception as e:
            logger.error(f"清理过期数据失败: {str(e)}")
            return 0

if __name__ == "__main__":
    # 测试代码
    data_pool = RealDataPool()
    
    # 测试存储数据
    test_data = {
        "user_id": "user123",
        "data": "这是敏感数据",
        "timestamp": datetime.now().isoformat()
    }
    
    data_id = data_pool.store_data(test_data, "user_data", "prober")
    print(f"存储数据ID: {data_id}")
    
    # 测试检索数据
    retrieved_data = data_pool.retrieve_data(data_id, "prober")
    print(f"检索数据: {retrieved_data}")
    
    # 测试数据切片
    slices = data_pool.slice_data(data_id, 50, "prober")
    print(f"数据切片数: {len(slices)}")
    for i, slice_data in enumerate(slices):
        print(f"切片 {i}: {slice_data['data'][:20]}...")
    
    # 测试列出数据
    data_list = data_pool.list_data()
    print(f"数据列表: {data_list}")
    
    # 测试清理过期数据
    expired_count = data_pool.clear_expired_data(0)  # 清理所有数据
    print(f"清理过期数据数: {expired_count}")
