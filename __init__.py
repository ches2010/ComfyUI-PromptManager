"""
ComfyUI提示词管理插件
支持保存、加载和随机组合提示词功能
"""
import os
import sys

# 检查是否需要自动安装依赖
def check_and_install_dependencies():
    # 仅在通过git clone手动安装时才尝试自动安装
    # 避免与ComfyUI Manager的安装流程冲突
    if not os.environ.get('COMFYUI_MANAGER_INSTALLING', False):
        try:
            # 检查是否已安装tkinter
            import tkinter
        except ImportError:
            print("检测到缺失依赖，尝试自动安装...")
            install_script = os.path.join(os.path.dirname(__file__), "install.py")
            if os.path.exists(install_script):
                try:
                    # 运行安装脚本
                    import subprocess
                    subprocess.check_call([sys.executable, install_script])
                except Exception as e:
                    print(f"自动安装依赖失败: {str(e)}")
                    print("请手动运行install.py安装依赖")

# 检查并安装依赖
check_and_install_dependencies()

# 导入节点模块
from .nodes import PromptManagerNode

# 节点注册
NODE_CLASS_MAPPINGS = {
    "PromptManagerNode": PromptManagerNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PromptManagerNode": "提示词管理器"
}

# 插件元数据
__version__ = "1.0.0"
__author__ = "ComfyUI用户"
__description__ = "ComfyUI提示词管理插件，支持保存、加载和随机组合提示词功能"

# 确保插件目录可被ComfyUI识别
WEB_DIRECTORY = "./web"

print(f"提示词管理器插件 v{__version__} 已加载")