import os
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

class TextureRenamerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("贴图批量重命名工具v1.2")
        self.root.geometry("620x550")  # 微调窗口高度以适配新控件
        self.root.resizable(False, False)

        # 变量
        self.folder_path = tk.StringVar()
        self.output_folder_path = tk.StringVar()  # 新增：输出文件夹变量
        self.remove_words = tk.StringVar(value="")
        self.suffix = tk.StringVar(value="")
        # 强匹配替换变量
        self.replace_old = tk.StringVar(value="")
        self.replace_new = tk.StringVar(value="")

        self.create_widgets()

    def create_widgets(self):
        # 标题
        title_label = ttk.Label(self.root, text="贴图批量重命名工具", font=("微软雅黑", 14, "bold"))
        title_label.pack(pady=10)

        # 源文件夹选择
        folder_frame = ttk.Frame(self.root)
        folder_frame.pack(fill="x", padx=20, pady=5)
        ttk.Label(folder_frame, text="源文件夹：").grid(row=0, column=0, sticky="w", padx=5)
        ttk.Entry(folder_frame, textvariable=self.folder_path, width=48).grid(row=0, column=1, padx=5)
        ttk.Button(folder_frame, text="选择文件夹", command=self.select_source_folder).grid(row=0, column=2)

        # 新增：输出文件夹选择
        output_folder_frame = ttk.Frame(self.root)
        output_folder_frame.pack(fill="x", padx=20, pady=5)
        ttk.Label(output_folder_frame, text="输出文件夹：").grid(row=0, column=0, sticky="w", padx=5)
        ttk.Entry(output_folder_frame, textvariable=self.output_folder_path, width=48).grid(row=0, column=1, padx=5)
        ttk.Button(output_folder_frame, text="选择文件夹", command=self.select_output_folder).grid(row=0, column=2)

        # 强匹配替换（核心功能）
        replace_frame = ttk.LabelFrame(self.root, text="✅ 强匹配精准替换")
        replace_frame.pack(fill="x", padx=20, pady=10)
        ttk.Label(replace_frame, text="要替换的完整文本：").grid(row=0, column=0, sticky="w", padx=5, pady=8)
        ttk.Entry(replace_frame, textvariable=self.replace_old, width=35).grid(row=0, column=1, padx=5)
        ttk.Label(replace_frame, text="替换为：").grid(row=1, column=0, sticky="w", padx=5, pady=8)
        ttk.Entry(replace_frame, textvariable=self.replace_new, width=35).grid(row=1, column=1, padx=5)

        # 移除内容
        remove_frame = ttk.LabelFrame(self.root, text="批量移除文字（多个用英文逗号 , 分隔）")
        remove_frame.pack(fill="x", padx=20, pady=8)
        ttk.Label(remove_frame, text="要删除的内容：").grid(row=0, column=0, sticky="w", padx=5, pady=8)
        ttk.Entry(remove_frame, textvariable=self.remove_words, width=40).grid(row=0, column=1, padx=5)

        # 添加后缀
        suffix_frame = ttk.LabelFrame(self.root, text="批量添加后缀")
        suffix_frame.pack(fill="x", padx=20, pady=8)
        ttk.Label(suffix_frame, text="添加后缀：").grid(row=0, column=0, sticky="w", padx=5, pady=8)
        ttk.Entry(suffix_frame, textvariable=self.suffix, width=20).grid(row=0, column=1, padx=5)

        # 执行按钮
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="🔹 精准强匹配替换", command=self.do_replace, width=18).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(btn_frame, text="仅删除文字", command=self.do_remove, width=12).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="仅添加后缀", command=self.do_suffix, width=12).grid(row=0, column=2, padx=5)

        # 状态
        self.status_label = ttk.Label(self.root, text="准备就绪", foreground="green")
        self.status_label.pack(pady=5)

    def select_source_folder(self):
        """选择源文件夹（原选择文件夹功能）"""
        path = filedialog.askdirectory()
        if path:
            self.folder_path.set(path)

    def select_output_folder(self):
        """新增：选择输出文件夹"""
        path = filedialog.askdirectory()
        if path:
            self.output_folder_path.set(path)

    def get_remove_list(self):
        raw = self.remove_words.get().strip()
        return [w.strip() for w in raw.split(",") if w.strip()]

    # 核心：强匹配替换逻辑（修改输出路径逻辑）
    def process_file(self, source_folder, output_folder, filename, remove_list, add_suffix, replace_old="", replace_new=""):
        texture_ext = {'.png', '.jpg', '.jpeg', '.tga', '.bmp', '.dds', '.exr', '.hdr'}
        old_path = os.path.join(source_folder, filename)
        if os.path.isdir(old_path):
            return

        name, ext = os.path.splitext(filename)
        if ext.lower() not in texture_ext:
            return

        new_name = name
        
        # 强匹配：只替换 完整一模一样的文本
        if replace_old and replace_old in new_name:
            new_name = new_name.replace(replace_old, replace_new)
        
        # 删除文字
        for w in remove_list:
            new_name = new_name.replace(w, "")

        # 添加后缀
        if add_suffix:
            sf = self.suffix.get()
            if not new_name.endswith(sf):
                new_name += sf

        new_filename = new_name + ext
        new_path = os.path.join(output_folder, new_filename)  # 使用输出文件夹作为新路径

        if old_path != new_path:
            shutil.copy2(old_path, new_path)  # 改为复制（避免移动源文件），如需移动可改回shutil.move

    def run_task(self, mode):
        source_folder = self.folder_path.get().strip()
        output_folder = self.output_folder_path.get().strip()  # 获取输出文件夹
        
        # 校验源文件夹和输出文件夹
        if not source_folder or not os.path.isdir(source_folder):
            messagebox.showerror("错误", "请先选择有效源文件夹")
            return
        if not output_folder or not os.path.isdir(output_folder):
            messagebox.showerror("错误", "请先选择有效输出文件夹")
            return

        self.status_label.config(text="处理中...", foreground="blue")
        self.root.update()

        remove_list = self.get_remove_list()
        replace_old = self.replace_old.get().strip()
        replace_new = self.replace_new.get().strip()

        try:
            for filename in os.listdir(source_folder):
                if mode == "replace":
                    self.process_file(source_folder, output_folder, filename, [], add_suffix=False, 
                                     replace_old=replace_old, replace_new=replace_new)
                elif mode == "remove":
                    self.process_file(source_folder, output_folder, filename, remove_list, add_suffix=False)
                elif mode == "suffix":
                    self.process_file(source_folder, output_folder, filename, [], add_suffix=True)

            self.status_label.config(text="✅ 处理完成！", foreground="green")
            messagebox.showinfo("完成", "批量重命名已执行完毕")
        except Exception as e:
            self.status_label.config(text="❌ 处理失败", foreground="red")
            messagebox.showerror("错误", str(e))

    # 强匹配替换
    def do_replace(self):
        self.run_task("replace")

    def do_remove(self):
        self.run_task("remove")

    def do_suffix(self):
        self.run_task("suffix")

if __name__ == "__main__":
    root = tk.Tk()
    app = TextureRenamerApp(root)
    root.mainloop()