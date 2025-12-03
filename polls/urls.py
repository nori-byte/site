from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views


app_name = 'polls'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    path('<int:question_id>/vote/', views.vote, name='vote'),
    path('create/', views.create_question, name='create_question'),
    path('accounts/login/', views.LoginView.as_view(), name='login'),
    path('accounts/profile/delete/', views.DeleteUserView.as_view(), name='profile_delete'),
    path('accounts/profile/change/', views.ChangeUserInfoView.as_view(), name='profile_change'),
    path('accounts/password/change/', views.PasswordChangeView.as_view(), name='password_change'),
    path('accounts/profile/', views.profile, name='profile'),
    path('accounts/register/', views.RegisterUserView.as_view(), name='register'),
    path('accounts/logout/', views.logout_view, name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)