import os
import re
import json
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from datetime import datetime

# 根目录模板文件
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_FILE = os.path.join(ROOT_DIR, "speed_templates.json")

LAYER_PATTERN = re.compile(r'"layerIndex"\s*:\s*(-?\d+)\s*,')
SPEED_PATTERN = re.compile(r'("moveSpeedRateX"\s*:\s*)(\d+\.?\d*)\s*,')

class PrefabSpeedTool:
    def __init__(self, root):
        self.root = root
        self.root.title("游戏场景速度修改工具v1.0")
        self.root.geometry("920x760")
        self.root.resizable(False, False)

        self.target_folder = tk.StringVar()
        self.backup_folder = tk.StringVar()
        self.chapter = tk.StringVar(value="1")
        self.areas = tk.StringVar()

        self.layer_rows = []
        self.templates = self.load_templates()
        self.selected_template = tk.StringVar()

        self.create_widgets()
        self.refresh_template_list()

    # 核心：不存在直接返回空，不创建、不报错
    def load_templates(self):
        if not os.path.exists(TEMPLATE_FILE):
            return {}
        try:
            with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}

    def save_templates(self):
        with open(TEMPLATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.templates, f, ensure_ascii=False, indent=2)

    def save_current_as_template(self):
        configs = self.get_layer_configs()
        if not configs:
            messagebox.showwarning("提示", "没有可保存的层级速度配置")
            return

        window = tk.Toplevel(self.root)
        window.title("保存模板")
        window.geometry("400x150")
        window.resizable(False, False)
        window.grab_set()

        tk.Label(window, text="请输入模板名称：", font=("微软雅黑", 12)).pack(pady=10)
        entry_name = tk.Entry(window, width=30, font=("微软雅黑", 11))
        entry_name.pack(pady=5)
        entry_name.focus()

        def confirm():
            name = entry_name.get().strip()
            if not name:
                messagebox.showwarning("提示", "模板名称不能为空", parent=window)
                return
            self.templates[name] = configs
            self.save_templates()
            self.refresh_template_list()
            self.log(f"✅ 模板已保存：{name}")
            window.destroy()

        tk.Button(window, text="确认保存", command=confirm, bg="#2196F3", fg="white", width=12).pack(pady=10)

    def delete_selected_template(self):
        name = self.selected_template.get()
        if not name or name not in self.templates:
            messagebox.showwarning("提示", "请先选择要删除的模板")
            return
        if messagebox.askyesno("确认删除", f"确定要删除模板：{name}？"):
            del self.templates[name]
            self.save_templates()
            self.refresh_template_list()
            self.selected_template.set("")
            self.log(f"🗑️ 模板已删除：{name}")

    def apply_template(self):
        name = self.selected_template.get()
        if not name or name not in self.templates:
            messagebox.showwarning("提示", "请选择有效的模板")
            return
        data = self.templates[name]
        self.clear_all_rows()
        for layer, speed in data:
            self.add_layer_row(layer, speed)
        self.log(f"📄 已加载模板：{name}")

    def refresh_template_list(self):
        self.cmb_template['values'] = list(self.templates.keys())

    def create_widgets(self):
        tk.Label(self.root, text="目标Prefab文件夹:", font=("微软雅黑", 10)).place(x=20, y=20)
        tk.Entry(self.root, textvariable=self.target_folder, width=78, state="readonly").place(x=150, y=20)
        tk.Button(self.root, text="选择", command=self.select_target, bg="#4CAF50", fg="white").place(x=820, y=15)

        tk.Label(self.root, text="备份保存目录:", font=("微软雅黑", 10)).place(x=20, y=55)
        tk.Entry(self.root, textvariable=self.backup_folder, width=78, state="readonly").place(x=150, y=55)
        tk.Button(self.root, text="选择", command=self.select_backup, bg="#1E90FF", fg="white").place(x=820, y=50)

        group = tk.LabelFrame(self.root, text="批量配置", font=("微软雅黑", 11), width=870, height=100)
        group.place(x=20, y=90)
        tk.Label(group, text="章节:", font=("微软雅黑", 10)).place(x=20, y=20)
        tk.Entry(group, textvariable=self.chapter, width=10).place(x=70, y=20)
        tk.Label(group, text="区域（1,2,3）:", font=("微软雅黑", 10)).place(x=180, y=20)
        tk.Entry(group, textvariable=self.areas, width=20).place(x=290, y=20)

        group_temp = tk.LabelFrame(self.root, text="层级速度模板管理", font=("微软雅黑", 11), width=870, height=100)
        group_temp.place(x=20, y=195)

        tk.Label(group_temp, text="选择模板:", font=("微软雅黑", 10)).place(x=20, y=20)
        self.cmb_template = ttk.Combobox(group_temp, textvariable=self.selected_template, width=22, state="readonly")
        self.cmb_template.place(x=100, y=20)

        tk.Button(group_temp, text="加载模板", command=self.apply_template, width=12).place(x=280, y=18)
        tk.Button(group_temp, text="保存为模板", command=self.save_current_as_template, width=12).place(x=400, y=18)
        tk.Button(group_temp, text="删除模板", command=self.delete_selected_template, width=12).place(x=520, y=18)
        tk.Label(group_temp, fg="green", text="配置好多层级速度后可保存为模板，下次一键加载").place(x=20, y=60)

        layer_container = tk.LabelFrame(self.root, text="层级与速度配置（可滚动）", font=("微软雅黑", 11), width=870, height=220)
        layer_container.place(x=20, y=300)

        self.canvas = tk.Canvas(layer_container, width=820, height=180)
        self.scroll_y = ttk.Scrollbar(layer_container, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = ttk.Frame(self.canvas)
        self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scroll_y.set)
        self.canvas.place(x=10, y=10, width=800, height=180)
        self.scroll_y.place(x=810, y=10, width=20, height=180)

        ttk.Label(self.scroll_frame, text="层级 layerIndex", font=("微软雅黑", 10, "bold")).grid(row=0, column=0, padx=40, pady=5)
        ttk.Label(self.scroll_frame, text="X速度 moveSpeedRateX", font=("微软雅黑", 10, "bold")).grid(row=0, column=1, padx=40, pady=5)

        tk.Button(self.root, text="+ 添加一行", command=self.add_layer_row, width=14).place(x=700, y=305)
        tk.Button(self.root, text="- 删除最后一行", command=self.remove_layer_row, width=14).place(x=740, y=340)

        tk.Button(self.root, text="开始批量修改", command=self.start_modify, bg="#2196F3", fg="white",
                  width=24, height=2, font=("微软雅黑", 12, "bold")).place(x=200, y=540)
        tk.Button(self.root, text="从原始备份还原", command=self.restore_backup, bg="#f44336", fg="white",
                  width=24, height=2, font=("微软雅黑", 12, "bold")).place(x=500, y=540)

        tk.Label(self.root, text="执行日志:", font=("微软雅黑", 10)).place(x=20, y=610)
        self.log_text = scrolledtext.ScrolledText(self.root, width=112, height=12, font=("微软雅黑", 9))
        self.log_text.place(x=20, y=640)

        self.add_layer_row("-5", "0.25")
        self.log("工具启动成功 ✅ 模板功能正常使用")

    def log(self, msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {msg}\n")
        self.log_text.see(tk.END)
        self.root.update()

    def select_target(self):
        path = filedialog.askdirectory(title="选择目标Prefab目录")
        if path:
            self.target_folder.set(path)
            self.log(f"目标目录：{path}")

    def select_backup(self):
        tgt = self.target_folder.get().strip()
        path = filedialog.askdirectory(title="选择独立备份目录")
        if not path:
            return
        if os.path.normpath(path) == os.path.normpath(tgt):
            messagebox.showerror("错误", "备份目录不能与目标目录相同！")
            return
        self.backup_folder.set(path)
        self.log(f"备份目录：{path}")

    def add_layer_row(self, layer="-5", speed="0.25"):
        row_idx = len(self.layer_rows) + 1
        e1 = ttk.Entry(self.scroll_frame, width=20)
        e2 = ttk.Entry(self.scroll_frame, width=22)
        e1.grid(row=row_idx, column=0, padx=20, pady=6)
        e2.grid(row=row_idx, column=1, padx=20, pady=6)
        e1.insert(0, layer)
        e2.insert(0, speed)
        self.layer_rows.append((e1, e2))

    def remove_layer_row(self):
        if len(self.layer_rows) <= 1:
            messagebox.showwarning("提示", "至少保留一行配置")
            return
        e1, e2 = self.layer_rows.pop()
        e1.destroy()
        e2.destroy()

    def clear_all_rows(self):
        while self.layer_rows:
            e1, e2 = self.layer_rows.pop()
            e1.destroy()
            e2.destroy()

    def get_layer_configs(self):
        configs = []
        for e_lay, e_sp in self.layer_rows:
            l = e_lay.get().strip()
            s = e_sp.get().strip()
            if not l or not s:
                continue
            try:
                float(s)
                configs.append([l, s])
            except ValueError:
                continue
        return configs

    def parse_areas(self):
        s = self.areas.get().strip()
        return [a.strip() for a in s.split(",") if a.strip().isdigit()]

    def backup_original(self, src):
        try:
            target_root = self.target_folder.get()
            backup_root = self.backup_folder.get()
            rel = os.path.relpath(src, target_root)
            bak_path = os.path.join(backup_root, rel)
            if os.path.exists(bak_path):
                return True
            os.makedirs(os.path.dirname(bak_path), exist_ok=True)
            shutil.copy2(src, bak_path)
            return True
        except Exception:
            return False

    def modify_file(self, path, configs):
        try:
            self.backup_original(path)
            with open(path, "r", encoding="utf-8") as f:
                lines = f.read().splitlines()

            new_lines = []
            layer_map = dict(configs)
            current_layer = None

            for line in lines:
                layer_match = LAYER_PATTERN.search(line)
                if layer_match:
                    current_layer = layer_match.group(1)
                if current_layer in layer_map:
                    line = SPEED_PATTERN.sub(rf"\g<1>{layer_map[current_layer]},", line)
                new_lines.append(line)

            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write("\n".join(new_lines))
            return True
        except Exception as e:
            self.log(f"修改失败：{str(e)}")
            return False

    def start_modify(self):
        target = self.target_folder.get().strip()
        backup = self.backup_folder.get().strip()
        chapter = self.chapter.get().strip()
        areas = self.parse_areas()
        configs = self.get_layer_configs()

        if not target or not backup:
            messagebox.showerror("错误", "请选择目标目录和备份目录")
            return
        if os.path.normpath(target) == os.path.normpath(backup):
            messagebox.showerror("错误", "目录不能相同")
            return
        if not chapter or not areas:
            messagebox.showerror("错误", "请填写章节和区域")
            return
        if not configs:
            messagebox.showerror("错误", "请填写至少一组层级+速度")
            return

        tips = "\n".join([f"层级{a} → 速度{b}" for a,b in configs])
        if not messagebox.askyesno("确认修改", f"章节：{chapter}\n区域：{areas}\n\n修改内容：\n{tips}"):
            return

        self.log("="*70)
        self.log("开始批量修改...")
        count, total = 0, 0
        for root_dir, _, files in os.walk(target):
            for f in files:
                if not f.endswith(".prefab"):
                    continue
                if not f.startswith(f"adventure-{chapter}-"):
                    continue
                area_part = f.replace(f"adventure-{chapter}-", "").split("-",1)[0]
                if area_part not in areas:
                    continue
                path = os.path.join(root_dir, f)
                total +=1
                if self.modify_file(path, configs):
                    count +=1
                    self.log(f"✅ {f}")
        self.log(f"修改完成：成功 {count}/{total}")
        self.log("="*70)
        messagebox.showinfo("完成", f"批量修改完成！\n成功：{count} 个文件")

    def restore_backup(self):
        target = self.target_folder.get().strip()
        backup = self.backup_folder.get().strip()
        if not target or not backup or not os.path.exists(backup):
            messagebox.showerror("错误", "目录无效")
            return
        if not messagebox.askyesno("确认还原", "确定还原为最原始版本？当前修改会被覆盖！"):
            return
        self.log("开始还原备份...")
        count = 0
        for b_root, _, files in os.walk(backup):
            for f in files:
                if f.endswith(".prefab"):
                    b_file = os.path.join(b_root, f)
                    rel = os.path.relpath(b_file, backup)
                    t_file = os.path.join(target, rel)
                    try:
                        shutil.copy2(b_file, t_file)
                        count +=1
                        self.log(f"还原：{rel}")
                    except:
                        self.log(f"失败：{rel}")
        self.log(f"还原完成：{count} 个文件")
        messagebox.showinfo("完成", f"还原成功：{count} 个文件")

if __name__ == "__main__":
    root = tk.Tk()
    app = PrefabSpeedTool(root)
    root.mainloop()