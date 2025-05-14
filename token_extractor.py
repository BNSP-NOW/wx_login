from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import json
import time
import re
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class WeChatTokenExtractor:
    """微信公众平台Token提取工具"""
    
    def __init__(self):
        self.driver = None
        self.network_logs = []
        self.token = None
        self.cookies = None
    
    def setup_driver(self):
        """设置启用网络监控的Chrome WebDriver"""
        # 启用Chrome的性能日志记录
        capabilities = DesiredCapabilities.CHROME
        capabilities["goog:loggingPrefs"] = {"performance": "ALL"}
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # 创建Chrome WebDriver
        self.driver = webdriver.Chrome(options=chrome_options, desired_capabilities=capabilities)
        logging.info("WebDriver已初始化")
    
    def start_login(self):
        """打开微信公众平台登录页面"""
        if not self.driver:
            self.setup_driver()
        
        self.driver.get("https://mp.weixin.qq.com/")
        logging.info("已打开微信公众平台登录页面")
        
        # 等待登录页面加载
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "login__type__container"))
        )
        
        # 点击扫码登录按钮（如果有其他登录选项的话）
        try:
            qr_login_btn = self.driver.find_element(By.XPATH, "//a[contains(text(), '扫码登录')]")
            qr_login_btn.click()
            time.sleep(1)
        except Exception as e:
            logging.info(f"直接进入扫码登录页面: {e}")
        
        # 截取二维码区域的图像
        qr_element = self.driver.find_element(By.CLASS_NAME, "login__type__container")
        qr_element.screenshot("static/qrcode.png")
        logging.info("已保存登录二维码")
        
        return True
    
    def wait_for_login(self, timeout=60):
        """等待用户扫码登录，超时返回False"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if "mp.weixin.qq.com/cgi-bin/home" in self.driver.current_url:
                logging.info("登录成功！")
                self.extract_auth_data()
                return True
            time.sleep(1)
        
        logging.warning("登录超时")
        return False
    
    def extract_auth_data(self):
        """提取认证数据（cookies和token）"""
        # 获取所有cookies
        all_cookies = self.driver.get_cookies()
        self.cookies = {cookie['name']: cookie['value'] for cookie in all_cookies}
        logging.info(f"已提取 {len(self.cookies)} 个cookies")
        
        # 从浏览器日志中提取token
        self.extract_token_from_logs()
        
        # 如果从日志中没有找到token，尝试其他方法
        if not self.token:
            self.extract_token_from_page()
        
        # 如果还是没有找到token，尝试打开特定页面查找
        if not self.token:
            self.extract_token_from_specific_page()
    
    def extract_token_from_logs(self):
        """从浏览器性能日志中提取token"""
        logs = self.driver.get_log("performance")
        
        for log_entry in logs:
            try:
                log_data = json.loads(log_entry["message"])["message"]
                if "Network.responseReceived" in log_data["method"]:
                    response_url = log_data["params"]["response"]["url"]
                    
                    # 查找可能包含token的请求
                    if "token=" in response_url:
                        token_match = re.search(r"token=([^&]+)", response_url)
                        if token_match:
                            self.token = token_match.group(1)
                            logging.info(f"从网络日志中找到token: {self.token}")
                            return
                    
                    # 尝试查找包含token的其他API请求
                    if "cgi-bin" in response_url and "lang=zh_CN" in response_url:
                        request_id = log_data["params"]["requestId"]
                        try:
                            # 获取响应体
                            response_body = self.driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id})
                            if "token" in response_body.get("body", ""):
                                token_match = re.search(r'"token"\s*:\s*"([^"]+)"', response_body["body"])
                                if token_match:
                                    self.token = token_match.group(1)
                                    logging.info(f"从响应体中找到token: {self.token}")
                                    return
                        except Exception as e:
                            pass  # 忽略无法获取的响应体
            except Exception as e:
                pass  # 忽略解析错误
    
    def extract_token_from_page(self):
        """从页面内容中提取token"""
        try:
            # 尝试从localStorage获取
            token = self.driver.execute_script("return localStorage.getItem('token') || ''")
            if token:
                self.token = token
                logging.info(f"从localStorage中找到token: {self.token}")
                return
            
            # 尝试从页面源码中获取
            page_source = self.driver.page_source
            token_match = re.search(r'"token"\s*:\s*"([^"]+)"', page_source)
            if token_match:
                self.token = token_match.group(1)
                logging.info(f"从页面源码中找到token: {self.token}")
                return
            
            # 尝试从JavaScript变量中获取
            token = self.driver.execute_script(
                "try { return window.wx.cgiData && window.wx.cgiData.token } catch(e) { return ''; }"
            )
            if token:
                self.token = token
                logging.info(f"从JavaScript变量中找到token: {self.token}")
                return
        except Exception as e:
            logging.error(f"从页面提取token时出错: {e}")
    
    def extract_token_from_specific_page(self):
        """通过访问特定页面来提取token"""
        try:
            # 访问设置页面，该页面可能包含token
            self.driver.get("https://mp.weixin.qq.com/cgi-bin/settingpage")
            time.sleep(2)
            
            # 从URL中提取
            if "token=" in self.driver.current_url:
                token_match = re.search(r"token=([^&]+)", self.driver.current_url)
                if token_match:
                    self.token = token_match.group(1)
                    logging.info(f"从设置页面URL中找到token: {self.token}")
                    return
            
            # 再次尝试从页面源码提取
            page_source = self.driver.page_source
            token_match = re.search(r'"token"\s*:\s*"([^"]+)"', page_source)
            if token_match:
                self.token = token_match.group(1)
                logging.info(f"从设置页面源码中找到token: {self.token}")
                return
        except Exception as e:
            logging.error(f"访问特定页面提取token时出错: {e}")
    
    def get_auth_data(self):
        """获取认证数据"""
        return {
            "cookies": self.cookies,
            "token": self.token
        }
    
    def close(self):
        """关闭WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            logging.info("WebDriver已关闭")


# 测试代码
if __name__ == "__main__":
    extractor = WeChatTokenExtractor()
    try:
        extractor.start_login()
        print("请扫描二维码登录...")
        if extractor.wait_for_login(timeout=60):
            auth_data = extractor.get_auth_data()
            print("认证数据:")
            print(f"Token: {auth_data['token']}")
            print(f"Cookies: {json.dumps(auth_data['cookies'], indent=2)}")
        else:
            print("登录超时或失败")
    finally:
        extractor.close() 