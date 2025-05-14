# 微信公众平台登录辅助工具

这是一个用于自动获取微信公众平台Cookie和Token的工具。它在Ubuntu服务器上运行，提供Web界面进行微信扫码登录，并自动提取登录凭证。

## 功能特点

- 自动获取微信公众平台登录二维码
- 显示实时登录状态
- 成功登录后自动提取Cookie和Token
- 提供复制功能便于获取凭证

## 安装说明

### 前提条件

- Ubuntu服务器
- Python 3.8+
- Chrome浏览器

### 安装步骤

1. 克隆本仓库到服务器：

```bash
git clone https://your-repository-url/wx_login.git
cd wx_login
```

2. 安装依赖：

```bash
pip install -r requirements.txt
```

3. 安装Chrome浏览器（如果尚未安装）：

```bash
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb
```

4. 创建静态目录：

```bash
mkdir -p static
```

## 启动服务

```bash
python app.py
```

服务默认在5000端口启动，可以通过`http://你的服务器IP:5000`访问。

## 使用方法

1. 访问工具网页
2. 点击"获取登录二维码"按钮
3. 使用微信扫描显示的二维码进行登录
4. 登录成功后，系统会自动获取Cookie和Token
5. 复制获取到的凭证用于你的平台

## 注意事项

- 为保障安全，建议在内网环境使用本工具
- 获取的Cookie和Token有一定的有效期，请及时使用
- 建议定期更新登录凭证

## 技术架构

- 后端：Flask
- 浏览器自动化：Selenium
- 前端：HTML, CSS, JavaScript 