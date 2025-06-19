import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
from colorama import init
from production_optimizer import ProductionOptimizer

init(autoreset=True)

def run_gui():
    def show_simplex_tableaux(optimizer):
        """вікно з симплекс-таблицями"""
        simplex_window = tk.Toplevel(window)
        simplex_window.title("Симплекс-таблиці")
        simplex_window.geometry("1000x700")

        tableaux = optimizer.get_simplex_tableaux()
        if not tableaux:
            messagebox.showwarning("капець", "Симплекс-таблиці недоступні")
            return

        notebook = ttk.Notebook(simplex_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        for tableau_data in tableaux:
            frame = ttk.Frame(notebook)
            notebook.add(frame, text=f"Ітерація {tableau_data['iteration']}")

            title = tk.Label(frame, text=tableau_data['description'],
                             font=("Arial", 12, "bold"), fg="blue")
            title.pack(pady=10)

            canvas = tk.Canvas(frame)
            scrollbar_v = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
            scrollbar_h = ttk.Scrollbar(frame, orient="horizontal", command=canvas.xview)
            scrollable_frame = ttk.Frame(canvas)

            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)

            tableau = tableau_data['tableau']
            basic_vars = tableau_data['basic_vars']

            headers = ['Базис'] + [f'x{i + 1}' for i in range(5)] + ['s1', 's2', 's3', 's4'] + ['Б']

            tree = ttk.Treeview(scrollable_frame, columns=headers[1:], show="tree headings", height=8)
            tree.heading("#0", text="Базис")
            tree.column("#0", width=80, anchor="center")

            for i, header in enumerate(headers[1:]):
                tree.heading(f"#{i + 1}", text=header)
                tree.column(f"#{i + 1}", width=80, anchor="center")

            resource_names = ["Сировина", "Електроенергія", "Накладні витрати", "Зарплата"]

            for i in range(len(tableau) - 1):
                if i < len(basic_vars):
                    if basic_vars[i] < 5:
                        basis_name = f"x{basic_vars[i] + 1}"
                    else:
                        basis_name = resource_names[basic_vars[i] - 5] if basic_vars[i] - 5 < len(
                            resource_names) else f"s{basic_vars[i] - 4}"
                else:
                    basis_name = f"s{i + 1}"

                values = [f"{val:.2f}" for val in tableau[i]]
                tree.insert("", "end", text=basis_name, values=values)
            f_values = [f"{val:.2f}" for val in tableau[-1]]
            tree.insert("", "end", text="F", values=f_values)

            tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            canvas.pack(side="left", fill="both", expand=True)
            scrollbar_v.pack(side="right", fill="y")
            scrollbar_h.pack(side="bottom", fill="x")

    def show_results_window(optimizer):

        results_window = tk.Toplevel(window)
        results_window.title("Результати оптимізації")
        results_window.geometry("800x600")

        notebook = ttk.Notebook(results_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        frame1 = ttk.Frame(notebook)
        notebook.add(frame1, text="План виробництва")

        title_label1 = tk.Label(frame1, text=f"ЗАГАЛЬНИЙ ВИПУСК: {optimizer.optimal_value:.2f} одиниць",
                                font=("Arial", 14, "bold"), fg="green")
        title_label1.pack(pady=10)

        # Таблиця плану виробництва
        tree1 = ttk.Treeview(frame1, columns=("tech", "time", "output"), show="headings", height=8)
        tree1.heading("tech", text="Технологія")
        tree1.heading("time", text="Час роботи (год)")
        tree1.heading("output", text="Випуск (од.)")

        tree1.column("tech", width=150, anchor="center")
        tree1.column("time", width=200, anchor="center")
        tree1.column("output", width=200, anchor="center")

        production_data = optimizer.get_production_data()
        for row in production_data:
            tree1.insert("", tk.END, values=row)

        tree1.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        frame2 = ttk.Frame(notebook)
        notebook.add(frame2, text="Ресурси")

        title_label2 = tk.Label(frame2, text="АНАЛІЗ ВИКОРИСТАННЯ РЕСУРСІВ",
                                font=("Arial", 14, "bold"), fg="blue")
        title_label2.pack(pady=10)

        tree2 = ttk.Treeview(frame2, columns=("resource", "used", "limit", "percent", "status"),
                             show="headings", height=8)
        tree2.heading("resource", text="Ресурс")
        tree2.heading("used", text="Використано")
        tree2.heading("limit", text="Ліміт")
        tree2.heading("percent", text="Використання %")
        tree2.heading("status", text="Статус")

        tree2.column("resource", width=150, anchor="center")
        tree2.column("used", width=120, anchor="center")
        tree2.column("limit", width=120, anchor="center")
        tree2.column("percent", width=130, anchor="center")
        tree2.column("status", width=130, anchor="center")

        resource_data = optimizer.get_resource_data()
        for i, row in enumerate(resource_data):
            if "ЛІМІТУЮЧИЙ" in row[4]:
                tree2.insert("", tk.END, values=row, tags=("critical",))
            else:
                tree2.insert("", tk.END, values=row, tags=("normal",))

        tree2.tag_configure("critical", background="#ffcccc")
        tree2.tag_configure("normal", background="#ccffcc")

        tree2.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        button_frame = tk.Frame(results_window)
        button_frame.pack(pady=10)

        btn_graphs = tk.Button(button_frame, text="Показати графіки",
                               command=optimizer.create_visualization,
                               bg="lightblue", font=("Arial", 11, "bold"))
        btn_graphs.pack(side=tk.LEFT, padx=5)

        btn_simplex = tk.Button(button_frame, text="Симплекс-таблиці",
                                command=lambda: show_simplex_tableaux(optimizer),
                                bg="lightyellow", font=("Arial", 11, "bold"))
        btn_simplex.pack(side=tk.LEFT, padx=5)

    def run_optimization():
        try:
            prod_rates = list(map(float, entry_prod.get().split(',')))
            res_constraints = list(map(float, entry_res.get().split(',')))
            norms_rows = text_norms.get("1.0", tk.END).strip().split('\n')
            norms_matrix = [list(map(float, row.split(','))) for row in norms_rows]

            optimizer = ProductionOptimizer(prod_rates, res_constraints, norms_matrix)

            if optimizer.solve_optimization():
                optimizer.analyze_results()  # Виведе в консоль
                show_results_window(optimizer)  # Покаже таблиці в GUI
                messagebox.showinfo("Успіх", "Обчислення завершено успішно! Відкрито вікно з результатами.")
            else:
                messagebox.showerror("Помилка", "Задача не має розв'язку.")
        except Exception as e:
            messagebox.showerror("Помилка вводу", f"Перевір правильність введених даних:\n{e}")

    window = tk.Tk()
    window.title("Оптимізація виробництва")
    window.geometry("700x550")

    title = tk.Label(window, text="СИСТЕМА ОПТИМІЗАЦІЇ ВИРОБНИЦТВА",
                     font=("Arial", 16, "bold"), fg="darkblue")
    title.pack(pady=10)
    input_frame = tk.Frame(window, relief=tk.RIDGE, bd=2)
    input_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

    tk.Label(input_frame, text="Продуктивність технологій (через кому):",
             font=("Arial", 11, "bold")).pack(pady=(10, 5))
    entry_prod = tk.Entry(input_frame, width=60, font=("Arial", 10))
    entry_prod.insert(0, "300,260,320,400,450")
    entry_prod.pack(pady=5)

    tk.Label(input_frame, text="Обмеження ресурсів (через кому):",
             font=("Arial", 11, "bold")).pack(pady=(15, 5))
    entry_res = tk.Entry(input_frame, width=60, font=("Arial", 10))
    entry_res.insert(0, "2000,300,1000,1600")
    entry_res.pack(pady=5)

    tk.Label(input_frame, text="Норми споживання ресурсів (кожен рядок = новий ресурс):",
             font=("Arial", 11, "bold")).pack(pady=(15, 5))
    text_norms = scrolledtext.ScrolledText(input_frame, width=60, height=6, font=("Arial", 10))
    text_norms.insert(tk.END, "15,20,12,14,18\n0.2,0.3,0.15,0.25,0.3\n4,5,6,3,2\n5,3,4,6,3")
    text_norms.pack(pady=5, padx=10)

    tk.Button(window, text="РОЗВ'ЯЗАТИ ЗАДАЧУ ОПТИМІЗАЦІЇ", command=run_optimization,
              bg="mediumseagreen", fg="white", font=("Arial", 14, "bold"),
              height=2).pack(pady=20)

    info_label = tk.Label(window,
                          text="💡 Результати будуть показані у новому вікні з таблицями, графіками та симплекс-таблицями",
                          font=("Arial", 10), fg="gray")
    info_label.pack(pady=5)

    window.mainloop()


if __name__ == "__main__":
    run_gui()