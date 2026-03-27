import os
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

class TextureRenamerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("贴图批量重命名工具 · 增强版")
        self.root.geometry("600x380")
        self.root.resizable(False, False)

        # 变量
        self.folder_path = tk.StringVar()
        self.remove_words = tk.StringVar(value="Head")
        self.suffix = tk.StringVar(value="#0")

        self.create_widgets()

    def create_widgets(self):
        # 标题
        title_label = ttk.Label(self.root, text="贴图批量重命名工具", font=("微软雅黑", 14, "bold"))
        title_label.pack(pady=10)

        # 文件夹选择
        folder_frame = ttk.Frame(self.root)
        folder_frame.pack(fill="x", padx=20, pady=5)
        ttk.Label(folder_frame, text="目标文件夹：").grid(row=0, column=0, sticky="w", padx=5)
        ttk.Entry(folder_frame, textvariable=self.folder_path, width=45).grid(row=0, column=1, padx=5)
        ttk.Button(folder_frame, text="选择文件夹", command=self.select_folder).grid(row=0, column=2)

        # 移除内容
        remove_frame = ttk.LabelFrame(self.root, text="批量移除文字（多个用英文逗号 , 分隔）")
        remove_frame.pack(fill="x", padx=20, pady=8)
        ttk.Label(remove_frame, text="要删除的内容：").grid(row=0, column=0, sticky="w", padx=5, pady=8)
        ttk.Entry(remove_frame, textvariable=self.remove_words, width=40).grid(row=0, column=1, padx=5)
        ttk.Label(remove_frame, text="示例：Head,Body,Test", font=("微软雅黑", 9)).grid(row=1, column=1, sticky="w")

        # 添加后缀
        suffix_frame = ttk.LabelFrame(self.root, text="批量添加后缀")
        suffix_frame.pack(fill="x", padx=20, pady=8)
        ttk.Label(suffix_frame, text="添加后缀：").grid(row=0, column=0, sticky="w", padx=5, pady=8)
        ttk.Entry(suffix_frame, textvariable=self.suffix, width=20).grid(row=0, column=1, padx=5)
        ttk.Label(suffix_frame, text="示例：#0、_1、_L、.new", font=("微软雅黑", 9)).grid(row=1, column=1, sticky="w")

        # 执行按钮
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="开始！", command=self.do_remove, width=15).grid(row=0, column=0, padx=10)
        #ttk.Button(btn_frame, text="仅添加后缀", command=self.do_suffix, width=15)
        #ttk.Button(btn_frame, text="先删后加", command=self.do_both, width=15)

        # 状态
        self.status_label = ttk.Label(self.root, text="准备就绪", foreground="green")
        self.status_label.pack(pady=5)

    def select_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.folder_path.set(path)

    def get_remove_list(self):
        raw = self.remove_words.get().strip()
        return [w.strip() for w in raw.split(",") if w.strip()]

    def process_file(self, folder, filename, remove_list, add_suffix):
        texture_ext = {'.png', '.jpg', '.jpeg', '.tga', '.bmp', '.dds', '.exr', '.hdr'}
        old_path = os.path.join(folder, filename)
        if os.path.isdir(old_path):
            return

        name, ext = os.path.splitext(filename)
        if ext.lower() not in texture_ext:
            return

        # 删除文字
        new_name = name
        for w in remove_list:
            new_name = new_name.replace(w, "")

        # 添加后缀
        if add_suffix:
            sf = self.suffix.get()
            if not new_name.endswith(sf):
                new_name += sf

        new_filename = new_name + ext
        new_path = os.path.join(folder, new_filename)

        if old_path != new_path:
            shutil.move(old_path, new_path)

    def run_task(self, mode):
        folder = self.folder_path.get().strip()
        if not folder or not os.path.isdir(folder):
            messagebox.showerror("错误", "请先选择有效文件夹")
            return

        self.status_label.config(text="处理中...", foreground="blue")
        self.root.update()

        remove_list = self.get_remove_list()

        try:
            for filename in os.listdir(folder):
                if mode == "remove":
                    self.process_file(folder, filename, remove_list, add_suffix=False)
                elif mode == "suffix":
                    self.process_file(folder, filename, [], add_suffix=True)
                elif mode == "both":
                    self.process_file(folder, filename, remove_list, add_suffix=True)

            self.status_label.config(text="处理完成！", foreground="green")
            messagebox.showinfo("完成", "批量重命名已完成")
        except Exception as e:
            self.status_label.config(text="处理失败", foreground="red")
            messagebox.showerror("错误", str(e))

    def do_remove(self):
        self.run_task("remove")

    def do_suffix(self):
        self.run_task("suffix")

    def do_both(self):
        self.run_task("both")

if __name__ == "__main__":
    root = tk.Tk()
    app = TextureRenamerApp(root)
    root.mainloop()