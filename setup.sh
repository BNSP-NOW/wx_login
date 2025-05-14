#!/bin/bash

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}  微信公众平台登录辅助工具部署脚本  ${NC}"
echo -e "${BLUE}=========================================${NC}"

# 检查Docker是否安装
echo -e "${GREEN}[1/5] 检查Docker是否安装...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker未安装，开始安装Docker...${NC}"
    sudo apt-get update
    sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
    sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
    sudo apt-get update
    sudo apt-get install -y docker-ce
    sudo systemctl enable docker
    sudo systemctl start docker
    echo -e "${GREEN}Docker安装完成${NC}"
else
    echo -e "${GREEN}Docker已安装${NC}"
fi

# 检查Docker Compose是否安装
echo -e "${GREEN}[2/5] 检查Docker Compose是否安装...${NC}"
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Docker Compose未安装，开始安装Docker Compose...${NC}"
    sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN}Docker Compose安装完成${NC}"
else
    echo -e "${GREEN}Docker Compose已安装${NC}"
fi

# 创建必要的目录
echo -e "${GREEN}[3/5] 创建必要的目录...${NC}"
mkdir -p static
chmod 777 static

# 构建Docker镜像
echo -e "${GREEN}[4/5] 构建Docker镜像...${NC}"
docker-compose build

# 启动服务
echo -e "${GREEN}[5/5] 启动服务...${NC}"
docker-compose up -d

# 检查服务是否正常启动
if [ $? -eq 0 ]; then
    echo -e "${GREEN}服务已成功启动!${NC}"
    echo -e "${GREEN}请访问 http://$(hostname -I | awk '{print $1}'):5000 使用微信公众平台登录工具${NC}"
else
    echo -e "${RED}服务启动失败，请检查日志${NC}"
    docker-compose logs
fi

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}  部署完成  ${NC}"
echo -e "${BLUE}=========================================${NC}"
echo -e "如需查看日志，请运行: ${GREEN}docker-compose logs -f${NC}"
echo -e "如需停止服务，请运行: ${GREEN}docker-compose down${NC}" 