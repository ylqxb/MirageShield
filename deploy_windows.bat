@echo off

REM MirageShield One-Click Deployment Script (Windows)
REM © 2026 MirageShield Team

echo ============================================
echo MirageShield Deployment Script
echo ============================================

REM Check if Python is installed
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed. Please install Python 3.8-3.11 first.
    echo You can download Python from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if Docker is installed
echo Checking Docker installation...
docker --version >nul 2>&1
if errorlevel 1 (
    echo Error: Docker is not installed. Please install Docker Desktop first.
    echo You can download Docker Desktop from: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

REM Check if Docker is running
echo Checking if Docker is running...
docker info >nul 2>&1
if errorlevel 1 (
    echo Error: Docker is not running. Please start Docker Desktop.
    pause
    exit /b 1
)

REM Check if docker-compose is available
echo Checking docker-compose...
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo Error: docker-compose is not available.
    echo Note: Docker Desktop usually includes docker-compose.
    echo Please make sure Docker Desktop is properly installed.
    pause
    exit /b 1
)

REM Build Docker image
echo Building Docker image...
docker build -t mirageshield .
if errorlevel 1 (
    echo Error: Failed to build Docker image.
    echo Please check your Docker installation and try again.
    pause
    exit /b 1
)

REM Start container
echo Starting container...
docker-compose up -d
if errorlevel 1 (
    echo Error: Failed to start container.
    echo Please check your Docker installation and try again.
    pause
    exit /b 1
)

echo ============================================
echo Deployment successful!
echo ============================================
echo Service URL: http://localhost:5000
echo Frontend URL: http://localhost:5000/ui
echo ============================================
echo Tips:
echo 1. First access requires account registration
echo 2. Service runs on port 5000 by default
echo 3. Data is stored in local data directory
echo 4. Logs are stored in local logs directory
echo 5. View logs: docker logs -f mirageshield
echo ============================================

pause