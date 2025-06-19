import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.optimize import linprog
from colorama import Fore, Style
from simplex_tableau import SimplexTableau

sns.set(style="whitegrid")

class ProductionOptimizer:
    def __init__(self, productivity_rates, resource_constraints, consumption_norms):
        self.productivity = np.array(productivity_rates)
        self.constraints = np.array(resource_constraints)
        self.consumption = np.array(consumption_norms)
        self.solution = None
        self.optimal_value = None
        self.simplex_solver = None

    def solve_optimization(self):
        c = -self.productivity
        result = linprog(
            c=c,
            A_ub=self.consumption,
            b_ub=self.constraints,
            method='highs',
            options={"disp": False}
        )
        self.simplex_solver = SimplexTableau(c, self.consumption, self.constraints)
        simplex_solution, simplex_optimal = self.simplex_solver.solve_with_tableaux()

        if result.success:
            self.solution = result.x
            self.optimal_value = -result.fun
            return True
        else:
            print(Fore.RED + "Задача не має розв'язку або розв'язок не знайдено")
            return False

    def get_production_data(self):
        """Повертає дані плану виробництва у вигляді списку для таблиці"""
        if self.solution is None:
            return []

        data = []
        for i, time in enumerate(self.solution):
            if time > 0.001:
                prod = time * self.productivity[i]
                data.append((f'Т{i + 1}', f'{time:.2f}', f'{prod:.2f}'))
        return data

    def get_resource_data(self):
        """Повертає дані використання ресурсів у вигляді списку для таблиці"""
        if self.solution is None:
            return []

        resource_names = ["Сировина", "Електроенергія", "Накладні витрати", "Зарплата"]
        data = []
        for i, (name, limit) in enumerate(zip(resource_names, self.constraints)):
            used = np.dot(self.consumption[i], self.solution)
            utilization = (used / limit) * 100
            status = "ЛІМІТУЮЧИЙ!" if utilization >= 99 else "Норма"
            data.append((name, f'{used:.2f}', f'{limit}', f'{utilization:.1f}%', status))
        return data

    def get_simplex_tableaux(self):
        """Повертає історію симплекс-таблиць"""
        if self.simplex_solver is None:
            return []
        return self.simplex_solver.tableau_history

    def analyze_results(self):
        if self.solution is None:
            print(Fore.RED + "Спочатку розв'яжіть задачу!")
            return

        print(Fore.CYAN + "=" * 65)
        print(Fore.GREEN + Style.BRIGHT + "РЕЗУЛЬТАТИ ОПТИМІЗАЦІЇ ВИРОБНИЦТВА".center(65))
        print(Fore.CYAN + "=" * 65)

        print(Fore.YELLOW + "\n 1. ОПТИМАЛЬНИЙ ПЛАН ВИРОБНИЦТВА:")
        print(Fore.YELLOW + "-" * 65)

        data = []
        for i, time in enumerate(self.solution):
            if time > 0.001:
                prod = time * self.productivity[i]
                data.append([f'Т{i + 1}', f'{time:.2f}', f'{prod:.2f}'])

        df = pd.DataFrame(data, columns=["Технологія", "Час роботи (год)", "Випуск (од.)"])
        print(Fore.WHITE + Style.BRIGHT + df.to_string(index=False))
        print(Fore.GREEN + f"\nЗАГАЛЬНИЙ ВИПУСК: {self.optimal_value:.2f} одиниць")

        print(Fore.YELLOW + "\n2. АНАЛІЗ ВИКОРИСТАННЯ РЕСУРСІВ:")
        print(Fore.YELLOW + "-" * 65)

        resource_names = ["Сировина", "Електроенергія", "Накладні витрати", "Зарплата"]
        for i, (name, limit) in enumerate(zip(resource_names, self.constraints)):
            used = np.dot(self.consumption[i], self.solution)
            utilization = (used / limit) * 100
            status = f"{Fore.RED}ЛІМІТУЮЧИЙ!" if utilization >= 99 else f"{Fore.GREEN}✅ Норма"
            print(f"{Fore.BLUE}{name:<20}: {used:6.2f} / {limit:<6} ({utilization:5.1f}%) {status}")

    def create_visualization(self):
        if self.solution is None:
            return

        sns.set(style="whitegrid")
        fig, axes = plt.subplots(1, 2, figsize=(16, 7))

        technologies = [f'T{i + 1}' for i in range(len(self.solution))]
        palette1 = sns.color_palette("Blues", len(self.solution))

        sns.barplot(x=technologies, y=self.solution, ax=axes[0], hue=technologies, palette=palette1, legend=False)
        axes[0].set_title('Розподіл часу роботи технологій', fontsize=14)
        axes[0].set_ylabel('Години')
        axes[0].set_xlabel('Технології')

        for i, value in enumerate(self.solution):
            axes[0].text(i, value + 0.05 * max(self.solution), f'{value:.2f}', ha='center', fontsize=10)

        resource_names = ["Сировина", "Електроенергія", "Накладні витрати", "Зарплата"]
        used_resources = [np.dot(self.consumption[i], self.solution) for i in range(len(self.constraints))]
        utilization = [(used / limit) * 100 for used, limit in zip(used_resources, self.constraints)]
        palette2 = ['crimson' if u >= 99 else 'mediumseagreen' for u in utilization]

        sns.barplot(x=resource_names, y=utilization, ax=axes[1], hue=resource_names, palette=palette2, legend=False)
        axes[1].set_title('Використання ресурсів (%)', fontsize=14)
        axes[1].set_ylabel('% використання')
        axes[1].set_ylim(0, 110)

        for i, u in enumerate(utilization):
            axes[1].text(i, u + 1.5, f'{u:.1f}%', ha='center', fontsize=10)

        plt.suptitle('Візуалізація результатів оптимізації', fontsize=16, weight='bold')
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        plt.show()