# MirageShield - 幻象屏障 

> 基于 AI 智能体的主动防御系统 | 开源网络安全工具 

[English](README.en.md) | [中文](README.md)

## ⚠️ 项目状态与免责声明

- **个人开发项目**：本项目为个人学习/研究作品，作者不承担任何因使用本软件导致的直接或间接损失。请在使用前充分测试。
- **开发状态**：处于早期开发阶段，功能可能不稳定，**不建议用于关键业务环境**。
- **测试环境**：仅在 Windows 11 测试通过，未在 Linux 环境中测试。
- **维护响应**：作者为个人开发者，响应时间不定，请谅解。

## 阅读指南

为了帮助您快速了解和使用 MirageShield，我们将文档分为以下几类，并建议按照以下顺序阅读：

### 入门
- [01_快速开始.md](./01_快速开始.md) - 快速部署和使用指南
- [README.md](./README.md) - 项目总览和核心功能介绍

### 部署
- [02_部署指南.md](./02_部署指南.md) - 详细部署步骤和配置

### 开发
- [03_开发指南.md](./03_开发指南.md) - 系统架构和开发规范
- [04_运维指南.md](./04_运维指南.md) - 系统维护和故障排查
- [06_开发贡献指南.md](./06_开发贡献指南.md) - 如何为项目贡献代码

### 参考
- [05_用户手册.md](./05_用户手册.md) - 系统功能使用说明
- [07_常见问题FAQ.md](./07_常见问题FAQ.md) - 常见问题解答
- [PRIVACY_POLICY.md](./PRIVACY_POLICY.md) - 隐私政策
- [COMMERCIAL_DRAFT.md](./COMMERCIAL_DRAFT.md) - 商业化规划草案

© 2026 MirageShield 团队 版权所有
本项目核心技术已申请发明专利（初审通过），开源版仅供学习、测试与非商业使用。

🚀 使用本项目即视为您已阅读、理解并同意：
• 版权声明与专利保护条款
• MIT 开源许可证约定
• 项目隐私政策
• 商业化使用规则

⚠️ 项目状态：

- 本项目为个人开发，时间有限，不能提供准确的更新和维护时间
- 仅在闲暇之余完善系统功能和修复问题
- 目前处于开发完善阶段，存在已知或未知 Bug，部分功能未完全稳定
- **重要提示**：系统未在 Linux 环境中测试，**请勿盲目用于 Linux 环境**
- 仅供学习、研究、测试使用，不建议直接用于生产环境

## 快速导航

- [项目简介](#项目简介)
- [系统效果图](#系统效果图)
- [核心功能](#核心功能)
- [环境准备](#环境准备)
- [系统构建步骤](#系统构建步骤)
- [模块构建指南](#模块构建指南)
- [测试和调试](#测试和调试)
- [部署最佳实践](#部署最佳实践)
- [快速开始](#快速开始)
- [故障排除](#故障排除)
- [性能优化](#性能优化)
- [安全加固](#安全加固)
- [核心 API 接口](#核心-api-接口)
- [配置说明](#配置说明)
- [未来扩展方向](#未来扩展方向)
- [贡献指南](#贡献指南)
- [许可证](#许可证)

## 项目简介

MirageShield 是一个基于 AI 智能体的主动防御系统，采用分层架构设计，具备强大的网络安全防护能力。系统通过三个核心智能体协同工作，实现主动防御、威胁检测和响应，保护网络环境免受各类攻击。

## 系统效果图 
 
 ### 系统状态 
 实时展示当前防御状态、威胁检测情况与 AI 智能体活跃度 
 ![系统状态](images/系统状态效果图.png) 
 
 ### 系统架构 
 展示多智能体协同防御的整体架构 
 ![系统架构](images/系统架构效果图.png) 
 
 ### 操作控制栏 
 提供一键防御、策略调整等快捷操作 
 ![操作控制栏](images/操作控制栏.png) 
 
 ### 硬件管理 
 管理接入的安全硬件设备 
 ![硬件管理](images/硬件管理.png) 
 
 ### 硬件管理详情 
 查看硬件设备的详细状态与配置 
 ![硬件管理详情](images/硬件管理详情.png)

## 核心功能

### 1. AI 智能体系统

- **Prober (探路者)**：网络探测与分析，数据采集和安全传输
- **Baiter (诱饵手)**：诱饵部署与管理，生成高仿真假数据和蜜罐
- **Watcher (守望者)**：网络监控与威胁分析，高级异常检测和攻击者分析

#### AI 智能体实现方式

MirageShield 的 AI 智能体采用了混合实现方式：

**1. 内部智能体实现**：

- 核心功能通过内部代码实现，包括网络探测、威胁监控、蜜罐管理等
- 采用异步编程模型，使用 Python asyncio 实现高效的并发处理
- 内置数据采集、分析和处理逻辑，确保系统的稳定性和可靠性

**2. 外部 API 集成**：

- 部分高级功能支持通过 API 调用外部服务，如：
  - 生成式 AI：用于生成高仿真的诱饵内容
  - IP 声誉查询：用于评估网络威胁
  - 加密服务：用于数据安全传输

**3. 模块化设计**：

- 智能体之间通过消息队列进行通信，实现松耦合
- 支持模拟模式和真实模式，便于开发和测试
- 可扩展性强，支持添加新的智能体和功能模块

**4. 安全性考虑**：

- 采用加密传输保护数据安全
- 使用代理（如 Tor）确保匿名性
- 实现水印和蜜令牌技术，便于追踪攻击者

### 2. 控制与数据平面

- **策略引擎**：根据威胁等级动态调整防御策略
- **安全评估**：计算威胁置信度，确定威胁等级
- **真实数据池**：加密存储真实数据，基于角色的访问控制
- **诱饵数据池**：管理诱饵数据和蜜罐，包含水印和蜜令牌
- **虚拟网络层**：网络拓扑管理，IP 旋转，网络整建迁移

### 3. 社区联防

- 威胁情报共享接口，支持匿名共享机制
- 协同防御，提高整体安全防护能力

### 4. API 与 Web 界面

- RESTful API 服务，支持系统管理和监控
- 直观的 Web 用户界面，实时监控系统状态

### 5. 高级防御能力

- **主动防御**：部署蜜罐和诱饵数据，引导攻击者远离真实目标
- **心理战**：通过延迟响应和虚假信息干扰攻击者
- **网络整建**：在严重威胁情况下快速切换网络拓扑
- **智能协同**：三个智能体协同工作，提供全方位防护

## 从0构建完整系统

### 环境准备

#### 1. 系统要求

- **操作系统**：Windows 10+（主要测试环境），Linux（实验性支持，未完全测试）
- **Python**：3.8\~3.11（推荐，3.12+ 可能存在 asyncio 兼容性问题）
- **硬件**：至少 4 核 CPU，8GB 内存，50GB 存储空间
- **网络**：稳定的网络连接，支持 IPv4/IPv6
- **Docker**：Docker Engine 20.10+（用于部署蜜罐，可选但推荐）

#### 2. 软件安装

**Windows 系统**：

1. 安装 Python 3.8+：从 [Python 官网](https://www.python.org/downloads/) 下载并安装
2. 安装 Git：从 [Git 官网](https://git-scm.com/downloads) 下载并安装
3. 安装 Docker Desktop：从 [Docker 官网](https://www.docker.com/products/docker-desktop) 下载并安装
4. 配置环境变量：确保 Python 和 Git 都已添加到系统 PATH

**Linux 系统**（**未测试，不建议使用**）：

> \[!WARNING]
> **重要提示**：系统未在 Linux 环境中测试，**请勿盲目用于 Linux 环境**
> 以下步骤仅供参考，可能无法正常工作

```bash
# 安装 Python 3.8+
sudo apt update
sudo apt install python3 python3-pip python3-venv

# 安装 Git
sudo apt install git

# 安装 Docker
sudo apt install docker.io
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

### 系统构建步骤

#### 1. 代码获取

```bash
# 克隆代码库
git clone https://github.com/yourusername/MirageShield.git
cd MirageShield

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

> [!TIP]
> 若安装失败，建议升级 pip：`pip install --upgrade pip`
> Linux 系统可能需要 `sudo` 权限
```

#### 2. 配置系统

**2.1 环境变量配置**

创建 `.env` 文件（在项目根目录）：

```dotenv
# 管理员密码
ADMIN_PASSWORD=your_secure_password

# 加密密钥
ENCRYPTION_KEY=your_encryption_key

# 水印密钥
WATERMARK_KEY=your_watermark_key

# 可选：Tor 控制密码
TOR_CONTROL_PASSWORD=your_tor_password

# 可选：IP 声誉 API 密钥
IP_REPUTATION_API_KEY=your_ip_reputation_api_key

# 可选：OpenAI API 密钥
OPENAI_API_KEY=your_openai_api_key
```

**2.2 配置文件调整**

修改 `config/` 目录下的配置文件：

- `prober_config.json`：探路者智能体配置
- `baiter_config.json`：诱饵手智能体配置
- `watcher_config.json`：守望者智能体配置
- `api_config.json`：API 相关配置

**2.3 目录结构创建**

确保以下目录存在：

```bash
# 创建必要的目录
mkdir -p data logs backups

# 设置目录权限
chmod 755 data logs backups
```

#### 3. 系统初始化

````bash
# 启动系统
python start_server.py

# 检查系统状态
curl http://localhost:5000/api/system/status

> [!TIP]
> 预期返回结果示例：
> ```json
> {
>   "status": "running",
>   "agents": ["prober", "baiter", "watcher"],
>   "protection_level": 1,
>   "last_check": "2026-01-01 12:00:00"
> }
> ```
````

#### 4. 验证安装

1. 访问 Web 界面：<http://localhost:5000>
2. 使用设置的管理员密码登录
3. 检查系统状态是否正常
4. 测试各功能模块是否正常工作

### 模块构建指南

#### 1. AI 智能体模块

**Prober 智能体**：

- 负责网络探测和数据采集
- 配置文件：`config/prober_config.json`
- 核心功能：网络扫描、数据采集、安全传输

**Baiter 智能体**：

- 负责诱饵部署和管理
- 配置文件：`config/baiter_config.json`
- 核心功能：蜜罐部署、假数据生成、诱饵管理

**Watcher 智能体**：

- 负责网络监控和威胁分析
- 配置文件：`config/watcher_config.json`
- 核心功能：网络监控、异常检测、威胁分析

#### 2. 控制平面模块

**策略引擎**：

- 根据威胁等级动态调整防御策略
- 实现文件：`control_plane/strategy_engine.py`

**安全评估**：

- 计算威胁置信度，确定威胁等级
- 实现文件：`control_plane/security_assessment.py`

**分层防御**：

- 实现多层防御机制
- 实现文件：`control_plane/layered_defense.py`

#### 3. 数据平面模块

**真实数据池**：

- 加密存储真实数据
- 实现文件：`data_plane/real_data_pool.py`

**诱饵数据池**：

- 管理诱饵数据和蜜罐
- 实现文件：`data_plane/decoy_data_pool.py`

**虚拟网络层**：

- 网络拓扑管理，IP 旋转
- 实现文件：`data_plane/virtual_network_layer.py`

#### 4. API 和 Web 界面

**API 服务**：

- RESTful API 接口
- 实现文件：`api/app.py`

**Web 界面**：

- 前端页面
- 实现文件：`ui/index.html`

### 测试和调试

#### 1. 单元测试

```bash
# 运行单元测试
python -m pytest tests/

# 查看测试覆盖率
python -m pytest tests/ --cov=.
```

#### 2. 集成测试

```bash
# 启动系统
python start_server.py

# 运行集成测试
python tests/integration_test.py
```

#### 3. 调试模式

```bash
# 启动调试模式
FLASK_DEBUG=1 python start_server.py

> [!WARNING]
> 调试模式仅用于开发环境，生产环境禁止启用
> 可指定主机和端口：`python start_server.py --host=0.0.0.0 --port=5000`
```

### 部署最佳实践

#### 1. 本地开发环境

- 使用虚拟环境隔离依赖
- 启用调试模式便于开发
- 使用模拟数据进行测试

#### 2. 生产环境部署

- 使用系统服务管理（如 systemd）
- 配置反向代理（如 Nginx）
- 启用 HTTPS 加密
- 定期备份数据
- 监控系统状态

#### 3. 容器化部署

#### 使用Docker命令
```bash
# 构建 Docker 镜像
docker build -t mirageshield .

# 运行容器
docker run -d --name mirageshield \
  -p 5000:5000 \
  -v ./data:/app/data \
  -v ./logs:/app/logs \
  --env-file .env \
  mirageshield
```

#### 使用Docker Compose
```bash
# 启动服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 停止服务
docker-compose down
```

### 4. 在线Demo

项目提供在线Demo，无需安装环境即可体验：
- **GitHub Pages**: [https://ylqxb.github.io/MirageShield](https://ylqxb.github.io/MirageShield)

### 5. 快速开始

#### 方法一：使用Docker（推荐）
```bash
# 直接运行Docker镜像
docker run -d --name mirageshield -p 5000:5000 ylqxb/mirageshield:latest

# 访问 http://localhost:5000
```

#### 方法二：在线Demo
直接访问 [https://ylqxb.github.io/MirageShield](https://ylqxb.github.io/MirageShield) 体验系统功能

#### 方法三：本地安装
按照前面的环境准备和系统构建步骤进行安装

### 故障排除

#### 1. 常见问题

| 问题         | 可能原因       | 解决方案                             | <br />          |
| ---------- | ---------- | -------------------------------- | :-------------- |
| 服务无法启动     | 端口被占用      | 检查 5000 端口是否被占用，使用 \`netstat -an | findstr :5000\` |
| 智能体连接失败    | 配置错误       | 检查配置文件和环境变量                      | <br />          |
| Web 界面无法访问 | 防火墙阻止      | 检查防火墙设置，确保 5000 端口开放             | <br />          |
| 蜜罐部署失败     | Docker 未运行 | 确保 Docker 服务正常运行                 | <br />          |

#### 2. 日志查看

```bash
# 查看系统日志
tail -f logs/system.log

# 查看智能体日志
tail -f logs/agent.log
```

#### 3. 系统恢复

```bash
# 恢复系统
# 1. 停止服务
# 2. 恢复备份
python -c "from utils.backup import restore_users_data; restore_users_data()"
# 3. 重启服务
python start_server.py
```

### 性能优化

#### 1. 硬件优化

- 使用 SSD 存储提高数据访问速度
- 增加内存提高并发处理能力
- 使用多核 CPU 提高计算性能

#### 2. 软件优化

- 启用缓存机制减少重复计算
- 优化数据库查询提高响应速度
- 使用异步编程提高并发处理能力
- 配置合适的日志级别减少 I/O 开销

#### 3. 网络优化

- 使用 CDN 加速静态资源访问
- 优化网络拓扑减少网络延迟
- 使用负载均衡提高系统可用性

### 安全加固

#### 1. 系统安全

- 定期更新系统和依赖包
- 配置防火墙限制访问
- 使用强密码和多因素认证
- 定期进行安全审计

#### 2. 数据安全

- 加密存储敏感数据
- 定期备份数据
- 实现数据访问控制
- 使用安全的传输协议

#### 3. 应用安全

- 实现输入验证防止注入攻击
- 使用 HTTPS 加密传输
- 定期进行漏洞扫描
- 遵循安全编码最佳实践

### 访问方式

- **Web 界面**：<http://localhost:5000>
- **API 接口**：<http://localhost:5000/api>

### 核心 API 接口

#### /api/system/status

- **方法**：GET
- **描述**：获取系统整体状态
- **请求参数**：无
- **响应示例**：
  ```json
  {
    "code": 200,
    "data": {
      "status": "running",
      "agents": ["prober", "baiter", "watcher"],
      "protection_level": 1,
      "last_check": "2026-01-01 12:00:00"
    },
    "msg": "success"
  }
  ```
- **错误码**：401（未授权）、500（系统异常）

#### /api/system/protection\_level

- **方法**：POST
- **描述**：设置防护级别
- **请求参数**：
  ```json
  {
    "level": 2
  }
  ```
- **响应示例**：
  ```json
  {
    "code": 200,
    "data": {
      "protection_level": 2
    },
    "msg": "success"
  }
  ```
- **错误码**：400（参数错误）、401（未授权）、500（系统异常）

#### /api/agents

- **方法**：GET
- **描述**：获取智能体列表
- **请求参数**：无
- **响应示例**：
  ```json
  {
    "code": 200,
    "data": {
      "agents": [
        {"name": "prober", "status": "active"},
        {"name": "baiter", "status": "active"},
        {"name": "watcher", "status": "active"}
      ]
    },
    "msg": "success"
  }
  ```
- **错误码**：401（未授权）、500（系统异常）

#### /api/strategy

- **方法**：GET/POST
- **描述**：获取/设置策略
- **请求参数**（POST）：
  ```json
  {
    "strategy": {
      "detection_level": "high",
      "response_mode": "automatic"
    }
  }
  ```
- **响应示例**：
  ```json
  {
    "code": 200,
    "data": {
      "strategy": {
        "detection_level": "high",
        "response_mode": "automatic"
      }
    },
    "msg": "success"
  }
  ```
- **错误码**：400（参数错误）、401（未授权）、500（系统异常）

#### /api/assessment

- **方法**：POST
- **描述**：进行安全评估
- **请求参数**：无
- **响应示例**：
  ```json
  {
    "code": 200,
    "data": {
      "assessment": {
        "threat_level": "low",
        "vulnerabilities": [],
        "recommendations": []
      }
    },
    "msg": "success"
  }
  ```
- **错误码**：401（未授权）、500（系统异常）

#### /api/network/topology

- **方法**：GET
- **描述**：获取网络拓扑
- **请求参数**：无
- **响应示例**：
  ```json
  {
    "code": 200,
    "data": {
      "topology": {
        "nodes": [],
        "edges": []
      }
    },
    "msg": "success"
  }
  ```
- **错误码**：401（未授权）、500（系统异常）

#### /api/community/sync

- **方法**：POST
- **描述**：同步威胁情报
- **请求参数**：无
- **响应示例**：
  ```json
  {
    "code": 200,
    "data": {
      "sync": {
        "status": "success",
        "updated_indicators": 10
      }
    },
    "msg": "success"
  }
  ```
- **错误码**：401（未授权）、500（系统异常）

#### /api/defense/layers

- **方法**：GET
- **描述**：获取防御层
- **请求参数**：无
- **响应示例**：
  ```json
  {
    "code": 200,
    "data": {
      "layers": [
        {"name": "边界防御", "status": "active"},
        {"name": "系统防御", "status": "active"},
        {"name": "应用防御", "status": "active"}
      ]
    },
    "msg": "success"
  }
  ```
- **错误码**：401（未授权）、500（系统异常）

## 配置说明

### 环境变量

运行系统前需要设置以下环境变量：

- `TOR_CONTROL_PASSWORD`：Tor 控制密码
- `ENCRYPTION_KEY`：加密密钥
- `IP_REPUTATION_API_KEY`：IP 声誉 API 密钥
- `OPENAI_API_KEY`：OpenAI API 密钥
- `WATERMARK_KEY`：水印密钥
- `DEFAULT_PASSWORD`：默认密码

### 配置文件

- `config/prober_config.json`：探路者智能体配置
- `config/baiter_config.json`：诱饵手智能体配置
- `config/watcher_config.json`：守望者智能体配置
- `config/api_config.json`：API 相关配置

## 未来扩展方向

### 1. 智能体增强

- **AI 模型升级**：集成更先进的 AI 模型，提高威胁检测和响应能力
- **新智能体开发**：添加专注于特定威胁类型的智能体，如 IoT 设备防护、云服务安全等
- **跨平台支持**：扩展智能体到不同操作系统和云环境

### 2. 功能扩展

- **容器安全**：增强容器环境的安全防护
- **云服务集成**：与主流云服务提供商的安全服务集成
- **边缘设备防护**：扩展到边缘计算设备的安全防护
- **区块链集成**：使用区块链技术增强威胁情报共享的安全性和可靠性

### 3. 技术创新

- **量子安全**：探索量子安全技术在防御系统中的应用
- **自动化响应**：实现更高级的自动化威胁响应机制
- **预测性分析**：基于机器学习的威胁预测和预防
- **零信任架构**：实现零信任安全架构的集成

### 4. 生态系统

- **插件系统**：开发可扩展的插件系统，支持第三方功能集成
- **API 市场**：构建 API 市场，促进安全服务的共享和交易
- **社区贡献**：建立开源社区，鼓励社区贡献和协作

## 系统功能清单

### 开源版功能

- **AI 智能体**：三个核心智能体（探路者、诱饵者、监视者）
- **主动防御**：威胁检测和主动防御措施
- **多层防护**：分层防御架构
- **社区联防**：威胁情报共享
- **Web 界面**：系统状态、硬件管理、日志查看
- **API 接口**：完整的 RESTful API
- **数据加密**：AES-256 加密保护
- **监控告警**：网络和系统监控
- **蜜罐部署**：基础蜜罐功能
- **配置管理**：灵活的配置系统

### 商业版预留功能（未来规划，尚未实现）

> 以上功能为未来规划，尚未实现，不代表当前版本能力。

- **高级威胁分析**：AI 模型集成
- **多租户管理**：企业级部署支持
- **专业技术支持**：7x24 小时技术支持
- **高级报告**：详细的安全报告和分析
- **合规审计**：符合行业标准的审计功能
- **集成第三方**：与企业现有系统集成

## 版本更新日志

### v0.1.0（2026-03-23）

- **初始版本**：项目创建和核心功能实现
- **AI 智能体**：实现三个核心智能体（探路者、诱饵者、监视者）
- **Web 界面**：系统状态、硬件管理、日志查看
- **API 接口**：完整的 RESTful API
- **主动防御**：威胁检测和主动防御措施
- **社区联防**：威胁情报共享
- **数据加密**：AES-256 加密保护
- **配置管理**：灵活的配置系统

## 核心优势

- **主动防御**：不仅仅检测威胁，更主动部署防御措施
- **AI 驱动**：利用人工智能提高威胁检测和响应的准确性
- **多层防护**：采用分层架构，提供全方位的安全防护
- **社区联防**：通过威胁情报共享，实现集体防御
- **灵活可扩展**：模块化设计，易于扩展和定制

## 贡献指南

### 如何贡献

1. **Fork 本仓库**
2. **创建特性分支**：`git checkout -b feature/xxx`
3. **提交代码**：`git commit -m 'feat: 添加 xxx 功能'`
4. **推送分支**：`git push origin feature/xxx`
5. **提交 Pull Request**

### 代码规范

- 遵循 PEP 8 代码风格
- 使用 4 空格缩进
- 每行代码不超过 80 字符
- 为函数和类添加文档字符串

### Issue 提交流程

1. 搜索现有 Issue，确保问题未被提出
2. 提供详细的问题描述
3. 包含复现步骤和预期行为
4. 如有可能，提供错误日志或截图

### 联系方式

- **GitHub Issues**：提交问题和功能请求
- **邮件**：<ylqxb_japcfyzakq@aka.yeah.net>

## 许可证

### MIT 许可证

```
MIT License

Copyright (c) 2026 MirageShield Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### 附加条款

本项目核心技术已申请发明专利（初审通过），开源版仅供学习、测试与非商业使用。商业使用需获得书面授权。

如果这个项目对你有帮助，欢迎 Star ⭐
