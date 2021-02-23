from django.template.loader import render_to_string
from django.core.signing import Signer

from billboard.settings import ALLOWED_HOSTS

# Создание цифровой подписи (с целью защиты от подделки)
# + Такое объявление почему-то экономит оперативную память
signer = Signer()
# Отправка писем с оповещением об активации
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
