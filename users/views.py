import json
from django.contrib import auth, messages
from django.http import JsonResponse
from django.shortcuts import render, HttpResponseRedirect, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import user_passes_test
from products.models import Company
from supervision.models import Permission, CheckArea
from supervision.tasks import check_deadline, check_expiry
from users.forms import UserLoginForm, UserRegistrationForm, UserProfileForm
from users.models import User
from django.core.mail import send_mail
from django.utils.translation import gettext as _
from decouple import config



def is_superuser(user):
    return user.is_superuser


# Create your views here.
def login(request):
    if request.method == 'POST':
        form = UserLoginForm(request=request, data=request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = auth.authenticate(username=username, password=password)
            if user and user.is_active:
                auth.login(request, user)
                return HttpResponseRedirect(reverse('index'))

    else:
        form = UserLoginForm
    context = {
        'form': form,
        'title': 'Авторизация'
    }
    return render(request, 'users/login.html', context)


@user_passes_test(is_superuser)
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            instance = form.save()
            group = Group.objects.get(name='ins')
            instance.groups.add(group)
            instance.save()
            return HttpResponseRedirect(reverse('users:user_list'))
    else:
        form = UserRegistrationForm()
    context = {
        'form': form,
        'title': 'Регистрация'
    }
    return render(request, 'users/register_inspector.html', context)

@user_passes_test(is_superuser)
def edit_user(request, user_slug):
    user = User.objects.get(username=user_slug)
    if request.method == 'POST':
        form = UserProfileForm(data=request.POST, files=request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('users:user_list'))
    else:
        form = UserProfileForm(instance=user)
    context = {
        'form': form,
        'edit': True,
        'inspector': user,
        'title': 'Изменить данные'
    }
    return render(request, 'users/register_inspector.html', context)


def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(data=request.POST, files=request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('users:profile'))
    else:
        form = UserProfileForm(instance=request.user)
    context = {
        'form': form,
        'title': 'Информация'
    }
    return render(request, 'users/profile.html', context)


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('index'))


@user_passes_test(is_superuser)
def user_list(request): 
    perms = Permission.objects.all()
    inspectors_group = get_object_or_404(Group, name='ins')
    users = inspectors_group.user_set.all()
    context = {
        'users': users,
        'perms': perms,
        'title': 'Инспекторы'
    }
    return render(request, 'users/user_list.html', context)




@user_passes_test(is_superuser)
def point(request, user_slug):
    from users.models import User
    user = User.objects.get(username=user_slug)
    permissions = None
    if user.groups.all().first().name == 'ins':
        permissions = Permission.objects.filter(user=user).order_by('id')
    companies = Company.objects.all()
    company_list = {}
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
            company_list.update({
                company.name: {
                    'company': company,
                    'perm': has,
                    'areas': areas
                }
            })
        else:
            company_list.update({
                company.name: {
                    'company': company,
                    'perm': has,
                }
            })

    context = {
        'companies': company_list,
        'inspector': user,
        'title': 'Доступ'
    }
    return render(request, 'users/point.html', context)


@user_passes_test(is_superuser)
def grant_access(request, user_slug):
    if request.method == 'POST':
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
            check_deadline()
            check_expiry()
        return redirect('users:permission', user_slug=user_slug)
    else:
        return JsonResponse({'message': 'Недопустимый запрос.'}, status=400)


@user_passes_test(is_superuser)
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


@user_passes_test(is_superuser)
def delete_user(request, user_slug):
    try:
        user = User.objects.get(username=user_slug)
        user.delete()
    except User.DoesNotExist:
        pass
    return redirect('users:user_list')


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()
        if user:
            password = user.password 
            print('sending')
            send_mail(
                _('Your Password'),  
                _('Your password is: ') + password,  
                config('EMAIL_HOST_USER'),  
                [email],
            )
            print('sent')
            return render(request, 'users/login.html')
        else:
            return render(request, 'users/forgot_password.html')
    else:
        return render(request, 'users/forgot_password.html')


@user_passes_test(is_superuser)
def delete_company(request, company_slug):
    try:
        company = Company.objects.get(slug=company_slug)
        company.delete()
    except Company.DoesNotExist:
        pass
    return redirect('users:companies_list')
