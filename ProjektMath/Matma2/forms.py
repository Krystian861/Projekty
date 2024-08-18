from django import forms
from .models import MathFormula, Category

class MathFormulaForm(forms.ModelForm):
    class Meta:
        model = MathFormula
        fields = ['name', 'formula', 'variables', 'description', 'category']


    def clean_variables(self):
        variables = self.cleaned_data.get('variables')
        if variables:
            variable_list = variables.split(',')
            if len(variable_list) < 3:
                raise forms.ValidationError("Podaj co najmniej trzy zmienne oddzielone przecinkami.")
        return variables

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if MathFormula.objects.filter(name=name).exists():
            raise forms.ValidationError("Wzór o takiej nazwie już istnieje.")
        return name

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if Category.objects.filter(name=name).exists():
            raise forms.ValidationError("Kategoria o takiej nazwie już istnieje.")
        return name

class FormulaEvaluationForm(forms.Form):
    pass


class TrigonometryForm(forms.Form):
    a = forms.FloatField(label='a', required=True)
    b = forms.FloatField(label='b', required=True)
    c = forms.FloatField(label='c', required=True)