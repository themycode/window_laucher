import io
import sys

# 修复 Windows 控制台 UTF-8 编码问题 (GitHub Actions)
if sys.platform.startswith("win"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import PyInstaller.__main__

# 定义资源路径格式 (Windows 使用分号，Mac/Linux 使用冒号)
sep = ";" if sys.platform.startswith("win") else ":"

# 打包配置
params = [
    "src/main.py",  # 主程序入口
    "--name=MyLauncher",  # 生成的 exe 文件名
    "--onefile",  # 打包成单个独立文件
    "--noconsole",  # 运行时不显示黑色命令行窗口
    # 关键步骤：包含前端资源。
    # 格式为："源路径;打包后的相对路径"
    f"--add-data=src/index.html{sep}src",
    # 数据配置
    f"--add-data=apps.json{sep}.",
    # 环境配置
    f"--add-data=.env{sep}.",
    # 如果你有图标，取消下面注释
    "--icon=assets/app.ico",
    "--clean",
]


def build():
    print("Starting build process...")
    PyInstaller.__main__.run(params)
    print("Build completed! Check dist folder.")


if __name__ == "__main__":
    build()
