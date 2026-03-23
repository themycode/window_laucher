# Project Name: Desktop Application Launcher

##  Description
This application can quickly launch a Chrome web app, which can be isolated from the data used by the Chrome browser and can also isolate extension apps, facilitating the use of independent web apps.


### **一、 技术栈选型**

* **后端核心**: **Python 3.x** \+ **pywebview** (用于构建轻量级原生窗口控制台)。  
* **前端 UI**: **HTML5 / CSS3 / JavaScript** (采用 **Glassmorphism** 磨砂玻璃设计语言)。  
* **环境管理**: **uv** (高性能 Python 包管理工具)。  
* **打包工具**: **PyInstaller** (支持静态资源注入与独立 .exe 生成)。  
* **浏览器引擎**: 自动调用系统已安装的 **Google Chrome (App Mode)**。

---

**二、 核心功能特性**

1. **磨砂玻璃交互界面**  
   * 利用 backdrop-filter 实现毛玻璃视觉效果。  
   * 支持 **无边框窗口拖拽** (pywebview-drag-region)，操作体验贴近原生系统。  
2. **配置自动初始化与持久化**  
   * **零配置分发**：程序启动时若检测不到外部配置，会自动从包内“释放”默认的 apps.json 和 .env。  
   * **热加载机制**：内置“刷新”按钮，修改外部 JSON 配置文件后无需重启即可实时更新图标列表。  
3. **统一浏览器隔离环境 (Shared Profile)**  
   * 所有应用共享同一个 USER\_DATA\_BASE\_DIR。  
   * **优势**：在不同应用间保持登录状态一致（如 GitHub、Google 账号只需登录一次），同时与用户日常使用的浏览器数据完全隔离。  
4. **智能搜索与过滤**  
   * 前端集成实时搜索框，支持通过标题或 ID 快速筛选应用图标。  
5. **跨平台路径兼容**  
   * 通过 \_MEIPASS 兼容层，确保图片、HTML 等静态资源在开发环境与打包后的 .exe 中路径始终正确。

---

**三、 逻辑架构简述**

* **数据流**：Python 后端读取 apps.json \-\> 通过 js\_api 暴露给前端 \-\> 前端 JS 渲染 Grid 布局。  
* **进程管理**：用户点击图标 \-\> JS 调用 Python 的 launch 方法 \-\> Python 使用 subprocess.Popen 唤起带有独立 user-data-dir 参数的 Chrome 进程。  
* **编码防护**：系统强制使用 UTF-8 输出流，解决 Windows 环境下 Emoji 字符导致的 GBK 编码崩溃问题。

---

**四、 快速部署 (Submission Guide)**

1. **依赖同步**: 执行 uv sync。  
2. **开发运行**: uv run python src/main.py。  
3. **一键打包**: 执行 uv run python build\_script.py，在 dist/ 目录下获取带图标的 .exe。