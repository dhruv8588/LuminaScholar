from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import resolve
from django.utils.http import urlsafe_base64_decode
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages, auth
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied

from paper.models import Author, Paper, Paper_Reviewer, Reviewer

from .utils import detectUser, send_verification_email

from .models import Role, additionalResearchArea, User
from .forms import additionalResearchAreaFormSet, UserForm


def register_user(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in!')
        return redirect('myAccount')
    elif request.method=='POST':
        form = UserForm(request.POST)
        formset = additionalResearchAreaFormSet(request.POST, prefix='research_areas')

        if form.is_valid() and formset.is_valid():
            user = form.save(commit=False)
            user.username = user.email.split("@")[0]
            password = User.objects.make_random_password()
            user.set_password(password)

            user.first_name = form.cleaned_data['first_name'].capitalize()
            user.last_name = form.cleaned_data['last_name'].capitalize()
            user.email = form.cleaned_data['email'].lower()
            user.institution = form.cleaned_data['institution'].capitalize()
            user.country = form.cleaned_data['country'].capitalize()
            user.state = form.cleaned_data['state'].capitalize()
            user.city = form.cleaned_data['city'].capitalize()
            
            user.save()

            try:
                author = Author.objects.get(email=user.email)
            except:
                author = None
            if author:
                if author:
                    author.user = user
                    author.first_name = user.first_name
                    author.last_name = user.last_name
                    author.institution = user.institution
                    author.country = user.country
                    author.state = user.state
                    author.city = user.city
                    author.save()

                    user.roles.add(Role.objects.get(name='AU'))
            try:
                reviewer = Reviewer.objects.get(email=user.email)
            except:
                reviewer = None
            if reviewer:
                reviewer.user = user    
                reviewer.first_name = user.first_name
                reviewer.last_name = user.last_name 
                reviewer.save()

                user.roles.add(Role.objects.get(name='REV'))

            for rform in formset:
                research_area = rform.save(commit=False)
                if research_area.name != '':
                    research_area.user = user
                    research_area.save()
                  
            mail_subject = 'Please activate your account'
            email_template = 'accounts/emails/account_verification.html'
            send_verification_email(request, user, mail_subject, email_template, password)

            messages.success(request, 'Your account has been registered sucessfully!')
            return redirect('login')
        else:
            print(form.errors)
            print(formset.errors)
    else:
        form = UserForm()
        formset = additionalResearchAreaFormSet(prefix='research_areas')
    context = {
        'form': form,
        'formset': formset,
    }
    return render(request, 'accounts/registerUser.html', context)


def edit_profile(request):
    changed = None
    if request.method=='POST':
        form = UserForm(request.POST, instance=request.user)
        formset = additionalResearchAreaFormSet(request.POST, prefix='research_areas', instance=request.user)
        if formset.is_valid():
            for rform in formset:
                research_area = rform.save(commit=False)
                if research_area.name != '':
                    research_area.user = request.user
                    research_area.save()
                elif research_area.name == '' and rform.instance.id:
                    rform.instance.delete()
        else:
            print(formset.errors)
 
        if form.is_valid():
            # user = form.save(commit=False) # This won't save research_areas
            # user.save()
            form.save()
        else:
            print(form.errors)

        changed = True    
    else:
        form = UserForm(instance=request.user)
        formset = additionalResearchAreaFormSet(prefix='research_areas', instance=request.user)
    
    context = {
        'form': form,
        'formset': formset,
        'changed': changed
    } 

    return render(request, 'accounts/edit_profile.html', context)


def check_username(request):
    username = request.POST.get('username')

    username_exists = False
    if User.objects.filter(username=username).exists():
        username_exists = True

    context = {
        'username_exists': username_exists
    }

    return render(request, 'partials/check_username.html', context)

def delete_research_area(request, pk):
    research_area = get_object_or_404(additionalResearchArea, id=pk)

    research_area.delete()
    
    return redirect('edit_profile')


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! Your account is activated.')
    else:
        messages.error(request, 'Invalid activation link')    
        
    return redirect('login')   

def login(request):
    if request.user.is_authenticated:
        return redirect('home')
    elif request.method=="POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
        
            return redirect('home')
        else:
            return redirect('login')
            
    
    return render(request, 'accounts/login.html')

def logout(request):
    auth.logout(request)
    return redirect('login')

@login_required(login_url='login')
def home(request):
    return render(request, 'home.html')


def forgot_password(request):
    if request.method=='POST':
        email = request.POST['email']

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email__exact=email)

            # send reset password email
            mail_subject = 'Your new Password'
            email_template = 'accounts/emails/reset_password.html'
            password = User.objects.make_random_password()
            user.set_password(password)
            user.save()
            send_verification_email(request, user, mail_subject, email_template, password) 

            messages.success(request, 'A new Password has been sent to your email address.')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exist')
            return redirect('forgot_password')
        
    return render(request, 'accounts/forgot_password.html')


def reset_password(request):
    changed = None
    if request.method=='POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password==confirm_password:
            user = request.user
            user.set_password(password)
            user.save()
            auth.login(request, user)
            changed = True
        else:
            changed = False

    context = {
        'changed': changed
    }        
    
    return render(request, 'accounts/reset_password.html', context)

