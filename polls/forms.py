from django import forms
from .models import AdvUser
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from .models import Question, Choice


class ChangeUserInfoForm(forms.ModelForm):
    email = forms.EmailField(required=True, label='Адрес электронной почты')
    class Meta:
        model = AdvUser
        fields = ('username', 'email', 'first_name', 'last_name', 'avatar')
        labels = {'avatar': 'Аватар'}


class RegisterUserForm(forms.ModelForm):
    email = forms.EmailField(required=True, label='Адрес электронной почты')
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput,
                                help_text=password_validation.password_validators_help_text_html())
    password2 = forms.CharField(label='Пароль (повторно)', widget=forms.PasswordInput,
                                help_text='Повторите тот же самый пароль еще раз')
    avatar = forms.ImageField(label='Аватар', required=True)


    def clean_password1(self):
        password = self.cleaned_data['password1']
        if password:
            password_validation.validate_password(password)
        return password

    def clean(self):
        super().clean()
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            errors = {'password2': ValidationError('Введенные пароли не совпадают')}
            raise ValidationError(errors)

    def save(self, commit=True):
        user = super().save(commit=True)
        user.set_password(self.cleaned_data['password1'])
        user.is_active = True
        user.is_activated = True
        if commit:
            user.save()
        return user

    class Meta:
        model = AdvUser
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'avatar')


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['title_text', 'question_text', 'image', 'short_description']
        labels = {'title_text': 'Заголовок вопроса', 'question_text': 'Текст вопроса', 'image': 'Изображение', 'short_description': 'Краткое описание' }


class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['choice_text']
        labels = {'choice_text': 'Вариант ответа'}


ChoiceFormSet = forms.inlineformset_factory(Question, Choice, form=ChoiceForm, extra=3, can_delete=False)