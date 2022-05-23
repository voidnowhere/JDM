from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from .forms import UserRegisterForm, UserUpdateForm
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.contrib.auth import login as auth_login
from cities_light.models import City
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from .utils import account_activation_token
from user.models import CustomUser
import uuid

User = get_user_model()


def register(request):
    results = City.objects.all
    if request.user.is_authenticated:
        messages.warning(request, f'Your are already logged in')
        return render(request, '/')
    else:
        if request.method == 'POST':
            form = UserRegisterForm(request.POST, request.FILES, )
            if form.is_valid():
                user = form.save(commit=False)
                username = form.cleaned_data.get('username')
                user.save()
                cust_user = CustomUser.objects.get(id=user.id)
                cust_user.email_token = uuid.uuid4()
                cust_user.save()
                uid64 = urlsafe_base64_encode(force_bytes(user.pk))
                domain = get_current_site(request).domain
                link = str(cust_user.email_token)
                activate_url = 'http://' + domain + '/user/email_verification/' + link
                email_body = 'Welcome ' + user.username + ' Please verify your account\n ' + activate_url
                email = EmailMessage(
                    'JDM',
                    email_body,
                    'jdmrent2022@gmail.com',
                    [user.email],
                )
                email.send(fail_silently=False)
                messages.success(request, f'Your account has been successfully created.')
                return redirect('/')
            else:
                return render(
                    request,
                    'user/register.html',
                    {
                        'form': form,
                        "City": results,
                        "username": request.POST['username'],
                        "first_name": request.POST['first_name'],
                        "last_name": request.POST['last_name'],
                        "email": request.POST['email'],
                        "phone": request.POST['phone'],
                        "idn": request.POST['idn'],
                        "address": request.POST['address'],
                        "city": request.POST['city'],
                        "birthday": request.POST['birthday'],
                        "city_id": int(request.POST['city']),
                    }
                )
        else:
            form = UserRegisterForm()
        messages.error(request, form.errors)
        return render(request, 'user/register.html', {'form': form, "City": results})


class LoginView(LoginView):
    template_name = 'user/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        username = form.get_user()
        user = User.objects.get(username=username)
        if user.is_active:
            auth_login(self.request, form.get_user())
            messages.success(self.request, f'You are now logged in as {user.username}')
            return redirect('/')


@login_required
def update(request):
    results = City.objects.all
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        if u_form.is_valid():
            u_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('user:profil')
    else:
        u_form = UserUpdateForm(instance=request.user)
    context = {
        'u_form': u_form,
        "City": results,
    }
    return render(request, 'user/profil.html', context)


def verify_email(request, token):
    client = CustomUser.objects.get(email_token=token)
    client.email_verified = True
    client.is_active = True
    client.save()
    return redirect('user:login')


def password_reset(request):
    if request.method == 'POST':
        try:
            user = CustomUser.objects.get(email=request.POST['email'])
            user.password_token = uuid4()
            user.save()
            domain = get_current_site(request).domain
            activate_url = 'http://' + domain + '/user/reset-password/' + str(user.password_token)
            email_body = 'Welcome ' + user.username + ' reset link\n ' + activate_url
            email = EmailMessage(
                'JDM',
                email_body,
                'jdmrent2022@gmail.com',
                [user.email],
            )
            email.send(fail_silently=False)
            messages.success(request, f'reset password link sent in email.')
            return redirect('home:index')
        except CustomUser.DoesNotExist:
            return redirect('home:index')
    else:
        return render(request, 'user/emailforestpassword.html')
