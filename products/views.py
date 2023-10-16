#views.py
import json
from datetime import datetime

from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from products.models import KindOfActivity, Company
from supervision.models import CheckArea, Permission
from supervision.forms import PrescriptionForm


def index(request):
    context = None
    if request.user.is_authenticated:
        context = {}
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
            list = {}
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
                        list.update({
                            company.slug: company,
                        })

            for company in companies:
                company.time_difference = company.validity - datetime.today().date()
            context = {
                'activities': KindOfActivity.objects.all(),
                'companies': list,
                'title': 'Главная',
            }
    return render(request, 'products/index.html', context)


def company_detail(request, company_slug):
    company = get_object_or_404(Company, slug=company_slug)
    return render(request, 'products/company_detail.html', {'company': company})


def control(request):
    return render(request, 'products/control.html')


def point(request, user_slug):
    from users.models import User
    user = User.objects.get(username=user_slug)
    permissions = None
    if user.groups.all().first().name == 'ins':
        permissions = Permission.objects.filter(user=user).order_by('id')
    companies = Company.objects.all()
    list = {}
    for company in companies:
        has = False
        areas = {}
        if permissions:
            check_areas = CheckArea.objects.filter(company=company)
            for ch in check_areas:
                for per in permissions:
                    if company == per.area.company:
                        areas.update({
                            per.area: {
                             'area': per.area,
                             'perm': per.access
                            }
                        })
                        has = True
            list.update({
                company.name: {
                    'company': company,
                    'perm': has,
                    'areas': areas
                }
            })
        else:
            list.update({
                company.name: {
                    'company': company,
                    'perm': has,
                }
            })

    context = {
        'companies': list,
        'user': user,
        'title': 'Доступ'
    }
    return render(request, 'products/point.html', context)


def company_titles(request, company_id):
    company = get_object_or_404(Company, pk=company_id)

    context = {
        'company': company,
        'title': 'Информация о компании'
    }
    return render(request, 'products/company_detail.html', context)


def grant_access(request, user_slug):
    if request.method == 'POST':
        print(request.POST)
        company_id = int(request.POST['company_id'])
        if Permission.objects.filter(area__company__id=company_id, user__username=user_slug).exists():
            perm = Permission.objects.filter(area__company__id=company_id, user__username=user_slug)
            perm.delete()
        else:
            from users.models import User
            user = User.objects.get(username=user_slug)
            areas = CheckArea.objects.filter(company__id=company_id)
            for area in areas:
                perm = Permission(area=area, user=user)
                perm.save()
        return redirect('products:point', user_slug=user_slug)
    else:
        return JsonResponse({'message': 'Недопустимый запрос.'}, status=400)


def update_perm(request, user_slug):
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)
        area_id = body_data.get('area_id')
        perm = Permission.objects.get(area__id=area_id, user__username=user_slug)
        perm.access = not perm.access
        perm.save()
        if perm.access:
            return JsonResponse({'message': True})
        else:
            return JsonResponse({'message': False})
    else:
        return JsonResponse({'message': 'Недопустимый запрос.'}, status=400)
