from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
# Для старницы входа
from django.contrib.auth.views import LoginView

# Для старницы выхода (дполнительно)
# Чтобы страица была доступна только зарегистрированным пользователям
from django.contrib.auth.mixins import LoginRequiredMixin

# Для страницы профиля
from django.contrib.auth.decorators import login_required

# Для страницы иземенения данных пользователя
from django.views.generic.edit import UpdateView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from .models import AdvUser
from .forms import ChangeUserInfoForm

# Правка пароля
from django.contrib.auth.views import PasswordChangeView

# Регистрация
from django.views.generic.edit import CreateView
from .forms import RegisterUserForm
from django.views.generic.base import TemplateView
from django.core.signing import BadSignature
from .utilities import signer

# Удаление
from django.views.generic.edit import DeleteView
from django.contrib.auth import logout
from django.contrib import messages

def index(request):
    return render(request, 'main/index.html')

def other_page(request, page):
    try:
        # К полученному имени выводимой страницы (page)
        # Добавляем расшиерение и префикс каталога
        # Затем пытаемся получить этот шаблон
        template = get_template('main/' + page + '.html')
    except TemplateDoesNotExist:
        raise Http404
    return HttpResponse(template.render(request=request))

# Страница входа
class BillBoardLoginView(LoginView):
    # задаем уть к шаблону
    template_name = 'main/login.html'

# Страница выхода
# Нужно, чтобы она была доступна только зарегистрированным пользователям
# Для этого добавляем класс LoginRequiredMixin
class BillBoardLogoutView(LoginRequiredMixin, LoginView):
    # задаем путь к шаблону
    template_name = 'main/logout.html'

# Страница профиля
# (Будет выводиться список объявлений пользователя)
# Страница доступна только авторизованным пользователям
@login_required
def profile(request):
    return render(request, 'main/profile.html')

# LoginRequiredMixin запрещает доступ к контроллеру готсям
# SuccessMessageMixin - вывод вслывающих сообщений об успешном выполнении операции
class ChangeUserInfoView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):

    model = AdvUser
    form_class = ChangeUserInfoForm
    template_name = 'main/change_user_info.html'
    success_url = reverse_lazy('main:profile')
    success_message = 'Личные данные пользователя изменены'

    # В процессе работы контроллер должен извлечь запись из модели AdvUser,
    # представляющую текущего пользователя,
    # для чего нужно получить ключ текущего пользователя (user.pk)
    #
    # Метод dispatch исполняется в САМОМ НАЧАЛЕ работы контроллера-класса,
    # поэтому это лучшее место для получения ключа
    def dispatch(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().dispatch(request, *args, **kwargs)

    # Извлечение исправляемой записи выполняется в get_object(),
    # которую конроллер-класс унаслеовал от SingleObjectMixin
    # queryset может быть как передан, так и не передан
    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)


class BillBoardPasswordChangeView(SuccessMessageMixin, LoginRequiredMixin, PasswordChangeView):
    template_name = 'main/password_change.html'
    success_url = reverse_lazy('main:profile')
    success_message = 'Пароль пользователя изменен'

# Контроллер регистрирующий пользователя
class RegisterUserView(CreateView):
    model = AdvUser
    template_name = 'main/register_user.html'
    form_class = RegisterUserForm
    success_url = reverse_lazy('main:register_done')

# Контроллер, выводящий сообщение об успшной регистрации
class RegisterDoneView(TemplateView):
    template_name = 'main/register_done.html'

def user_activate(request, sign):
    # Идетнтификатор sgn приходит в составе интернет-адреса
    try:
        # Извлекаем имя пользователя
        username = signer.usign(sign)
    except BadSignature:
        # Если подпись скомпроментирована, выводим старницу о неуспешной активации
        return render(request, 'main/bad_signature.html')
    # Ищем пользователя с именем
    user = get_object_or_404(AdvUser, username=username)
    if user.is_activated:
        template = 'main/user_is_activated.html'
    else:
        template = 'main/activation_done.html'
        # Делаем пользователя активным
        user.is_active = True
        user.is_activated = True
        user.save()
    return render(request, template)

class DeleteUserView(LoginRequiredMixin, DeleteView):
    model = AdvUser
    template_name = 'main/delete_user.html'
    success_url = reverse_lazy('main:index')

    # Сохраняем ключ пользователя
    def dispatch(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().dispatch(request, *args, **kwargs)

    # Выполнить выход перед удалением
    # После выполнения выхода сообщение пропадает
    # Поэтому мы создаем это сообщение самостоятельно
    def post(self, request, *args, **kwargs):
        logout(request)
        messages.add_message(request, messages.SUCCESS, 'Пользователь удален')
        return super().post(request, *args, **kwargs)

    # Извлечение удаляемой записи выполняется в get_object(),
    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)



def by_rubric(request, pk):
    pass

