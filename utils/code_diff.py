# © 2026 MirageShield 团队 版权所有，侵权必究
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s:%(funcName)s:%(lineno)d - %(message)s'
)
logger = logging.getLogger('utils.code_diff')

# 默认删除阈值
DEFAULT_DELETION_THRESHOLD = 100

def count_deleted_lines(old_content, new_content):
    """
    计算两个字符串之间删除的行数
    
    Args:
        old_content (str): 旧版本的内容
        new_content (str): 新版本的内容
    
    Returns:
        int: 删除的行数
    """
    # 分割成行，不保留换行符
    old_lines = old_content.splitlines()
    new_lines = new_content.splitlines()
    
    # 初始化计数器
    deleted_lines = 0
    
    # 使用双指针法比较
    i = j = 0
    old_len, new_len = len(old_lines), len(new_lines)
    
    while i < old_len and j < new_len:
        if old_lines[i] == new_lines[j]:
            # 行相同，继续比较下一行
            i += 1
            j += 1
        else:
            # 行不同，尝试在旧内容中找到当前新行
            found = False
            for k in range(i + 1, old_len):
                if old_lines[k] == new_lines[j]:
                    # 找到匹配点，计算中间删除的行数
                    deleted_lines += k - i
                    i = k + 1
                    j += 1
                    found = True
                    break
            if not found:
                # 新行在旧内容中不存在，继续检查下一个新行
                j += 1
    
    # 处理剩余的旧行
    deleted_lines += old_len - i
    
    return deleted_lines


def count_deleted_lines_from_files(old_file_path, new_file_path):
    """
    计算两个文件之间删除的行数
    
    Args:
        old_file_path (str): 旧版本文件路径
        new_file_path (str): 新版本文件路径
    
    Returns:
        int: 删除的行数
    """
    try:
        with open(old_file_path, 'r', encoding='utf-8') as f:
            old_content = f.read()
        with open(new_file_path, 'r', encoding='utf-8') as f:
            new_content = f.read()
        return count_deleted_lines(old_content, new_content)
    except Exception as e:
        logger.error(f"Error reading files: {e}")
        return 0


def check_deletion_threshold(old_content, new_content, threshold=DEFAULT_DELETION_THRESHOLD, file_path=None, reason=None):
    """
    检查代码删除是否超过阈值
    
    Args:
        old_content (str): 旧版本的内容
        new_content (str): 新版本的内容
        threshold (int): 删除阈值，默认为100行
        file_path (str, optional): 删除操作的文件路径
        reason (str, optional): 删除原因
    
    Returns:
        tuple: (是否超过阈值, 删除的行数)
    """
    deleted_lines = count_deleted_lines(old_content, new_content)
    exceeds_threshold = deleted_lines > threshold
    
    if exceeds_threshold:
        # 触发通知机制
        notify_deletion_exceeds_threshold(deleted_lines, threshold, file_path, reason)
    
    return exceeds_threshold, deleted_lines


def check_deletion_threshold_from_files(old_file_path, new_file_path, threshold=DEFAULT_DELETION_THRESHOLD, file_path=None, reason=None):
    """
    检查文件删除是否超过阈值
    
    Args:
        old_file_path (str): 旧版本文件路径
        new_file_path (str): 新版本文件路径
        threshold (int): 删除阈值，默认为100行
        file_path (str, optional): 删除操作的文件路径
        reason (str, optional): 删除原因
    
    Returns:
        tuple: (是否超过阈值, 删除的行数)
    """
    try:
        with open(old_file_path, 'r', encoding='utf-8') as f:
            old_content = f.read()
        with open(new_file_path, 'r', encoding='utf-8') as f:
            new_content = f.read()
        return check_deletion_threshold(old_content, new_content, threshold, file_path, reason)
    except Exception as e:
        logger.error(f"Error reading files: {e}")
        return False, 0


def notify_deletion_exceeds_threshold(deleted_lines, threshold, file_path=None, reason=None):
    """
    当删除行数超过阈值时触发通知
    
    Args:
        deleted_lines (int): 删除的行数
        threshold (int): 阈值
        file_path (str, optional): 删除操作的文件路径
        reason (str, optional): 删除原因
    """
    # 构建通知模板
    notification_template = f"""
    🚨 代码删除告警 🚨
    
    🔍 检测到代码删除操作：
    - 文件路径: {file_path or '未知文件'}
    - 删除行数: {deleted_lines} 行
    - 阈值设置: {threshold} 行
    - 删除原因: {reason or '未提供'}
    
    ⚠️  请注意：删除行数已超过设定阈值，请确认是否为正常操作。
    """
    
    # 记录告警日志
    logger.warning(notification_template)
    
    # 这里可以扩展其他通知方式，如邮件、短信等
    # 例如：发送邮件通知管理员
    # send_email_notification("代码删除阈值告警", notification_template)
    
    # 例如：发送系统内部通知
    # from control_plane.strategy_engine import StrategyEngine
    # strategy_engine = StrategyEngine()
    # strategy_engine.notify("code_deletion_warning", {
    #     "deleted_lines": deleted_lines, 
    #     "threshold": threshold,
    #     "file_path": file_path,
    #     "reason": reason
    # })

