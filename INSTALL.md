# 手动安装指南

如果你在使用自动部署脚本时遇到问题，可以按照以下步骤手动安装和配置：

## 1. 安装基本依赖

```bash
# 更新系统包
sudo apt update

# 安装Python和pip
sudo apt install -y python3 python3-pip

# 安装Chrome浏览器
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install -y ./google-chrome-stable_current_amd64.deb
```

## 2. 安装Python依赖

```bash
# 创建虚拟环境（可选但推荐）
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install flask==2.3.3 selenium==4.11.2 webdriver-manager==4.0.0
```

## 3. 创建静态目录

```bash
mkdir -p static
chmod 777 static
```

## 4. 启动服务

```bash
python3 app.py
```

## 常见问题解决

### 1. Selenium版本不兼容

如果遇到 WebDriver 初始化参数不兼容的问题（如 `desired_capabilities` 错误），可能是 Selenium 版本不匹配。尝试以下解决方案：

```bash
# 安装特定版本的Selenium
pip uninstall -y selenium
pip install selenium==4.11.2
```

### 2. ChromeDriver未找到

如果遇到 ChromeDriver 未找到的错误，可以尝试手动安装：

```bash
# 首先查看Chrome浏览器版本
google-chrome --version

# 然后下载对应版本的ChromeDriver
# 例如，如果Chrome是114版本
wget https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver
```

### 3. Headless模式问题

如果在无头模式下遇到问题，可以修改`token_extractor.py`文件，去掉`--headless`参数：

```python
# 注释或移除这一行
# chrome_options.add_argument("--headless")
```

### 4. 权限问题

如果遇到权限错误，确保当前用户有足够权限：

```bash
# 确保当前目录权限正确
sudo chown -R $(whoami):$(whoami) .
chmod -R 755 .
chmod 777 static
```

### 5. 网络监控日志获取失败

如果无法获取网络日志，可以尝试其他辅助方法：

```bash
# 安装xvfb (X Virtual Frame Buffer)，用于在无头环境下运行浏览器
sudo apt install -y xvfb

# 使用xvfb运行
xvfb-run python3 app.py
```

## 调试提示

如果需要更详细的日志进行调试：

1. 修改`app.py`中的日志级别：
```python
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
```

2. 运行时重定向日志到文件：
```bash
python3 app.py > app.log 2>&1
```

3. 实时查看日志：
```bash
tail -f app.log
``` 