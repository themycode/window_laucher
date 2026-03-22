# -*- coding: utf-8 -*-
import json
import os
import shutil
import subprocess
import sys

import webview
from dotenv import load_dotenv

load_dotenv()


def get_resource_path(relative_path):
    """核心路径兼容函数"""
    if hasattr(sys, "_MEIPASS"):
        # 打包后的临时目录
        return os.path.join(sys._MEIPASS, relative_path)
    # 开发环境下的当前目录
    return os.path.join(os.path.abspath("."), relative_path)


class MyAppLogic:
    def __init__(self):
        # 1. 获取 .exe 所在的真实外部目录
        if hasattr(sys, "_MEIPASS"):
            # 打包环境：.exe 所在的文件夹
            self.base_dir = os.path.dirname(sys.executable)
        else:
            # 开发环境：项目根目录
            self.base_dir = os.path.abspath(".")

        load_dotenv(os.path.join(self.base_dir, ".env"))
        # 2. 定义外部文件的目标路径
        self.ext_config = os.path.join(self.base_dir, "apps.json")
        self.ext_env = os.path.join(self.base_dir, ".env")
        # 3. 自动初始化逻辑
        self.ensure_config_exists()
        # 4. 始终加载外部文件（因为刚才已经确保它存在了）
        self.config_path = self.ext_config
        self.load_config()
        # 优先读取环境变量，如果不存在则使用默认值
        self.chrome_path = os.getenv(
            "CHROME_PATH",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        )
        self.version = os.getenv("VERSION", "0.1.0")
        self.user_data_base = os.getenv(
            "USER_DATA_BASE_DIR", os.path.join(os.environ["LOCALAPPDATA"], "MyLauncher")
        )
        # 动态获取 JSON 路径
        self.config_path = get_resource_path("apps.json")
        # self.load_config()

    def ensure_config_exists(self):
        """如果外部没有配置，则从内部释放一份默认的"""
        # 处理 apps.json
        if not os.path.exists(self.ext_config):
            internal_json = get_resource_path("apps.json")
            if os.path.exists(internal_json):
                shutil.copy(internal_json, self.ext_config)

        # 处理 .env
        if not os.path.exists(self.ext_env):
            internal_env = get_resource_path(".env")
            if os.path.exists(internal_env):
                shutil.copy(internal_env, self.ext_env)

    def get_env_info(self):
        return {
            "is_debug": os.getenv("APP_DEBUG", "False"),
            "version": self.version,
        }

    def refresh_config(self):
        """供前端调用的热加载接口"""
        try:
            # 重新从外部路径加载
            with open(self.ext_config, "r", encoding="utf-8") as f:
                self.apps = json.load(f)
            print("🔄 配置已手动刷新")
            return {"status": "success", "data": self.apps}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def restart_app(self):
        """彻底重启进程 (可选)"""
        # 获取当前运行的 exe 或脚本路径并重新启动
        os.execl(sys.executable, sys.executable, *sys.argv)

    def load_config(self):
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.apps = json.load(f)
        except Exception as e:
            print(f"读取配置失败: {e}")
            self.apps = []

    def get_apps(self):
        return self.apps

    def launch(self, app_id):
        app = next((a for a in self.apps if a["id"] == app_id), None)
        if not app:
            return False
        user_data = os.path.join(self.user_data_base, app["id"])
        os.makedirs(user_data, exist_ok=True)
        cmd = [
            self.chrome_path,
            f"--user-data-dir={user_data}",
            f"--app={app['url']}",
            f"--window-size={app.get('size', '1280,720')}",
        ]
        subprocess.Popen(cmd)
        print(" App模式已启动")
        return True


app_logic = MyAppLogic()


def run():
    print("Hello from window-laucher!")
    icon_path = os.path.abspath(get_resource_path(os.path.join("assets", "app-16.ico")))
    html_path = get_resource_path(os.path.join("src", "index.html"))
    if not os.path.exists(html_path):
        print(f"错误: 找不到界面文件: {html_path}")
        return
    # 创建窗口,指向你的H5页面
    webview.create_window(
        "APP控制台",
        url=html_path,
        js_api=app_logic,
        width=500,
        height=600,
        transparent=True,
        # frameless=True,
        easy_drag=True,
    )
    debug_mode = os.getenv("APP_DEBUG", "False").lower() == "true"
    webview.start(
        icon=icon_path,
        debug=debug_mode,
    )


if __name__ == "__main__":
    run()
