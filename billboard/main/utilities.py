# Модуль utilities - хорошее место для кода
# не относящеося ни к моделям, ни к контроллерам

from django.template.loader import render_to_string
from django.core.signing import Signer

from billboard.settings import ALLOWED_HOSTS

# Получить время для картинок
from datetime import datetime
from os.path import splitext

# Создание цифровой подписи (с целью защиты от подделки)
# + Такое объявление почему-то экономит оперативную память
signer = Signer()

# Отправка писем с оповещением об активации
# МОЖЕТ БУДЕТ РАБОТАТЬ НА НАСТОЯЩЕМ СЕРВЕРЕ
# Тут упирается в localhost
# и пользователь не может получить письмо
# и перейти по ссылке, которая подствердит регистрацию
def send_activation_notification(user):
    # Домен на котором нахожится наш сайт (используем 1й в списке)
    # Если список доменов пуст, используем адрес отладочного веб-сервера
    if ALLOWED_HOSTS:
        host = 'http://' + ALLOWED_HOSTS[0]
    else:
        host = 'http://localhost:8000'

    context = {'user': user, 'host': host,
               'sign': signer.sign(user.username)}
    subject = render_to_string('email/activation_letter_subject.txt', context)
    body_text = render_to_string('email/activation_letter_body.txt', context)
    user.email_user(subject, body_text)

"""
    Подготовка к обработе выгрежнных файлов:
        pip install pillow
        pip install easy-thumbnails
        pip install django-cleanup
"""

def get_timestamp_path(instance, filename):
    return '%s%s' % (datetime.now().timestamp(), splitext(filename)[1])


# !!! НЕ РАБОТАЕТ !!!!
def send_new_comment_notification(comment):
    if ALLOWED_HOSTS:
        host = 'http://' + ALLOWED_HOSTS[0]
    else:
        host = 'http://localhost:8000'

    author = comment.poster.author
    context = {'author': author, 'host': host, 'comment': comment}
    subject = render_to_string('email/new_comment_letter_subject.txt', context)
    body_text = render_to_string('email/new_comment_letter_body.txt', context)
    author.email_user(subject, body_text)