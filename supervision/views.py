import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from documents.views import get_checklist
from supervision.forms import CheckMonthForm
from supervision.models import CheckArea, CheckMonth, Permission, OversightPeriod, Deadline
from documents.models import Checklist
from django.http import JsonResponse, HttpResponseNotFound
from datetime import datetime, timedelta
import locale
from django.contrib.auth.decorators import user_passes_test
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
def control(request, company_slug):
    today = datetime.today().date()
    if 'period' in request.GET:
        period = request.GET['period']
        date = OversightPeriod.objects.get(company__slug=company_slug, period=period)
    else:
        date = OversightPeriod.objects.get(start__lt=today, end__gt=today, company__slug=company_slug)

    table_html = table_date(date)
    check = []
    check_areas = None

    if request.user.groups.all().first().name == 'avia' or request.user.is_superuser:
        check_areas = CheckArea.objects.filter(company__slug=company_slug).order_by('id')
    elif request.user.groups.all().first().name == 'ins':
        check_areas = Permission.objects.filter(area__company__slug=company_slug, user=request.user,
                                                access=True).order_by('id')
    for check_area in check_areas:

        months = {}
        for i in range(1, 21):
            check_month = None
            if request.user.groups.all().first().name == 'avia' or request.user.is_superuser:
                check_month = CheckMonth.objects.get(area=check_area, month=i)
                if not request.user.is_superuser:
                    permission = Permission.objects.filter(area=check_month.area, user=request.user)
                    if permission.exists():
                        deadline = Deadline.objects.filter(user=request.user, month=check_month)
                        if deadline.exists():
                            deadline = deadline.first()
                            if not deadline.email_sent:
                                if deadline.until_the_deadline - today >= 10:
                                    deadline.email_sent = True
                                    deadline.save()
                        else:
                            deadline = Deadline(user=request.user, until_the_deadline=(check_month.date - today), email_sent=False, months=check_month)
                            deadline.save()
            elif request.user.groups.all().first().name == 'ins':
                check_month = CheckMonth.objects.get(area=check_area.area, month=i)
            months[i] = check_month
        if request.user.groups.all().first().name == 'avia' or request.user.is_superuser:
            check.append((check_area, months))
        else:
            check.append((check_area.area, months))

    form = CheckMonthForm()
    context = {
        'check_areas': check,
        'table_html': table_html,
        'form1': form,
        'company_slug': company_slug,
        'periods': OversightPeriod.objects.filter(company__slug=company_slug)
    }
    return render(request, 'supervision/check_area_table.html', context)


def create_period(request, company_slug):

    return redirect('supervision:control', company_slug=company_slug)


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
        {'category': 'Непроверочные', 'percentage': out_check},
    ]

    context = {
        'company_slug': company_slug,
        'data': json.dumps(data),
        'areas': areas,
        'select': select,
        'comments': comments,
        'all_month': not_checked + checked + checking + out_check
    }
    return render(request, 'supervision/dashboard.html', context)


@user_passes_test(is_superuser)
def update_check_month(request, check_month_id):
    check_month = CheckMonth.objects.get(id=check_month_id)
    if request.method == 'POST':
        check_month.checking = not check_month.checking
        check_month.save()
    return JsonResponse({'check_month': check_month.checking})


count: int = 1


def supervise(request, company_slug):
    global count
    count = 1
    groups = request.user.groups.all().first().name
    area = int(request.GET['area'])
    month = int(request.GET['month'])
    try:
        ch_area = CheckMonth.objects.get(month=month, area__id=area)
        if ch_area.checking:
            checklist, ch_exists = get_checklist(0, area, month)
            context = checklist
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


