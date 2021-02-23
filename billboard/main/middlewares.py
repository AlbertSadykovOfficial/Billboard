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
    return context
