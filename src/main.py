# -*- coding: utf-8 -*-
import io
import json
import os
import shutil
import subprocess
import sys

import webview
from dotenv import load_dotenv

# --- 编码补丁：解决 Windows 下打印 Emoji 报 GBK 错误的问题 ---
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")


def get_resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class MyAppLogic:
    def __init__(self):
        if hasattr(sys, "_MEIPASS"):
            self.base_dir = os.path.dirname(sys.executable)
        else:
            self.base_dir = os.path.abspath(".")

        load_dotenv(os.path.join(self.base_dir, ".env"))

        self.ext_config = os.path.join(self.base_dir, "apps.json")
        self.ext_env = os.path.join(self.base_dir, ".env")

        self.ensure_config_exists()

        # 统一使用外部配置路径
        self.config_path = self.ext_config

        self.chrome_path = os.getenv(
            "CHROME_PATH",
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",  # 修正了常见的路径
        )
        self.version = os.getenv("VERSION", "0.1.0")

        # 统一的用户数据存放目录
        self.user_data_base = os.getenv(
            "USER_DATA_BASE_DIR",
            os.path.join(os.environ["LOCALAPPDATA"], "MyLauncher", "SharedProfile"),
        )

        self.load_config()

    def ensure_config_exists(self):
        if not os.path.exists(self.ext_config):
            internal_json = get_resource_path("apps.json")
            if os.path.exists(internal_json):
                shutil.copy(internal_json, self.ext_config)

        if not os.path.exists(self.ext_env):
            internal_env = get_resource_path(".env")
            if os.path.exists(internal_env):
                shutil.copy(internal_env, self.ext_env)

    def load_config(self):
        try:
            # 确保使用 self.config_path (即外部路径)
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.apps = json.load(f)
        except Exception as e:
            print(f"读取配置失败: {e}")
            self.apps = []

    def refresh_config(self):
        try:
            with open(self.ext_config, "r", encoding="utf-8") as f:
                self.apps = json.load(f)
            return {"status": "success", "data": self.apps}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def launch(self, app_id):
        app = next((a for a in self.apps if a["id"] == app_id), None)
        if not app:
            return False

        # --- 核心修改：不再根据 ID 创建子文件夹，全部共用一个目录 ---
        # 这样你在一个 App 登录了 GitHub，其他 App 访问 GitHub 也会是登录状态
        os.makedirs(self.user_data_base, exist_ok=True)

        cmd = [
            self.chrome_path,
            f"--user-data-dir={self.user_data_base}",  # 使用统一目录
            "--profile-directory=Default",  # 明确使用 Default 配置文件
            f"--app={app['url']}",
            f"--window-size={app.get('size', '1280,800')}",
            "--no-first-run",  # 优化启动体验
            "--disk-cache-dir="
            + os.path.join(self.user_data_base, "Cache"),  # 明确缓存目录
        ]
        subprocess.Popen(cmd)
        return True

    def get_apps(self):
        return self.apps

    def get_env_info(self):
        return {"version": self.version}

    def restart_app(self):
        os.execl(sys.executable, sys.executable, *sys.argv)


app_logic = MyAppLogic()


def run():
    icon_path = os.path.abspath(get_resource_path(os.path.join("assets", "app-16.ico")))
    html_path = get_resource_path(os.path.join("src", "index.html"))

    # 增加窗口默认宽高，给自适应布局留空间
    webview.create_window(
        "APP控制台",
        url=html_path,
        js_api=app_logic,
        width=500,  # 稍微加宽一点
        height=750,  # 稍微加长一点
        min_size=(320, 400),
        transparent=True,
        easy_drag=True,
    )

    debug_mode = os.getenv("APP_DEBUG", "False").lower() == "true"
    webview.start(icon=icon_path, debug=debug_mode)


if __name__ == "__main__":
    run()
