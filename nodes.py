import os
import random
import sys

# 尝试导入tkinter，如果失败则使用命令行输入
try:
    import tkinter as tk
    from tkinter import filedialog
    HAS_TKINTER = True
except ImportError:
    HAS_TKINTER = False

class PromptManagerNode:
    """
    提示词管理节点，支持保存、加载和随机组合提示词功能
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "placeholder": "输入或粘贴提示词...",
                    "dynamicPrompts": True
                }),
                "action": (["none", "save", "load", "random_combination"], {
                    "default": "none",
                    "label": "操作"
                }),
                "file_path": ("STRING", {
                    "default": "",
                    "placeholder": "手动输入文件路径（无图形界面时使用）"
                }),
            },
            "hidden": {
                "node_id": "UNIQUE_ID",
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("prompt", "status")
    FUNCTION = "process"
    CATEGORY = "提示词管理"
    
    def process(self, prompt, action, file_path, node_id):
        """处理提示词操作"""
        if action == "save":
            return self._save_prompt(prompt, file_path)
        elif action == "load":
            return self._load_prompt(file_path)
        elif action == "random_combination":
            return self._random_combination(file_path)
        else:
            return (prompt, "")
    
    def _get_save_path(self, default_path):
        """获取保存路径，支持图形界面和命令行两种方式"""
        if default_path and os.path.dirname(default_path):
            return default_path
            
        if HAS_TKINTER:
            try:
                root = tk.Tk()
                root.withdraw()
                root.wm_attributes('-topmost', 1)
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".txt",
                    filetypes=[("Text files", "*.txt"), ("All files", "*")],
                    title="保存提示词文件"
                )
                root.destroy()
                return file_path
            except Exception:
                pass
                
        # 无图形界面时使用命令行输入
        print("\n请输入保存路径（例如：/path/to/prompt.txt）:")
        return input("> ").strip()
    
    def _get_open_path(self, default_path):
        """获取打开路径，支持图形界面和命令行两种方式"""
        if default_path and os.path.exists(default_path):
            return default_path
            
        if HAS_TKINTER:
            try:
                root = tk.Tk()
                root.withdraw()
                root.wm_attributes('-topmost', 1)
                file_path = filedialog.askopenfilename(
                    filetypes=[("Text files", "*.txt"), ("All files", "*")],
                    title="选择提示词文件"
                )
                root.destroy()
                return file_path
            except Exception:
                pass
                
        # 无图形界面时使用命令行输入
        print("\n请输入文件路径（例如：/path/to/prompt.txt）:")
        return input("> ").strip()
    
    def _save_prompt(self, prompt, file_path):
        """保存提示词到文件"""
        if not prompt.strip():
            return (prompt, "错误：提示词为空，无法保存")
        
        try:
            file_path = self._get_save_path(file_path)
            
            if not file_path:
                return (prompt, "取消：未选择保存路径")
            
            # 确保目录存在
            dir_name = os.path.dirname(file_path)
            if dir_name and not os.path.exists(dir_name):
                os.makedirs(dir_name, exist_ok=True)
                
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(prompt)
            
            status = f"成功：提示词已保存到\n{file_path}"
            return (prompt, status)
            
        except Exception as e:
            error_msg = f"错误：保存文件时出错\n{str(e)}"
            return (prompt, error_msg)
    
    def _load_prompt(self, file_path):
        """从文件加载提示词"""
        try:
            file_path = self._get_open_path(file_path)
            
            if not file_path or not os.path.exists(file_path):
                return ("", "错误：文件不存在")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                loaded_prompt = f.read()
            
            status = f"成功：已从\n{file_path}\n加载提示词"
            return (loaded_prompt, status)
            
        except Exception as e:
            error_msg = f"错误：读取文件时出错\n{str(e)}"
            return ("", error_msg)
    
    def _random_combination(self, file_path):
        """从提示词库中随机组合提示词"""
        try:
            file_path = self._get_open_path(file_path)
            
            if not file_path or not os.path.exists(file_path):
                return ("", "错误：文件不存在")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 按逗号分割提示词，去除空字符串和空白
            prompts = [p.strip() for p in content.split(',') if p.strip()]
            
            if not prompts:
                return ("", f"错误：在文件中未找到有效的提示词")
            
            # 随机选择1-3个提示词进行组合
            num_choices = random.randint(1, min(3, len(prompts)))
            selected = random.sample(prompts, num_choices)
            combined = ", ".join(selected)
            
            status = f"成功：从文件随机组合了{num_choices}个提示词"
            return (combined, status)
            
        except Exception as e:
            error_msg = f"错误：处理文件时出错\n{str(e)}"
            return ("", error_msg)

# 节点注册
NODE_CLASS_MAPPINGS = {
    "PromptManagerNode": PromptManagerNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PromptManagerNode": "提示词管理器"
}
    