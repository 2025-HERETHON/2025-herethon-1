import re
from django.shortcuts import render, redirect
from .models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout

def signup(request):
    step = request.GET.get('step', '1')
    field_errors = {}

    # --- STEP 1 ---
    if step == '1':
        # 중복 확인용 GET 요청 처리
        if request.method == 'GET' and request.GET.get('check') == '1':
            username = request.GET.get('username', '').strip()
            if not username:
                modal_message = "아이디를 입력하세요."
            elif User.objects.filter(username=username).exists():
                modal_message = "이미 사용 중인 아이디입니다."
            else:
                modal_message = "사용 가능한 아이디입니다."
            return render(request, 'signup.html', {
                'step': '1',
                'modal_message': modal_message
            })

        # 비밀번호 확인용 POST 요청 처리
        elif request.method == 'POST' and request.POST.get('next') == '1':
            username = request.POST.get('username', '').strip()
            password = request.POST.get('password', '')
            repeat = request.POST.get('repeat', '')
            modal_message = None

            if not username:
                field_errors['username'] = "아이디를 입력하세요."
            elif User.objects.filter(username=username).exists():
                field_errors['username'] = "이미 사용 중인 아이디입니다."
                
            # 유효성 검사
            if not password:
                field_errors['password'] = "비밀번호를 입력하세요."
            elif not re.match(r'^(?=.*[a-zA-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$', password):
                field_errors['password'] = "영문, 숫자, 특수기호 포함 8자 이상이어야 합니다."

            if not repeat:
                field_errors['repeat'] = "비밀번호 확인란을 입력하세요."
            elif password != repeat:
                field_errors['repeat'] = "비밀번호가 일치하지 않습니다."

            if field_errors:
                return render(request, 'signup.html', {
                    'step': '1',
                    'username' : username,
                    'field_errors': field_errors,
                })

            # 성공: step2로 이동
            return render(request, 'signup.html', {
                'step': '2',
                'username': username,
                'password': password,
            })

    # --- STEP 2 ---
    elif step == '2' and request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        sex = request.POST.get('sex')
        birth_year = request.POST.get('birth_year')

        # 유저 생성
        User.objects.create_user(
            username=username,
            password=password,
            sex=sex,
            birth_year=birth_year
        )
        return render(request, 'signup.html', {
            'step': '3'
        })

    # 기본 진입 (step=1)
    return render(request, 'signup.html', {'step': '1'})


def login(request):
    if request.method=='POST':
        username=request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            print('로그인 성공')
            return redirect('articles:home')
        else: 
            error_message = "아이디 또는 비밀번호가 잘못되었습니다."
            return render(request, 'login.html', {'error_message': error_message})
   
    else:
        return render(request, 'login.html')
    
def logout(request):
    auth_logout(request)
    return redirect('accounts:login')