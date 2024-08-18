import re
from django.contrib.auth.decorators import login_required
import re
import logging

from django.urls import reverse
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django import forms

from sympy import symbols, sympify, sqrt, expand, Eq, solve, simplify, nan
from .models import MathFormula, Category
from .forms import MathFormulaForm, CategoryForm, FormulaEvaluationForm

# Konfiguracja loggera
logger = logging.getLogger(__name__)

def company2(request):
    return render(request, 'company.html')

def edit_formula2(request, pk):
    formula = get_object_or_404(MathFormula, pk=pk)
    if request.method == 'POST':
        form = MathFormulaForm(request.POST, instance=formula)
        if form.is_valid():
            form.save()
            return redirect('home2')
    else:
        form = MathFormulaForm(instance=formula)
    return render(request, 'Matma2/edit_formula2.html', {'form': form})

def edit_category2(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('home2')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'Matma2/edit_category2.html', {'form': form})

def users2(request):
    return render(request, 'users.html')

def contact2(request):
    return render(request, 'contact.html')

def delete_category2(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        return redirect('home2')
    return render(request, 'Matma2/delete_category2.html', {'category': category})

def add_formula2(request):
    if request.method == 'POST':
        form = MathFormulaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home2')
    else:
        form = MathFormulaForm()
    return render(request, 'add_formula.html', {'form': form})

def delete_formula2(request, pk):
    formula = get_object_or_404(MathFormula, pk=pk)
    if request.method == 'POST':
        formula.delete()
        return redirect('home2')
    return render(request, 'Matma2/delete_formula.html', {'formula': formula})

def add_category2(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home2')
    else:
        form = CategoryForm()
    return render(request, 'Matma2/add_category2.html', {'form': form})

def formula_list2(request):
    query = request.GET.get('q', '')
    sort_by = request.GET.get('sort_by', '')

    # Querying categories and formulas based on search query
    if query:
        categories = Category.objects.filter(formulas__name__icontains=query).distinct()
        formulas = MathFormula.objects.filter(name__icontains=query)
    else:
        categories = Category.objects.all()
        formulas = MathFormula.objects.all()

    # Sorting based on parameters
    if sort_by == 'alphabetically':
        categories = categories.order_by('name')
        formulas = formulas.order_by('name')
    elif sort_by == 'date_added':
        formulas = formulas.order_by('-created_at')

    # Handling AJAX request
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        categories_list = [
            {
                "id": cat.id,
                "name": cat.name,
                "edit_url": reverse('edit_category2', args=[cat.id]),
                "delete_url": reverse('delete_category2', args=[cat.id]),
                "formulas": [
                    {
                        "id": formula.id,
                        "name": formula.name,
                        "detail_url": reverse('formula_detail2', args=[formula.id]),
                        "edit_url": reverse('edit_formula2', args=[formula.id]),
                        "delete_url": reverse('delete_formula2', args=[formula.id])
                    } for formula in cat.formulas.filter(name__icontains=query)
                ]
            }
            for cat in categories
        ]
        formulas_list = [
            {
                "id": formula.id,
                "name": formula.name,
                "detail_url": reverse('formula_detail2', args=[formula.id]),
                "edit_url": reverse('edit_formula2', args=[formula.id]),
                "delete_url": reverse('delete_formula2', args=[formula.id])
            } for formula in formulas
        ]

        if not categories_list and not formulas_list:
            return JsonResponse({"message": "Nie znaleziono kategorii ani wzorów o podanej nazwie."})

        return JsonResponse({"categories": categories_list, "formulas": formulas_list})

    return render(request, 'Matma2/home2.html', {
        'categories': categories,
        'formulas': formulas,
    })

def add_multiplication_signs2(expression):
    expression = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', expression)
    expression = re.sub(r'([a-zA-Z])(\d)', r'\1*\2', expression)
    expression = re.sub(r'([a-zA-Z])([a-zA-Z])', r'\1*\2', expression)
    return expression

def expand_an_minus_one2(n):
    if n < 1:
        raise ValueError("n must be greater than or equal to 1")
    a = symbols('a')
    terms = [a ** i for i in range(n - 1, -1, -1)]
    return f"(a - 1) * ({' + '.join(map(str, terms))})"

def handle_logarithms2(expression):
    expression = re.sub(r'log\(([^,]+),([^,]+)\)', r'log(\1, \2)', expression)
    expression = re.sub(r'log\(([^)]+)\)', r'log(\1)', expression)
    return expression

def handle_arithmetic_sequence(formula_expression, cleaned_data):
    a_n = cleaned_data.get("a_n")
    a_1 = cleaned_data.get("a_1")
    d = cleaned_data.get("d")
    n = cleaned_data.get("n")

    if all(v is not None for v in [a_n, a_1, d, n]):
        return f"Eq({a_n}, {a_1} + ({n} - 1) * {d})"
    else:
        return formula_expression

def handle_trigonometry(expression, cleaned_data):
    expression = expression.replace('sin', 'sin')
    expression = expression.replace('cos', 'cos')
    expression = expression.replace('tan', 'tan')

    x = float(cleaned_data.get('x', 0))
    y = float(cleaned_data.get('y', 0))
    r = sqrt(x**2 + y**2)

    expression = expression.replace('r', str(r))

    return expression

def apply_special_formula2(formula_expression, variables, cleaned_data):
    for var in variables:
        value = cleaned_data.get(var)
        if value is not None:
            formula_expression = formula_expression.replace(var, value)

    formula_expression = handle_trigonometry(formula_expression, cleaned_data)

    if "=" in formula_expression:
        lhs, rhs = formula_expression.split('=')
        lhs = lhs.strip()
        rhs = rhs.strip()
        return f"Eq({lhs}, {rhs})"
    else:
        return formula_expression

@login_required
def formula_detail2(request, pk):
    formula = get_object_or_404(MathFormula, pk=pk)
    variables = formula.variables.split(',')
    dynamic_form_fields = {var: forms.CharField(label=var, required=False) for var in variables}
    DynamicFormulaEvaluationForm = type('DynamicFormulaEvaluationForm', (FormulaEvaluationForm,), dynamic_form_fields)

    result = None
    results = []
    displayed_formulas = []
    steps_list = []

    if request.method == 'POST' and 'calculate' in request.POST:
        form = DynamicFormulaEvaluationForm(request.POST)
        if form.is_valid():
            try:
                cleaned_data = form.cleaned_data
                formula_expression = formula.formula.strip().replace('√', 'sqrt')
                formula_expressions = formula_expression.split(',')

                for expr in formula_expressions:
                    expr = expr.strip()
                    expr = expr

                    sympy_vars = symbols(variables)
                    symbol_dict = {str(var): var for var in sympy_vars}

                    displayed_formula = expr
                    for var, value in cleaned_data.items():
                        displayed_formula = displayed_formula.replace(var, str(value))

                    try:
                        expression = sympify(expr, locals=symbol_dict)
                    except Exception as e:
                        logger.error(f"Error sympifying expression {expr}: {e}")
                        results.append(f"Error in evaluation: {e}")
                        displayed_formulas.append(displayed_formula)
                        steps_list.append([])
                        continue

                    for var, value in cleaned_data.items():
                        if value.isnumeric():
                            value = float(value)
                        else:
                            value = sympify(value, locals=symbol_dict)
                        expression = expression.subs(var, value)

                    steps = []
                    steps.append(f"Original formula: {expression}")
                    expanded_expression = expand(expression)
                    steps.append(f"Expanded formula: {expanded_expression}")
                    simplified_expression = simplify(expanded_expression)

                    evaluated_result = simplified_expression.evalf()
                    if evaluated_result.is_number and not evaluated_result.has(nan):
                        result = int(evaluated_result)
                    else:
                        result = evaluated_result

                    steps.append(f"Simplified formula: {simplified_expression}")

                    results.append(result)
                    displayed_formulas.append(displayed_formula)
                    steps_list.append(steps)

            except Exception as e:
                logger.error(f"Error during calculation: {e}")
                results.append(f"Error in evaluation: {e}")
                displayed_formulas.append(formula_expression)
                steps_list.append([])
    else:
        form = DynamicFormulaEvaluationForm()

    zipped_results = zip(displayed_formulas, results, steps_list)

    return render(request, 'Matma2/formula_detail2.html', {
        "result": result,
        'formula': formula,
        'form': form,
        'zipped_results': zipped_results
    })