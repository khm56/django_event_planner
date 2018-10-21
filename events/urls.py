from django.urls import path
from .views import Login, Logout, Signup, home
from events import views

urlpatterns = [
	path('', home, name='home'),
    path('signup/', Signup.as_view(), name='signup'),
    path('login/', Login.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),
    path('dashboard/', views.concert_list, name='concert-dashboard'),
    path('dashboard/<int:concert_id>/', views.concert_detail, name='concert-detail'),
    path('concert/create/', views.concert_create, name='concert-create'),
    path('concert/update/<int:concert_id>/', views.concert_update, name='concert-update'),
]