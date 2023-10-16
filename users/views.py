from django.contrib import auth, messages
from django.shortcuts import render, HttpResponseRedirect, redirect
from django.urls import reverse
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import user_passes_test
from products.models import Company
from users.forms import UserLoginForm, UserRegistrationForm, UserProfileForm
from users.models import User


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
        form = UserRegistrationForm(data=request.POST)
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
    from supervision.models import Permission
    perms = Permission.objects.all()
    users = User.objects.all()
    companies = Company.objects.all()
    context = {
        'users': users,
        'perms': perms,
        'companies': companies,
        'title': 'Пользователи'}
    return render(request, 'users/user_list.html', context)


@user_passes_test(is_superuser)
def create_company(request):
    from products.forms import CompanyForm
    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            instance = form.save()
            instance.save()
            return redirect('users:user_list')  # Redirect to a success page
    else:
        form = CompanyForm()

    return render(request, 'users/register_avia.html', {'form': form, 'title': 'Регистрация'})
