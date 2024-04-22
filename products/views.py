#views.py
from datetime import datetime
from django.shortcuts import render, get_object_or_404, redirect
from products.models import KindOfActivity, Company
from products.forms import CompanyForm
from supervision.models import Permission
from django.contrib.auth.decorators import user_passes_test


def is_superuser(user):
    return user.is_superuser


def index(request):
    context = None
    if request.user.is_authenticated:
        if request.user.is_superuser:
            companies = Company.objects.all()
            for company in companies:
                company.time_difference = company.validity - datetime.today().date()
            context = {
                'activities': KindOfActivity.objects.all(),
                'companies': companies,
                'title': 'Главная'
            }
        elif request.user.groups.all().first().name == 'avia':
            companies = Company.objects.get(user=request.user)
            context = {
                'activities': KindOfActivity.objects.all(),
                'company': companies,
                'title': 'Главная'
            }
        else:
            companies_list = {}
            permissions = Permission.objects.filter(user=request.user)
            companies = Company.objects.all()
            for company in companies:
                has = False
                if permissions and permissions.exists():
                    for per in permissions:
                        if company == per.area.company:
                            has = True
                            break
                    if has:
                        companies_list.update({
                            company.slug: company,
                        })

            for company in companies:
                company.time_difference = company.validity - datetime.today().date()
            context = {
                'activities': KindOfActivity.objects.all(),
                'companies': companies_list,
                'title': 'Главная',
            }
    return render(request, 'products/index.html', context)


@user_passes_test(is_superuser)
def companies_list(request):
    companies = Company.objects.all()
    context = {
        'companies': companies,
        'title': 'Компании'}
    return render(request, 'users/user_list.html', context)


@user_passes_test(is_superuser)
def create_company(request):
    from products.forms import CompanyForm
    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('products:companies_list')  # Redirect to a success page
    else:
        form = CompanyForm()

    return render(request, 'products/register_avia.html', {'form': form, 'title': 'Регистрация'})


@user_passes_test(is_superuser)
def edit_company(request, company_slug):
    company = Company.objects.get(slug=company_slug)
    if request.method == 'POST':
        form = CompanyForm(request.POST, instance=company)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = CompanyForm(instance=company)
        form.fields.pop('password', None)  # Remove 'password' field from the form

    return render(request, 'products/register_avia.html', {'form': form, 'title': 'Регистрация'})

russian_month_names = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']

