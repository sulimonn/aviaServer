import json
from dateutil.relativedelta import relativedelta
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from documents.views import get_checklist
from products.models import Company
from supervision.forms import CheckMonthForm, OversightPeriodForm
from supervision.models import CheckArea, CheckMonth, Permission, OversightPeriod
from documents.models import Checklist
from django.http import JsonResponse, HttpResponseNotFound
from datetime import datetime, timedelta
import locale
import calendar
from django.contrib.auth.decorators import user_passes_test
from supervision.tasks import check_deadline, check_expiry
from users.views import is_superuser
locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')

russian_month_names = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
   

def table_date(date):
    start_date = date.start
    end_date = date.end
    current_date = start_date
    months = []
    years = {}

    while current_date <= end_date:
        months.append(russian_month_names[current_date.month - 1].capitalize())
        if current_date.year in years:
            years[current_date.year] += 1
        else:
            years[current_date.year] = 1
        current_date += timedelta(days=31)

    table_html = "<tr>\n"

    for year, m in years.items():
        table_html += f'    <th colspan="{m}" class="text-center">{year}</th>\n'
    table_html += "</tr>\n"
    table_html += "<tr>\n"

    for month in months:
        table_html += f'    <td><div class="ops_td text-center">{month}</div></td>\n'
    table_html += "</tr>\n"
    return table_html


@login_required
def control(request, company_slug, edit=False):
    if 'period' in request.GET:
        period = request.GET['period']
        try:
            date = OversightPeriod.objects.get(company__slug=company_slug, period=period)
        except OversightPeriod.DoesNotExist:
            date = None
    else:
        try:
            date = OversightPeriod.objects.filter(company__slug=company_slug).first()
        except OversightPeriod.DoesNotExist:
            date = None
    if date is None:
        context = {
            'check_areas': None,
            'company_slug': company_slug,
            'period_form': OversightPeriodForm()
        }
        return render(request, 'supervision/check_area_table.html', context)
    table_html = table_date(date)
    check = []
    check_areas = None
    if request.user.is_superuser or request.user.groups.all().first().name == 'avia':
        check_areas = CheckArea.objects.filter(company__slug=company_slug).order_by('id')
    elif request.user.groups.all().first().name == 'ins':
        check_areas = Permission.objects.filter(area__company__slug=company_slug, user=request.user,
                                                access=True).order_by('id')
        if not check_areas.exists():
            return HttpResponseNotFound('<div style="display:flex;width:100vw; margin-top: 30vh;">'
                                        '   <h1 style="margin:auto;">Page Does Not Exist...</h1>'
                                        '</div>')
    for check_area in check_areas:

        months = {}
        for i in range(1, 21):
            check_month = None
            if request.user.is_superuser or request.user.groups.all().first().name == 'avia' :
                try:
                    check_month = CheckMonth.objects.get(area=check_area, month=i)
                except CheckMonth.DoesNotExist:
                    check_month = {
                        'key': i,
                        'month': None
                    }
            elif request.user.groups.all().first().name == 'ins':
                try:
                    check_month = CheckMonth.objects.get(area=check_area.area, month=i)
                except CheckMonth.DoesNotExist:
                    check_month = {
                        'key': i,
                        'month': None
                    }
            months[i] = check_month
        if request.user.is_superuser or request.user.groups.all().first().name == 'avia':
            check.append((check_area, months))
        else:
            check.append((check_area.area, months))

    context = {
        'range': range(1, 21),
        'check_areas': check,
        'table_html': table_html,
        'edit': edit,
        'company_slug': company_slug,
        'periods': OversightPeriod.objects.filter(company__slug=company_slug)
    }
    return render(request, 'supervision/check_area_table.html', context)


@login_required
def dashboard(request, company_slug):
    select = None
    areas = CheckArea.objects.filter(company__slug=company_slug)
    if 'select' in request.GET:
        select = int(request.GET['select'])
        if select != 0:
            areas = CheckArea.objects.filter(company__slug=company_slug, id=select)

    not_checked = 0
    checked = 0
    checking = 0
    out_check = 0
    comments = {}
    for area in areas:
        months = CheckMonth.objects.filter(area=area)
        for month in months:
            if month.checking:
                try:
                    checklist = Checklist.objects.get(area=area, month=month, original=None)
                    if checklist.comment:
                        checking += 1
                        comments.update({area.title: month})
                    else:
                        checked += 1

                except Checklist.DoesNotExist:
                    not_checked += 1
            else:
                out_check += 1

    areas = CheckArea.objects.filter(company__slug=company_slug)

    data = [
        {'category': 'Без предписаний', 'percentage': checked},
        {'category': 'Предписание', 'percentage': checking},
        {'category': 'Еще не проверено', 'percentage': not_checked},
    ]

    context = {
        'company_slug': company_slug,
        'data': json.dumps(data),
        'areas': areas,
        'select': select,
        'comments': comments,
        'all_month': not_checked + checked + checking #+ out_check
    }
    return render(request, 'supervision/dashboard.html', context)


@user_passes_test(is_superuser)
def delete_check_month(request, month_id):
    if request.method == 'POST':
        check_month = CheckMonth.objects.get(id=month_id)
        area_id = check_month.area.pk
        month = check_month.month
        check_month.delete()
        return JsonResponse({'url': f'/oversight/api/{area_id}/{month}/add/'})
    return JsonResponse({})


@user_passes_test(is_superuser)
def add_check_month(request, month_id, area_id):
    if request.method == 'POST':                
        check_month = CheckMonth(
            area_id=area_id,
            month=month_id,
        )
        check_month.checking = True
        check_month.save()
        check_deadline()
        check_expiry()
        return JsonResponse({'url': f'/oversight/api/{check_month.pk}/delete/'})
    return JsonResponse({})


count: int = 1


def supervise(request, company_slug):
    global count
    count = 1
    if request.user.is_superuser:
        groups = 'admin'
    else:
        groups = request.user.groups.all().first().name
    area = int(request.GET['area'])
    month = int(request.GET['month'])
    try:
        ch_area = CheckMonth.objects.get(month=month, area__id=area)
        if ch_area.checking:
            context, _ = get_checklist(0, area, month)
            perm = Permission.objects.filter(user=request.user)
            return render(request, 'supervision/supervise.html', {
                'group': groups,
                'context': context,
                'area': area,
                'month': month,
                'company_slug': company_slug,
                'perm': perm,
                'title': 'Проверка'
            })
        else:
            return HttpResponseNotFound('<div style="display:flex;width:100vw; margin-top: 30vh;">'
                                        '   <h1 style="margin:auto;">Page Does Not Exist...</h1>'
                                        '</div>')
    except CheckMonth.DoesNotExist:
        return HttpResponseNotFound('<div style="display:flex;width:100vw; margin-top: 30vh;">'
                                    '<h1 style="margin:auto;">Page Does Not Exist...</h1>'
                                    '</div>')


def create_period(request, company_slug):
    if request.method == 'POST':
        form = OversightPeriodForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start']
            start_date = start_date.replace(day=1)
            end_date = start_date + relativedelta(months=+19)
            company = Company.objects.get(slug=company_slug)
            period = f'{start_date.year}-{end_date.year}'

            oversight_period = OversightPeriod.objects.create(
                start=start_date,
                end=end_date,
                company=company,
                period=period
            )
            oversight_period.save()

            return redirect('supervision:control', company_slug=company_slug)
        

@user_passes_test(is_superuser)
def move_check(request, area_id):
    area = CheckArea.objects.get(id=int(area_id))
    checkmonths = CheckMonth.objects.filter(area_id=int(area_id))
    serialized_months = []
    current_date = datetime.now().date() 
    for mon in range(1, 21):
        checkmonth = None
        try:
            checkmonth = checkmonths.get(month=mon)
        except CheckMonth.DoesNotExist:
            pass
        if checkmonth:
            serialized_months.append({
                'month_name': russian_month_names[current_date.month - 1] + ' месяц ' + str(current_date.year),
                'month': mon,
                'checking': True,
                'id': checkmonth.pk
            })
        else:
            serialized_months.append({
                'month_name': russian_month_names[current_date.month - 1] + ' месяц ' + str(current_date.year),
                'month': mon,
                'checking': False
            })
        current_date += timedelta(days=31)
    return JsonResponse({'months': serialized_months, 'area': area.title})
