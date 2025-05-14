from flask import Flask, render_template, jsonify, request
from token_extractor import WeChatTokenExtractor
import time
import json
import os
import logging
import threading

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 微信公众平台登录URL
WECHAT_LOGIN_URL = "https://mp.weixin.qq.com/"

# 存储获取到的数据
captured_data = {
    "cookies": None,
    "token": None,
    "status": "未登录"
}

# 全局提取器实例
extractor = None
extractor_lock = threading.Lock()

@app.route('/')
def index():
    """主页，展示微信扫码登录界面"""
    return render_template('index.html')

@app.route('/login')
def login():
    """打开微信公众平台登录页面，并返回页面截图"""
    global extractor, captured_data
    
    with extractor_lock:
        # 如果已有提取器实例且正在运行，先关闭它
        if extractor:
            try:
                extractor.close()
            except Exception as e:
                logging.error(f"关闭旧提取器时出错: {e}")
            extractor = None
    
        # 创建新的提取器实例
        extractor = WeChatTokenExtractor()
        
        try:
            # 开始登录流程
            if extractor.start_login():
                # 更新状态
                captured_data["status"] = "等待扫码"
                
                # 在后台线程中等待登录完成
                def wait_login_complete():
                    global captured_data
                    if extractor.wait_for_login(timeout=120):
                        # 登录成功，提取认证数据
                        auth_data = extractor.get_auth_data()
                        captured_data["cookies"] = auth_data["cookies"]
                        captured_data["token"] = auth_data["token"]
                        captured_data["status"] = "已登录"
                    else:
                        captured_data["status"] = "登录超时"
                
                login_thread = threading.Thread(target=wait_login_complete)
                login_thread.daemon = True
                login_thread.start()
                
                return jsonify({"status": "success", "message": "登录页面已加载，请扫描二维码"})
            else:
                return jsonify({"status": "error", "message": "启动登录流程失败"})
        
        except Exception as e:
            logging.error(f"登录失败: {e}")
            return jsonify({"status": "error", "message": str(e)})

@app.route('/check_status')
def check_status():
    """检查登录状态"""
    return jsonify(captured_data)

@app.route('/get_credentials')
def get_credentials():
    """获取已捕获的cookie和token"""
    if captured_data["status"] == "已登录" and captured_data["cookies"]:
        return jsonify({
            "status": "success",
            "cookies": captured_data["cookies"],
            "token": captured_data["token"]
        })
    else:
        return jsonify({
            "status": "error", 
            "message": "尚未获取到登录凭证，当前状态：" + captured_data["status"]
        })

@app.route('/reset')
def reset():
    """重置登录状态"""
    global extractor, captured_data
    
    with extractor_lock:
        # 关闭提取器
        if extractor:
            try:
                extractor.close()
            except Exception as e:
                logging.error(f"关闭提取器时出错: {e}")
            extractor = None
        
        # 重置数据
        captured_data = {
            "cookies": None,
            "token": None,
            "status": "未登录"
        }
        
        # 删除旧的二维码图片
        if os.path.exists("static/qrcode.png"):
            try:
                os.remove("static/qrcode.png")
            except Exception as e:
                logging.error(f"删除二维码图片时出错: {e}")
    
    return jsonify({"status": "success", "message": "登录状态已重置"})

if __name__ == '__main__':
    # 确保static目录存在
    os.makedirs("static", exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True) 