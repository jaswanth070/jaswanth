from django.contrib import admin
from django.urls import path,include
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
#     path('admin/', admin.site.urls),
    path('',views.home,name='Home'),
    path('add_book/', views.add_book,name='add_book'),
    path('Home/',views.home,name='Home'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('login/',views.login,name='login'),
    path('about/',views.about,name='about'),
    path('maintenance/',views.under_dev,name='maintenance'),
    path('logout/',auth_views.LogoutView.as_view(),name='logout'),
    path('signup/',views.signup,name='signup'),
    path('activate/<uidb64>/<token>',views.activate,name='activate'),
    # path('signup/POST',views.signup,name='signup'),
    path("social-auth/",include('social_django.urls',namespace='social'))

]
