# MirageShield - 幻象屏障 

> 基于 AI 智能体的主动防御系统 | 开源网络安全工具 

[English](README.en.md) | [中文](README.md)

© 2026 MirageShield 团队 版权所有
本项目核心技术已申请发明专利（初审通过），开源版仅供学习、测试与非商业使用。

💡 使用本项目即视为您已阅读、理解并同意：
• 版权声明与专利保护条款
• MIT 开源许可证约定
• 项目隐私政策
• 商业化使用规则

## ⚠️ 项目状态与免责声明

- **个人开发项目**：本项目为个人学习/研究作品，作者不承担任何因使用本软件导致的直接或间接损失。请在使用前充分测试。
- **开发状态**：处于功能验证阶段，核心功能已实现但可能存在不稳定情况，**不建议用于生产环境**。
- **测试环境**：仅在 Windows 11 测试通过，未在 Linux 环境中测试。
- **维护响应**：作者为个人开发者，响应时间不定，请谅解。

## 🚀 快速体验

**下载最新版本**：https://github.com/ylqxb/MirageShield/releases/latest

- Windows 用户：解压后双击 `deploy_windows.bat`
- Linux 用户：
  > [!WARNING]
  > **重要警告**：系统未在 Linux 环境中测试，**请勿盲目用于 Linux 环境**
  > 以下步骤仅供参考，可能无法正常工作
  > 解压后在终端运行 `bash deploy_linux.sh`

> 首次运行会自动安装依赖，请确保网络畅通。

## 阅读指南

为了帮助您快速了解和使用 MirageShield，我们将文档分为以下几类，并建议按照以下顺序阅读：

### 入门
- [01_quick_start.md](./01_quick_start.md) - 快速部署和使用指南
- [README.md](./README.md) - 项目总览和核心功能介绍

### 部署
- [02_deployment_guide.md](./02_deployment_guide.md) - 详细部署步骤和配置

### 开发
- [03_development_guide.md](./03_development_guide.md) - 系统架构和开发规范
- [04_operations_guide.md](./04_operations_guide.md) - 系统维护和故障排查
- [06_contribution_guide.md](./06_contribution_guide.md) - 如何为项目贡献代码

### 参考
- [05_user_manual.md](./05_user_manual.md) - 系统功能使用说明
- [07_faq.md](./07_faq.md) - 常见问题解答
- [PRIVACY_POLICY.md](./PRIVACY_POLICY.md) - 隐私政策
- [COMMERCIAL_DRAFT.md](./COMMERCIAL_DRAFT.md) - 商业化规划草案

## 项目简介

MirageShield 是一个基于 AI 智能体的主动防御系统，采用分层架构设计，具备强大的网络安全防护能力。系统通过三个核心智能体协同工作，实现主动防御、威胁检测和响应，保护网络环境免受各类攻击。

## 系统效果图 

### 系统状态 
实时展示当前防御状态、威胁检测情况与 AI 智能体活跃度 
![系统状态](images/system_status.png) 

### 系统架构 
展示多智能体协同防御的整体架构 
![系统架构](images/system_architecture.png) 

### 操作控制栏 
提供一键防御、策略调整等快捷操作 
![操作控制栏](images/control_panel.png) 

### 硬件管理 
管理接入的安全硬件设备 
![硬件管理](images/hardware_management.png) 

### 硬件管理详情 
查看硬件设备的详细状态与配置 
![硬件管理详情](images/hardware_management_details.png)

## 核心功能

### 1. AI 智能体系统

- **Prober (探路者)**：网络探测与分析，数据采集和安全传输
- **Baiter (诱饵手)**：诱饵部署与管理，生成高仿真假数据和蜜罐
- **Watcher (守望者)**：网络监控与威胁分析，高级异常检测和攻击者分析

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

## 快速开始

### 方法一：一键部署（推荐）

**Windows 系统**：
1. 确保已安装 Python 3.8+ 和 Docker Desktop
2. 下载项目代码后，在项目根目录双击运行 `deploy_windows.bat`
3. 脚本会自动检查环境、构建镜像并启动服务
4. 部署完成后，根据提示访问服务地址

**Linux 系统**：
> [!WARNING]
> **重要警告**：系统未在 Linux 环境中测试，**请勿盲目用于 Linux 环境**
> 以下步骤仅供参考，可能无法正常工作
1. 确保已安装 Python 3.8+、Docker 和 docker-compose
2. 下载项目代码后，在项目根目录执行：
   ```bash
   chmod +x deploy_linux.sh
   ./deploy_linux.sh
   ```
3. 脚本会自动检查环境、构建镜像并启动服务
4. 部署完成后，根据提示访问服务地址

### 方法二：使用Docker

**Windows 系统**：
```bash
# 直接运行Docker镜像
docker run -d --name mirageshield -p 5000:5000 ylqxb/mirageshield:latest

# 访问 http://localhost:5000
```

**Linux 系统**：
> [!WARNING]
> **重要警告**：系统未在 Linux 环境中测试，**请勿盲目用于 Linux 环境**
> 以下步骤仅供参考，可能无法正常工作
```bash
# 直接运行Docker镜像
docker run -d --name mirageshield -p 5000:5000 ylqxb/mirageshield:latest

# 访问 http://localhost:5000
```

### 方法三：在线Demo
直接访问 [https://ylqxb.github.io/MirageShield](https://ylqxb.github.io/MirageShield) 体验系统功能

### 方法四：本地安装
按照 [02_部署指南.md](./02_部署指南.md) 中的步骤进行安装

## 登录指南

1. **访问系统**：打开浏览器，访问 http://localhost:5000
2. **首次登录**：
   - 用户名：admin
   - 密码：系统首次启动时会在控制台生成随机密码，或通过环境变量 ADMIN_PASSWORD 设置
3. **密码重置**：
   - 方法一：设置环境变量 ADMIN_PASSWORD 为新密码，然后重启系统
   - 方法二：删除 data/users.json 文件，重启系统后会重新生成管理员账户和密码
4. **登录后操作**：
   - 首次登录后，系统会提示修改初始密码
   - 进入系统后，可以通过右侧菜单访问各项功能

## 界面导航

- **右侧菜单**：包含系统状态、智能体状态、网络状态、局域网管理、数据传输、社区联防、操作控制、威胁评估历史、防护结果、系统日志、系统监控、硬件管理等功能模块
- **顶部导航**：显示系统名称、语言切换和用户信息
- **主内容区**：展示当前功能模块的详细信息
- **操作控制栏**：提供一键防御、策略调整等快捷操作

## 故障排除

### 常见问题

| 问题         | 可能原因       | 解决方案                             |
| ---------- | ---------- | -------------------------------- |
| 服务无法启动     | 端口被占用      | 检查 5000 端口是否被占用，使用 `netstat -an | findstr :5000` |
| 智能体连接失败    | 配置错误       | 检查配置文件和环境变量                      |
| Web 界面无法访问 | 防火墙阻止      | 检查防火墙设置，确保 5000 端口开放             |
| 蜜罐部署失败     | Docker 未运行 | 确保 Docker 服务正常运行                 |

### 日志查看

```bash
# 查看系统日志
tail -f logs/system.log

# 查看智能体日志
tail -f logs/agent.log
```

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