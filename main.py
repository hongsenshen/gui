import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
import tkinter as tk
from tkinter import ttk as tkinter_ttk


class QueryClientApp:
    def __init__(self):
        self.root = ttk.Window(themename="flatly")  # 使用flatly主题
        self.root.title("信息查询客户端")
        self.current_user = None
        self.setup_login_window()

    def setup_login_window(self):
        """设置登录窗口"""
        # 固定窗口大小并禁用最大化
        self.root.geometry("800x600")
        self.root.resizable(False, False)

        # 创建登录框架
        login_frame = ttk.Frame(self.root, padding=20)
        login_frame.pack(expand=True)

        # 标题
        ttk.Label(login_frame, text="信息查询系统", font=("微软雅黑", 20, "bold")).pack(pady=20)

        # 表单容器
        form_frame = ttk.Frame(login_frame)
        form_frame.pack(expand=True)

        # 用户名行
        user_row = ttk.Frame(form_frame)
        user_row.pack(pady=10, fill=X)
        ttk.Label(user_row, text="用户名:", width=8).pack(side=LEFT)
        self.username_entry = ttk.Entry(user_row)
        self.username_entry.pack(side=LEFT, expand=True, fill=X)

        # 密码行
        pwd_row = ttk.Frame(form_frame)
        pwd_row.pack(pady=10, fill=X)
        ttk.Label(pwd_row, text="密　码:", width=8).pack(side=LEFT)
        self.password_entry = ttk.Entry(pwd_row, show="*")
        self.password_entry.pack(side=LEFT, expand=True, fill=X)

        # 登录按钮
        ttk.Button(form_frame, text="登　录",
                   command=self.login,
                   style="success.TButton",
                   width=12).pack(pady=20)

    def login(self):
        """处理登录逻辑"""
        username = self.username_entry.get()
        password = self.password_entry.get()
        # 这里应该有真正的登录验证，这里简单示例
        if username and password:
            self.current_user = username
            self.show_main_window()
        else:
            Messagebox.show_error("请输入用户名和密码", "登录失败")

    def show_main_window(self):
        """显示主窗口"""
        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.geometry("1600x1200")
        self.root.resizable(True, True)

        # 创建主框架
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=BOTH, expand=True)

        # 用户信息和退出登录
        user_frame = ttk.Frame(self.main_frame)
        user_frame.pack(side=TOP, fill=X, padx=10, pady=5)
        self.user_menu = ttk.Menubutton(user_frame, text=f"欢迎, {self.current_user}")
        self.user_menu.pack(side=RIGHT)
        menu = ttk.Menu(self.user_menu)
        menu.add_command(label="退出登录", command=self.logout)
        self.user_menu.configure(menu=menu)

        # 按钮框架
        btn_frame = ttk.Frame(self.main_frame)
        btn_frame.pack(fill=X, padx=10, pady=10)
        ttk.Button(btn_frame, text="CPU名称查询", command=self.show_cpu_name_query, style="primary.TButton").pack(side=LEFT, padx=5)
        ttk.Button(btn_frame, text="CPU规格参数查询", command=self.show_cpu_spec_query, style="primary.TButton").pack(side=LEFT, padx=5)

        # 内容框架
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        self.show_cpu_name_query()  # 默认显示CPU名称查询

    def create_query_page(self, fields, table_headers):
        """创建带对比功能的查询页面"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # ======================
        # 左侧搜索和结果区域
        # ======================
        left_frame = ttk.Frame(self.content_frame)
        left_frame.pack(side=LEFT, fill=BOTH, padx=5, pady=5)

        # 搜索条件框架
        search_frame = ttk.LabelFrame(left_frame, text="搜索条件", padding=15)
        search_frame.pack(fill=X)

        # 搜索表单组件
        self.search_vars = {}
        for row, (field, field_type) in enumerate(fields.items()):
            ttk.Label(search_frame, text=f"{field}：", anchor="e").grid(row=row, column=0, padx=5, pady=8, sticky="ew")
            if field_type == "entry":
                var = tk.StringVar()
                entry = ttk.Entry(search_frame, textvariable=var)
                entry.grid(row=row, column=1, padx=5, pady=5, sticky="ew")
                self.search_vars[field] = var

            elif field_type == "combo":
                var = tk.StringVar()
                combo = ttk.Combobox(search_frame, textvariable=var,
                                     values=["选项1", "选项2", "选项3"], state="readonly")
                combo.grid(row=row, column=1, padx=5, pady=5, sticky="ew")
                combo.current(0)
                self.search_vars[field] = var

            elif field_type == "radio":
                var = tk.StringVar(value="是")
                radio_frame = ttk.Frame(search_frame)
                radio_frame.grid(row=row, column=1, padx=5, pady=5, sticky="w")
                for option in ["是", "否"]:
                    ttk.Radiobutton(radio_frame, text=option, value=option,
                                    variable=var).pack(side=LEFT, padx=5)
                self.search_vars[field] = var

            elif field_type == "check":
                var = tk.BooleanVar()
                check = ttk.Checkbutton(search_frame, text="启用", variable=var,
                                        bootstyle="round-toggle")
                check.grid(row=row, column=1, padx=5, pady=5, sticky="w")
                self.search_vars[field] = var
            # 各类型表单项（代码同原create_query_page）
            # [此处保留原有的表单项创建逻辑]

        ttk.Button(search_frame, text="查　询",
                   command=self.perform_search,
                   style="success.TButton").grid(row=len(fields) + 1, columnspan=2, pady=15)

        # 查询结果容器
        result_container = ttk.Frame(left_frame)
        result_container.pack(fill=BOTH, expand=True)

        # ======================
        # 右侧对比区域
        # ======================
        compare_container = ttk.Frame(self.content_frame)
        compare_container.pack(side=RIGHT, expand=True, fill=BOTH, padx=5, pady=5)

        # 固定列容器（制造商、核心数）
        fixed_frame = ttk.Frame(compare_container, width=150)
        fixed_frame.pack(side=LEFT, fill=Y)

        # 固定列标题
        ttk.Label(fixed_frame, text="型号", style="primary.TLabel").pack(pady=5)
        ttk.Label(fixed_frame, text="制造商", style="primary.TLabel").pack(pady=5)
        ttk.Label(fixed_frame, text="核心数", style="primary.TLabel").pack(pady=5)

        # 滚动区域容器
        scroll_frame = ttk.Frame(compare_container)
        scroll_frame.pack(side=LEFT, expand=True, fill=BOTH)

        # 创建画布和滚动条
        self.compare_canvas = tk.Canvas(scroll_frame, highlightthickness=0)
        scroll_x = ttk.Scrollbar(scroll_frame, orient=HORIZONTAL, command=self.compare_canvas.xview)
        self.compare_canvas.configure(xscrollcommand=scroll_x.set)

        # 内部框架
        self.compare_inner_frame = ttk.Frame(self.compare_canvas)
        self.compare_canvas.create_window((0, 0), window=self.compare_inner_frame, anchor="nw")

        # 布局
        scroll_x.pack(side=BOTTOM, fill=X)
        self.compare_canvas.pack(side=TOP, expand=True, fill=BOTH)

        # 存储固定列和滚动区域的组件
        # 固定列容器（型号、制造商、核心数）
        fixed_frame = ttk.Frame(compare_container, width=150)
        fixed_frame.pack(side=LEFT, fill=Y)

        # 固定列标题（使用table_headers的前三个字段）
        self.fixed_headers = table_headers # 获取前三个字段作为固定列
        for header in self.fixed_headers:
            ttk.Label(fixed_frame,
                      text=header,
                      style="primary.TLabel",
                      anchor="center",
                      padding=5).pack(fill=X, pady=5)

        # # 结果列表容器（带垂直滚动）
        # result_canvas = tk.Canvas(result_container, highlightthickness=0)
        # result_scroll = ttk.Scrollbar(result_container, command=result_canvas.yview)
        # result_canvas.configure(yscrollcommand=result_scroll.set)

        # 结果内部框架
        # self.result_inner_frame = ttk.Frame(result_canvas)
        # result_canvas.create_window((0, 0), window=self.result_inner_frame, anchor="nw")

        # 布局
        # result_scroll.pack(side=RIGHT, fill=Y)
        # result_canvas.pack(side=LEFT, expand=True, fill=BOTH)

        # 绑定配置事件
        # self.result_inner_frame.bind("<Configure>",
        #                              lambda e: result_canvas.configure(scrollregion=result_canvas.bbox("all")))
        # self.compare_inner_frame.bind("<Configure>",
        #                               lambda e: self.compare_canvas.configure(
        #                                   scrollregion=self.compare_canvas.bbox("all")))

    def perform_search(self):
        """执行查询并自动添加所有结果到对比"""
        # 清空现有对比项
        for widget in self.compare_inner_frame.winfo_children():
            widget.destroy()

        # 生成示例数据
        sample_data = [
            {"型号": "i9-13900K", "制造商": "Intel", "核心数": "24", "频率": "5.8GHz"},
            {"型号": "Ryzen 9 7950X", "制造商": "AMD", "核心数": "16", "频率": "5.7GHz"},
            {"型号": "Xeon W-3375", "制造商": "Intel", "核心数": "38", "频率": "4.0GHz"}
        ]

        # 自动添加所有结果到对比
        for data in sample_data:
            self.add_to_compare(data)

        # 更新滚动区域
        self.compare_inner_frame.update_idletasks()
        self.compare_canvas.configure(scrollregion=self.compare_canvas.bbox("all"))

    # def add_to_compare(self, item_data):
    #     """添加项目到对比列表（优化样式）"""
    #     # 创建对比卡片
    #     card = ttk.Frame(self.compare_inner_frame,
    #                      padding=15,
    #                      width=180)  # 固定卡片宽度
    #     card.pack(side=LEFT, fill=Y, padx=5, pady=5, ipady=10)
    #
    #     # 卡片内容
    #     ttk.Label(card, text=item_data["型号"],
    #               font=("微软雅黑", 10, "bold"),
    #               wraplength=150).pack(pady=5)
    #     ttk.Separator(card).pack(fill=X, pady=5)
    #
    #     # 动态生成参数项
    #     for key in ["制造商", "核心数", "频率"]:
    #         row = ttk.Frame(card)
    #         row.pack(fill=X, pady=2)
    #         ttk.Label(row, text=f"{key}:", width=8, style="secondary.TLabel").pack(side=LEFT)
    #         ttk.Label(row, text=item_data[key]).pack(side=LEFT)
    #
    #     # 移除按钮
    #     ttk.Button(card, text="移除",
    #                style="danger.TButton",
    #                command=lambda c=card: c.destroy()).pack(pady=8)
    def add_to_compare(self, item_data):
        """添加项目到对比列表（优化对齐版）"""
        # 创建对比卡片
        card = ttk.Frame(self.compare_inner_frame,
                         padding=(15, 5),
                         width=180,
                         style="info.TFrame")
        card.pack(side=LEFT, fill=Y, padx=5, pady=5)

        # 显示固定字段的值（与左侧标签对齐）
        for header in self.fixed_headers:
            value = item_data.get(header, "N/A")
            lbl = ttk.Label(card,
                            text=value,
                            font=("微软雅黑", 9),
                            anchor="center",
                            width=15)
            lbl.pack(fill=X, pady=4)

        # 显示其他参数（带滚动条的部分）
        ttk.Separator(card).pack(fill=X, pady=5)
        other_params = [k for k in item_data if k not in self.fixed_headers]

        for param in other_params:
            row = ttk.Frame(card)
            row.pack(fill=X, pady=2)
            ttk.Label(row,
                      text=f"{param}:",
                      width=8,
                      style="secondary.TLabel").pack(side=LEFT)
            ttk.Label(row,
                      text=item_data[param],
                      width=6).pack(side=RIGHT)

        # 移除按钮
        ttk.Button(card,
                   text="移除",
                   style="danger.Outline.TButton",
                   command=lambda c=card: c.destroy()).pack(pady=8)

    def show_cpu_name_query(self):
        """显示CPU名称查询页面"""
        fields = {
            "CPU型号": "entry",
            "制造商": "combo",
            "是否超频": "radio",
            "包含参数": "check"
        }
        headers = ["型号", "制造商", "核心数", "频率"]
        self.create_query_page(fields, headers)

    def show_cpu_spec_query(self):
        """显示CPU规格参数查询页面"""
        fields = {
            "核心数": "entry",
            "线程数": "entry",
            "制程": "combo",
            "是否支持超线程": "radio"
        }
        headers = ["核心数", "线程数", "缓存", "TDP"]
        self.create_query_page(fields, headers)

    def logout(self):
        """退出登录"""
        self.current_user = None
        # 重置窗口属性和状态
        # self.root.withdraw()  # 隐藏当前窗口
        self.root.state('normal')  # 重置窗口状态
        # self.root.resizable(False, False)  # 禁用调整大小

        for widget in self.root.winfo_children():
            widget.destroy()

        # self.root.deiconify()
        self.setup_login_window()



    def run(self):
        """运行应用"""
        self.root.mainloop()


if __name__ == "__main__":
    app = QueryClientApp()
    app.run()
