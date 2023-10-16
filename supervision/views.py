import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from supervision.forms import MovedForm, ChecklistForm, CheckMonthForm, PrescriptionForm, PKDForm, ApprovalForm, \
    EliminationForm, ReportForm, NotificationForm
from supervision.models import CheckArea, CheckMonth, Permission, OversightPeriod
from documents.models import Checklist, Prescription, PKD, Approval, Elimination, Report, Notification, Moved
from django.http import JsonResponse, HttpResponseNotFound
from datetime import datetime, timedelta
import locale
from .serializers import PrescriptionSerializer, ChecklistSerializer, PkdSerializer, ApprovalSerializer, \
    EliminationSerializer, ReportSerializer, NotificationSerializer

locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')


def table_date(start_date, end_date):
    current_date = start_date
    months = []
    years = {}

    while current_date <= end_date:
        months.append(current_date.strftime("%B"))
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
    start_date = date.start
    end_date = date.end
    table_html = table_date(start_date, end_date)
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


def move_check(request, company_slug, area_id):
    months = CheckMonth.objects.filter(area_id=int(area_id)).order_by('month')
    serialized_months = list(months.values())
    russian_month_names = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь',
                           'Октябрь', 'Ноябрь', 'Декабрь']
    current_date = datetime(2023, 6, 1)
    for mon in serialized_months:
        mon['month_name'] = russian_month_names[current_date.month - 1] + ' месяц ' + str(current_date.year)
        current_date += timedelta(days=31)
    return JsonResponse({'months': serialized_months, 'area': months.first().area.title})


def update_check_month(request, check_month_id):
    check_month = CheckMonth.objects.get(id=check_month_id)
    if request.method == 'POST':
        check_month.checking = not check_month.checking
        check_month.save()
    return JsonResponse({'check_month': check_month.checking})


def update_move_check(request, company_slug):
    if request.method == 'POST':
        current = CheckMonth.objects.get(id=int(request.POST['current']))
        current.status = 'Moved'
        current.save()
        move_to = CheckMonth.objects.get(id=int(request.POST['select']))
        move_to.checking = True
        move_to.save()
    return redirect('supervision:control', company_slug=company_slug)


def get_moved(request, company_slug):
    if 'area' and 'month' in request.GET:
        area = int(request.GET['area'])
        month = int(request.GET['month'])
        try:
            raport = Moved.objects.get(area_id=area, month__month=month)
            context = {
                'raport': raport,
                'exists': True
            }
        except Moved.DoesNotExist:
            form = MovedForm()
            form_data = {
                'raport': form['raport'],
                'saveto': 'moved'
            }
            context = {
                'form': form_data,
                'exists': False
            }
        context.update({
            'company_slug': company_slug,
            'area': area,
            'month': month
        })
        return render(request, 'supervision/moved.html', context)
    else:
        return HttpResponseNotFound('<div style="display:flex;width:100vw; margin-top: 30vh;">' +
                                    '<h1 style="margin:auto;">Page Does Not Exist...</h1>' +
                                    '</div>')


def post(request):
    area = int(request.GET['area'])
    month = int(request.GET['month'])
    saveto = request.GET['saveto']
    company_slug = request.GET['company']
    result = None
    match saveto:
        case 'checklist':
            result = post_checklist(request)
        case 'prescription':
            result = post_prescription(request)
        case 'pkd':
            result = post_pkd(request)
        case 'approval':
            result = post_approval(request)
        case 'elim':
            result = post_elimination(request)
        case 'report':
            result = post_report(request)
        case 'notification':
            result = post_notification(request)
        case 'moved':
            result = post_raport(request)
    if saveto == 'moved':
        url = reverse("supervision:moved", kwargs={'company_slug': company_slug})
    else:
        url = reverse("supervision:check_area_table", kwargs={'company_slug': company_slug})
    url += f'?area={area}&month={month}'
    return redirect(url)


def post_raport(request):
    area = int(request.GET['area'])
    month = int(request.GET['month'])
    if request.method == 'POST':
        form = MovedForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save()
            moved = Moved.objects.get(id=instance.id)
            check_area = CheckArea.objects.get(id=area)
            moved.month = CheckMonth.objects.get(month=month, area=check_area)
            moved.area = check_area
            moved.save()
    return True


def post_checklist(request):
    area = int(request.GET['area'])
    month = int(request.GET['month'])
    ch_count = int(request.GET['count']) // 5
    if int(request.GET['count']) == 6:
        ch_count = 1
    elif int(request.GET['count']) == 9:
        ch_count = 2
    elif int(request.GET['count']) == 12:
        ch_count = 3
    form = ChecklistForm(request.POST, request.FILES)
    if form.is_valid():
        instance = form.save()
        card = Checklist.objects.get(id=instance.id)
        if ch_count == 0:
            check_area = CheckArea.objects.get(id=area)
            card.month = CheckMonth.objects.get(month=month, area=check_area)
            card.area = check_area
        else:
            checklist = Checklist.objects.get(area__id=area, month__month=month, count=ch_count)
            card.original = checklist
        card.save()
        return True
    return False


def post_prescription(request):
    area = int(request.GET['area'])
    month = int(request.GET['month'])
    ch_count = int(request.GET['count']) // 5 + 1
    if request.method == 'POST':
        checklist = Checklist.objects.get(area__id=area, month__month=month, count=ch_count)
        if not Prescription.objects.filter(checklist=checklist).exists():
            letter = request.FILES['letter']
            if 'fine_protocol' in request.FILES:
                fine_protocol = request.FILES['fine_protocol']
                prescription = Prescription(fine_protocol=fine_protocol, letter=letter, checklist=checklist)
            else:
                prescription = Prescription(letter=letter, checklist=checklist)
            prescription.save()
        return True


def post_pkd(request):
    area = int(request.GET['area'])
    month = int(request.GET['month'])
    ch_count = int(request.GET['count']) // 5 + 1
    if int(request.GET['count']) == 6:
        ch_count = 2
    elif int(request.GET['count']) == 9:
        ch_count = 3
    elif int(request.GET['count']) == 12:
        ch_count = 4
    if request.method == 'POST':
        checklist = Checklist.objects.get(area__id=area, month__month=month, count=ch_count)
        if not PKD.objects.filter(checklist=checklist).exists():
            letter = request.FILES['letter']
            pkd = request.FILES['pkd']
            pkd = PKD(letter=letter, pkd=pkd, checklist=checklist)
            pkd.save()
        return True


def post_approval(request):
    area = int(request.GET['area'])
    month = int(request.GET['month'])
    ch_count = int(request.GET['count']) // 5 + 1
    if request.method == 'POST':
        checklist = Checklist.objects.get(area__id=area, month__month=month, count=ch_count)
        if not Approval.objects.filter(checklist=checklist).exists():
            approval = request.FILES['approval']
            app = Approval(approval=approval, checklist=checklist)
            app.deadline = request.POST.get('deadline')
            app.save()
        return True


def post_elimination(request):
    area = int(request.GET['area'])
    month = int(request.GET['month'])
    ch_count = int(request.GET['count']) // 6 + 1
    if request.method == 'POST':
        checklist = Checklist.objects.get(area__id=area, month__month=month, count=ch_count)
        if checklist.count == 1:
            app = Approval.objects.get(checklist=checklist)
            if app.deadline >= datetime.today().date():
                if not Elimination.objects.filter(checklist=checklist).exists():
                    letter = request.FILES['letter']
                    el = Elimination(letter=letter, checklist=checklist)
                    el.save()
        else:
            if not Elimination.objects.filter(checklist=checklist).exists():
                letter = request.FILES['letter']
                el = Elimination(letter=letter, checklist=checklist)
                el.save()
            return True
        return False


def post_report(request):
    area = int(request.GET['area'])
    month = int(request.GET['month'])
    ch_count = int(request.GET['count']) // 5 + 1
    if int(request.GET['count']) == 6:
        ch_count = 2
    elif int(request.GET['count']) == 9:
        ch_count = 3
    elif int(request.GET['count']) == 12:
        ch_count = 4
    if request.method == 'POST':
        checklist = Checklist.objects.get(area__id=area, month__month=month, count=ch_count)
        if not Report.objects.filter(checklist=checklist).exists() and not Notification.objects.filter(checklist=checklist).exists():
            report_file = request.FILES['report']
            report = Report(report=report_file, checklist=checklist)
            report.save()
            letter = request.FILES['letter']
            notification = Notification(letter=letter, checklist=checklist)
            notification.save()
        return True


def post_notification(request):
    area = int(request.GET['area'])
    month = int(request.GET['month'])
    ch_count = int(request.GET['count']) // 5 + 1
    if int(request.GET['count']) == 6:
        ch_count = 2
    elif int(request.GET['count']) == 9:
        ch_count = 3
    elif int(request.GET['count']) == 12:
        ch_count = 4
    if request.method == 'POST':
        checklist = Checklist.objects.get(area__id=area, month__month=month, count=ch_count)
        letter = request.FILES['letter']
        if not Notification.objects.filter(checklist=checklist).exists():
            notification = Notification(letter=letter, checklist=checklist)
            notification.save()
        return True


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


def get_checklist(checklist_id, area=0, month=0):
    global count
    try:
        if checklist_id == 0:
            checklist = Checklist.objects.get(area__id=area, month__month=month, count=1)
        else:
            count += 1
            checklist = Checklist.objects.get(original_id=checklist_id)
        serializer = ChecklistSerializer(checklist)
        context = {
            str(checklist.count) + 'checklist': checklist,
        }
        print(checklist.files.field.name)
        if not checklist.comment:
            if checklist.count == 1:
                return context, False
            elif checklist.count != 1:
                report, exists = get_report(checklist.pk)
                context.update(report)
                return context, True
        if checklist.count == 1:
            prescription, p_exists = get_prescription(checklist.pk)
            context.update(prescription)
        elif checklist.count != 1:
            notification, n = get_notification(checklist.pk)
            context.update(notification)
        elif checklist.count == 3:
            pro = {
                'over': ''
            }
            context.update(pro)
        return context, True
    except Checklist.DoesNotExist:
        form = ChecklistForm()
        form_data = {
            'saveto': 'checklist',
            'Контрольная карта': str(form['files']),
            'Замечание': str(form['comment']),
        }
        if checklist_id != 0:
            checklist = Checklist.objects.get(id=checklist_id)
            form_data.update({'checklist_id': checklist.pk})
        context = {
            'iform': form_data
        }
        return context, False


def get_prescription(checklist_id):
    global count
    checklist = Checklist.objects.get(pk=int(checklist_id))
    try:
        prescription = Prescription.objects.get(checklist=checklist)
        serializer = PrescriptionSerializer(prescription)
        context = {
            str(checklist.count) + 'prescription': prescription
        }
        pkd, exists = get_pkd(checklist.pk)
        context.update(pkd)
        return context, True
    except Prescription.DoesNotExist:
        form = PrescriptionForm()
        form_data = {
            'saveto': 'prescription',
            'Письмо в авиакомпанию': str(form['letter']),
            'Протокол штрафа': str(form['fine_protocol']),
            'checklist_id': checklist.pk
        }
        context = {
            'iform': form_data
        }
        return context, False


def get_pkd(checklist_id):
    global count

    checklist = Checklist.objects.get(pk=int(checklist_id))
    try:
        pkd = PKD.objects.get(checklist=checklist)
        serializer = PkdSerializer(pkd)
        context = {
            str(checklist.count) + 'pkd': pkd
        }
        approval, a_exists = get_approval(checklist.pk)
        context.update(approval)

        return context, True
    except PKD.DoesNotExist:
        form = PKDForm()
        form_data = {
            'saveto': 'pkd',
            'Письмо от авиакомпании': str(form['letter']),
            'ПКД': str(form['pkd']),
            'checklist_id': checklist.pk
        }
        context = {
            'form': form_data
        }
        return context, False


def get_approval(checklist_id):
    global count
    checklist = Checklist.objects.get(id=checklist_id)
    try:
        approval = Approval.objects.get(checklist=checklist)
        serializer = ApprovalSerializer(approval)
        context = {
            str(checklist.count) + 'approval': approval
        }
        elim, exists = get_elimination(checklist.pk)
        context.update(elim)
        return context, True
    except Approval.DoesNotExist:
        form = ApprovalForm()
        form_data = {
            'saveto': 'approval',
            'Одобрение от ГАГА': str(form['approval']),
            'Срок': str(form['deadline']),
            'checklist_id': checklist.pk
        }
        context = {
            f'iform': form_data
        }
        return context, False


def get_elimination(checklist_id):
    global count
    checklist = Checklist.objects.get(id=checklist_id)
    try:
        elim = Elimination.objects.get(checklist=checklist)
        serializer = EliminationSerializer(elim)
        serializer.data.update({'deadline': 12})
        context = {
            str(checklist.count) + 'elim': elim
        }
        checklist, exists = get_checklist(checklist.pk)
        context.update(checklist)
        return context, True
    except Elimination.DoesNotExist:

        context = {}
        form = EliminationForm()
        if checklist.count == 1:
            app = Approval.objects.get(checklist=checklist)
            if app.deadline >= datetime.today().date():
                form_data = {
                    'saveto': 'elim',
                    'Письмо об устранении замечаний': str(form['letter']),
                    'checklist_id': checklist.pk,
                    'todeadline': app.deadline - datetime.today().date()
                }
                context = {
                    f'form': form_data
            }
        else:
            form_data = {
                'saveto': 'elim',
                'Письмо об устранении замечаний': str(form['letter']),
                'checklist_id': checklist.pk,
            }

            context = {
                f'form': form_data
            }
        return context, False


def get_report(checklist_id):
    global count
    checklist = Checklist.objects.get(id=checklist_id)
    try:
        report = Report.objects.get(checklist=checklist)
        serializer = ReportSerializer(report)
        notification, exists = get_notification(checklist.pk)
        context = {
            str(checklist.count) + 'report': report
        }
        context.update(notification)
        return context, True
    except Report.DoesNotExist:
        form = ReportForm()
        form2 = NotificationForm()
        form_data = {
            'saveto': 'report',
            'Отчет': str(form['report']),
            'Уведомление авиакомпании': str(form2['letter']),
            'checklist_id': checklist.pk
        }
        context = {
            f'iform': form_data
        }
        return context, False


def get_notification(checklist_id):
    global count
    checklist = Checklist.objects.get(id=checklist_id)
    try:
        notification = Notification.objects.get(checklist=checklist)
        serializer = NotificationSerializer(notification)
        context = {
            str(checklist.count) + 'notification': notification
        }
        if checklist.comment:
            checklist, p = get_elimination(checklist.pk)
            context.update(checklist)
        return context, True
    except Notification.DoesNotExist:

        if checklist.count != 3:
            form = NotificationForm()
            if checklist.comment:
                form_data = {
                    'saveto': 'notification',
                    'Уведомление авиакомпанию': str(form['letter']),
                    'checklist_id': checklist.pk
                }
            else:
                form_data = {
                    'saveto': 'notification',
                    'Уведомление авиакомпанию': str(form['letter']),
                    'checklist_id': checklist.pk
                }
            context = {
                f'iform': form_data
            }
        else:
            form_data = {
                'over': 'Рекомендуется повторная сертификация эксплуатанта ВТ',
                'stop': True
            }
            context = {
                f'iform': form_data
            }
        return context, False
