# MirageShield - Phantom Barrier

> AI Agent-based Active Defense System | Open Source Network Security Tool

[English](README.en.md) | [中文](README.md)

© 2026 MirageShield Team. All rights reserved.
The core technology of this project has applied for a patent (preliminary examination passed). The open-source version is for learning, testing, and non-commercial use only.

💡 By using this project, you are deemed to have read, understood, and agreed to:
• Copyright statement and patent protection terms
• MIT open-source license agreement
• Project privacy policy
• Commercial use rules

## ⚠️ Project Status and Disclaimer

- **Personal Development Project**: This is a personal learning/research project. The author is not responsible for any direct or indirect losses caused by the use of this software. Please fully test before use.
- **Development Status**: In feature verification stage, core functions are implemented but may have unstable situations, **not recommended for production environments**.
- **Testing Environment**: Only tested on Windows 11, not tested in Linux environment.
- **Maintenance Response**: The author is an individual developer, response time may vary, please understand.

## 🚀 Quick Experience

**Download Latest Version**: https://github.com/ylqxb/MirageShield/releases/latest

- Windows users: After decompression, double-click `deploy_windows.bat`
- Linux users:
  > [!WARNING]
  > **Important Warning**: The system has not been tested in Linux environment. **Do not blindly use it in Linux environment**
  > The following steps are for reference only and may not work properly
  > After decompression, run `bash deploy_linux.sh` in the terminal

> Dependencies will be automatically installed on first run, please ensure network connectivity.

## Reading Guide

To help you quickly understand and use MirageShield, we have categorized the documentation as follows, and recommend reading in this order:

### Getting Started
- [01_quick_start.md](./01_quick_start.md) - Quick deployment and usage guide
- [README.md](./README.md) - Project overview and core features

### Deployment
- [02_deployment_guide.md](./02_deployment_guide.md) - Detailed deployment steps and configuration

### Development
- [03_development_guide.md](./03_development_guide.md) - System architecture and development guidelines
- [04_operations_guide.md](./04_operations_guide.md) - System maintenance and troubleshooting
- [06_contribution_guide.md](./06_contribution_guide.md) - How to contribute to the project

### Reference
- [05_user_manual.md](./05_user_manual.md) - System functionality usage instructions
- [07_faq.md](./07_faq.md) - Frequently asked questions
- [PRIVACY_POLICY.md](./PRIVACY_POLICY.md) - Privacy policy
- [COMMERCIAL_DRAFT.md](./COMMERCIAL_DRAFT.md) - Commercialization planning draft

## Project Introduction

MirageShield is an AI agent-based active defense system with a layered architecture design, providing powerful network security protection capabilities. The system works through three core agents to achieve active defense, threat detection, and response, protecting network environments from various attacks.

## System Screenshots

### System Status
![System Status](images/system_status.png)

### System Architecture
![System Architecture](images/system_architecture.png)

### Operation Control Bar
![Operation Control Bar](images/control_panel.png)

### Hardware Management
![Hardware Management](images/hardware_management.png)

### Hardware Management Details
![Hardware Management Details](images/hardware_management_details.png)

## Core Features

### 1. AI Agent System
- **Prober**: Network detection and analysis, data collection and secure transmission
- **Baiter**: Bait deployment and management, generating high-fidelity fake data and honeypots
- **Watcher**: Network monitoring and threat analysis, advanced anomaly detection and attacker analysis

### 2. Control and Data Plane
- **Strategy Engine**: Dynamically adjusts defense strategies based on threat levels
- **Security Assessment**: Calculates threat confidence and determines threat levels
- **Real Data Pool**: Encrypts and stores real data with role-based access control
- **Decoy Data Pool**: Manages decoy data and honeypots, including watermarks and honeytokens
- **Virtual Network Layer**: Network topology management, IP rotation, network restructuring and migration

### 3. Community Defense
- Threat intelligence sharing interface, supporting anonymous sharing mechanisms
- Collaborative defense to improve overall security protection capabilities

### 4. API and Web Interface
- RESTful API services, supporting system management and monitoring
- Intuitive web user interface, real-time monitoring of system status

### 5. Advanced Defense Capabilities
- **Active Defense**: Deploy honeypots and decoy data to guide attackers away from real targets
- **Psychological Warfare**: Interfere with attackers through delayed responses and false information
- **Network Restructuring**: Quickly switch network topology in case of severe threats
- **Intelligent Collaboration**: Three agents work together to provide comprehensive protection

## Quick Start

### Method 1: One-click Deployment (Recommended)

**Windows System**:
1. Ensure Python 3.8+ and Docker Desktop are installed
2. After downloading the project code, double-click `deploy_windows.bat` in the project root directory
3. The script will automatically check the environment, build the image, and start the service
4. After deployment is complete, access the service address according to the prompt

**Linux System**:
> [!WARNING]
> **Important Warning**: The system has not been tested in Linux environment. **Do not blindly use it in Linux environment**
> The following steps are for reference only and may not work properly
1. Ensure Python 3.8+, Docker, and docker-compose are installed
2. After downloading the project code, execute in the project root directory:
   ```bash
   chmod +x deploy_linux.sh
   ./deploy_linux.sh
   ```
3. The script will automatically check the environment, build the image, and start the service
4. After deployment is complete, access the service address according to the prompt

### Method 2: Using Docker

**Windows System**:
```bash
# Run Docker image directly
docker run -d --name mirageshield -p 5000:5000 ylqxb/mirageshield:latest

# Visit http://localhost:5000
```

**Linux System**:
> [!WARNING]
> **Important Warning**: The system has not been tested in Linux environment. **Do not blindly use it in Linux environment**
> The following steps are for reference only and may not work properly
```bash
# Run Docker image directly
docker run -d --name mirageshield -p 5000:5000 ylqxb/mirageshield:latest

# Visit http://localhost:5000
```

### Method 3: Online Demo
Directly visit [https://ylqxb.github.io/MirageShield](https://ylqxb.github.io/MirageShield) to experience the system features

### Method 4: Local Installation
Follow the steps in [02_部署指南.md](./02_部署指南.md)

## Login Guide

1. **Access System**: Open browser and visit http://localhost:5000
2. **First Login**:
   - Username: admin
   - Password: System will generate a random password in the console on first startup, or set via ADMIN_PASSWORD environment variable
3. **Password Reset**:
   - Method 1: Set ADMIN_PASSWORD environment variable to new password, then restart system
   - Method 2: Delete data/users.json file, system will regenerate admin account and password on restart
4. **Post-login Operations**:
   - After first login, system will prompt to change initial password
   - After entering the system, you can access various functions through the right menu

## Interface Navigation

- **Right Menu**: Contains system status, agent status, network status, LAN management, data transmission, community defense, operation control, threat assessment history, protection results, system logs, system monitoring, hardware management and other functional modules
- **Top Navigation**: Displays system name, language switch and user information
- **Main Content Area**: Shows detailed information of the current functional module
- **Operation Control Bar**: Provides one-click defense, strategy adjustment and other quick operations

## Troubleshooting

### Common Issues

| Problem | Possible Cause | Solution |
|---------|---------------|----------|
| Service cannot start | Port occupied | Check if port 5000 is occupied, use `netstat -an | findstr :5000` |
| Agent connection failed | Configuration error | Check configuration files and environment variables |
| Web interface cannot be accessed | Firewall block | Check firewall settings, ensure port 5000 is open |
| Honeypot deployment failed | Docker not running | Ensure Docker service is running normally |

### Log Viewing

```bash
# View system logs
tail -f logs/system.log

# View agent logs
tail -f logs/agent.log
```

## Core Advantages

- **Active Defense**: Not just detecting threats, but actively deploying defense measures
- **AI-driven**: Using artificial intelligence to improve the accuracy of threat detection and response
- **Multi-layer Protection**: Adopting a layered architecture to provide comprehensive security protection
- **Community Defense**: Achieving collective defense through threat intelligence sharing
- **Flexible and Extensible**: Modular design, easy to extend and customize

## Contribution Guide

### How to Contribute

1. **Fork this repository**
2. **Create a feature branch**: `git checkout -b feature/xxx`
3. **Commit code**: `git commit -m 'feat: add xxx feature'`
4. **Push branch**: `git push origin feature/xxx`
5. **Submit Pull Request**

### Contact Information

- **GitHub Issues**: Submit issues and feature requests
- **Email**: ylqxb_japcfyzakq@aka.yeah.net

## License

### MIT License

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

### Additional Terms

The core technology of this project has applied for a patent (preliminary examination passed). The open-source version is for learning, testing, and non-commercial use only. Commercial use requires written authorization.

If this project has helped you, welcome to Star ⭐