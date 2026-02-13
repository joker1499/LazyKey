import tkinter as tk
from tkinter import simpledialog, messagebox
import json
import random
import string
import pyperclip
import re

class PasswordManager:
    def __init__(self, root):
        self.root = root
        self.root.title("极简密码管理器")
        self.root.geometry("600x400")
        
        # 使用应用程序所在目录的绝对路径
        import os
        self.data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "accounts.json")
        
        # 加载现有数据
        self.accounts = self.load_accounts()
        
        # 创建主界面
        self.create_widgets()
        
        # 首次启动提示
        self.show_welcome_message()
    
    def load_accounts(self):
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def save_accounts(self):
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.accounts, f, indent=2, ensure_ascii=False)
    
    def generate_password(self):
        # 生成12位密码，包含大小写字母、数字和符号
        chars = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(random.choice(chars) for _ in range(12))
        return password
    
    def extract_domain(self, url):
        # 从URL提取域名
        match = re.search(r'^(?:https?://)?(?:www\.)?([^/]+)', url)
        if match:
            domain = match.group(1)
            # 移除.com等后缀
            if '.' in domain:
                return domain.split('.')[0]
            return domain
        return url
    
    def create_widgets(self):
        # 顶部按钮
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill=tk.X, pady=10)
        
        # 生成密码按钮
        generate_btn = tk.Button(top_frame, text="添加账号", command=self.on_generate_password, width=15, height=2)
        generate_btn.pack(side=tk.LEFT, padx=10)
        
        # 清空所有按钮
        clear_btn = tk.Button(top_frame, text="清空所有", command=self.on_clear_all, width=15, height=2, fg="red")
        clear_btn.pack(side=tk.RIGHT, padx=10)
        
        # 账号列表框架
        list_frame = tk.Frame(self.root)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 滚动条
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 创建Canvas用于滚动
        self.canvas = tk.Canvas(list_frame, yscrollcommand=scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.canvas.yview)
        
        # 创建内部框架
        self.accounts_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.accounts_frame, anchor=tk.NW)
        
        # 绑定配置事件
        self.accounts_frame.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all')))
        
        # 更新列表
        self.update_account_list()
    
    def update_account_list(self):
        # 清空所有子组件
        for widget in self.accounts_frame.winfo_children():
            widget.destroy()
        
        # 按网站名排序
        sorted_accounts = sorted(self.accounts.items(), key=lambda x: x[0])
        
        # 添加到框架
        for site, accounts in sorted_accounts:
            for i, account in enumerate(accounts):
                # 创建账号行框架
                account_row = tk.Frame(self.accounts_frame, bg="#f0f0f0", pady=5, padx=10)
                account_row.pack(fill=tk.X, pady=2, padx=5, ipady=3)
                
                # 左边：网站名称
                site_label = tk.Label(account_row, text=f"📋 {site}: ", 
                                    bg="#f0f0f0", anchor=tk.W)
                site_label.pack(side=tk.LEFT, padx=5)
                
                # 用户名显示和复制按钮
                username_frame = tk.Frame(account_row, bg="#f0f0f0")
                username_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
                
                username_label = tk.Label(username_frame, text=account['username'], 
                                       bg="#f0f0f0", anchor=tk.W)
                username_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                copy_username_btn = tk.Button(username_frame, text="📋", 
                                           command=lambda s=site, idx=i: self.on_copy_username(s, idx),
                                           bg="#e0e0e0", relief=tk.FLAT, width=3)
                copy_username_btn.pack(side=tk.LEFT, padx=5)
                
                # 右边：删除按钮
                delete_btn = tk.Button(account_row, text="🗑️", 
                                     command=lambda s=site, idx=i: self.on_delete_account_direct(s, idx),
                                     bg="#ffcccc", relief=tk.FLAT, width=5)
                delete_btn.pack(side=tk.RIGHT, padx=5)
                
                # 中间：修改密码按钮
                edit_btn = tk.Button(account_row, text="✏️", 
                                   command=lambda s=site, idx=i: self.on_edit_password(s, idx),
                                   bg="#ffffcc", relief=tk.FLAT, width=5)
                edit_btn.pack(side=tk.RIGHT, padx=5)
                
                # 密码复制按钮
                copy_password_btn = tk.Button(account_row, text="🔑", 
                                            command=lambda s=site, idx=i: self.on_copy_password_direct(s, idx),
                                            bg="#e0e0e0", relief=tk.FLAT, width=3)
                copy_password_btn.pack(side=tk.RIGHT, padx=5)
    
    def generate_username(self):
        # 生成随机用户名
        chars = string.ascii_lowercase + string.digits
        username = 'user_' + ''.join(random.choice(chars) for _ in range(8))
        return username
    
    def on_generate_password(self):
        # 获取网站名称
        site = simpledialog.askstring("生成密码", "请输入网站名称（如baidu）:")
        if not site:
            return
        
        # 询问是否随机生成用户名
        answer = messagebox.askyesno("生成用户名", "是否随机生成用户名？\n\n选择'是'：自动生成用户名\n选择'否'：手动输入用户名")
        
        if answer:
            # 自动生成用户名
            username = self.generate_username()
        else:
            # 手动输入用户名
            username = simpledialog.askstring("生成密码", "请输入用户名:")
            if not username:
                return
        
        # 生成密码
        password = self.generate_password()
        
        # 保存账号
        if site not in self.accounts:
            self.accounts[site] = []
        
        # 添加新账号到列表
        self.accounts[site].append({
            "username": username,
            "password": password
        })
        
        self.save_accounts()
        self.update_account_list()
        
        # 提示
        messagebox.showinfo("成功", f"密码已生成并保存：{site}\n用户名：{username}\n密码已复制到剪贴板")
    
    def on_add_account(self):
        # 获取网站名称
        site = simpledialog.askstring("添加账号", "请输入网站名称（如baidu）:")
        if not site:
            return
        
        # 获取用户名
        username = simpledialog.askstring("添加账号", "请输入用户名:")
        if not username:
            return
        
        # 生成密码
        password = self.generate_password()
        
        # 保存账号
        self.accounts[site] = {
            "username": username,
            "password": password
        }
        
        self.save_accounts()
        self.update_account_list()
        
        # 提示
        messagebox.showinfo("成功", f"账号已添加：{site}\n密码已生成并保存")
    
    def on_copy_password_direct(self, site, idx):
        # 获取密码
        if site in self.accounts and 0 <= idx < len(self.accounts[site]):
            password = self.accounts[site][idx]['password']
            
            # 复制到剪贴板
            pyperclip.copy(password)
            
            # 提示
            messagebox.showinfo("成功", f"密码已复制到剪贴板")
    
    def on_copy_username(self, site, idx):
        # 获取用户名
        if site in self.accounts and 0 <= idx < len(self.accounts[site]):
            username = self.accounts[site][idx]['username']
            
            # 复制到剪贴板
            pyperclip.copy(username)
            
            # 提示
            messagebox.showinfo("成功", f"用户名已复制到剪贴板")
    
    def on_delete_account_direct(self, site, idx):
        # 确认删除
        if messagebox.askyesno("确认", f"确定要删除账号 {site} 吗？"):
            if site in self.accounts and 0 <= idx < len(self.accounts[site]):
                del self.accounts[site][idx]
                # 如果该网站没有账号了，删除网站条目
                if not self.accounts[site]:
                    del self.accounts[site]
                self.save_accounts()
                self.update_account_list()
                messagebox.showinfo("成功", f"账号 {site} 已删除")
    
    def on_edit_password(self, site, idx):
        # 询问用户是否手动输入密码
        answer = messagebox.askyesno("修改密码", f"是否手动输入新密码？\n\n选择'是'：手动输入密码\n选择'否'：自动生成密码")
        
        if answer:
            # 手动输入密码
            new_password = simpledialog.askstring("修改密码", f"请输入新密码：", show="*")
            if not new_password:
                return
        else:
            # 自动生成密码
            new_password = self.generate_password()
        
        # 更新密码
        if site in self.accounts and 0 <= idx < len(self.accounts[site]):
            self.accounts[site][idx]['password'] = new_password
            self.save_accounts()
            
            # 复制新密码到剪贴板
            pyperclip.copy(new_password)
            
            messagebox.showinfo("成功", f"密码已更新：{site}\n新密码已复制到剪贴板")
    

    
    def on_clear_all(self):
        # 确认
        if messagebox.askyesno("确认", "确定要清空所有账号记录吗？"):
            self.accounts.clear()
            self.save_accounts()
            self.update_account_list()
            messagebox.showinfo("成功", "所有账号记录已清空")
    
    def show_welcome_message(self):
        # 显示欢迎消息
        messagebox.showinfo(
            "欢迎使用极简密码管理器",
            "输入网站名称和用户名，自动生成12位复杂密码并保存\n\n"+
            "⚠️ 重要提示：\n"+
            "- 本产品仅适用于非个人核心账号\n"+
            "- 数据明文存储在本地\n"+
            "- 不推荐用于银行、支付类账户！"
        )

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordManager(root)
    root.mainloop()