from django.urls import include, path

from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('register_user/', views.register_user, name='register_user'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),

    path('login/', views.login, name="login"),
    path('logout/', views.logout, name="logout"),

    path('activate/<uidb64>/<token>/', views.activate, name='activate'),

    path('forgot_password/', views.forgot_password, name='forgot_password'),
    # path('author/forgot_password/', views.forgot_password, name='forgot_password_author'),
    # path('admin/forgot_password/', views.forgot_password, name='forgot_password_admin'),

    path('reset_password/', views.reset_password, name='reset_password'),

    path('conference/', include('conference.urls')),
    path('paper/', include('paper.urls')),

    path('registerUser/deleteResearchArea/<int:pk>/', views.delete_research_area, name="delete_research_area"),
]  

hmtx_urlpatterns = [
    path("check-username/", views.check_username, name='check-username'),
]

urlpatterns += hmtx_urlpatterns