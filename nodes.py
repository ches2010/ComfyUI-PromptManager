import os
import random
import tkinter as tk
from tkinter import filedialog, messagebox

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
            },
            "hidden": {
                "node_id": "UNIQUE_ID",
                "prompt_text": "STRING",
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("prompt", "status")
    FUNCTION = "process"
    CATEGORY = "提示词管理"
    
    def __init__(self):
        self.prompt_text = ""
        self.status = ""
    
    def process(self, prompt, action, node_id, prompt_text=None):
        """
        处理提示词操作
        
        Args:
            prompt (str): 当前提示词
            action (str): 操作类型：none, save, load, random_combination
            node_id (str): 节点ID
            prompt_text (str): 隐藏的提示词文本
            
        Returns:
            tuple: (处理后的提示词, 状态信息)
        """
        # 初始化Tkinter根窗口（隐藏）
        root = tk.Tk()
        root.withdraw()
        root.wm_attributes('-topmost', 1)  # 确保对话框在最上层
        
        try:
            if action == "save":
                return self._save_prompt(prompt, root)
            elif action == "load":
                return self._load_prompt(root)
            elif action == "random_combination":
                return self._random_combination(root)
            else:
                # 默认返回原始提示词和空状态
                return (prompt, "")
        finally:
            # 确保Tkinter资源被释放
            root.destroy()
    
    def _save_prompt(self, prompt, root):
        """
        保存提示词到文件
        
        Args:
            prompt (str): 要保存的提示词
            root (tk.Tk): Tkinter根窗口
            
        Returns:
            tuple: (提示词, 状态信息)
        """
        if not prompt.strip():
            return (prompt, "错误：提示词为空，无法保存")
        
        try:
            # 显示文件保存对话框
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*")],
                title="保存提示词文件",
                parent=root
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(prompt)
                
                status = f"成功：提示词已保存到\n{file_path}"
                print(status)
                return (prompt, status)
            else:
                return (prompt, "取消：未选择保存路径")
                
        except Exception as e:
            error_msg = f"错误：保存文件时出错\n{str(e)}"
            print(error_msg)
            return (prompt, error_msg)
    
    def _load_prompt(self, root):
        """
        从文件加载提示词
        
        Args:
            root (tk.Tk): Tkinter根窗口
            
        Returns:
            tuple: (加载的提示词, 状态信息)
        """
        try:
            # 显示文件打开对话框
            file_path = filedialog.askopenfilename(
                filetypes=[("Text files", "*.txt"), ("All files", "*")],
                title="加载提示词文件",
                parent=root
            )
            
            if file_path:
                with open(file_path, 'r', encoding='utf-8') as f:
                    loaded_prompt = f.read()
                
                status = f"成功：已从\n{file_path}\n加载提示词"
                print(status)
                return (loaded_prompt, status)
            else:
                return ("", "取消：未选择文件")
                
        except Exception as e:
            error_msg = f"错误：读取文件时出错\n{str(e)}"
            print(error_msg)
            return ("", error_msg)
    
    def _random_combination(self, root):
        """
        从提示词库中随机组合提示词
        
        Args:
            root (tk.Tk): Tkinter根窗口
            
        Returns:
            tuple: (组合的提示词, 状态信息)
        """
        try:
            # 显示文件打开对话框
            file_path = filedialog.askopenfilename(
                filetypes=[("Text files", "*.txt"), ("All files", "*")],
                title="选择提示词库文件",
                parent=root
            )
            
            if file_path:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 按逗号分割提示词，去除空字符串和空白
                prompts = [p.strip() for p in content.split(',') if p.strip()]
                
                if not prompts:
                    return ("", f"错误：在文件\n{file_path}\n中未找到有效的提示词")
                
                # 随机选择1-3个提示词进行组合
                num_choices = random.randint(1, min(3, len(prompts)))
                selected = random.sample(prompts, num_choices)
                combined = ", ".join(selected)
                
                status = f"成功：从\n{file_path}\n随机组合了{num_choices}个提示词"
                print(status)
                return (combined, status)
            else:
                return ("", "取消：未选择文件")
                
        except Exception as e:
            error_msg = f"错误：处理文件时出错\n{str(e)}"
            print(error_msg)
            return ("", error_msg)

# 节点注册
NODE_CLASS_MAPPINGS = {
    "PromptManagerNode": PromptManagerNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PromptManagerNode": "提示词管理器"
}
