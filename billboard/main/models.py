from django.db import models
from django.contrib.auth.models import AbstractUser

# Для сигнала
from django.dispatch import Signal
from .utilities import send_activation_notification

# Не забыть добавить в settings.py
# AUTH_USER_MODEL = 'main.AdvUser'
#
# Затем стоит сделать миграции
# python manage.py makemigrations
# python manage.py migrate
class AdvUser(AbstractUser):
    # Прошел ли пользователь процедурур активации
    is_active = models.BooleanField(default=True,
                                    db_index=True,
                                    verbose_name='Прошел активацию?')
    # Желает ли пользователь получать уведомления
    send_messages = models.BooleanField(default=True,
                                        verbose_name='Отправлять оповещения о новых комментариях?')

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