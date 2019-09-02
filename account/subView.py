from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User

from account.models import Sepet


def adresFormPostForCheckOutView(request, Adress_Form, basket, basket_items):
    form = Adress_Form(request.POST)
    if form.is_valid():
        nform = form.save(commit=False)
        if request.POST.get("createaccount"):
            if not User.objects.filter(email=form.cleaned_data["mail"]):
                user = User.objects.create(username=form.cleaned_data["mail"], email=form.cleaned_data["mail"])
                user.set_password(request.POST.get("account_password"))
                user.save()
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            else:
                messages.add_message(request, messages.ERROR, "Bu mail ile zaten bir hesap var. Lütfen Giriş Yapın")
        if request.user.is_authenticated:
            nform.user = User.objects.get(id=request.user.id)
        nform.save()
        request.session["adresID"] = nform.id
    else:
        messages.add_message(request, messages.ERROR, form.errors)  # message errors


def userLogin(request, loginForm):
    if loginForm.is_valid():
        username = loginForm.cleaned_data.get("username")
        password = loginForm.cleaned_data.get("password")
        user = authenticate(username=username, password=password)
        login(request, user)
        messages.add_message(request, messages.SUCCESS, "Giriş Başarılı")
        return True
    else:
        messages.add_message(request, messages.ERROR, loginForm.errors)
        return False


def userRegister(request, registerForm):
    user = registerForm.save(commit=False)
    user.is_active = True
    password = registerForm.cleaned_data.get('password1')
    f_mail = registerForm.cleaned_data.get('email')
    if not User.objects.filter(email=f_mail).exists():
        user.set_password(password)
        user.is_staff = user.is_superuser = True
        user.save()
        messages.success(request, 'Kayıt işlemini tamamlandı')
    else:
        messages.add_message(request, messages.WARNING, 'Bu e-posta zaten kullanılıyor')


def userBasketUpdateAfterUserLogin(request, oldBasket, basket):
    Sepet.clone_old_basket_items_to_new_basket(Sepet, oldBasket, basket)
