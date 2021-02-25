from django.db import models
from django.contrib.auth.models import AbstractUser

# Для сигнала
from django.dispatch import Signal
from .utilities import send_activation_notification

# Для модели Poster
from .utilities import get_timestamp_path

# Сигнал для комменатриев
from django.db.models.signals import post_save
from .utilities import send_new_comment_notification

# Не забыть добавить в settings.py
# AUTH_USER_MODEL = 'main.AdvUser'
#
# Затем стоит сделать миграции
# python manage.py makemigrations
# python manage.py migrate
class AdvUser(AbstractUser):
    # Прошел ли пользователь процедурур активации
    is_activated = models.BooleanField(default=True,
                                    db_index=True,
                                    verbose_name='Прошел активацию?')
    # Желает ли пользователь получать уведомления
    send_messages = models.BooleanField(default=True,
                                        verbose_name='Отправлять оповещения о новых комментариях?')

    # Явное удлаение объявлений при удалении пользователя
    # Может не будет работать
    def delete(self, *args, **kwargs):
        for poster in self.poster_set.all():
            poster.delete()
        super().delete(*args, **kwargs)

    class Meta(AbstractUser.Meta):
        pass

# Rubric - базовая модель, в ней будут храниться рубрики и подрубрики,
# поэтому никаких параметров мы ей не задаем,
# пользователи не будут работать с этой моделью непосредственно
#
# После того как классы (модели) будут созданы,
# Следует произвести миграции:
#   python manage.py makemigrations
#   python manage.py migrate
class Rubric(models.Model):
    name = models.CharField(max_length=20, db_index=True, unique=True,
                            verbose_name='Название')
    order = models.SmallIntegerField(default=0, db_index=True,
                                     verbose_name='Порядок')
    super_rubric = models.ForeignKey('SuperRubric', on_delete=models.PROTECT, null=True, blank=True,
                                     verbose_name='Надрубрика')

# Диспетчер записей
class SuperRubricManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(super_rubric__isnull=True)

# Модель надрубрик
class SuperRubric(Rubric):
    objects = SuperRubricManager()

    def __str__(self):
        return self.name

    class Meta:
        proxy = True
        ordering = ('order', 'name')
        verbose_name = 'Надрубрика'
        verbose_name_plural = 'Надрубрики'

# Моедль подрубрик:
# Диспетчер будет отбирать лишь записи с непустым полум super_rubric (подрубркии)
class SubRubricManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(super_rubric__isnull=False)

class SubRubric(Rubric):
    objects = SubRubricManager()

    def __str__(self):
        # Название надрубрики - название подрубрики
        return '%s - %s' % (self.super_rubric.name, self.name)

    class Meta:
        proxy = True
        ordering = ('super_rubric__order', 'super_rubric__name', 'order', 'name')
        verbose_name = 'Подрубрика'
        verbose_name_plural = 'Подрубрики'

#Сигнал для отправки писем с требованием активации
user_registrated = Signal(providing_args=['instance'])

def user_registration_dispatcher(sender, **kwargs):
    send_activation_notification(kwargs['instance'])

user_registrated.connect(user_registration_dispatcher)


class Poster(models.Model):
    rubric = models.ForeignKey(SubRubric, on_delete=models.PROTECT, verbose_name='Рубрика')
    title = models.CharField(max_length=40, verbose_name='Товар')
    content = models.TextField(verbose_name='Описание')
    price = models.FloatField(default=0, verbose_name='Цена')
    contacts = models.TextField(verbose_name='Контакты')
    image = models.ImageField(blank=True, upload_to=get_timestamp_path, verbose_name='Изображение')
    author = models.ForeignKey(AdvUser, on_delete=models.CASCADE, verbose_name='Автор объявления')
    is_active = models.BooleanField(default=True, db_index=True, verbose_name='Выводить в списке?')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Опубликовано')

    # Переопределяем delete, т.к.:
    # Перед удалением записи,
    # Мы дполонительно удаляем все связанные картинки
    # При вызове метода, возникает сигнаг post_delete
    # (обр. django_cleanup), который удлить все файлы
    def delete(self, *args, **kwargs):
        for ai in self.additionalimage_set.all():
            ai.delete()
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = 'Объявление'
        verbose_name_plural = 'Объявления'
        ordering = ['-created_at']

# Модель дополнительных иллюстраций
class AdditionalImage(models.Model):
    # Прикрепление к модели
    # Чтобы удалятсья при ее удалении
    # НО НЕ РАБОТАЕТ, миниатюры НЕ удлаюятся
    poster = models.ForeignKey(Poster, on_delete=models.CASCADE, verbose_name='Объявление')
    image = models.ImageField(upload_to=get_timestamp_path, verbose_name='Изображение')

    class Meta:
        verbose_name = 'Дополнительная иллюстрация'
        verbose_name_plural = 'Дополнительные иллюстрации'

class Comment(models.Model):
    poster = models.ForeignKey(Poster, on_delete=models.CASCADE, verbose_name='Объявление')
    author = models.CharField(max_length=30, verbose_name='Автор')
    content = models.TextField(verbose_name='Содержание')
    is_active = models.BooleanField(default=True, db_index=True, verbose_name='Выводить на экран?')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Опубликован')

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        # Сортировка по увеличению даты и времени
        # Старые - в начале, новые - в конце
        ordering = ['created_at']

"""
!!!! НЕ РАБОТАЕТ
# Привязываем сигнал к обработчику после добавления комменария
def post_save_dispatcher(sender, **kwargs):
    author = kwargs['instance'].poster.author
    # Проверяем не запретил ли пользователь отправку оповещений
    if kwargs['created'] and author.send_messages:
        send_new_comment_notification(kwargs['instance'])
post_save.connect(post_save_dispatcher, sender=Comment)
"""