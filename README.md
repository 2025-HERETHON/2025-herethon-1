# 2025-herethon-1
2025 여기톤 : HER+ETHON 1팀

<hr/>

- **서비스 소개**

  정치, 젠더 등 민감하지만 사회적으로 중요한 이슈를 학습하고 토론할 수 있는 플랫폼, 사상사이

- **기술 스택**

  <span>프론트엔드: </span> <img src="https://img.shields.io/badge/html-E34F26?style=for-the-badge&logo=html5&logoColor=white"> <img src="https://img.shields.io/badge/css-1572B6?style=for-the-badge&logo=css3&logoColor=white"> <img src="https://img.shields.io/badge/javascript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black">

  <span>백엔드: </span><img src="https://img.shields.io/badge/python-3776AB?style=for-the-badge&logo=python&logoColor=white"> <img src="https://img.shields.io/badge/django-092E20?style=for-the-badge&logo=Django&logoColor=white">

  <span>기획·디자인: </span> <img src="https://img.shields.io/badge/figma-F24E1E?style=for-the-badge&logo=figma&logoColor=white">

- **팀원 소개**
  <table border="" cellspacing="0" cellpadding="0" width="100%">
  <tr width="100%">
  <td align="center">이규빈</a></td>
  <td align="center">이은서</a></td>
  <td align="center">고소영</a></td>
  <td align="center">임제영</a></td>
  <td align="center">조주현</a></td>
  <td align="center">이연서</a></td>
  </tr>
  <tr width="100%">
  <td  align="center"><a href="https://imgbb.com/"><img src="https://i.ibb.co/sWXnzcJ/befbedf87e51f5b02aac8b882ada60fd-sticker.png" alt="befbedf87e51f5b02aac8b882ada60fd-sticker" border="0" width="90px"></a></td>
  <td  align="center"><a href="https://imgbb.com/"><img src="https://i.ibb.co/MRr1QMW/f67635fddb50d05f2d0f142e63b0ab5c-sticker.png" alt="f67635fddb50d05f2d0f142e63b0ab5c-sticker" border="0" width="90px"></a></td>
  <td  align="center"><a href="https://imgbb.com/"><img src="https://i.ibb.co/2KDG82L/d006044e5996d0023cd2e18425aa4677-sticker.png" alt="d006044e5996d0023cd2e18425aa4677-sticker" border="0" width="90px"></a></td>
  <td  align="center"><a href="https://imgbb.com/"><img src="https://i.ibb.co/sWXnzcJ/befbedf87e51f5b02aac8b882ada60fd-sticker.png" alt="befbedf87e51f5b02aac8b882ada60fd-sticker" border="0" width="90px"></a></td>
  <td  align="center"><a href="https://imgbb.com/"><img src="https://i.ibb.co/MRr1QMW/f67635fddb50d05f2d0f142e63b0ab5c-sticker.png" alt="f67635fddb50d05f2d0f142e63b0ab5c-sticker" border="0" width="90px"></a></td>
  <td  align="center"><a href="https://imgbb.com/"><img src="https://i.ibb.co/2KDG82L/d006044e5996d0023cd2e18425aa4677-sticker.png" alt="d006044e5996d0023cd2e18425aa4677-sticker" border="0" width="90px"></a></td>
  </tr>
  <tr width="100%">
  <td  align="center">기획·디자인</td>
  <td  align="center">기획·디자인</td>
  <td  align="center">백엔드</td>
  <td  align="center">백엔드</td>
  <td  align="center">프론트엔드</td>
  <td  align="center">프론트엔드</td>
     </tr>
      <tr width="100%">
        <td  align="center"><p></p><p></p><p></p></td>
        <td  align="center"><p></p><p></p><p></p></td>
        <td  align="center"><p>로그인/회원가입</p><p>아티클</p><p>정책 제안</p></td>
        <td  align="center"><p>커뮤니티</p><p>외부 API 연동</p><p>스크랩</p></td>
        <td  align="center"><p>아티클</p><p>정책 제안</p><p></p></td>
        <td  align="center"><p>로그인/회원가입</p>커뮤니티<p></p><p>스크랩</p></td>
     </tr>
  </table>

- **폴더 구조**

  ```
  📂 2025-HERETHON-1
  └─ theCommunityProject
   ├─ config
   │  ├─ __init__.py
   │  ├─ asgi.py
   │  ├─ settings.py
   │  ├─ urls.py
   │  └─ wsgi.py
   ├─ accounts
   │  ├─ templates
   │  │  ├─ login.html
   │  │  └─ signup.html
   │  ├─ __init__.py
   │  ├─ admin.py
   │  ├─ apps.py
   │  ├─ models.py
   │  ├─ tests.py
   │  ├─ urls.py
   │  └─ views.py
   ├─ articles
   │  ├─ templates
   │  │  ├─ article_detail.html
   │  │  └─ article_home.html
   │  ├─ templatetags
   │  │  ├─ __init__.py
   │  │  └─ custom_filters.py
   │  ├─ __init__.py
   │  ├─ admin.py
   │  ├─ apps.py
   │  ├─ form.py
   │  ├─ models.py
   │  ├─ tests.py
   │  ├─ urls.py
   │  └─ views.py
   ├─ community
   │  ├─ templates
   │  │  ├─ _comment_list.html
   │  │  ├─ community_detail_comment.html
   │  │  ├─ community_detail.html
   │  │  └─ community_home.html
   │  ├─ templatetags
   │  │  ├─ __init__.py
   │  │  └─ extra_dict.py
   │  ├─ __init__.py
   │  ├─ admin.py
   │  ├─ apis.py
   │  ├─ apps.py
   │  ├─ form.py
   │  ├─ models.py
   │  ├─ tests.py
   │  ├─ urls.py
   │  └─ views.py
   ├─ proposals
   │  ├─ templates
   │  │  ├─ proposals_detail.html
   │  │  └─ proposals_home.html
   │  ├─ __init__.py
   │  ├─ admin.py
   │  ├─ apps.py
   │  ├─ form.py
   │  ├─ models.py
   │  ├─ tests.py
   │  ├─ urls.py
   │  └─ views.py
   ├─ scraps
   │  ├─ templates
   │  │  ├─ scrapped_article.html
   │  │  ├─ scrapped_community.html
   │  │  └─ scrapped_proposal.html
   │  ├─ __init__.py
   │  ├─ admin.py
   │  ├─ apps.py
   │  ├─ models.py
   │  ├─ tests.py
   │  ├─ urls.py
   │  └─ views.py
   ├─ static
   │  ├─ css
   │  ├─ js
   │  └─ thumbnail
   ├─ manage.py
   └─ requirements.txt
  └─ .env.example
  ```

- **개발환경에서의 실행 방법**
  ```
  .env 파일 생성 후 .env.example 파일 참고해서 실제 값으로 변경
  $ cd theCommunityProject/
  $ pip install -r requirements.txt
  (버전이 맞지 않을 경우 $ pip install django 명령어 실행 후 위 명령어 실행)
  $ python manage.py makemigrations
  $ python manage.py migrate
  $ python manage.py runserver
  ```
<hr/>
