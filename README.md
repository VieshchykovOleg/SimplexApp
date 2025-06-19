SimplexApp is a Python application for solving linear programming problems using the simplex method. It’s designed for users who want to find the optimal way to allocate limited resources—like time, labor, or raw materials—across different production tasks.

The app uses SciPy’s `linprog` to find optimal solutions numerically, and it also includes a custom implementation of the simplex method from scratch, which records and shows each step of the algorithm as a simplex tableau.

In addition, SimplexApp provides a graphical user interface (GUI) built with Tkinter, allowing users to easily input data like productivity rates, resource limits, and consumption coefficients. The results are presented both as text and visual graphs using Matplotlib and Seaborn. This makes it easier to follow how the solution evolves and understand the logic behind it.

The app is useful for educational purposes, operational research, production planning, or anyone learning linear optimization in practice.
