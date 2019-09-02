from django import forms
from .models import Adress
from django.contrib.auth import authenticate
from django.contrib.auth.models import User


class Adress_Form(forms.ModelForm):
    class Meta:
        model = Adress
        exclude = ['cargo']

    def __init__(self, *args, **kwargs):
        super(Adress_Form, self).__init__(*args, **kwargs)
        self.fields['user'].required = False
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'input-text'


class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, label='Kullanıcı Adı')
    password = forms.CharField(max_length=100, label='Parola', widget=forms.PasswordInput)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError("Kullanıcı adını veya şifreyi yanlış girdiniz!")
        return super(LoginForm, self).clean()


class RegisterForm(forms.ModelForm):
    username = forms.CharField(max_length=100, label='Kullanıcı Adı',
                               widget=forms.TextInput(attrs={'class': "woocommerce-Input woocommerce-Input--text input-text"}), )
    password1 = forms.CharField(max_length=100, label='Parola',
                                widget=forms.PasswordInput(attrs={'class': "woocommerce-Input woocommerce-Input--text input-text"}), )
    password2 = forms.CharField(max_length=100, label='Parola Doğrulama',
                                widget=forms.PasswordInput(attrs={'class': "woocommerce-Input woocommerce-Input--text input-text"}), )
    email = forms.EmailField(max_length=200, help_text='Gerekli',
                             widget=forms.EmailInput(attrs={'class': "woocommerce-Input woocommerce-Input--text input-text"}), )

    class Meta:
        model = User
        fields = [
            'username',
            'password1',
            'password2',
            'email',
        ]

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Şifreler eşleşmiyor!")
        return password2
