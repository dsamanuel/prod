from django.shortcuts import render
from django.contrib.auth.views import LoginView
from django.views.generic import FormView
from .forms import CustomUserCreationForm, CustomUserChangeForm
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import PasswordResetView
# Create your views here.
from django.contrib.auth.decorators import login_required
from .models import Profile
from .forms import ProfileForm
from django.http.response import HttpResponse, HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404
import json
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from program.models import Program
import json
from django.db.models import Max, Avg,Sum,Count

from collections import defaultdict
from itertools import chain
from django import template
from easyaudit.models import CRUDEvent, RequestEvent, LoginEvent




 

register = template.Library()
import datetime




def jsonify(data):
    if isinstance(data, dict):
        return data
    else:
        return json.loads(data)
    

@login_required(login_url='login')
def user(request):
    user_activity = CRUDEvent.objects.filter(user=1).order_by('-id')[:12]
    for item in  user_activity:
        item.object_json_repr = jsonify(item.object_json_repr)
    qs1 = RequestEvent.objects.filter(user_id=1).values('datetime__date').annotate(id_count=Count('id', distinct=True))
    qs2 = RequestEvent.objects.filter(user_id=1, method='POST').values('datetime__date').annotate(count_login=Count('id', distinct=True))
    collector = defaultdict(dict)

    for collectible in chain(qs1, qs2):
        collector[collectible['datetime__date']].update(collectible.items())

    all_request = list(collector.values()) 

  
    
    context = {'user_activity':user_activity, 'all_request':all_request}
    return render(request, 'user/accounts.html', context)

@register.filter(name='jsonify')
def jsonify(data):
    if isinstance(data, dict):
        return data
    else:
        return json.loads(data)

@login_required(login_url='login')
def user_activity(request):
    qs1 = RequestEvent.objects.filter(user_id=request.user).values('datetime__date').annotate(id_count=Count('id', distinct=True))
    qs2 = RequestEvent.objects.filter(user_id=request.user, method='POST').values('datetime__date').annotate(count_login=Count('id', distinct=True))
  




    collector = defaultdict(dict)

    for collectible in chain(qs1, qs2):
        collector[collectible['datetime__date']].update(collectible.items())

    all_request = list(collector.values())

    context = {'all_request':all_request,}
    return render(request, 'user/partial/user_activity.html', context)



     

@login_required(login_url='login')
def activity_filter(request):
    query = request.GET.get('dates', '')
    print(query)
    print("hye")
    
    return render(request, 'user/partial/admin_boundary.html')

  
class Login(LoginView):
    template_name = 'user/registration/login.html'

class RegisterView(FormView):
    form_class = CustomUserCreationForm
    template_name = 'user/registration/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        form.save()  # save the user
        return super().form_valid(form)



class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'user/registration/password_reset.html'
    email_template_name = 'user/registration/password_reset_email.html'
    subject_template_name = 'user/registration/password_reset_subject'
    success_message = "We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy('account')
    



# Create your views here.
@login_required(login_url='login')
def userprofile(request):
 
    user = User.objects.get(pk=request.user.id)
    context = {'user': user}
    return render(request, 'user/partial/user_profile.html', context)

@login_required(login_url='login')
def add_profile(request): 
    user =User.objects.get(pk=request.user.id)
    if request.method == 'POST':
        user_form = CustomUserChangeForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return HttpResponse(
                status=204,
                headers={
                    'HX-Trigger': json.dumps({
                        "UserprofileChanged": None,
                        "showMessage": f"{user.email} updated."
                    })
                })
        else:
            user_form = CustomUserChangeForm(instance=user)
            profile_form = ProfileForm(instance=user.profile)
            
    else:
        profile_form = ProfileForm(instance=user.profile)
        user_form = CustomUserChangeForm(instance=user)
        return render(request, 'user/profile_form.html', {
        'profile_form': profile_form, 'user_form':user_form
    })
    return render(request, 'user/profile_form.html', {
         'user_form' :CustomUserChangeForm(instance=user),'profile_form': ProfileForm()})

@login_required(login_url='login')
def user_profile(request): 
    
    user = User.objects.get(pk=request.user.id)
    context = {'user': user}
        
    
    return render(request, 'user/partial/user_profile.html', context)


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('change_success')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'password_change_form.html', {
        'form': form
    })
def change_success(request):
    return render(request, 'partial/password_change_success.html')