from django.urls import path

from .views import index
from .views import other_page
from .views import BillBoardLoginView
from .views import BillBoardLogoutView
from .views import profile
from .views import ChangeUserInfoView
from .views import BillBoardPasswordChangeView
from .views import RegisterUserView, RegisterDoneView
from .views import user_activate
from .views import DeleteUserView
from .views import by_rubric

app_name = 'main'
urlpatterns = [

    path('accounts/register/activate/<str:sign>/', user_activate, name='register_activate'),
    path('accounts/register/done/', RegisterDoneView.as_view(), name='register_done'),
    path('accounts/register/', RegisterUserView.as_view(), name='register'),

    path('accounts/password/change/', BillBoardPasswordChangeView.as_view(), name='password_change'),

    path('accounts/profile/delete/', DeleteUserView.as_view(), name='profile_delete'),
    path('accounts/profile/change/', ChangeUserInfoView.as_view(), name='profile_change'),
    path('accounts/profile/', profile, name='profile'),

    # Путь к странцие входа
    path('accounts/login/', BillBoardLoginView.as_view(), name='login'),
    # Или: path('accounts/login/', LoginView.as_view(template_name='main/login.html'), name='login')
    # Имя шаблона выаодимой страницы передается через page
    path('accounts/logout/', BillBoardLogoutView.as_view(), name='logout'),

    # (by_rubric) должен быть до (other_page)
    # Т.к. в обратном случае
    # при просмотре списка маршрутов Django примет пристуствующий ключ рубрики за имя шаблона страницы
    # и запустит other_page, что породит 404 ошибку.
    path('<int:pk>/', by_rubric, name='by_rubric'),
    path('<str:page>/', other_page, name='other'),
    path('', index, name='index'),
]