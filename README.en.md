# 幻影屏障 MirageShield

> AI Agent-driven Active Network Defense System | One-click Deployable Open Source Security Tool

MirageShield (Phantom Barrier), referred to as 幻影盾 (Phantom Shield)

[English](README.en.md) | [中文](README.md)

**Quick Experience**:
- [Download Latest Version](https://github.com/ylqxb/MirageShield/releases/latest)
- [Online Demo](https://ylqxb.github.io/MirageShield)

If this project helps you, welcome to Star ⭐

## Project Introduction

MirageShield is an AI agent-based active defense system with a layered architecture design, providing powerful network security protection capabilities. The system works through three core agents to achieve active defense, threat detection, and response, protecting network environments from various attacks.

## 💪 Core Test Data

- 🔒 Protection Capability: Port scan interception rate 95%+ | Brute force attack interception rate 99%+ | Unknown attack recognition rate 85%+
- ⚡ Response Speed: Attack response delay < 50ms, quick interception/deception completion
- 🪶 Resource Usage: Idle CPU usage < 5% | Full protection CPU usage < 10% | Memory usage stable < 200MB
- 🚀 Deployment Threshold: Docker one-line command quick startup | Windows one-click deployment simple and convenient | Zero configuration out of the box

> *The above data are actual test environment results. Actual usage effects may vary depending on operating environment and attack types*

## Core Advantages

- **Active Defense**: Not just detecting threats, but actively deploying defense measures
- **AI-driven**: Using artificial intelligence to improve the accuracy of threat detection and response
- **Multi-layer Protection**: Adopting a layered architecture to provide comprehensive security protection
- **Community Defense**: Achieving collective defense through threat intelligence sharing
- **Flexible and Extensible**: Modular design, easy to extend and customize

## System Screenshots

### System Status
Real-time display of current defense status, threat detection, and AI agent activity
![System Status](https://raw.githubusercontent.com/ylqxb/MirageShield/main/images/system_status.png)

### System Architecture
Shows the overall architecture of multi-agent collaborative defense
![System Architecture](https://raw.githubusercontent.com/ylqxb/MirageShield/main/images/system_architecture.png)

### Operation Control Bar
Provides one-click defense, strategy adjustment and other quick operations
![Operation Control Bar](https://raw.githubusercontent.com/ylqxb/MirageShield/main/images/control_panel.png)

### Hardware Management
Manage connected security hardware devices
![Hardware Management](https://raw.githubusercontent.com/ylqxb/MirageShield/main/images/hardware_management.png)

### Hardware Management Details
View detailed status and configuration of hardware devices
![Hardware Management Details](https://raw.githubusercontent.com/ylqxb/MirageShield/main/images/hardware_management_details.png)

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

### Method 1: Enhanced One-click Deployment (Recommended)

**Windows System**:
1. After downloading the project code, double-click `deploy.bat` in the project root directory
2. Select deployment mode:
   - Docker Deployment (Recommended): Automatically install Docker (if not installed) and build container
   - Local Direct Deployment: No Docker required, run service directly locally
   - Update Demo Page Only: Update demo page to show latest interface
3. The script will automatically check the environment, install dependencies, and start the service
4. After deployment is complete, the browser will automatically open to access the service address

**Linux System**:
> [!WARNING]
> **Important Note**: The system is currently mainly tested in Windows environment, Linux environment adaptation is in progress
> The following steps are for reference only, recommended for testing environment use
1. After downloading the project code, execute in the project root directory:
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```
2. Select deployment mode:
   - Docker Deployment (Recommended): Automatically install Docker (if not installed) and build container
   - Local Direct Deployment: No Docker required, run service directly locally
   - Update Demo Page Only: Update demo page to show latest interface
3. The script will automatically check the environment, install dependencies, and start the service
4. After deployment is complete, the browser will automatically open to access the service address

### Method 2: Traditional One-click Deployment

**Windows System**:
1. Ensure Python 3.8+ and Docker Desktop are installed
2. After downloading the project code, double-click `deploy.bat` in the project root directory
3. The script will automatically check the environment, build the image, and start the service
4. After deployment is complete, access the service address according to the prompt

**Linux System**:
1. Ensure Python 3.8+, Docker, and docker-compose are installed
2. After downloading the project code, execute in the project root directory:
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```
3. The script will automatically check the environment, build the image, and start the service
4. After deployment is complete, access the service address according to the prompt

### Method 3: Using Docker

**Windows System**:
```bash
# Run Docker image directly
docker run -d --name mirageshield -p 8080:8080 ylqxb/mirageshield:latest

# Visit http://localhost:8080
```

**Linux System**:
```bash
# Run Docker image directly
docker run -d --name mirageshield -p 8080:8080 ylqxb/mirageshield:latest

# Visit http://localhost:8080
```

### Method 4: Online Demo
Directly visit [https://ylqxb.github.io/MirageShield](https://ylqxb.github.io/MirageShield) to experience the system features

### Method 5: Local Installation
Follow the steps in [01_quick_start.md](./01_quick_start.md)

## Login Guide

1. **Access System**: Open browser and visit http://localhost:8080
2. **First Login**:
   - Username: admin
   - Password: A random password will be generated in the console when the system starts for the first time
   - The password will also be saved to the `data/initial_password.txt` file
3. **Password Reset**:
   - Method 1: Set ADMIN_PASSWORD environment variable to new password, then restart system
   - Method 2: Delete data/users.json file, system will regenerate admin account and password on restart
4. **Post-login Operations**:
   - After first login, the system will force you to change the password
   - The temporary password file will be automatically deleted after password change
   - After entering the system, you can access various functions through the right menu

## Interface Navigation

- **Right Menu**: Contains system status, agent status, network status, LAN management, data transmission, community defense, operation control, threat assessment history, protection results, system logs, system monitoring, hardware management and other functional modules
- **Top Navigation**: Displays system name, language switch and user information
- **Main Content Area**: Shows detailed information of the current functional module
- **Operation Control Bar**: Provides one-click defense, strategy adjustment and other quick operations

## Keyboard Shortcuts

The system supports the following keyboard shortcuts for quick operations:

| Shortcut | Function Description |
|----------|---------------------|
| `M` | Toggle the display/hide state of the right navigation menu |
| `Escape` | Close the currently open modal (such as system resource monitoring window) |

> **Tip**: Shortcuts are case-insensitive, pressing `m` or `M` both trigger the navigation menu toggle.

## Troubleshooting

### Common Issues

| Problem | Possible Cause | Solution |
|---------|---------------|----------|
| Service cannot start | Port occupied | Check if port 8080 is occupied, use `netstat -an | findstr :8080` |
| Agent connection failed | Configuration error | Check configuration files and environment variables |
| Web interface cannot be accessed | Firewall block | Check firewall settings, ensure port 8080 is open |
| Honeypot deployment failed | Docker not running | Ensure Docker service is running normally |

### Log Viewing

```bash
# View system logs
tail -f logs/system.log

# View agent logs
tail -f logs/agent.log
```

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

This project is open source under the MIT License, see [LICENSE](LICENSE) file for details. You can freely use, copy, modify, merge, publish, distribute, sublicense this project's code without any non-commercial use restrictions.

### Patent Additional Terms

The core technology of this project has applied for patent protection. Commercial use of the patented technology in this project requires prior written authorization from the rights holder. Personal non-commercial learning and research use is not restricted by this term.

## Disclaimer

1. This project is a personal learning and research work. The author is not responsible for any direct or indirect losses caused by the use of this software. Please fully test before use.
2. The project is currently in the feature verification stage. Core functions have been implemented but may have unstable situations. **Not recommended for direct use in production environments**.
3. This project has been mainly tested on Windows 11. Linux environment adaptation is in progress. Please do not blindly use it in production-level Linux environments.
4. The author is an individual developer, response time and maintenance time are不定, please understand.

© 2026 MirageShield All Rights Reserved