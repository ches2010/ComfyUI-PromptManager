import os
import sys
import subprocess
import importlib

def install_packages():
    """安装所需的依赖包"""
    try:
        # 检查是否需要安装依赖
        requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
        
        if os.path.exists(requirements_path):
            print("开始安装提示词管理器插件依赖...")
            
            # 使用当前Python环境安装依赖
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "-r", requirements_path
            ])
            
            print("提示词管理器插件依赖安装完成")
        else:
            print("未找到requirements.txt，跳过依赖安装")
            
    except Exception as e:
        print(f"安装依赖时出错: {str(e)}")
        # 非致命错误，继续执行

def check_and_install_tkinter():
    """检查并尝试安装tkinter（如果缺失）"""
    try:
        importlib.import_module('tkinter')
        print("tkinter已安装")
    except ImportError:
        print("未找到tkinter，尝试安装...")
        try:
            # 根据不同平台尝试安装tkinter
            if sys.platform.startswith('win'):
                print("Windows系统通常已预装tkinter，若仍有问题请重新安装Python并勾选tkinter组件")
            elif sys.platform.startswith('darwin'):  # macOS
                subprocess.check_call(['brew', 'install', 'python-tk'])
            else:  # Linux
                subprocess.check_call(['sudo', 'apt-get', 'install', 'python3-tk'])
                
            print("tkinter安装成功")
        except Exception as e:
            print(f"自动安装tkinter失败: {str(e)}")
            print("请手动安装tkinter后再使用本插件")

def main():
    """安装入口函数"""
    print("正在安装ComfyUI提示词管理器插件...")
    
    # 安装依赖
    install_packages()
    
    # 检查并安装tkinter
    check_and_install_tkinter()
    
    print("ComfyUI提示词管理器插件安装完成，重启ComfyUI即可使用")

if __name__ == "__main__":
    main()