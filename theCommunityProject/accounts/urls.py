from django.urls import path
from accounts import views

app_name = "accounts" # 이 앱의 namespace가 accounts임을 명시

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    # 중복 확인 버튼을 클릭할 때 내부적으로 get 요청
    path('check_username/', views.check_username, name='check_username'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
]