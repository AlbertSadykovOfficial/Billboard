from .models import SubRubric

# Нам надо, чтобы в панеле навигаций
# выводились созданные к данному моменту рубрики
#
# Нужно поместить в контекст каждого шаблона переменную,
# в которой хранится список подрубрик
# (на его основе будут формироваться пункты панели навигации)
#
# Обработчик контекста
def billboard_context_processor(request):
    context = {}
    context['rubrics'] = SubRubric.objects.all()
    # Для формирования адоесов в гиперссылках навигатора
    context['keyword'] = ''
    # Добавим к интернет-адресам гиперссылок, указывающих на страницы сведений об объявлении
    context['all'] = ''
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            context['keyword'] = '?keyword=' + keyword
            context['all'] = context['keyword']
    if 'page' in request.GET:
        page = request.GET['page']
        if page != '1':
            if context['all']:
                context['all'] += '&page=' + page
            else:
                context['all'] = '?page=' + page
    return context
