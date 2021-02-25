from django.contrib import admin
from .models import AdvUser
# Для Инструментов администрирования
from .utilities import send_activation_notification
import datetime

# Для администрирования рубрик
from .models import SuperRubric, SubRubric
from .forms import SubRubricForm

# Администрирование объявлений
from .models import Poster, AdditionalImage

# Регистрируем модель пользователя
#admin.site.register(AdvUser)

# Инструменты администрирования:

# (НЕ РАБОТАЕТ)

#  Рассылка пользователямписем с предписанием выполнить активацию
# НЕ РАБОТАЕТ
# МОЖЕТ БУДЕТ РАБОТАТЬ НА НАСТОЯЩЕМ СЕРВЕРЕ
# Тут, наверное, все упирается в localhost
# Пользователь не может получить письмо
# и перейти по ссылке, которая подтвердит регистрацию
# Поэтому в БД приходится вручную уставнавливать is_active = 1
def send_activation_notifications(modeladmin, request, queryset):
    for rec in queryset:
        if not rec.is_activated:
            # Рассылаем тем, кто не выполнил активацию
            send_activation_notification(rec)
    modeladmin.message_user(request, 'Письма с оповещениями отправлены')

send_activation_notifications.short_description = 'Отправка писем с оповещениями об активации'

class NonactivatedFilter(admin.SimpleListFilter):
    title = 'Прошли активацию?'
    parameter_name = 'actstate'

    def lookups(self, request, model_admin):
        return (
                    ('activated', 'Прошли'),
                    ('threedays', 'Не прошли более 3 дней'),
                    ('week', 'Не прошли более недели'),
               )

    def queryset(self, request, queryset):
        val = self.value()
        if val == 'activated':
            return queryset.filter(is_active=True, is_activated=True)
        if val == 'threedays':
            d = datetime.date.today() - datetime.timedelta(days=3)
            return queryset.filter(is_active=False, is_activated=False, date_joined__date__lt=d)
        if val == 'week':
            d = datetime.date.today() - datetime.timedelta(weeks=1)
            return queryset.filter(is_active=False, is_activated=False, date_joined__date__lt=d)

class AdvUserAdmin(admin.ModelAdmin):
    # Вы одим строковое предствалени записи (имя пользователя как в AbstractUser)
    list_display = ('__str__', 'is_activated', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = (NonactivatedFilter,)
    fields = (('username', 'email'), ('first_name', 'last_name'),
              ('send_messages', 'is_active', 'is_activated'),
              ('is_staff', 'is_superuser'),
              'groups', 'user_permissions',
              ('last_login', 'date_joined')
              )
    readonly_fields = ('last_login', 'date_joined')
    actions = (send_activation_notifications,)

admin.site.register(AdvUser, AdvUserAdmin)

# Все работы над подрубриками и подрубриками будут
# поводится средствами Администартивного сайта
# Поэтому для моделей нужно написать редакторы и вспомог. класы
#
class SubRubricInline(admin.TabularInline):
    model = SubRubric

class SuperRubricAdmin(admin.ModelAdmin):
    # В редакторе надрубрик нам не надо выводить сами надрубрики
    execlude = ('super_rubric',)
    inlines = (SubRubricInline,)

admin.site.register(SuperRubric, SuperRubricAdmin)

class SubRubricAdmin(admin.ModelAdmin):
    form = SubRubricForm

admin.site.register(SubRubric, SubRubricAdmin)

# Инструменты администрирования объявлений

# Работа с дополнительными иллюстрациями
class AdditionalImageInline(admin.TabularInline):
    model = AdditionalImage

# Редактор объявления
class PosterAdmin(admin.ModelAdmin):
    list_display = ('rubric', 'title', 'content', 'author', 'created_at')
    # Выводим ('rubric', 'author') в 1 строку (для компактности)
    fields = (('rubric', 'author'), 'title', 'content', 'price',
              'contacts', 'image', 'is_active')
    inlines = (AdditionalImageInline,)

admin.site.register(Poster, PosterAdmin)