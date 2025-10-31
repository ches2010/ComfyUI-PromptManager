import os
import random
import sys
from datetime import datetime

# 尝试导入tkinter，如果失败则使用命令行输入
try:
    import tkinter as tk
    from tkinter import filedialog
    HAS_TKINTER = True
except ImportError:
    HAS_TKINTER = False

class PromptManagerNode:
    """
    提示词管理节点，支持保存、加载和随机组合提示词功能，包含去重机制
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
                "action": (["none", "save", "load", "load_history", "random_combination", 
                           "clean_library", "add_to_library"], {
                    "default": "none",
                    "label": "操作"
                }),
                "history_file_path": ("STRING", {
                    "default": os.path.join(os.path.expanduser("~"), "comfyui_prompt_history.txt"),
                    "placeholder": "提示词历史文件路径"
                }),
                "prompt_library_path": ("STRING", {
                    "default": os.path.join(os.path.expanduser("~"), "comfyui_prompt_library.txt"),
                    "placeholder": "提示词库文件路径（随机组合用）"
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
    
    def process(self, prompt, action, history_file_path, prompt_library_path, node_id):
        """处理提示词操作"""
        if action == "save":
            return self._save_prompt(prompt, history_file_path)
        elif action == "load":
            return self._load_prompt(history_file_path)
        elif action == "load_history":
            return self._load_history(history_file_path)
        elif action == "random_combination":
            return self._random_combination(prompt_library_path)
        elif action == "clean_library":
            return self._clean_library(prompt_library_path)
        elif action == "add_to_library":
            return self._add_to_library(prompt, prompt_library_path)
        else:
            return (prompt, "")
    
    def _get_path(self, default_path, is_save=False):
        """获取文件路径，支持图形界面和命令行两种方式"""
        if default_path and (is_save or os.path.exists(default_path)):
            return default_path
            
        if HAS_TKINTER:
            try:
                root = tk.Tk()
                root.withdraw()
                root.wm_attributes('-topmost', 1)
                
                if is_save:
                    file_path = filedialog.asksaveasfilename(
                        defaultextension=".txt",
                        filetypes=[("Text files", "*.txt"), ("All files", "*")],
                        title="选择文件"
                    )
                else:
                    file_path = filedialog.askopenfilename(
                        filetypes=[("Text files", "*.txt"), ("All files", "*")],
                        title="选择文件"
                    )
                root.destroy()
                return file_path
            except Exception:
                pass
                
        # 无图形界面时使用命令行输入
        print("\n请输入文件路径（例如：/path/to/file.txt）:")
        return input("> ").strip()
    
    def _get_existing_prompts(self, history_file):
        """从历史文件中提取所有已存在的提示词（用于去重）"""
        existing = set()
        
        if not os.path.exists(history_file):
            return existing
            
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 分割所有提示词部分
            sections = content.split("===")
            for section in sections:
                section = section.strip()
                if not section:
                    continue
                # 提取提示词内容（去除时间戳行）
                if '\n' in section:
                    prompt_text = '\n'.join(section.split('\n')[1:]).strip()
                else:
                    prompt_text = ""
                if prompt_text:
                    existing.add(prompt_text)
                    
        except Exception as e:
            print(f"读取历史文件时出错: {str(e)}")
            
        return existing
    
    def _save_prompt(self, prompt, history_file_path):
        """将提示词追加保存到历史文件（自动去重）"""
        prompt_text = prompt.strip()
        if not prompt_text:
            return (prompt, "错误：提示词为空，无法保存")
        
        try:
            # 获取历史文件路径
            file_path = self._get_path(history_file_path, is_save=True)
            
            if not file_path:
                return (prompt, "取消：未选择保存路径")
            
            # 确保目录存在
            dir_name = os.path.dirname(file_path)
            if dir_name and not os.path.exists(dir_name):
                os.makedirs(dir_name, exist_ok=True)
                
            # 检查是否已存在相同提示词
            existing_prompts = self._get_existing_prompts(file_path)
            if prompt_text in existing_prompts:
                return (prompt, "提示：该提示词已存在于历史记录中，未重复保存")
                
            # 追加提示词，带时间戳
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(f"=== {timestamp} ===\n")
                f.write(prompt_text + "\n\n")
            
            status = f"成功：提示词已追加到历史文件\n{file_path}"
            return (prompt, status)
            
        except Exception as e:
            error_msg = f"错误：保存文件时出错\n{str(e)}"
            return (prompt, error_msg)
    
    def _load_prompt(self, history_file_path):
        """从历史文件加载最后一条提示词"""
        try:
            file_path = self._get_path(history_file_path)
            
            if not file_path or not os.path.exists(file_path):
                return ("", "错误：历史文件不存在")
            
            # 读取文件所有内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 查找最后一条提示词（以===开头的行）
            sections = content.split("===")
            if len(sections) >= 3:
                # 最后一个有效部分
                last_section = sections[-2].strip()
                # 去除时间戳行，获取提示词
                if '\n' in last_section:
                    prompt_text = '\n'.join(last_section.split('\n')[1:]).strip()
                else:
                    prompt_text = ""
            else:
                prompt_text = content.strip()
            
            status = f"成功：已从历史文件加载最后一条提示词\n{file_path}"
            return (prompt_text, status)
            
        except Exception as e:
            error_msg = f"错误：读取文件时出错\n{str(e)}"
            return ("", error_msg)
    
    def _load_history(self, history_file_path):
        """加载整个历史文件内容"""
        try:
            file_path = self._get_path(history_file_path)
            
            if not file_path or not os.path.exists(file_path):
                return ("", "错误：历史文件不存在")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                history_content = f.read()
            
            status = f"成功：已加载完整历史文件\n{file_path}"
            return (history_content, status)
            
        except Exception as e:
            error_msg = f"错误：读取历史文件时出错\n{str(e)}"
            return ("", error_msg)
    
    def _load_library(self, library_path):
        """加载提示词库并去重"""
        if not os.path.exists(library_path):
            return []
            
        try:
            with open(library_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 按逗号分割提示词，去除空字符串和空白
            prompts = [p.strip() for p in content.split(',') if p.strip()]
            # 去重但保持顺序
            seen = set()
            unique_prompts = []
            for p in prompts:
                if p not in seen:
                    seen.add(p)
                    unique_prompts.append(p)
                    
            return unique_prompts
            
        except Exception as e:
            print(f"加载提示词库时出错: {str(e)}")
            return []
    
    def _random_combination(self, prompt_library_path):
        """从提示词库中随机组合提示词（使用去重后的库）"""
        try:
            file_path = self._get_path(prompt_library_path)
            
            if not file_path:
                return ("", "错误：未选择提示词库文件")
            
            # 加载并自动去重提示词库
            prompts = self._load_library(file_path)
            
            if not prompts:
                return ("", f"错误：提示词库为空或格式不正确\n{file_path}")
            
            # 随机选择1-3个提示词进行组合
            num_choices = random.randint(1, min(3, len(prompts)))
            selected = random.sample(prompts, num_choices)
            combined = ", ".join(selected)
            
            status = f"成功：从提示词库随机组合了{num_choices}个提示词（共{len(prompts)}个独特提示词）"
            return (combined, status)
            
        except Exception as e:
            error_msg = f"错误：处理提示词库时出错\n{str(e)}"
            return ("", error_msg)
    
    def _clean_library(self, prompt_library_path):
        """清理提示词库，去除重复项"""
        try:
            file_path = self._get_path(prompt_library_path)
            
            if not file_path:
                return ("", "错误：未选择提示词库文件")
            
            # 加载并去重
            original_prompts = self._load_library(file_path)
            if not original_prompts:
                return ("", f"提示：提示词库为空或格式不正确\n{file_path}")
                
            # 保存去重后的结果
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(', '.join(original_prompts))
            
            status = f"成功：提示词库去重完成\n原数量: {len(original_prompts)}（已去重）\n文件: {file_path}"
            return (', '.join(original_prompts), status)
            
        except Exception as e:
            error_msg = f"错误：清理提示词库时出错\n{str(e)}"
            return ("", error_msg)
    
    def _add_to_library(self, prompt, prompt_library_path):
        """将当前提示词添加到提示词库（自动去重）"""
        prompt_text = prompt.strip()
        if not prompt_text:
            return (prompt, "错误：提示词为空，无法添加到库")
        
        try:
            file_path = self._get_path(prompt_library_path, is_save=True)
            
            if not file_path:
                return (prompt, "取消：未选择提示词库文件")
            
            # 确保目录存在
            dir_name = os.path.dirname(file_path)
            if dir_name and not os.path.exists(dir_name):
                os.makedirs(dir_name, exist_ok=True)
                
            # 加载现有库并去重
            existing_prompts = self._load_library(file_path)
            
            # 检查是否已存在
            new_prompts = [p.strip() for p in prompt_text.split(',') if p.strip()]
            added_count = 0
            
            for p in new_prompts:
                if p not in existing_prompts:
                    existing_prompts.append(p)
                    added_count += 1
            
            if added_count == 0:
                return (prompt, "提示：所有提示词已存在于库中，未添加新内容")
                
            # 保存更新后的库
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(', '.join(existing_prompts))
            
            status = f"成功：已添加{added_count}个新提示词到库中\n总数量: {len(existing_prompts)}\n文件: {file_path}"
            return (prompt, status)
            
        except Exception as e:
            error_msg = f"错误：添加到提示词库时出错\n{str(e)}"
            return (prompt, error_msg)

# 节点注册
NODE_CLASS_MAPPINGS = {
    "PromptManagerNode": PromptManagerNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PromptManagerNode": "提示词管理器"
}
    