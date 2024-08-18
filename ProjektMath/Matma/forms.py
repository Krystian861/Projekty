from django import forms
from .models import MathFormula, Category

class MathFormulaForm(forms.ModelForm):
    class Meta:
        model = MathFormula
        fields = ['name', 'formula', 'variables', 'description', 'category']

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
