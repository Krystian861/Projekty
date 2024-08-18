import re
from sympy import symbols, sympify
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class MathFormula(models.Model):
    name = models.CharField(max_length=100)
    formula = models.TextField(help_text='Comma-separated formulas')
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='formulas')
    variables = models.CharField(max_length=100, help_text='Comma-separated variable names')

    def evaluate(self, **kwargs):
        try:
            variables = symbols(self.variables.split(','))

            substitutions = {var: value for var, value in kwargs.items()}
            expr = sympify(self.formula).subs(substitutions)

            result = expr.evalf()

        except Exception as e:
            result = f"Error in evaluation: {e}"

        return result

    def __str__(self):
        return self.name
