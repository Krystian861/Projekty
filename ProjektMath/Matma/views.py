import re
from django.contrib.auth.decorators import login_required

from django.urls import reverse
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django import forms
from sympy import symbols, sympify, sqrt, expand, Eq, solve, simplify, nan, I
from .models import MathFormula, Category
from .forms import MathFormulaForm, CategoryForm, FormulaEvaluationForm


def odkiedy(request):
    return render(request, 'Termin/odkiedy.html')

def dokiedy(request):
    return render(request, 'Termin/dokiedy.html')

def Pomysl(request):
    return render(request, 'Termin/Pomysl.html')

def company(request):
    return render(request, 'company.html')


def edit_formula(request, pk):
    formula = get_object_or_404(MathFormula, pk=pk)
    if request.method == 'POST':
        form = MathFormulaForm(request.POST, instance=formula)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = MathFormulaForm(instance=formula)
    return render(request, 'edit_formula.html', {'form': form})


def edit_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'edit_category.html', {'form': form})


def users(request):
    return render(request, 'users.html')


def contact(request):
    return render(request, 'contact.html')


def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        return redirect('home')
    return render(request, 'delete_category.html', {'category': category})


def add_formula(request):
    if request.method == 'POST':
        form = MathFormulaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = MathFormulaForm()
    return render(request, 'add_formula.html', {'form': form})


def delete_formula(request, pk):
    formula = get_object_or_404(MathFormula, pk=pk)
    if request.method == 'POST':
        formula.delete()
        return redirect('home')
    return render(request, 'delete_formula.html', {'formula': formula})


def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = CategoryForm()
    return render(request, 'add_category.html', {'form': form})


def formula_list(request):
    query = request.GET.get('q')

    if query:
        categories = Category.objects.filter(formulas__name__icontains=query).distinct()
        formulas = MathFormula.objects.filter(name__icontains=query)
    else:
        categories = Category.objects.all()
        formulas = MathFormula.objects.all()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        categories_list = [
            {
                "id": cat.id,
                "name": cat.name,
                "edit_url": reverse('edit_category', args=[cat.id]),
                "delete_url": reverse('delete_category', args=[cat.id]),
                "formulas": [
                    {
                        "id": formula.id,
                        "name": formula.name,
                        "detail_url": reverse('formula_detail', args=[formula.id]),
                        "edit_url": reverse('edit_formula', args=[formula.id]),
                        "delete_url": reverse('delete_formula', args=[formula.id])
                    } for formula in cat.formulas.filter(name__icontains=query)
                ]
            }
            for cat in categories
        ]
        formulas_list = [
            {
                "id": formula.id,
                "name": formula.name,
                "detail_url": reverse('formula_detail', args=[formula.id]),
                "edit_url": reverse('edit_formula', args=[formula.id]),
                "delete_url": reverse('delete_formula', args=[formula.id])
            } for formula in formulas
        ]

        if not categories_list and not formulas_list:
            return JsonResponse({"message": "Nie znaleziono kategorii ani wzorów o podanej nazwie."})

        return JsonResponse({"categories": categories_list, "formulas": formulas_list})

    return render(request, 'home.html', {
        'categories': categories,
        'formulas': formulas,
    })

def add_multiplication_signs(expression):
    expression = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', expression)
    expression = re.sub(r'([a-zA-Z])(\d)', r'\1*\2', expression)
    expression = re.sub(r'([a-zA-Z])([a-zA-Z])', r'\1*\2', expression)
    return expression


def apply_special_formula(expression, variables, cleaned_data):
    for var in variables:
        value = cleaned_data.get(var)
        if value is not None:
            expression = expression.replace(var, str(value))

    expression = expression.replace("^2", "**2").replace("^3", "**3")


    if expression == "a^2 - b^2":
        return "(a - b)*(a + b)"
    elif expression == "a^2 - 1":
        return "(a - 1)*(a + 1)"
    elif expression == "a^3 - b^3":
        return "(a - b)*(a**2 + a*b + b**2)"
    elif expression == "a^3 - 1":
        return "(a - 1)*(a**2 + a + 1)"
    elif expression == "a^3 + b^3":
        return "(a + b)*(a**2 - a*b + b**2)"
    elif expression == "a^3 + 1":
        return "(a + 1)*(a**2 - a + 1)"
    elif "a^n - 1" in expression:
        n_value = int(cleaned_data.get('n', 1))
        return expand_an_minus_one(n_value)
    elif "log" in expression:
        return handle_logarithms(expression)
    if "=" in expression:
        lhs, rhs = expression.split('=')
        lhs = lhs.strip()
        rhs = rhs.strip()
        return f"Eq({lhs}, {rhs})"
    else:
        return expression


def expand_an_minus_one(n):
    if n < 1:
        raise ValueError("n must be greater than or equal to 1")
    a = symbols('a')
    terms = [a ** i for i in range(n - 1, -1, -1)]
    return f"(a - 1) * ({' + '.join(map(str, terms))})"


def handle_logarithms(expression):
    expression = re.sub(r'log\(([^,]+),([^,]+)\)', r'log(\1, \2)', expression)
    expression = re.sub(r'log\(([^)]+)\)', r'log(\1)', expression)
    return expression

@login_required
def formula_detail(request, pk):
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
                formula_expression = apply_special_formula(formula_expression, variables, cleaned_data)

                sympy_vars = symbols(variables)
                symbol_dict = {str(var): var for var in sympy_vars}

                print(f"Processing formula: {formula_expression}")

                displayed_formula = formula_expression
                for var, value in cleaned_data.items():
                    displayed_formula = displayed_formula.replace(var, str(value))

                if '=' in formula_expression:
                    lhs, rhs = formula_expression.split('=')
                    lhs = sympify(lhs, locals=symbol_dict)
                    rhs = sympify(rhs, locals=symbol_dict)
                    unknown_vars = [var for var in sympy_vars if str(var) not in cleaned_data]

                    if len(unknown_vars) == 1:
                        equation = Eq(lhs, rhs)
                        solution = solve(equation, unknown_vars[0])
                        result = solution[0]
                        steps = [
                            f"Równanie: {equation}",
                            f"Rozwiązanie: {unknown_vars[0]} = {result}"
                        ]
                    else:
                        result = "Nie można rozwiązać równania, zbyt wiele nieznanych zmiennych."
                        steps = []
                else:
                    try:
                        expression = sympify(formula_expression, locals=symbol_dict)
                        expression = expression.subs(sqrt(-1), I)

                    except Exception as e:
                        print(f"Error sympifying expression {formula_expression}: {e}")
                        results.append(f"Error in evaluation: {e}")
                        displayed_formulas.append(displayed_formula)
                        steps_list.append([])
                        raise

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
                print(f"Error during calculation: {e}")
                results.append(f"Error in evaluation: {e}")
                displayed_formulas.append(formula_expression)
                steps_list.append([])
    else:
        form = DynamicFormulaEvaluationForm()

    print(f"Length of displayed_formulas: {len(displayed_formulas)}")
    print(f"Length of results: {len(results)}")
    print(f"Length of steps_list: {len(steps_list)}")

    zipped_results = zip(displayed_formulas, results, steps_list)

    return render(request, 'formula_detail.html', {
        "result": result,
        'formula': formula,
        'form': form,
        'zipped_results': zipped_results
    })
