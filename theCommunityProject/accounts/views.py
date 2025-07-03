import re
from django.shortcuts import render, redirect
from .models import User
from django.views.decorators.http import require_GET
from django.http import JsonResponse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout

def signup(request):
    if request.method == 'POST':
        password = request.POST.get('password', '')
        repeat = request.POST.get('repeat', '')

        # 비밀번호 제한 사항 (8자 이상, 영문, 숫자, 특수기호 최소 1개씩)
        pattern = r'^(?=.*[a-zA-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
        if password != repeat:
            error_message = "비밀번호가 일치하지 않습니다."
            return render(request, 'signup.html', {'error_message': error_message})

        if not re.match(pattern, password):
            error_message = "영문, 숫자, 특수기호를 포함하여 8자 이상 입력해 주세요."
            return render(request, 'signup.html', {'error_message': error_message})

        new_user = User.objects.create_user(
            username=request.POST['username'],
            password=request.POST['password'],
            sex=request.POST['sex'],
            birth_year=request.POST['birth_year']
        )
        print('회원가입 성공')
        return redirect('home')

    else:
        return render(request, 'signup.html')

# 아이디 중복 확인용 함수
@require_GET 
def check_username(request):
    username = request.GET.get('username')
    
    is_taken = User.objects.filter(username=username).exists()
    return JsonResponse({'is_taken': is_taken})

def login(request):
    if request.method=='POST':
        username=request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            print('로그인 성공')
            return redirect('home')
        else: 
            error_message = "아이디 또는 비밀번호가 잘못되었습니다."
            return render(request, 'login.html', {'error_message': error_message})
   
    else:
        return render(request, 'login.html')
    
def logout(request):
    auth_logout(request)
    print('로그아웃 성공')
    return redirect('home')