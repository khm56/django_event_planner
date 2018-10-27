from django.urls import path
from .views import Login, Logout, Signup, home
from events import views

urlpatterns = [
	path('', home, name='home'),
    path('test/', views.test, name='test'),
    path('signup/', Signup.as_view(), name='signup'),
    path('login/', Login.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),
    path('dashboard/', views.concert_dashboard, name='concert-dashboard'),
    path('list/', views.concert_list, name='concert-list'),
    path('dashboard/<int:concert_id>/', views.concert_detail, name='concert-detail'),
    path('concert/create/', views.concert_create, name='concert-create'),
    path('concert/update/<int:concert_id>/', views.concert_update, name='concert-update'),
    # path('concert/<int:concert_id>/<int:quantity>/book/', views.concert_book, name='concert-book'),
    path('concert/<int:attend_id>/unbook/', views.unbook, name='concert-unbook'),
    path('profile/update/<int:profile_id>/', views.profile_update, name='profile-update'),
    path('users/<int:user_id>/follow/',views.user_follow ,name='user-follow'),
    path('users/followed/',views.followed_users ,name='followed-users'),
    path('organizer/detail/<int:organizer_id>',views.organizer_detail ,name='organizer-detail'),
]