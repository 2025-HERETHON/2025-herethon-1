# api.py
import google.generativeai as genai
import requests
import os
from dotenv import load_dotenv
import xml.etree.ElementTree as ET

load_dotenv()  # .env 파일에서 환경변수를 읽어옴

GEMINI_KEY = os.getenv("GEMINI_KEY")
DBPIA_KEY = os.getenv("DBPIA_KEY")
search_word = ""

def get_gemini_response(prompt):
    """
    GEMINI AI
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_KEY}"  # API 엔드포인트 URL

    headers = {
        "Content-Type": "application/json"  # 요청 본문이 JSON 형식임을 명시
    }
    data = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
    }
    response = requests.post(url, json=data, headers=headers)
    response_json = response.json()
    text = response_json['candidates'][0]['content']['parts'][0]['text']

    #텍스트 변환
    cleaned_text = text.replace('**', '')  # 볼드 제거
    cleaned_text = cleaned_text.replace('*', '')

    print(cleaned_text)

    title, link = get_dbpia_response(cleaned_text)
    #개발 중인 부분 주석 처리
    # paper = get_dbpia_response(cleaned_text)
    #
    # check_prompt = paper + ("이 자료들이 ") + prompt + ("의견을 뒷받침하기에 적당한지 판단하고, 가장 적합한 것을 한 개 이상 남겨 줘. "
    #                                              "남은 자료들을 다시 텍스트로 정리해서 가독성 좋게 보여 줘. "
    #                                                "그리고 링크로 된 자료들은 링크 url을 마지막에 포함해 줘")
    #
    # data = {
    #     "contents": [
    #         {
    #             "parts": [
    #                 {"text": check_prompt}
    #             ]
    #         }
    #     ],
    # }
    # response = requests.post(url, json=data, headers=headers)
    # response_json = response.json()
    # text = response_json['candidates'][0]['content']['parts'][0]['text']
    #
    # # 텍스트 변환
    # cleaned_text = text.replace('**', '')  # 볼드 제거
    # cleaned_text = cleaned_text.replace('*', '')

    return title, link #cleaned_text


def get_dbpia_response(search_word):
    """
    DBpia
    """
    # 논문 DBPia 접근
    url = f"http://api.dbpia.co.kr/v2/search/search.xml?key={DBPIA_KEY}&target=se&searchall={search_word}"

    response = requests.get(url)
    if response.status_code == 200:
        root = ET.fromstring(response.content)  # XML 파싱
        # print(ET.tostring(root, encoding='unicode'))  # 디버그용 전체 응답 출력
        # root = ET.tostring(root, encoding='unicode')

        first_item = root.find('.//item')

        if first_item is not None:
            title = first_item.findtext('title')
            title = title.replace('<!HS>', '')
            title = title.replace('<!HE>', '')
            link = first_item.findtext('link_url')
            if title == '' or None:
                title = '논문 검색 결과가 없습니다.'
                link = 'https://www.dbpia.co.kr/'
            print('title:', title)
            print('link:', link)
            return title, link

    print("API 호출 실패", response.status_code)
    return "논문 검색 결과가 없습니다.", 'https://www.dbpia.co.kr/'
