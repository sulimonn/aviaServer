# forms.py
from django import forms
from .models import Company


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'number', 'code', 'validity', 'status', 'address', 'first_phone', 'second_phone', 'email', 'kind_of_activity', 'password', 'slug']
        widgets = {
            'password': forms.PasswordInput(attrs={'placeholder': 'Введите пароль'}),
            'first_phone': forms.NumberInput(attrs={'placeholder': 'Введите первый номер телефона'}),
            'second_phone': forms.NumberInput(attrs={'placeholder': 'Введите второй номер телефона'}),
            'validity': forms.DateInput(attrs={'placeholder': 'ГГГГ-ММ-ДД'}),
        }
        labels = {
            'name': 'Название компании',
            'number': 'Номер СЭ',
            'code': '3-буквен КОД ИКАО',
            'validity': 'Действительно до',
            'status': 'Статус СЭ',
            'address': 'Адрес компании',
            'first_phone': 'Первый номер телефона',
            'second_phone': 'Второй номер телефона',
            'email': 'Электронная почта',
            'kind_of_activity': 'Вид деятельности',
            'password': 'Пароль',
            'slug': 'Username'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['placeholder'] = 'Введите название компании'
        self.fields['number'].widget.attrs['placeholder'] = 'Введите номер'
        self.fields['code'].widget.attrs['placeholder'] = 'Введите код'
        self.fields['address'].widget.attrs['placeholder'] = 'Введите адрес'
        self.fields['first_phone'].widget.attrs['placeholder'] = 'Введите первый номер телефона'
        self.fields['second_phone'].widget.attrs['placeholder'] = 'Введите второй номер телефона'
        self.fields['email'].widget.attrs['placeholder'] = 'Введите адрес эл.почты'
        self.fields['slug'].widget.attrs['readonly'] = True
        for field_name, filed in self.fields.items():
            if field_name != 'status':
                filed.widget.attrs['class'] = 'form-control py-2'
                
        instance = getattr(self, 'instance', None)
        if instance and instance.pk: 
            self.fields['password'].required = False
            self.fields['slug'].required = False
        else:
            self.fields['slug'].required = False
            self.fields['slug'].widget.attrs['hidden']= True
            self.fields['slug'].label = ''
                
    def clean(self):
        cleaned_data = super().clean()
        instance = getattr(self, 'instance', None)

        if instance and instance.pk:
            if 'password' not in self.cleaned_data:
                cleaned_data['password'] = instance.password
            if 'slug' not in self.cleaned_data:
                cleaned_data['slug'] = instance.slug
        return cleaned_data