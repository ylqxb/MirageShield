# © 2026 MirageShield 团队 版权所有，侵权必究
# 本项目已申请发明专利，未经许可禁止商用
import os
import logging
import json
import threading
import time
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request

# 导入缓存装饰器和清除缓存函数
from utils.cache import cached, clear_cache

# 创建硬件管理蓝图
hardware_bp = Blueprint('hardware', __name__, url_prefix='/api/hardware')

# 配置日志
logger = logging.getLogger('api.hardware')

# 硬件设备状态存储
hardware_status = {
    'camera': {
        'status': 'unknown',  # unknown, enabled, disabled, in_use
        'last_access': None,
        'last_access_app': None,
        'allowed_apps': ['Teams.exe', 'Zoom.exe', 'Skype.exe', 'Chrome.exe'],
        'priority': 'high'
    },
    'microphone': {
        'status': 'unknown',
        'last_access': None,
        'last_access_app': None,
        'allowed_apps': ['Teams.exe', 'Zoom.exe', 'Skype.exe', 'Chrome.exe'],
        'priority': 'medium'
    },
    'speaker': {
        'status': 'unknown',
        'last_access': None,
        'last_access_app': None,
        'allowed_apps': ['Teams.exe', 'Zoom.exe', 'Skype.exe', 'Chrome.exe', 'Spotify.exe'],
        'priority': 'medium'
    },
    'storage': {
        'status': 'unknown',
        'last_access': None,
        'last_access_app': None,
        'allowed_apps': ['Explorer.exe', 'Notepad.exe', 'Office.exe'],
        'priority': 'high'
    },
    'network': {
        'status': 'unknown',
        'last_access': None,
        'last_access_app': None,
        'allowed_apps': ['Chrome.exe', 'Firefox.exe', 'Teams.exe'],
        'priority': 'high'
    },
    'bluetooth': {
        'status': 'unknown',
        'last_access': None,
        'last_access_app': None,
        'allowed_apps': ['BluetoothManager.exe', 'Teams.exe'],
        'priority': 'medium'
    },
    'printer': {
        'status': 'unknown',
        'last_access': None,
        'last_access_app': None,
        'allowed_apps': ['Word.exe', 'Excel.exe', 'PowerPoint.exe'],
        'priority': 'low'
    }
}

# 硬件访问事件存储
hardware_events = []

# 硬件访问请求存储
hardware_requests = []

# 进程状态存储 (blocked: 禁用, allowed: 允许)
process_status = {
    'blocked': ['TestApp.exe'],
    'allowed': [
        'Teams.exe', 'Zoom.exe', 'Skype.exe', 'Chrome.exe',
        'Firefox.exe', 'Edge.exe', 'Safari.exe', 'Opera.exe',
        'Word.exe', 'Excel.exe', 'PowerPoint.exe', 'Outlook.exe',
        'Notepad.exe', 'Explorer.exe', 'Taskmgr.exe', 'cmd.exe',
        'Spotify.exe', 'VLC.exe', 'Photoshop.exe', 'VSCode.exe',
        'IntelliJ.exe', 'VisualStudio.exe', 'Git.exe', 'Node.exe',
        'OneNote.exe', 'Access.exe', 'Publisher.exe', 'Project.exe',
        'Acrobat.exe', 'WinRAR.exe', '7z.exe', 'Notepad++.exe',
        'Paint.exe', 'Calculator.exe', 'SnippingTool.exe', 'StickyNotes.exe',
        'Discord.exe', 'Slack.exe', 'Telegram.exe', 'WhatsApp.exe',
        'Steam.exe', 'Origin.exe', 'EpicGamesLauncher.exe', 'Battle.net.exe',
        'Python.exe', 'Java.exe', 'dotnet.exe', 'npm.exe',
        'yarn.exe', 'pip.exe', 'docker.exe', 'kubectl.exe'
    ]
}

hardware_lock = threading.RLock()

# 清理过期事件

def cleanup_old_events():
    """清理过期的硬件访问事件"""
    global hardware_events
    with hardware_lock:
        # 保留最近7天的事件
        cutoff_time = datetime.now() - timedelta(days=7)
        hardware_events = [event for event in hardware_events if datetime.fromisoformat(event['timestamp']) > cutoff_time]
        logger.info(f"清理过期事件后，剩余事件数量: {len(hardware_events)}")

# 模拟硬件访问监控（实际部署时替换为真实监控）
def monitor_hardware():
    """模拟硬件访问监控"""
    logger.info("硬件监控服务启动")
    # 实际实现时，这里会使用Windows API监控硬件访问
    
    # 启动定时清理任务
    def cleanup_task():
        while True:
            time.sleep(3600)  # 每小时清理一次
            cleanup_old_events()
    
    cleanup_thread = threading.Thread(target=cleanup_task, daemon=True)
    cleanup_thread.start()

# 初始化硬件监控
hardware_monitor_thread = threading.Thread(target=monitor_hardware, daemon=True)
hardware_monitor_thread.start()

# 硬件设备名称映射
hardware_names = {
    'camera': '摄像头',
    'microphone': '麦克风',
    'speaker': '扬声器',
    'storage': '存储设备',
    'network': '网络适配器',
    'bluetooth': '蓝牙设备',
    'printer': '打印机'
}

# 获取硬件设备列表
@hardware_bp.route('/devices', methods=['GET'])
@cached(timeout=10)
def get_hardware_devices():
    """获取硬件设备列表"""
    try:
        devices = []
        for device_id, status in hardware_status.items():
            devices.append({
                "id": device_id,
                "name": hardware_names.get(device_id, device_id),
                "priority": status.get('priority', 'medium'),
                "status": status['status'],
                "last_access": status['last_access'],
                "last_access_app": status['last_access_app']
            })
        return jsonify(devices)
    except Exception as e:
        logger.error(f"获取硬件设备列表失败: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 获取硬件设备状态
@hardware_bp.route('/status/<device_id>', methods=['GET'])
@cached(timeout=5)
def get_hardware_status(device_id):
    """获取硬件设备状态"""
    try:
        if device_id not in hardware_status:
            return jsonify({"error": "设备不存在"}), 404
        
        status = hardware_status[device_id]
        last_access_app = status['last_access_app']
        
        # 检查最后访问的应用是否在黑名单中
        if last_access_app and last_access_app in process_status['blocked']:
            # 如果最后访问的应用在黑名单中，返回blocked状态，但不显示被阻止的应用
            return jsonify({
                "device_id": device_id,
                "status": "blocked",
                "last_access": status['last_access'],
                "last_access_app": "",  # 不显示被阻止的应用
                "allowed_apps": status['allowed_apps']
            })
        
        # 否则返回原始状态
        return jsonify({
            "device_id": device_id,
            "status": status['status'],
            "last_access": status['last_access'],
            "last_access_app": status['last_access_app'],
            "allowed_apps": status['allowed_apps']
        })
    except Exception as e:
        logger.error(f"获取硬件状态失败: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 管理硬件访问策略
@hardware_bp.route('/policy/<device_id>', methods=['GET', 'POST'])
def manage_hardware_policy(device_id):
    """管理硬件访问策略"""
    try:
        if device_id not in hardware_status:
            return jsonify({"error": "设备不存在"}), 404
        
        if request.method == 'GET':
            # 获取当前策略
            policy = {
                "device_id": device_id,
                "allowed_apps": hardware_status[device_id]['allowed_apps'],
                "blocked_apps": []  # 实际实现时可添加
            }
            return jsonify(policy)
        
        elif request.method == 'POST':
            # 更新策略
            data = request.get_json()
            if 'allowed_apps' in data:
                # 检查是否包含黑名单中的应用
                blocked_apps_in_request = [app for app in data['allowed_apps'] if app in process_status['blocked']]
                if blocked_apps_in_request:
                    # 拒绝包含黑名单应用的请求
                    logger.warning(f"拒绝更新策略: 包含黑名单应用 {blocked_apps_in_request}")
                    return jsonify({"success": False, "message": f"更新失败: 不能将黑名单应用 {blocked_apps_in_request} 添加到白名单中"}), 403
                
                with hardware_lock:
                    hardware_status[device_id]['allowed_apps'] = data['allowed_apps']
                    logger.info(f"更新{device_id}的访问策略: {data['allowed_apps']}")
                # 清除相关缓存
                clear_cache(['get_hardware_devices', 'get_hardware_status', 'get_hardware_policy', 'get_processes'])
            return jsonify({"success": True, "message": "策略更新成功"})
    except Exception as e:
        logger.error(f"管理硬件策略失败: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 查询硬件访问事件
@hardware_bp.route('/events', methods=['GET'])
def get_hardware_events():
    """查询硬件访问事件"""
    try:
        limit = int(request.args.get('limit', 50))
        events = hardware_events[-limit:]
        return jsonify(events)
    except Exception as e:
        logger.error(f"获取硬件事件失败: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 模拟硬件访问检测（实际部署时替换为真实检测）
def simulate_hardware_access(device_id, app_name, status):
    """模拟硬件访问检测"""
    with hardware_lock:
        # 强制将黑名单应用的状态设置为blocked
        if app_name in process_status['blocked']:
            actual_status = "blocked"
            action = "blocked"
        else:
            is_allowed = app_name in hardware_status[device_id]['allowed_apps'] or app_name in process_status['allowed']
            actual_status = status if is_allowed else "blocked"
            action = "allowed" if is_allowed else "blocked"
        
        # 更新硬件状态
        hardware_status[device_id]['status'] = actual_status
        hardware_status[device_id]['last_access'] = datetime.now().isoformat()
        hardware_status[device_id]['last_access_app'] = app_name
        
        # 记录事件
        event = {
            "timestamp": datetime.now().isoformat(),
            "device_id": device_id,
            "device_name": hardware_names.get(device_id, device_id),
            "app_name": app_name,
            "status": actual_status,
            "action": action
        }
        hardware_events.append(event)
        if len(hardware_events) > 1000:
            hardware_events.pop(0)
        
        # 为白名单应用创建访问请求
        if app_name in process_status['allowed']:
            # 创建访问请求
            request_id = f"req_{datetime.now().timestamp()}"
            hardware_request = {
                "id": request_id,
                "device_id": device_id,
                "device_name": hardware_names.get(device_id, device_id),
                "app_name": app_name,
                "reason": "应用需要访问硬件设备",
                "status": "approved",  # 白名单应用自动批准
                "timestamp": datetime.now().isoformat(),
                "security_verified": True
            }
            hardware_requests.append(hardware_request)
            if len(hardware_requests) > 100:
                hardware_requests.pop(0)
            
            logger.info(f"白名单应用访问请求: {app_name} 请求访问 {device_id} - 自动批准")
        # 为未知应用创建访问请求
        elif app_name not in process_status['blocked'] and not is_allowed:
            # 创建访问请求
            request_id = f"req_{datetime.now().timestamp()}"
            hardware_request = {
                "id": request_id,
                "device_id": device_id,
                "device_name": hardware_names.get(device_id, device_id),
                "app_name": app_name,
                "reason": "应用需要访问硬件设备",
                "status": "pending",  # 未知应用需要批准
                "timestamp": datetime.now().isoformat(),
                "security_verified": False
            }
            hardware_requests.append(hardware_request)
            if len(hardware_requests) > 100:
                hardware_requests.pop(0)
            
            logger.info(f"未知应用访问请求: {app_name} 请求访问 {device_id} - 等待批准")
        
        # 记录详细日志
        logger.info(f"{device_id}访问事件: {app_name} - {actual_status} - {action} - 黑名单: {app_name in process_status['blocked']} - 白名单: {is_allowed}")
        # 清除相关缓存
        clear_cache(['get_hardware_devices', 'get_hardware_status'])

# 测试端点
@hardware_bp.route('/test', methods=['POST'])
def test_hardware_access():
    """测试硬件访问"""
    try:
        data = request.get_json()
        device_id = data.get('device_id')
        app_name = data.get('app_name')
        status = data.get('status', 'in_use')
        
        if not device_id or not app_name:
            return jsonify({"error": "缺少参数"}), 400
        
        # 检查应用是否在黑名单中
        if app_name in process_status['blocked']:
            # 黑名单应用直接显示为blocked
            status = 'blocked'
        
        # 调用模拟硬件访问检测函数
        simulate_hardware_access(device_id, app_name, status)
        return jsonify({"success": True, "message": "硬件访问测试成功"})
    except Exception as e:
        logger.error(f"测试硬件访问失败: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 禁用硬件访问
@hardware_bp.route('/disable/<device_id>', methods=['POST'])
def disable_hardware(device_id):
    """禁用硬件访问"""
    try:
        if device_id not in hardware_status:
            return jsonify({"error": "设备不存在"}), 404
        
        data = request.get_json()
        app_name = data.get('app_name')
        
        if not app_name:
            return jsonify({"error": "缺少应用名称"}), 400
        
        with hardware_lock:
            # 记录禁用事件
            event = {
                "timestamp": datetime.now().isoformat(),
                "device_id": device_id,
                "device_name": hardware_names.get(device_id, device_id),
                "app_name": app_name,
                "status": "disabled",
                "action": "blocked",
                "reason": "unauthorized_access"
            }
            hardware_events.append(event)
            if len(hardware_events) > 1000:
                hardware_events.pop(0)
            
            # 更新硬件状态
            hardware_status[device_id]['status'] = 'disabled'
            hardware_status[device_id]['last_access'] = datetime.now().isoformat()
            hardware_status[device_id]['last_access_app'] = app_name
            
            logger.info(f"禁用{device_id}访问: {app_name} - 原因: 未授权访问")
            # 清除相关缓存
            clear_cache(['get_hardware_devices', 'get_hardware_status'])
        
        return jsonify({"success": True, "message": f"已禁用{app_name}对{device_id}的访问"})
    except Exception as e:
        logger.error(f"禁用硬件访问失败: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 获取硬件访问控制策略
@hardware_bp.route('/policy', methods=['GET'])
@cached(timeout=30)
def get_hardware_policy():
    """获取硬件访问控制策略"""
    try:
        policy = {
            "deterrence_level": 2,  # 威慑级别: 1-低, 2-中, 3-高
            "auto_block_threshold": 3,  # 自动阻止阈值
            "require_approval": True  # 要求手动批准硬件访问
        }
        
        # 添加所有硬件设备的策略
        for device_id, status in hardware_status.items():
            policy[device_id] = {
                "allowed_apps": status['allowed_apps'],
                "blocked_apps": []
            }
        
        return jsonify(policy)
    except Exception as e:
        logger.error(f"获取硬件策略失败: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 发送硬件访问请求
@hardware_bp.route('/request', methods=['POST'])
def request_hardware_access():
    """发送硬件访问请求"""
    try:
        data = request.get_json()
        device_id = data.get('device_id')
        app_name = data.get('app_name')
        reason = data.get('reason', '需要访问硬件设备')
        
        if not device_id or not app_name:
            return jsonify({"error": "缺少参数"}), 400
        
        if device_id not in hardware_status:
            return jsonify({"error": "设备不存在"}), 404
        
        with hardware_lock:
            # 检查应用是否在黑名单中
            if app_name in process_status['blocked']:
                # 直接拒绝黑名单中的应用访问
                event = {
                    "timestamp": datetime.now().isoformat(),
                    "device_id": device_id,
                    "device_name": "摄像头" if device_id == 'camera' else "麦克风",
                    "app_name": app_name,
                    "status": "blocked",
                    "action": "blocked",
                    "reason": "blacklisted_app"
                }
                hardware_events.append(event)
                if len(hardware_events) > 1000:
                    hardware_events.pop(0)
                
                # 更新硬件状态
                hardware_status[device_id]['status'] = 'blocked'
                hardware_status[device_id]['last_access'] = datetime.now().isoformat()
                hardware_status[device_id]['last_access_app'] = app_name
                
                logger.info(f"拒绝黑名单应用访问: {app_name} 请求访问 {device_id} - 原因: 应用在黑名单中")
                return jsonify({"success": False, "message": "访问被拒绝: 应用在黑名单中", "action": "blocked"}), 403
            
            # 创建访问请求
            request_id = f"req_{datetime.now().timestamp()}"
            hardware_request = {
                "id": request_id,
                "device_id": device_id,
                "device_name": "摄像头" if device_id == 'camera' else "麦克风",
                "app_name": app_name,
                "reason": reason,
                "status": "pending",  # pending, approved, denied
                "timestamp": datetime.now().isoformat(),
                "security_verified": False
            }
            hardware_requests.append(hardware_request)
            if len(hardware_requests) > 100:
                hardware_requests.pop(0)
            
            logger.info(f"收到硬件访问请求: {app_name} 请求访问 {device_id} - 原因: {reason}")
        
        return jsonify({"success": True, "message": "硬件访问请求已提交", "request_id": request_id})
    except Exception as e:
        logger.error(f"发送硬件访问请求失败: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 获取硬件访问请求列表
@hardware_bp.route('/requests', methods=['GET'])
def get_hardware_requests():
    """获取硬件访问请求列表"""
    try:
        status = request.args.get('status', 'all')
        
        if status == 'all':
            requests = hardware_requests
        else:
            requests = [req for req in hardware_requests if req['status'] == status]
        
        return jsonify(requests)
    except Exception as e:
        logger.error(f"获取硬件访问请求失败: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 批准硬件访问请求
@hardware_bp.route('/request/<request_id>/approve', methods=['POST'])
def approve_hardware_request(request_id):
    """批准硬件访问请求"""
    try:
        with hardware_lock:
            for req in hardware_requests:
                if req['id'] == request_id and req['status'] == 'pending':
                    # 批准请求
                    req['status'] = 'approved'
                    req['security_verified'] = True
                    req['approved_at'] = datetime.now().isoformat()
                    
                    # 将应用添加到白名单
                    device_id = req['device_id']
                    app_name = req['app_name']
                    if app_name not in hardware_status[device_id]['allowed_apps']:
                        hardware_status[device_id]['allowed_apps'].append(app_name)
                        logger.info(f"已将 {app_name} 添加到 {device_id} 的白名单")
                    
                    # 记录批准事件
                    event = {
                        "timestamp": datetime.now().isoformat(),
                        "device_id": device_id,
                        "device_name": req['device_name'],
                        "app_name": app_name,
                        "status": "approved",
                        "action": "allowed",
                        "reason": "user_approval"
                    }
                    hardware_events.append(event)
                    if len(hardware_events) > 1000:
                        hardware_events.pop(0)
                    
                    logger.info(f"批准硬件访问请求: {app_name} 可以访问 {device_id}")
                    # 清除相关缓存
                    clear_cache(['get_hardware_devices', 'get_hardware_status', 'get_hardware_policy', 'get_processes'])
                    return jsonify({"success": True, "message": "硬件访问请求已批准"})
        
        return jsonify({"error": "请求不存在或已处理"}), 404
    except Exception as e:
        logger.error(f"批准硬件访问请求失败: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 拒绝硬件访问请求
@hardware_bp.route('/request/<request_id>/deny', methods=['POST'])
def deny_hardware_request(request_id):
    """拒绝硬件访问请求"""
    try:
        with hardware_lock:
            for req in hardware_requests:
                if req['id'] == request_id and req['status'] == 'pending':
                    # 拒绝请求
                    req['status'] = 'denied'
                    req['denied_at'] = datetime.now().isoformat()
                    
                    # 记录拒绝事件
                    event = {
                        "timestamp": datetime.now().isoformat(),
                        "device_id": req['device_id'],
                        "device_name": req['device_name'],
                        "app_name": req['app_name'],
                        "status": "denied",
                        "action": "blocked",
                        "reason": "user_denial"
                    }
                    hardware_events.append(event)
                    if len(hardware_events) > 1000:
                        hardware_events.pop(0)
                    
                    # 将应用添加到禁用列表
                    if req['app_name'] not in process_status['blocked']:
                        process_status['blocked'].append(req['app_name'])
                    
                    # 从允许列表中移除
                    if req['app_name'] in process_status['allowed']:
                        process_status['allowed'].remove(req['app_name'])
                    
                    logger.info(f"拒绝硬件访问请求: {req['app_name']} 不允许访问 {req['device_id']}")
                    # 清除相关缓存
                    clear_cache(['get_hardware_devices', 'get_hardware_status', 'get_hardware_policy', 'get_processes'])
                    return jsonify({"success": True, "message": "硬件访问请求已拒绝"})
        
        return jsonify({"error": "请求不存在或已处理"}), 404
    except Exception as e:
        logger.error(f"拒绝硬件访问请求失败: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 获取进程状态列表
@hardware_bp.route('/processes', methods=['GET'])
def get_processes():
    """获取进程状态列表"""
    try:
        logger.info(f"返回进程状态: {process_status}")
        return jsonify(process_status)
    except Exception as e:
        logger.error(f"获取进程状态失败: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 禁用进程
@hardware_bp.route('/process/block', methods=['POST'])
def block_process():
    """禁用进程"""
    try:
        data = request.get_json()
        process_name = data.get('process_name')
        
        if not process_name:
            return jsonify({"error": "缺少进程名称"}), 400
        
        with hardware_lock:
            # 添加到禁用列表
            if process_name not in process_status['blocked']:
                process_status['blocked'].append(process_name)
            
            # 从允许列表中移除
            if process_name in process_status['allowed']:
                process_status['allowed'].remove(process_name)
            
            # 从硬件白名单中移除
            for device_id in hardware_status:
                if process_name in hardware_status[device_id]['allowed_apps']:
                    hardware_status[device_id]['allowed_apps'].remove(process_name)
            
            # 记录事件
            event = {
                "timestamp": datetime.now().isoformat(),
                "device_id": "system",
                "device_name": "系统",
                "app_name": process_name,
                "status": "blocked",
                "action": "blocked",
                "reason": "user_block"
            }
            hardware_events.append(event)
            if len(hardware_events) > 1000:
                hardware_events.pop(0)
            
            logger.info(f"禁用进程: {process_name}")
            # 清除相关缓存
            clear_cache(['get_hardware_devices', 'get_hardware_status', 'get_hardware_policy', 'get_processes'])
        
        return jsonify({"success": True, "message": f"已禁用进程: {process_name}"})
    except Exception as e:
        logger.error(f"禁用进程失败: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 允许进程
@hardware_bp.route('/process/allow', methods=['POST'])
def allow_process():
    """允许进程"""
    try:
        data = request.get_json()
        process_name = data.get('process_name')
        
        if not process_name:
            return jsonify({"error": "缺少进程名称"}), 400
        
        with hardware_lock:
            # 添加到允许列表
            if process_name not in process_status['allowed']:
                process_status['allowed'].append(process_name)
            
            # 从禁用列表中移除
            if process_name in process_status['blocked']:
                process_status['blocked'].remove(process_name)
            
            # 添加到硬件白名单
            for device_id in hardware_status:
                if process_name not in hardware_status[device_id]['allowed_apps']:
                    hardware_status[device_id]['allowed_apps'].append(process_name)
            
            # 记录事件
            event = {
                "timestamp": datetime.now().isoformat(),
                "device_id": "system",
                "device_name": "系统",
                "app_name": process_name,
                "status": "allowed",
                "action": "allowed",
                "reason": "user_allow"
            }
            hardware_events.append(event)
            if len(hardware_events) > 1000:
                hardware_events.pop(0)
            
            logger.info(f"允许进程: {process_name}")
            # 清除相关缓存
            clear_cache(['get_hardware_devices', 'get_hardware_status', 'get_hardware_policy', 'get_processes'])
        
        return jsonify({"success": True, "message": f"已允许进程: {process_name}"})
    except Exception as e:
        logger.error(f"允许进程失败: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 手动变换进程身份
@hardware_bp.route('/process/transform', methods=['POST'])
def transform_process():
    """手动变换进程身份"""
    try:
        data = request.get_json()
        process_name = data.get('process_name')
        new_identity = data.get('new_identity')
        
        if not process_name or not new_identity:
            return jsonify({"error": "缺少参数"}), 400
        
        with hardware_lock:
            # 记录变换事件
            event = {
                "timestamp": datetime.now().isoformat(),
                "device_id": "system",
                "device_name": "系统",
                "app_name": process_name,
                "status": "transformed",
                "action": "transformed",
                "reason": "user_transform",
                "new_identity": new_identity
            }
            hardware_events.append(event)
            if len(hardware_events) > 1000:
                hardware_events.pop(0)
            
            logger.info(f"变换进程身份: {process_name} -> {new_identity}")
        
        return jsonify({"success": True, "message": f"已变换进程身份: {process_name} -> {new_identity}"})
    except Exception as e:
        logger.error(f"变换进程身份失败: {str(e)}")
        return jsonify({"error": str(e)}), 500
