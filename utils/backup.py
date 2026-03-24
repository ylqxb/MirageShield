# © 2026 MirageShield 团队 版权所有，侵权必究
# 本项目已申请发明专利，未经许可禁止商用
# 备份模块自动备份机制
import os
import shutil
import datetime
import logging

# 配置日志
logger = logging.getLogger('utils.backup')

# 备份目录
BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backups')

# 确保备份目录存在
def ensure_backup_dir():
    """确保备份目录存在"""
    os.makedirs(BACKUP_DIR, exist_ok=True)

# 备份用户数据文件
def backup_users_data():
    """备份用户数据文件"""
    ensure_backup_dir()
    
    # 用户数据文件路径
    users_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'users.json')
    
    if not os.path.exists(users_file):
        logger.warning("用户数据文件不存在，跳过备份")
        return False
    
    # 生成备份文件名
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(BACKUP_DIR, f'users_{timestamp}.json')
    
    try:
        shutil.copy2(users_file, backup_file)
        logger.info(f"用户数据备份成功: {backup_file}")
        
        # 清理旧备份，保留最近5个
        cleanup_old_backups()
        
        return True
    except Exception as e:
        logger.error(f"备份用户数据失败: {str(e)}")
        return False

# 清理旧备份
def cleanup_old_backups():
    """清理旧备份，保留最近5个"""
    ensure_backup_dir()
    
    # 获取所有备份文件
    backup_files = [f for f in os.listdir(BACKUP_DIR) if f.startswith('users_') and f.endswith('.json')]
    
    # 按修改时间排序
    backup_files.sort(key=lambda x: os.path.getmtime(os.path.join(BACKUP_DIR, x)), reverse=True)
    
    # 保留最近5个备份
    if len(backup_files) > 5:
        for file_to_delete in backup_files[5:]:
            file_path = os.path.join(BACKUP_DIR, file_to_delete)
            try:
                os.remove(file_path)
                logger.info(f"清理旧备份: {file_to_delete}")
            except Exception as e:
                logger.error(f"清理旧备份失败: {str(e)}")

# 恢复用户数据
def restore_users_data(backup_file=None):
    """恢复用户数据"""
    ensure_backup_dir()
    
    # 用户数据文件路径
    users_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'users.json')
    
    # 如果没有指定备份文件，使用最新的
    if not backup_file:
        backup_files = [f for f in os.listdir(BACKUP_DIR) if f.startswith('users_') and f.endswith('.json')]
        if not backup_files:
            logger.error("没有找到备份文件")
            return False
        
        # 按修改时间排序，获取最新的
        backup_files.sort(key=lambda x: os.path.getmtime(os.path.join(BACKUP_DIR, x)), reverse=True)
        backup_file = os.path.join(BACKUP_DIR, backup_files[0])
    
    if not os.path.exists(backup_file):
        logger.error(f"备份文件不存在: {backup_file}")
        return False
    
    try:
        # 先创建当前状态的备份
        backup_users_data()
        
        # 恢复备份
        shutil.copy2(backup_file, users_file)
        logger.info(f"用户数据恢复成功: {backup_file}")
        return True
    except Exception as e:
        logger.error(f"恢复用户数据失败: {str(e)}")
        return False

# 获取备份列表
def get_backup_list():
    """获取备份列表"""
    ensure_backup_dir()
    
    backup_files = [f for f in os.listdir(BACKUP_DIR) if f.startswith('users_') and f.endswith('.json')]
    
    # 按修改时间排序
    backup_files.sort(key=lambda x: os.path.getmtime(os.path.join(BACKUP_DIR, x)), reverse=True)
    
    # 构建备份信息列表
    backup_list = []
    for file_name in backup_files:
        file_path = os.path.join(BACKUP_DIR, file_name)
        try:
            file_size = os.path.getsize(file_path) / 1024  # KB
            modified_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
            backup_list.append({
                'file_name': file_name,
                'size': f"{file_size:.2f} KB",
                'modified_time': modified_time.strftime('%Y-%m-%d %H:%M:%S'),
                'path': file_path
            })
        except Exception as e:
            logger.error(f"获取备份信息失败: {str(e)}")
    
    return backup_list

# 初始化备份目录
ensure_backup_dir()
