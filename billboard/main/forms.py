from django import forms
from .models import AdvUser

from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError

# Формы добавления, удаления и правки объявлений
from django.forms import inlineformset_factory
from .models import Poster, AdditionalImage

# Формы добавления, комментариев
from captcha.fields import CaptchaField
from .models import Comment

from .models import user_registrated

from .models import SuperRubric, SubRubric

# Форма, связанная с моделю AdvUser
# В форму будут заноситься новые личные данные
class ChangeUserInfoForm(forms.ModelForm):
    # Выполняем полное объявление поля email модели AdvUser
    # Так как оно обязательно
    email = forms.EmailField(required=True,
                             label='Адрес электронной почты')
    class Meta:
        model = AdvUser
        fields = ('username', 'email', 'first_name', 'last_name', 'send_messages')


# НЕ РАБОТАЕТ, ПОЧИНИТЬ
class RegisterUserForm(forms.ModelForm):
    # Полное объявление - обязательно для заполнения:
    email = forms.EmailField(required=True,
                             label='Адрес электронной почты')
    password1 = forms.CharField(label='Пароль',
                                widget=forms.PasswordInput,
                                help_text=password_validation.password_validators_help_text_html())
    password2 = forms.CharField(label='Пароль (повторно)',
                                widget=forms.PasswordInput,
                                help_text='Введите тот же самый пароль еще раз для проверки')
    # Валидация пароля
    def clean_password1(self):
        password1 = self.cleaned_data['password1']
        if password1:
            password_validation.validate_password(password1)
        return password1

    # Проверка совпадения введеннных паролей
    def clean(self):
        super().clean()
        #cleaned_data = super(RegisterUserForm, self).clean()
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']
        if password1 and password2 and password1 != password2:
            errors = {'password2': ValidationError(
                                                    'Введенные пароли не совпадают',
                                                    code='password_mismatch'
                                                )
            }
            raise ValidationError(errors)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        # Выставляем, что пользователь при сохранении:
        # Не активный и НЕ выполнил процедуру активации
        user.is_active = False
        user.is_activated = False
        if commit:
            user.save()
        # Отправляем сигнал, чтобы отослать письмо с требованием активации
        user_registrated.send(RegisterUserForm, instance=user)
        return user

    class Meta:
        model = AdvUser
        fields = ('username', 'email', 'password1', 'password2',
                  'first_name', 'last_name', 'send_messages')


# Форма
# Для работы с подрубриками, поле надрубркии - обязательно
class SubRubricForm(forms.ModelForm):
    super_rubric = forms.ModelChoiceField(
        queryset=SuperRubric.objects.all(),
        # Убрать пустой пункт у раскрывающегося списка
        # Так, это будет сигнализировать о том, что поле обязательное
        empty_label=None,
        label='Надрубрика',
        required=True
    )
    class Meta:
        model = SubRubric
        fields = '__all__'

#
class SearchForm(forms.Form):
    keyword = forms.CharField(required=False, max_length=20, label='')


# Формы добавления, удаления и правки объявлений
# В форме выводим все поля модели Poster
# Поле author спрячем, значение туда занесется автоматически
class PosterForm(forms.ModelForm):
    class Meta:
        model = Poster
        fields = '__all__'
        widgets = {'author': forms.HiddenInput}

# Набор форм
AIFormSet = inlineformset_factory(Poster, AdditionalImage, fields='__all__')


class UserCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        # Делаем так, чтобы комментарий всегда выводился на странце
        exclude = ('is_active',)
        widgets = {'poster': forms.HiddenInput}

class GuestCommentForm(forms.ModelForm):
    captcha = CaptchaField(label='Введите текст с картинке',
                           error_messages={'invalid': 'Неправильный текст'})
    class Meta:
        model = Comment
        exclude = ('is_active',)
        widgets = {'poster': forms.HiddenInput}
