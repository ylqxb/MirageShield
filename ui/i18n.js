// © 2026 MirageShield 团队 版权所有，侵权必究
// 多语言支持
const i18n = {
    // 中文
    'zh-CN': {
        // 页面标题
        'page.title': 'MirageShield 幻象屏障主动防御系统',
        'page.subtitle': '实时监控与管理平台',
        
        // 状态区域
        'section.system_status': '系统状态',
        'section.agent_status': '智能体状态',
        'section.network_status': '网络状态',
        'section.lan_status': '局域网管理',
        'section.data_transfer': '数据传输',
        'section.community_status': '社区联防',
        'section.operation_control': '操作控制',

        'section.assessment_history': '威胁评估历史',
        'section.protection_result': '防护结果',
        'section.logs': '系统日志',
        'section.monitoring': '系统监控',
        'section.hardware': '硬件管理',
        'hardware.camera': '摄像头',
        'hardware.microphone': '麦克风',
        'hardware.speaker': '扬声器',
        'hardware.storage': '存储设备',
        'hardware.network': '网络适配器',
        'hardware.bluetooth': '蓝牙设备',
        'hardware.printer': '打印机',
        'hardware.status': '状态',
        'hardware.last_access': '上次访问',
        'hardware.last_app': '访问应用',
        'hardware.priority': '优先级',
        'hardware.priority.high': '高优先级',
        'hardware.priority.medium': '中等优先级',
        'hardware.priority.low': '低优先级',
        'hardware.status.unknown': '未知',
        'hardware.status.enabled': '已启用',
        'hardware.status.disabled': '已禁用',
        'hardware.status.in_use': '使用中',
        'hardware.allowed': '允许',
        'hardware.success.block': '禁用成功: ',
        'hardware.error.block': '禁用失败: ',
        'hardware.success.approve': '批准成功: ',
        'hardware.error.approve': '批准失败: ',
        'hardware.success.deny': '拒绝成功: ',
        'hardware.error.deny': '拒绝失败: ',
        'hardware.success.allow': '允许成功: ',
        'hardware.error.allow': '允许失败: ',
        'hardware.success.transform': '变换成功: ',
        'hardware.error.transform': '变换失败: ',
        'hardware.error.unknown': '未知错误',
        'hardware.error.operation': '操作失败: ',
        'hardware.error.enter_process_name': '请输入进程名称',
        'hardware.error.enter_transform_info': '请输入原进程名称和新身份',
        'button.refresh_hardware': '刷新状态',
        'button.test_hardware': '测试访问',
        'toast.hardware_refreshed': '硬件状态已刷新',
        'toast.hardware_test_success': '硬件访问测试成功',
        'toast.hardware_test_failed': '硬件访问测试失败',
        'hardware.never': '从未',
        'hardware.none': '无',
        'button.detailed_monitoring': '详细监控',
        'hardware.allowed_apps': '允许访问的应用',
        'hardware.events': '硬件访问事件',
        'hardware.requests': '硬件访问请求',
        'hardware.processes': '进程管理',
        'hardware.refresh_events': '刷新事件',
        'hardware.refresh_requests': '刷新请求',
        'hardware.refresh_processes': '刷新进程',
        'hardware.time': '时间',
        'hardware.device': '设备',
        'hardware.app': '应用',
        'hardware.reason': '原因',
        'hardware.action': '操作',
        'hardware.system_action': '系统操作',
        'hardware.manual_action': '手动操作',
        'hardware.loading': '加载中...',
        'hardware.allowed_processes': '允许的进程',
        'hardware.blocked_processes': '禁用的进程',
        'hardware.process_actions': '进程操作',
        'hardware.process_name': '进程名称:',
        'hardware.block_process': '禁用进程',
        'hardware.allow_process': '允许进程',
        'hardware.transform_identity': '变换进程身份',
        'hardware.original_process': '原进程名称:',
        'hardware.new_identity': '新身份:',
        'hardware.transform': '变换身份',
        'hardware.real_time_updating': '实时更新中',
        'hardware.back_to_main': '返回主界面',
        'hardware.blocked': '阻止',
        'hardware.block_access': '禁用访问',
        'hardware.no_requests': '暂无请求',
        'hardware.example': '例如:',
        'hardware.status.pending': '待处理',
        'hardware.status.approved': '已批准',
        'hardware.status.denied': '已拒绝',
        'hardware.approve': '批准',
        'hardware.deny': '拒绝',
        'hardware.status.enabled': '已启用',
        'hardware.status.disabled': '已禁用',
        'hardware.status.in_use': '使用中',
        'hardware.allowed': '允许',
        'hardware.success.block': '禁用成功: ',
        'hardware.error.block': '禁用失败: ',
        'hardware.success.approve': '批准成功: ',
        'hardware.error.approve': '批准失败: ',
        'hardware.success.deny': '拒绝成功: ',
        'hardware.error.deny': '拒绝失败: ',
        'hardware.success.allow': '允许成功: ',
        'hardware.error.allow': '允许失败: ',
        'hardware.success.transform': '变换成功: ',
        'hardware.error.transform': '变换失败: ',
        'hardware.error.unknown': '未知错误',
        'hardware.error.operation': '操作失败: ',
        'hardware.error.enter_process_name': '请输入进程名称',
        'hardware.error.enter_transform_info': '请输入原进程名称和新身份',
        
        // 防护级别
        'protection.level': '防护级别:',
        'protection.level.0': '0 - 关闭防护',
        'protection.level.1': '1 - 基础防护',
        'protection.level.2': '2 - 标准防护',
        'protection.level.3': '3 - 高级防护',
        'protection.level.4': '4 - 全面防护',
        'protection.apply': '应用',
        
        // 按钮
        'button.refresh': '刷新状态',

        'button.advanced': '高级选项',
        'button.sync_community': '同步社区情报',
        'button.rotate_ips': '执行IP轮换',
        'button.reconstruct': '网络整建迁移',
        'button.confirm_safety': '确认安全',
        'button.refresh_nodes': '刷新节点',
        'button.connect_node': '连接节点',
        'button.send_data': '发送数据',
        'button.refresh_transfers': '刷新传输',
        'button.back_to_main': '返回主页面',
        'button.refresh_logs': '刷新日志',
        'button.view_logs': '查看系统日志',
        'log.level.all': '所有级别',
        'log.level.error': '错误',
        'log.level.warning': '警告',
        'log.level.info': '信息',
        'log.search.placeholder': '搜索日志...',
        'log.stats': '显示 {count} 条日志，共 {total} 条',
        'logs.page.title': '系统日志 - MirageShield',
        'logs.page.subtitle': '实时系统日志查看与管理',
        
        // 高级操作
        'advanced.title': '高级操作',
        
        // 防护结果
        'protection.status': '当前威胁状态',
        'protection.current_level': '当前防护级别',
        'protection.strategy': '防护策略',
        'protection.capability': '防护能力',
        'protection.bait_ratio': '诱饵比例',
        'protection.path_complexity': '路径复杂度',
        'protection.psychological_level': '心理战等级',
        'protection.safety_confirm': '安全确认',
        'protection.safety_confirm_hint': '确认安全后可调整防护级别',
        
        // 威胁状态
        'threat.safe': '安全',
        'threat.confirmed_safe': '已确认安全',
        'threat.high': '存在高威胁',
        'threat.low': '低威胁',
        'threat.adjustable': '可调整',
        'threat.basic': '基础防护',
        'threat.standard': '标准防护',
        'threat.full': '全面防护',
        'threat.system_protected': '系统已启动最高级别防护',
        'threat.system_normal': '系统运行正常',
        
        // 系统状态
        'system.status': '系统状态',
        'system.last_updated': '最后更新',
        'system.current_strategy': '当前策略',
        
        // 智能体状态
        'agent.prober': '数据采集和安全传输',
        'agent.baiter': '假数据生成和蜜罐管理',
        'agent.watcher': '监控和分析',
        
        // 网络状态
        'network.health_score': '网络健康分数',
        'network.node_status': '节点状态',
        'network.total_nodes': '总节点',
        'network.active_nodes': '活跃',
        'network.inactive_nodes': '不活跃',
        'network.ip_pool': 'IP池状态',
        'network.available_ips': '可用IP',
        'network.used_ips': '已用IP',
        
        // 社区联防
        'community.blacklist': '黑名单',
        'community.ip_count': 'IP数量',
        'community.fingerprint_count': '指纹数量',
        'community.last_updated': '最后更新',
        
        // 威胁评估历史
        'assessment.no_history': '无评估历史',
        'assessment.no_records': '暂无威胁评估记录',
        'assessment.attack_type': '攻击类型',
        'assessment.ip': 'IP',
        'assessment.time': '时间',
        

        
        // 提示信息
        'toast.community_sync_success': '社区同步成功',
        'toast.community_sync_failed': '社区同步失败',
        'toast.ip_rotate_success': 'IP轮换成功',
        'toast.ip_rotate_failed': 'IP轮换失败',
        'toast.reconstruct_success': '网络整建迁移成功',
        'toast.reconstruct_failed': '网络整建迁移失败',
        'toast.protection_level_set': '防护级别已设置为',
        'toast.protection_level_failed': '设置防护级别失败',
        'toast.cannot_lower_level': '当前存在高威胁，无法降低防护级别。请先确认安全。',
        'toast.check_threat_failed': '检查威胁状态失败',
        'toast.auto_adjust_failed': '自动调整防护级别失败',
        'toast.confirmed_safe': '已确认安全，现在可以调整防护级别',
        
        // 确认对话框
        'confirm.rotate_ips': '确定要执行IP轮换吗？',
        'confirm.reconstruct': '确定要执行网络整建迁移吗？这可能会暂时影响网络连接。',
        
        // 防护级别提示
        'protection.level.0.warning': '警告: 关闭防护将使系统完全暴露在攻击风险中。确定要继续吗？',
        'protection.level.1.info': '基础防护: 提供基本的安全保障，对系统性能影响最小。',
        'protection.level.2.info': '标准防护: 提供平衡的安全保障和性能。',
        'protection.level.3.info': '高级防护: 提供全面的安全保障，可能对系统性能有一定影响。',
        'protection.level.4.info': '全面防护: 提供最高级别的安全保障，可能会影响系统响应速度。',
        
        // 错误信息
        'error.loading': '加载中...',
        'error.failed_to_get_threat_history': '无法获取威胁历史',
        'error.failed_to_get_protection_result': '无法获取防护结果',
        'error.failed_to_get_system_status': '无法获取系统状态',
        'error.failed_to_get_agent_status': '无法获取智能体状态',
        'error.failed_to_get_network_status': '无法获取网络状态',
        'error.failed_to_get_community_status': '无法获取社区状态',
        'error.failed_to_get_assessment_history': '无法获取评估历史',
        'error.failed_to_get_monitoring_data': '获取系统监控数据失败',
        'error.failed_to_get_lan_nodes': '获取局域网节点失败',
        'error.failed_to_connect_node': '连接节点失败',
        'error.failed_to_send_data': '发送数据失败',
        'error.failed_to_get_transfers': '获取传输列表失败',
        'error.failed_to_get_transfer_status': '获取传输详情失败',
        'error.failed_to_pause_transfer': '暂停传输失败',
        'error.failed_to_resume_transfer': '恢复传输失败',
        'error.failed_to_cancel_transfer': '取消传输失败',
        // 日志相关
        'logs.no_records': '无日志记录',
        'logs.no_logs_generated': '系统尚未生成任何日志记录',
        'logs.no_matching_logs': '没有符合条件的日志记录',
        'logs.loading_failed': '加载失败',
        'logs.failed_to_get_logs': '获取日志失败',
        // 局域网管理相关
        'lan.no_nodes': '无局域网节点',
        'lan.no_nodes_found': '未发现任何局域网节点',
        'lan.connect_success': '连接成功',
        'lan.connect_failed': '连接失败',
        'lan.enter_ip': '请输入节点IP:',
        'lan.enter_port': '请输入节点端口:',
        'lan.management': '局域网管理',
        'lan.refresh_nodes': '刷新节点',
        'lan.connect_node': '连接节点',
        'lan.ip': 'IP',
        'lan.port': '端口',
        'lan.status': '状态',
        // 数据传输相关
        'transfer.no_records': '无传输记录',
        'transfer.no_transfers_found': '未发现任何传输记录',
        'transfer.send_success': '数据发送成功',
        'transfer.send_failed': '数据发送失败',
        'transfer.status': '传输详情',
        'transfer.pause': '暂停',
        'transfer.resume': '恢复',
        'transfer.cancel': '取消',
        'transfer.confirm_cancel': '确定要取消此传输吗？',
        'transfer.paused': '传输已暂停',
        'transfer.resumed': '传输已恢复',
        'transfer.cancelled': '传输已取消',
        'transfer.enter_target': '请输入目标IP:',
        'transfer.enter_data': '请输入要发送的数据:',
        'transfer.target': '目标',
        'transfer.status_label': '状态',
        'transfer.progress': '进度',
        'transfer.size': '大小',
        'transfer.transfer': '传输',
        'transfer.id': 'ID',
        'transfer.start_time': '开始时间',
        'transfer.end_time': '结束时间',
        'transfer.error.invalid_ip': '无效的IP地址格式',
        'transfer.error.empty_fields': '请输入目标IP和数据',
        'transfer.error.data_too_large': '数据大小超过限制（最大1MB）',
        'transfer.error.unsafe_content': '数据包含不安全内容',
        // 传输状态
        'transfer.status.pending': '待处理',
        'transfer.status.in_progress': '进行中',
        'transfer.status.completed': '已完成',
        'transfer.status.failed': '失败',
        'transfer.status.paused': '已暂停',
        
        // 监控相关
        'monitoring.cpu_usage': 'CPU使用率',
        'monitoring.average': '平均',
        'monitoring.cores': '核心数',
        'monitoring.memory_usage': '内存使用',
        'monitoring.used': '已用',
        'monitoring.available': '可用',
        'monitoring.usage_percent': '使用率',
        'monitoring.disk_usage': '磁盘使用',
        'monitoring.free': '空闲',
        'monitoring.network_traffic': '网络流量',
        'monitoring.sent': '发送',
        'monitoring.received': '接收',
        'monitoring.process_info': '进程信息',
        'monitoring.total_processes': '总进程数',
        'monitoring.active_processes': '活跃进程',
        'monitoring.loading_failed': '加载失败',
        'monitoring.Bytes': 'Bytes',
        'monitoring.KB': 'KB',
        'monitoring.MB': 'MB',
        'monitoring.GB': 'GB',
        'monitoring.TB': 'TB',
        
        // 页脚
        'footer.copyright': '© 2026 MirageShield 团队 版权所有，侵权必究 - 版本 1.0.0',
        
        // 语言切换
        'language.zh': '中文',
        'language.en': 'English',
        
        // 导航栏
        'nav.title': '导航',
        'nav.navigation': 'Navigation',
        
        // 登录相关
        'login.title': '用户登录',
        'login.username': '用户名',
        'login.password': '密码',
        'login.button': '登录',
        'login.cancel': '取消',
        'login.register': '没有账号？立即注册',
        'login.success': '登录成功',
        'login.failure': '登录失败',
        
        // 注册相关
        'register.title': '用户注册',
        'register.username': '用户名',
        'register.password': '密码',
        'register.button': '注册',
        'register.cancel': '取消',
        'register.login': '已有账号？立即登录',
        'register.success': '注册成功，请登录',
        'register.failure': '注册失败',
        
        // 密码修改相关
        'password.change.title': '修改密码',
        'password.change.current': '当前密码',
        'password.change.new': '新密码',
        'password.change.confirm': '确认新密码',
        'password.change.button': '修改密码',
        'password.change.cancel': '取消',
        'password.change.first_login': '首次登录请修改初始密码',
        'password.change.success': '密码修改成功',
        'password.change.failure': '密码修改失败',
        'password.change.mismatch': '新密码和确认密码不一致',
        
        // 退出相关
        'logout.button': '退出',
        'logout.success': '退出登录成功'
    },
    
    // 英文
    'en-US': {
        // 页面标题
        'page.title': 'MirageShield Active Defense System',
        'page.subtitle': 'Real-time Monitoring and Management Platform',
        
        // 状态区域
        'section.system_status': 'System Status',
        'section.agent_status': 'Agent Status',
        'section.network_status': 'Network Status',
        'section.lan_status': 'LAN Management',
        'section.data_transfer': 'Data Transfer',
        'section.community_status': 'Community Defense',
        'section.operation_control': 'Operation Control',

        'section.assessment_history': 'Threat Assessment History',
        'section.protection_result': 'Protection Results',
        'section.logs': 'System Logs',
        'section.monitoring': 'System Monitoring',
        'section.hardware': 'Hardware Management',
        'hardware.camera': 'Camera',
        'hardware.microphone': 'Microphone',
        'hardware.speaker': 'Speaker',
        'hardware.storage': 'Storage Device',
        'hardware.network': 'Network Adapter',
        'hardware.bluetooth': 'Bluetooth Device',
        'hardware.printer': 'Printer',
        'hardware.status': 'Status',
        'hardware.last_access': 'Last Access',
        'hardware.last_app': 'Access App',
        'hardware.priority': 'Priority',
        'hardware.priority.high': 'High Priority',
        'hardware.priority.medium': 'Medium Priority',
        'hardware.priority.low': 'Low Priority',
        'hardware.status.unknown': 'Unknown',
        'hardware.status.enabled': 'Enabled',
        'hardware.status.disabled': 'Disabled',
        'hardware.status.in_use': 'In Use',
        'hardware.allowed': 'Allowed',
        'hardware.success.block': 'Blocked successfully: ',
        'hardware.error.block': 'Block failed: ',
        'hardware.success.approve': 'Approved successfully: ',
        'hardware.error.approve': 'Approve failed: ',
        'hardware.success.deny': 'Denied successfully: ',
        'hardware.error.deny': 'Deny failed: ',
        'hardware.success.allow': 'Allowed successfully: ',
        'hardware.error.allow': 'Allow failed: ',
        'hardware.success.transform': 'Transformed successfully: ',
        'hardware.error.transform': 'Transform failed: ',
        'hardware.error.unknown': 'Unknown error',
        'hardware.error.operation': 'Operation failed: ',
        'hardware.error.enter_process_name': 'Please enter process name',
        'hardware.error.enter_transform_info': 'Please enter original process name and new identity',
        'button.refresh_hardware': 'Refresh Status',
        'button.test_hardware': 'Test Access',
        'toast.hardware_refreshed': 'Hardware status refreshed',
        'toast.hardware_test_success': 'Hardware access test successful',
        'toast.hardware_test_failed': 'Hardware access test failed',
        'hardware.never': 'Never',
        'hardware.none': 'None',
        'button.detailed_monitoring': 'Detailed Monitoring',
        'hardware.allowed_apps': 'Allowed Apps',
        'hardware.events': 'Hardware Access Events',
        'hardware.requests': 'Hardware Access Requests',
        'hardware.processes': 'Process Management',
        'hardware.refresh_events': 'Refresh Events',
        'hardware.refresh_requests': 'Refresh Requests',
        'hardware.refresh_processes': 'Refresh Processes',
        'hardware.time': 'Time',
        'hardware.device': 'Device',
        'hardware.app': 'App',
        'hardware.reason': 'Reason',
        'hardware.action': 'Action',
        'hardware.system_action': 'System Action',
        'hardware.manual_action': 'Manual Action',
        'hardware.loading': 'Loading...',
        'hardware.allowed_processes': 'Allowed Processes',
        'hardware.blocked_processes': 'Blocked Processes',
        'hardware.process_actions': 'Process Actions',
        'hardware.process_name': 'Process Name:',
        'hardware.block_process': 'Block Process',
        'hardware.allow_process': 'Allow Process',
        'hardware.transform_identity': 'Transform Process Identity',
        'hardware.original_process': 'Original Process:',
        'hardware.new_identity': 'New Identity:',
        'hardware.transform': 'Transform',
        'hardware.real_time_updating': 'Real-time Updating',
        'hardware.back_to_main': 'Back to Main Page',
        'hardware.blocked': 'Blocked',
        'hardware.block_access': 'Block Access',
        'hardware.no_requests': 'No Requests',
        'hardware.example': 'Example:',
        'hardware.status.pending': 'Pending',
        'hardware.status.approved': 'Approved',
        'hardware.status.denied': 'Denied',
        'hardware.approve': 'Approve',
        'hardware.deny': 'Deny',
        'hardware.status.enabled': 'Enabled',
        'hardware.status.disabled': 'Disabled',
        'hardware.status.in_use': 'In Use',
        'hardware.allowed': 'Allowed',
        'hardware.success.block': 'Blocked successfully: ',
        'hardware.error.block': 'Block failed: ',
        'hardware.success.approve': 'Approved successfully: ',
        'hardware.error.approve': 'Approve failed: ',
        'hardware.success.deny': 'Denied successfully: ',
        'hardware.error.deny': 'Deny failed: ',
        'hardware.success.allow': 'Allowed successfully: ',
        'hardware.error.allow': 'Allow failed: ',
        'hardware.success.transform': 'Transformed successfully: ',
        'hardware.error.transform': 'Transform failed: ',
        'hardware.error.unknown': 'Unknown error',
        'hardware.error.operation': 'Operation failed: ',
        'hardware.error.enter_process_name': 'Please enter process name',
        'hardware.error.enter_transform_info': 'Please enter original process name and new identity',
        
        // 防护级别
        'protection.level': 'Protection Level:',
        'protection.level.0': '0 - Disable Protection',
        'protection.level.1': '1 - Basic Protection',
        'protection.level.2': '2 - Standard Protection',
        'protection.level.3': '3 - Advanced Protection',
        'protection.level.4': '4 - Full Protection',
        'protection.apply': 'Apply',
        
        // 按钮
        'button.refresh': 'Refresh Status',

        'button.advanced': 'Advanced Options',
        'button.sync_community': 'Sync Community Intelligence',
        'button.rotate_ips': 'Execute IP Rotation',
        'button.reconstruct': 'Network Reconstruction Migration',
        'button.confirm_safety': 'Confirm Safety',
        'button.refresh_nodes': 'Refresh Nodes',
        'button.connect_node': 'Connect Node',
        'button.send_data': 'Send Data',
        'button.refresh_transfers': 'Refresh Transfers',
        'button.back_to_main': 'Back to Main Page',
        'button.refresh_logs': 'Refresh Logs',
        'button.view_logs': 'View System Logs',
        'log.level.all': 'All Levels',
        'log.level.error': 'Error',
        'log.level.warning': 'Warning',
        'log.level.info': 'Info',
        'log.search.placeholder': 'Search logs...',
        'log.stats': 'Showing {count} logs, total {total}',
        'logs.page.title': 'System Logs - MirageShield',
        'logs.page.subtitle': 'Real-time System Logs Viewing and Management',
        
        // 高级操作
        'advanced.title': 'Advanced Operations',
        
        // 防护结果
        'protection.status': 'Current Threat Status',
        'protection.current_level': 'Current Protection Level',
        'protection.strategy': 'Protection Strategy',
        'protection.capability': 'Protection Capability',
        'protection.bait_ratio': 'Bait Ratio',
        'protection.path_complexity': 'Path Complexity',
        'protection.psychological_level': 'Psychological Warfare Level',
        'protection.safety_confirm': 'Safety Confirmation',
        'protection.safety_confirm_hint': 'You can adjust protection level after confirming safety',
        
        // 威胁状态
        'threat.safe': 'Safe',
        'threat.confirmed_safe': 'Safety Confirmed',
        'threat.high': 'High Threat Detected',
        'threat.low': 'Low Threat',
        'threat.adjustable': 'Adjustable',
        'threat.basic': 'Basic Protection',
        'threat.standard': 'Standard Protection',
        'threat.full': 'Full Protection',
        'threat.system_protected': 'System has activated highest level protection',
        'threat.system_normal': 'System running normally',
        
        // 系统状态
        'system.status': 'System Status',
        'system.last_updated': 'Last Updated',
        'system.current_strategy': 'Current Strategy',
        
        // 智能体状态
        'agent.prober': 'Data collection and secure transmission',
        'agent.baiter': 'Fake data generation and honeypot management',
        'agent.watcher': 'Monitoring and analysis',
        
        // 网络状态
        'network.health_score': 'Network Health Score',
        'network.node_status': 'Node Status',
        'network.total_nodes': 'Total Nodes',
        'network.active_nodes': 'Active',
        'network.inactive_nodes': 'Inactive',
        'network.ip_pool': 'IP Pool Status',
        'network.available_ips': 'Available IPs',
        'network.used_ips': 'Used IPs',
        
        // 社区联防
        'community.blacklist': 'Blacklist',
        'community.ip_count': 'IP Count',
        'community.fingerprint_count': 'Fingerprint Count',
        'community.last_updated': 'Last Updated',
        
        // 威胁评估历史
        'assessment.no_history': 'No Assessment History',
        'assessment.no_records': 'No threat assessment records',
        'assessment.attack_type': 'Attack Type',
        'assessment.ip': 'IP',
        'assessment.time': 'Time',
        

        
        // 提示信息
        'toast.community_sync_success': 'Community sync successful',
        'toast.community_sync_failed': 'Community sync failed',
        'toast.ip_rotate_success': 'IP rotation successful',
        'toast.ip_rotate_failed': 'IP rotation failed',
        'toast.reconstruct_success': 'Network reconstruction successful',
        'toast.reconstruct_failed': 'Network reconstruction failed',
        'toast.protection_level_set': 'Protection level set to',
        'toast.protection_level_failed': 'Failed to set protection level',
        'toast.cannot_lower_level': 'High threat detected, cannot lower protection level. Please confirm safety first.',
        'toast.check_threat_failed': 'Failed to check threat status',
        'toast.auto_adjust_failed': 'Failed to automatically adjust protection level',
        'toast.confirmed_safe': 'Safety confirmed, you can now adjust protection level',
        
        // 确认对话框
        'confirm.rotate_ips': 'Are you sure you want to execute IP rotation?',
        'confirm.reconstruct': 'Are you sure you want to execute network reconstruction? This may temporarily affect network connectivity.',
        
        // 防护级别提示
        'protection.level.0.warning': 'Warning: Disabling protection will fully expose the system to attack risks. Are you sure you want to continue?',
        'protection.level.1.info': 'Basic Protection: Provides basic security with minimal impact on system performance.',
        'protection.level.2.info': 'Standard Protection: Provides balanced security and performance.',
        'protection.level.3.info': 'Advanced Protection: Provides comprehensive security, which may have some impact on system performance.',
        'protection.level.4.info': 'Full Protection: Provides the highest level of security, which may affect system response speed.',
        
        // 错误信息
        'error.loading': 'Loading...',
        'error.failed_to_get_threat_history': 'Failed to get threat history',
        'error.failed_to_get_protection_result': 'Failed to get protection result',
        'error.failed_to_get_system_status': 'Failed to get system status',
        'error.failed_to_get_agent_status': 'Failed to get agent status',
        'error.failed_to_get_network_status': 'Failed to get network status',
        'error.failed_to_get_community_status': 'Failed to get community status',
        'error.failed_to_get_assessment_history': 'Failed to get assessment history',
        'error.failed_to_get_monitoring_data': 'Failed to get system monitoring data',
        'error.failed_to_get_lan_nodes': 'Failed to get LAN nodes',
        'error.failed_to_connect_node': 'Failed to connect node',
        'error.failed_to_send_data': 'Failed to send data',
        'error.failed_to_get_transfers': 'Failed to get transfers',
        'error.failed_to_get_transfer_status': 'Failed to get transfer status',
        'error.failed_to_pause_transfer': 'Failed to pause transfer',
        'error.failed_to_resume_transfer': 'Failed to resume transfer',
        'error.failed_to_cancel_transfer': 'Failed to cancel transfer',
        // 日志相关
        'logs.no_records': 'No Log Records',
        'logs.no_logs_generated': 'No log records have been generated yet',
        'logs.no_matching_logs': 'No matching logs found',
        'logs.loading_failed': 'Loading Failed',
        'logs.failed_to_get_logs': 'Failed to get logs',
        // 局域网管理相关
        'lan.no_nodes': 'No LAN Nodes',
        'lan.no_nodes_found': 'No LAN nodes found',
        'lan.connect_success': 'Connection successful',
        'lan.connect_failed': 'Connection failed',
        'lan.enter_ip': 'Please enter node IP:',
        'lan.enter_port': 'Please enter node port:',
        'lan.management': 'LAN Management',
        'lan.refresh_nodes': 'Refresh Nodes',
        'lan.connect_node': 'Connect Node',
        'lan.ip': 'IP',
        'lan.port': 'Port',
        'lan.status': 'Status',
        // 数据传输相关
        'transfer.no_records': 'No Transfer Records',
        'transfer.no_transfers_found': 'No transfer records found',
        'transfer.send_success': 'Data sent successfully',
        'transfer.send_failed': 'Failed to send data',
        'transfer.status': 'Transfer Details',
        'transfer.pause': 'Pause',
        'transfer.resume': 'Resume',
        'transfer.cancel': 'Cancel',
        'transfer.confirm_cancel': 'Are you sure you want to cancel this transfer?',
        'transfer.paused': 'Transfer paused',
        'transfer.resumed': 'Transfer resumed',
        'transfer.cancelled': 'Transfer cancelled',
        'transfer.enter_target': 'Please enter target IP:',
        'transfer.enter_data': 'Please enter data to send:',
        'transfer.target': 'Target',
        'transfer.status_label': 'Status',
        'transfer.progress': 'Progress',
        'transfer.size': 'Size',
        'transfer.transfer': 'Transfer',
        'transfer.id': 'ID',
        'transfer.start_time': 'Start Time',
        'transfer.end_time': 'End Time',
        'transfer.error.invalid_ip': 'Invalid IP address format',
        'transfer.error.empty_fields': 'Please enter target IP and data',
        'transfer.error.data_too_large': 'Data size exceeds limit (max 1MB)',
        'transfer.error.unsafe_content': 'Data contains unsafe content',
        // 传输状态
        'transfer.status.pending': 'Pending',
        'transfer.status.in_progress': 'In Progress',
        'transfer.status.completed': 'Completed',
        'transfer.status.failed': 'Failed',
        'transfer.status.paused': 'Paused',
        // 监控相关
        'monitoring.cpu_usage': 'CPU Usage',
        'monitoring.average': 'Average',
        'monitoring.cores': 'Cores',
        'monitoring.memory_usage': 'Memory Usage',
        'monitoring.used': 'Used',
        'monitoring.available': 'Available',
        'monitoring.usage_percent': 'Usage',
        'monitoring.disk_usage': 'Disk Usage',
        'monitoring.free': 'Free',
        'monitoring.network_traffic': 'Network Traffic',
        'monitoring.sent': 'Sent',
        'monitoring.received': 'Received',
        'monitoring.process_info': 'Process Info',
        'monitoring.total_processes': 'Total Processes',
        'monitoring.active_processes': 'Active Processes',
        'monitoring.loading_failed': 'Loading Failed',
        'monitoring.Bytes': 'Bytes',
        'monitoring.KB': 'KB',
        'monitoring.MB': 'MB',
        'monitoring.GB': 'GB',
        'monitoring.TB': 'TB',
        
        // 页脚
        'footer.copyright': '© 2026 MirageShield Team. All rights reserved. - Version 1.0.0',
        
        // 语言切换
        'language.zh': '中文',
        'language.en': 'English',
        
        // 导航栏
        'nav.title': 'Navigation',
        'nav.navigation': 'Navigation',
        
        // 登录相关
        'login.title': 'User Login',
        'login.username': 'Username',
        'login.password': 'Password',
        'login.button': 'Login',
        'login.cancel': 'Cancel',
        'login.register': 'Don\'t have an account? Register now',
        'login.success': 'Login successful',
        'login.failure': 'Login failed',
        
        // 注册相关
        'register.title': 'User Registration',
        'register.username': 'Username',
        'register.password': 'Password',
        'register.button': 'Register',
        'register.cancel': 'Cancel',
        'register.login': 'Already have an account? Login now',
        'register.success': 'Registration successful, please login',
        'register.failure': 'Registration failed',
        
        // 密码修改相关
        'password.change.title': 'Change Password',
        'password.change.current': 'Current Password',
        'password.change.new': 'New Password',
        'password.change.confirm': 'Confirm New Password',
        'password.change.button': 'Change Password',
        'password.change.cancel': 'Cancel',
        'password.change.first_login': 'Please change your initial password for first login',
        'password.change.success': 'Password changed successfully',
        'password.change.failure': 'Password change failed',
        'password.change.mismatch': 'New password and confirm password do not match',
        
        // 退出相关
        'logout.button': 'Logout',
        'logout.success': 'Logout successful'
    }
};

// 获取当前语言
function getCurrentLanguage() {
    return localStorage.getItem('language') || 'zh-CN';
}

// 设置语言
function setLanguage(lang) {
    localStorage.setItem('language', lang);
    document.documentElement.lang = lang;
    updateUI();
}

// 翻译函数
function t(key) {
    const lang = getCurrentLanguage();
    return i18n[lang][key] || key;
}

// 更新UI
function updateUI() {
    // 检查当前页面是否是logs.html
    const currentUrl = window.location.href;
    if (currentUrl.includes('logs.html')) {
        // 在logs.html页面上
        // 更新页面标题
        document.querySelector('title').textContent = t('logs.page.title');
        const headerH1 = document.getElementById('page-title');
        if (headerH1) {
            headerH1.textContent = t('logs.page.title');
        }
        const headerP = document.getElementById('page-subtitle');
        if (headerP) {
            headerP.textContent = t('logs.page.subtitle');
        }
        
        // 更新按钮
        const backButton = document.getElementById('back-button');
        if (backButton) {
            backButton.textContent = t('button.back_to_main');
        }
        const refreshButton = document.getElementById('refresh-button');
        if (refreshButton) {
            refreshButton.textContent = t('button.refresh_logs');
        }
        
        // 更新选择框选项
        const optionAll = document.getElementById('option-all');
        if (optionAll) {
            optionAll.textContent = t('log.level.all');
        }
        const optionError = document.getElementById('option-error');
        if (optionError) {
            optionError.textContent = t('log.level.error');
        }
        const optionWarning = document.getElementById('option-warning');
        if (optionWarning) {
            optionWarning.textContent = t('log.level.warning');
        }
        const optionInfo = document.getElementById('option-info');
        if (optionInfo) {
            optionInfo.textContent = t('log.level.info');
        }
        
        // 更新搜索框占位符
        const searchInput = document.getElementById('log-search');
        if (searchInput) {
            searchInput.placeholder = t('log.search.placeholder');
        }
        
        // 更新统计信息
        const logStatsText = document.getElementById('log-stats-text');
        if (logStatsText) {
            const logCount = document.getElementById('log-count').textContent;
            const totalLogCount = document.getElementById('total-log-count').textContent;
            logStatsText.textContent = t('log.stats').replace('{count}', logCount).replace('{total}', totalLogCount);
        }
        
        // 设置部分标题
        const sectionTitles = document.querySelectorAll('.section-title');
        sectionTitles.forEach(element => {
            element.textContent = t('section.logs');
        });
    } else {
        // 在其他页面上
        // 更新页面标题
        document.querySelector('title').textContent = t('page.title');
        const headerH1 = document.querySelector('header h1');
        if (headerH1) {
            headerH1.textContent = t('page.title');
        }
        const headerP = document.querySelector('header p');
        if (headerP) {
            headerP.textContent = t('page.subtitle');
        }
        
        // 按照顺序设置标题
        document.querySelectorAll('.section-title').forEach((element, index) => {
            const keys = [
                'section.system_status',
                'section.agent_status',
                'section.network_status',
                'section.lan_status',
                'section.data_transfer',
                'section.community_status',
                'section.operation_control',

                'section.assessment_history',
                'section.protection_result',
                'section.monitoring',
                'section.hardware'
            ];
            if (keys[index]) {
                element.textContent = t(keys[index]);
            }
        });
    }
    
    // 更新防护级别选择器
    const protectionLevelSelector = document.querySelector('.protection-level-selector');
    if (protectionLevelSelector) {
        const levelLabel = protectionLevelSelector.querySelector('label');
        if (levelLabel) {
            levelLabel.textContent = t('protection.level');
        }
        const levelButton = protectionLevelSelector.querySelector('button');
        if (levelButton) {
            levelButton.textContent = t('protection.apply');
        }
        
        // 更新防护级别选项
        const levelOptions = document.querySelectorAll('#protection-level option');
        levelOptions.forEach((option, index) => {
            option.textContent = t(`protection.level.${index}`);
        });
    }
    
    // 更新按钮
    // 刷新状态按钮
    const refreshButton = document.querySelector('button[onclick="refreshStatus()"]');
    if (refreshButton) {
        refreshButton.textContent = t('button.refresh');
    }
    

    
    // 高级选项按钮
    const advancedButton = document.querySelector('button[onclick="toggleAdvancedOptions()"]');
    if (advancedButton) {
        advancedButton.textContent = t('button.advanced');
    }
    
    // 查看系统日志按钮
    const viewLogsButton = document.getElementById('view-logs-button');
    if (viewLogsButton) {
        viewLogsButton.textContent = t('button.view_logs');
    }
    
    // 详情监控按钮
    const detailedMonitoringButton = document.getElementById('detailed-monitoring-button');
    if (detailedMonitoringButton) {
        detailedMonitoringButton.textContent = t('button.detailed_monitoring');
    }
    
    // 同步社区情报按钮
    const syncButton = document.querySelector('button[onclick="syncCommunity()"]');
    if (syncButton) {
        syncButton.textContent = t('button.sync_community');
    }
    
    // 执行IP轮换按钮
    const rotateButton = document.querySelector('button[onclick="rotateIPs()"]');
    if (rotateButton) {
        rotateButton.textContent = t('button.rotate_ips');
    }
    
    // 网络整建迁移按钮
    const reconstructButton = document.querySelector('button[onclick="reconstructNetwork()"]');
    if (reconstructButton) {
        reconstructButton.textContent = t('button.reconstruct');
    }
    
    // 确认安全按钮
    const confirmButton = document.querySelector('button[onclick="confirmSafety()"]');
    if (confirmButton) {
        confirmButton.textContent = t('button.confirm_safety');
    }
    
    // 应用按钮
    const applyButton = document.querySelector('.protection-level-selector button');
    if (applyButton) {
        applyButton.textContent = t('protection.apply');
    }
    
    // 局域网管理按钮
    const refreshNodesButton = document.querySelector('button[onclick="refreshLanNodes()"]');
    if (refreshNodesButton) {
        refreshNodesButton.textContent = t('button.refresh_nodes');
    }
    const connectNodeButton = document.querySelector('button[onclick="connectToLanNode()"]');
    if (connectNodeButton) {
        connectNodeButton.textContent = t('button.connect_node');
    }
    
    // 数据传输按钮
    const sendDataButton = document.querySelector('button[onclick="sendData()"]');
    if (sendDataButton) {
        sendDataButton.textContent = t('button.send_data');
    }
    const refreshTransfersButton = document.querySelector('button[onclick="refreshTransfers()"]');
    if (refreshTransfersButton) {
        refreshTransfersButton.textContent = t('button.refresh_transfers');
    }
    
    // 硬件管理按钮
    const refreshHardwareButton = document.querySelector('button[onclick="refreshHardwareStatus()"]');
    if (refreshHardwareButton) {
        refreshHardwareButton.textContent = t('button.refresh_hardware');
    }
    const testHardwareButton = document.querySelector('button[onclick="testHardwareAccess()"]');
    if (testHardwareButton) {
        testHardwareButton.textContent = t('button.test_hardware');
    }
    
    // 更新高级操作标题
    const advancedTitle = document.querySelector('#advanced-options .card-title');
    if (advancedTitle) {
        advancedTitle.textContent = t('advanced.title');
    }
    
    // 更新页脚
    document.querySelector('.footer p').textContent = t('footer.copyright');
    
    // 更新导航栏
    const navItems = document.querySelectorAll('.quick-nav li');
    const navKeys = [
        'section.system_status',
        'section.agent_status',
        'section.network_status',
        'section.lan_status',
        'section.data_transfer',
        'section.community_status',
        'section.operation_control',
        'section.assessment_history',
        'section.protection_result',
        'section.logs',
        'section.monitoring',
        'section.hardware'
    ];
    navItems.forEach((item, index) => {
        if (navKeys[index]) {
            const link = item.querySelector('a');
            if (link) {
                link.textContent = t(navKeys[index]);
            }
        }
    });
    

    
    // 更新登录按钮
    const loginButton = document.getElementById('loginBtn');
    if (loginButton) {
        loginButton.textContent = t('login.button');
    }
    
    // 更新退出按钮
    const logoutButton = document.querySelector('.user-info button');
    if (logoutButton) {
        logoutButton.textContent = t('logout.button');
    }
    
    // 更新登录模态框
    const loginModalTitle = document.querySelector('#loginModal .modal-header h2');
    if (loginModalTitle) {
        loginModalTitle.textContent = t('login.title');
    }
    const loginUsernameLabel = document.querySelector('#loginModal label[for="loginUsername"]');
    if (loginUsernameLabel) {
        loginUsernameLabel.textContent = t('login.username');
    }
    const loginPasswordLabel = document.querySelector('#loginModal label[for="loginPassword"]');
    if (loginPasswordLabel) {
        loginPasswordLabel.textContent = t('login.password');
    }
    const loginCancelButton = document.querySelector('#loginModal .btn-secondary');
    if (loginCancelButton) {
        loginCancelButton.textContent = t('login.cancel');
    }
    const loginSubmitButton = document.querySelector('#loginModal .btn-primary');
    if (loginSubmitButton) {
        loginSubmitButton.textContent = t('login.button');
    }
    const loginRegisterLink = document.querySelector('#loginModal .auth-link a');
    if (loginRegisterLink) {
        loginRegisterLink.textContent = t('login.register');
    }
    
    // 更新注册模态框
    const registerModalTitle = document.querySelector('#registerModal .modal-header h2');
    if (registerModalTitle) {
        registerModalTitle.textContent = t('register.title');
    }
    const registerUsernameLabel = document.querySelector('#registerModal label[for="registerUsername"]');
    if (registerUsernameLabel) {
        registerUsernameLabel.textContent = t('register.username');
    }
    const registerPasswordLabel = document.querySelector('#registerModal label[for="registerPassword"]');
    if (registerPasswordLabel) {
        registerPasswordLabel.textContent = t('register.password');
    }
    const registerCancelButton = document.querySelector('#registerModal .btn-secondary');
    if (registerCancelButton) {
        registerCancelButton.textContent = t('register.cancel');
    }
    const registerSubmitButton = document.querySelector('#registerModal .btn-primary');
    if (registerSubmitButton) {
        registerSubmitButton.textContent = t('register.button');
    }
    const registerLoginLink = document.querySelector('#registerModal .auth-link a');
    if (registerLoginLink) {
        registerLoginLink.textContent = t('register.login');
    }
    
    // 更新密码修改模态框
    const passwordChangeModalTitle = document.querySelector('#passwordChangeModal .modal-header h2');
    if (passwordChangeModalTitle) {
        passwordChangeModalTitle.textContent = t('password.change.title');
    }
    const passwordChangeHint = document.querySelector('#passwordChangeModal .modal-header p');
    if (passwordChangeHint) {
        passwordChangeHint.textContent = t('password.change.first_login');
    }
    const currentPasswordLabel = document.querySelector('#passwordChangeModal label[for="currentPassword"]');
    if (currentPasswordLabel) {
        currentPasswordLabel.textContent = t('password.change.current');
    }
    const newPasswordLabel = document.querySelector('#passwordChangeModal label[for="newPassword"]');
    if (newPasswordLabel) {
        newPasswordLabel.textContent = t('password.change.new');
    }
    const confirmPasswordLabel = document.querySelector('#passwordChangeModal label[for="confirmPassword"]');
    if (confirmPasswordLabel) {
        confirmPasswordLabel.textContent = t('password.change.confirm');
    }
    const passwordChangeCancelButton = document.querySelector('#passwordChangeModal .btn-secondary');
    if (passwordChangeCancelButton) {
        passwordChangeCancelButton.textContent = t('password.change.cancel');
    }
    const passwordChangeSubmitButton = document.querySelector('#passwordChangeModal .btn-primary');
    if (passwordChangeSubmitButton) {
        passwordChangeSubmitButton.textContent = t('password.change.button');
    }
    
    // 刷新状态以更新动态内容
    refreshStatus();
}

// 初始化语言
function initLanguage() {
    const currentLang = getCurrentLanguage();
    document.documentElement.lang = currentLang;
    
    // 检查是否已经存在语言切换按钮
    let langSelector = document.getElementById('lang-selector');
    if (!langSelector) {
        // 添加语言切换按钮
        const header = document.querySelector('header');
        langSelector = document.createElement('div');
        langSelector.id = 'lang-selector';
        langSelector.style.position = 'absolute';
        langSelector.style.top = '20px';
        langSelector.style.right = '20px';
        header.appendChild(langSelector);
    }
    
    // 更新语言切换按钮内容
    langSelector.innerHTML = `
        <button class="btn btn-sm" onclick="setLanguage('zh-CN')" style="margin-right: 10px; background-color: rgba(255, 255, 255, 0.8); color: #0a192f; border: 1px solid rgba(0, 123, 255, 0.5); z-index: 1; position: relative;">${t('language.zh')}</button>
        <button class="btn btn-sm" onclick="setLanguage('en-US')" style="background-color: rgba(255, 255, 255, 0.8); color: #0a192f; border: 1px solid rgba(0, 123, 255, 0.5); z-index: 1; position: relative;">${t('language.en')}</button>
    `;
    
    // 更新UI
    updateUI();
}

// 导出函数
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { i18n, getCurrentLanguage, setLanguage, t, updateUI, initLanguage };
}
