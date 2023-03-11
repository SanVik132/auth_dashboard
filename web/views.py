from django.shortcuts import render

# Create your views here.
from django.contrib.auth import views as auth_views
from web.forms import LoginForm, SignUpForm,FileForm
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import View, UpdateView
from web.models import User,Document
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from web.tokens import account_activation_token
from django.contrib.auth import login
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import logout as django_logout
from django.contrib.auth.mixins import LoginRequiredMixin


class LoginView(auth_views.LoginView):
    form_class = LoginForm
    template_name = 'login.html'


#Logout
class LogoutView(View):
    def get(self, request, *args, **kwargs):
        django_logout(request)
        messages.success(request, "Succesfully Loged Out...")
        return redirect("login")

class DashboardView(LoginRequiredMixin,View):
    form_class = FileForm
    template_name = 'profile.html'
    login_url = 'login'
    redirect_field_name = 'redirect_to'
    
    def get(self, request, *args, **kwargs):
        form = self.form_class()
        files = Document.objects.filter(user = request.user)
        print(files)
        return render(request, self.template_name, {'form': form,'files':files})
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()
            return redirect('/profile')
        else:
            print(form.errors)



# Sign Up View
class SignUpView(View):
    form_class = SignUpForm
    template_name = 'register.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():

            user = form.save(commit=False)
            user.is_active = False # Deactivate account till it is confirmed
            user.save()

            current_site = get_current_site(request)
            subject = 'Activate Your Account'
            message = render_to_string('account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject, message)

            messages.success(request, ('Please Confirm your email to complete registration.'))

            return redirect('login')

        return render(request, self.template_name, {'form': form})
    
class ActivateAccount(View):

    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            login(request, user)
            messages.success(request, ('Your account have been confirmed.'))
            return redirect('profile')
        else:
            messages.warning(request, ('The confirmation link was invalid, possibly because it has already been used.'))
            return redirect('profile')