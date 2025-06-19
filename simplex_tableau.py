import numpy as np

class SimplexTableau:
    def __init__(self, c, A, b):
        self.c = np.array(c)
        self.A = np.array(A)
        self.b = np.array(b)
        self.tableau_history = []
        self.basic_vars = []
        self.iteration = 0

    def solve_with_tableaux(self):
        """Розв'язує задачу симплекс-методом з записом кожної таблиці"""
        m, n = self.A.shape

        tableau = np.zeros((m + 1, n + m + 1))

        tableau[:-1, :n] = self.A
        tableau[:-1, n:n + m] = np.eye(m)  # Одинична матриця для slack змінних
        tableau[:-1, -1] = self.b
        tableau[-1, :n] = self.c

        # Базисні змінні (спочатку slack змінні)
        basic_vars = list(range(n, n + m))

        self.tableau_history.append({
            'iteration': 0,
            'tableau': tableau.copy(),
            'basic_vars': basic_vars.copy(),
            'description': 'Початкова симплекс-таблиця'
        })

        iteration = 1
        while True:
            if all(tableau[-1, j] >= 0 for j in range(n + m)):
                break

            entering_col = np.argmin(tableau[-1, :n + m])

            ratios = []
            for i in range(m):
                if tableau[i, entering_col] > 0:
                    ratios.append(tableau[i, -1] / tableau[i, entering_col])
                else:
                    ratios.append(float('inf'))

            if all(r == float('inf') for r in ratios):
                break

            leaving_row = np.argmin(ratios)

            # Оновлюємо базисні змінні
            basic_vars[leaving_row] = entering_col

            # Виконуємо операції Гауса
            pivot = tableau[leaving_row, entering_col]
            tableau[leaving_row, :] /= pivot

            for i in range(m + 1):
                if i != leaving_row:
                    factor = tableau[i, entering_col]
                    tableau[i, :] -= factor * tableau[leaving_row, :]

            self.tableau_history.append({
                'iteration': iteration,
                'tableau': tableau.copy(),
                'basic_vars': basic_vars.copy(),
                'description': f'Ітерація {iteration}: x{entering_col + 1} входить, x{basic_vars[leaving_row] + 1} виходить'
            })

            iteration += 1

            if iteration > 20:
                break

        solution = np.zeros(n)
        for i, var in enumerate(basic_vars):
            if var < n:
                solution[var] = tableau[i, -1]

        optimal_value = -tableau[-1, -1] if len(self.tableau_history) > 0 else 0

        return solution, optimal_value