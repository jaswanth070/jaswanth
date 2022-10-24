from datetime import datetime
from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth.models import User
from django.contrib import messages
# from django.contrib.messages import constants as messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as LOGIN_CHK
from django.contrib.auth import logout as LOGOUT_CHK
from django.core.mail import EmailMessage, send_mail
from . import models
from .forms import LoginForm,UserRegistrationForm
from django.contrib.auth.decorators import login_required
from Library import settings 
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from . token import generate_token
from django.db import IntegrityError
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie


# Create your views here.

def login_excluded(redirect_to):
    """ This decorator kicks authenticated users out of a view """ 
    def _method_wrapper(view_method):
        def _arguments_wrapper(request, *args, **kwargs):
            if request.user.is_authenticated:
                return redirect(redirect_to) 
            return view_method(request, *args, **kwargs)
        return _arguments_wrapper
    return _method_wrapper

@login_required
def dashboard(request):
    return render(request,'dash_all.html',{'name':request.user.first_name})

@login_required
def dashboard_religious(request):
    return render(request,'dash_reg.html',{'name':request.user.first_name})
    
@login_required
def dashboard_biography(request):
    return render(request,'dash_bio.html',{'name':request.user.first_name})

@login_required
def dashboard_english(request):
    return render(request,'dash_eng.html',{'name':request.user.first_name})

@login_required
def dashboard_computers(request):
    return render(request,'dash_comp.html',{'name':request.user.first_name})


def under_dev(request):
    return render(request,'under_dev.html')

def contact(request):
    if request.method == "POST":
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        desc = request.POST.get('desc')
        contact = models.Contact(name=name,email=email,phone=phone,desc=desc,date = datetime.today())
        contact.save()
        messages.success(request,"Your message has been sent!")
    return render(request,'contact.html')

def about(request):
    return render(request,'about.html')


@login_excluded('dashboard')
def home(request):
    return render(request,'home.html')

@login_excluded('dashboard')
# @ensure_csrf_cookie
# @method_decorator(ensure_csrf_cookie)
# @method_decorator(csrf_protect)
# @csrf_protect
@ensure_csrf_cookie
def login(request):
    try:
        if request.method == 'POST':
             # AuthenticationForm_can_also_be_used
            form = LoginForm(request.POST)

            if form.is_valid():
                cd = form.cleaned_data
                user = authenticate(request,username=cd['username'], password=cd['password'])

                if user is not None:
                    # if user.is_active():
                    LOGIN_CHK(request, user)
                    messages.success(request,f"Successfully Logged In as {user.first_name} {user.   last_name}")
                    return render(request,'dash_temp.html',{'name': user.first_name})
                    # else:
                    #     messages.warning(request,"Please activate your account through the email sent     yo you")
                    #     return render(request,'login.html')

                else:
                    messages.warning(request,"If not activate your account through the email senet to   your registered email")
                    messages.warning(request,"Bad Credintails")
                    return render(request,'login.html')
        else:
            form = LoginForm()
            # messages.success(request,f"Successfully Logged")
            # return render(request,'login.html',{'form':form})
            # return render(request,'login.html')
    except:
        messages.warning(request, 'Activate your account through the email sent to your registered email')
        render(request,'login.html')
    return render(request,'login.html',{'form':form})

@login_excluded('dashboard')
def signup(request):
    try:      
        if request.method == 'POST':
            usr_name = request.POST['username']
            password = request.POST['password']
            email = request.POST['email']
            fname = request.POST['firstname']
            lname = request.POST['lastname']

            if User.objects.filter(username=usr_name).exists():
                messages.warning(request, 'Username Already Exists!!')
                render(request,'signup.html')

            if User.objects.filter(email=email).exists():
                messages.warning(request, 'Email Already taken!!')
                return render(request,'signup.html')
                render(request,'signup.html')

            if len(usr_name)>20:
                messages.warning(request, "Username must be under 20 charcters!!")
                return render(request,'signup.html')
                render(request,'signup.html')


            if not usr_name.isalnum():
                messages.warning(request, "Username must be Alpha-Numeric!!")
                return render(request,'signup.html')
                render(request,'signup.html')
            
            if len(password)<8:
                messages.warning(request, "Password must contain atleast 8 characters")
                return render(request,'signup.html')
                render(request,'signup.html')

            new_user = User.objects.create_user(usr_name,email,password)
            new_user.first_name = fname
            new_user.last_name = lname
            new_user.is_active = False
            new_user.save()

            # Welcome mail
            subject = "Welocome to E-Library!!"
            message = "Hello " + new_user.first_name +" "+ lname + "!! \n"+ "Welcome to E-LIBRARY!!     \nThank you for visiting our website.\nWe have also sent you a confirmation email, please confirm your email address. \n\nThanking You\nJaswanth Madiya"
            from_email = settings.EMAIL_HOST_USER
            to_list = [new_user.email]
            send_mail(subject, message,from_email, to_list,fail_silently=True)

            # Confiramation mail
            current_site = get_current_site(request)
            email_subject = 'Confirm your email @E-Library Login!!'
            message2 = render_to_string('email_confirmation.html',{
                'name': new_user.first_name,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(new_user.pk)),
                'token': generate_token.make_token(new_user)
            })
            email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [new_user.email],
            )
            email.fail_silently = True
            email.send()

            messages.warning(request, 'Activate your account through the link sent to your registered email')
            messages.success(request, 'Account Cretaed Successfully!')
            return render(request,'login.html')
    except(IntegrityError):
            messages.warning(request, 'Username Already Exists!!')
            render(request,'signup.html')
    return render(request,'signup.html')

def activate(request,uidb64,token,backend='django.contrib.auth.backends.ModelBackend'):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError,ValueError,OverflowError,User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser,token):
        myuser.is_active = True
        # user.profile.signup_confirmation = True
        myuser.save()
        # login(request,myuser)
        LOGIN_CHK(request, myuser,backend='django.contrib.auth.backends.ModelBackend')
        # fname = myuser.first_name
        # messages.success(request, "Your Account has been activated!!")
        return render(request,'dashboard.html',{'name': myuser.first_name})
    else:
        return render(request,'activation_failed.html')
   

def add_book(request):
    if request.method == "POST":
        name = request.POST['name']
        author = request.POST['author']
        isbn = request.POST['isbn']
        category = request.POST['category']
 
        books = models.Book.objects.create(name=name, author=author, isbn=isbn, category=category)
        books.save()
        alert = True
        return render(request, "add_book.html", {'alert':alert})
    return render(request, "add_book.html")

@login_required
def logout(request):
    LOGOUT_CHK(request)
    # auth_logout(request)
    # messages.success(request, "Logged Out Successfully")
    return render(request,'home.html')


