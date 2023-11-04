#views.py
from datetime import datetime

from django.shortcuts import render, get_object_or_404
from products.models import KindOfActivity, Company
from supervision.models import Permission


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


def company_detail(request, company_slug):
    company = get_object_or_404(Company, slug=company_slug)
    return render(request, 'products/company_detail.html', {'company': company})


def control(request):
    return render(request, 'products/control.html')


def company_titles(request, company_id):
    company = get_object_or_404(Company, pk=company_id)

    context = {
        'company': company,
        'title': 'Информация о компании'
    }
    return render(request, 'products/company_detail.html', context)


