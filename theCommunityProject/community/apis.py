# api.py
import google.generativeai as genai
import requests
import os
from dotenv import load_dotenv
import xml.etree.ElementTree as ET
import json

load_dotenv()  # .env 파일에서 환경변수를 읽어옴

GEMINI_KEY = os.getenv("GEMINI_KEY")
DBPIA_KEY = os.getenv("DBPIA_KEY")
KOSIS_KEY = os.getenv("KOSIS_KEY")
LIB_KEY = os.getenv('LIB_KEY')
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
    cleaned_text = cleaned_text.replace('\n', '')

    print(cleaned_text)

    #title, link = get_dbpia_response(cleaned_text)
    #개발 중인 부분
    papers, links = get_dbpia_response(cleaned_text)
    # statistics_data = cleaned_text.replace("'", '"')
    # statistics_data = "'" + '"' + statistics_data + '"' + "'"
    #
    # print(statistics_data)
    # print(json.loads(statistics_data))
    # statistics_data = json.loads(statistics_data)
    # statistics = get_kosis_response(statistics_data)

    words = cleaned_text.split(',', 1)

    first = words[0].strip() if len(words) > 0 else ""
    second = words[1].strip() if len(words) > 1 else ""

    lib_title, lib_author, lib_year = get_library_response(first, second)


    #check_prompt = papers[0] + ',' + papers[1] + "이 두 개는 dbpia에 등재된 논문 이름이야. 이 두 논문만을 인용해서" + prompt + (" 라는 의견을 뒷받침할 수 있도록 근거를 3개 작성해 줘. 줄바꿈을 꼭 해 주고, 각 근거의 뒤에 어떤 논문의 어떤 부분을 인용했는지 써 줘."
                                                 #" "
                                                   #)

    check_prompt = "다음은 최대 3개 이하의 DBpia 논문 제목입니다:" + papers[0] + ',' + papers[1] + "그리고 다음은 어떤 주제에 대한 사용자의 글입니다." + prompt + ("글 전문을 기반으로, 글에서 드러난 핵심 키워드 1순위와 입장(찬성, 반대, 중립), "
                                                                                                                              "질문 여부를 직접 파악하여 해당 입장을 지지하거나 분석적으로 설명할 수 있는 논문 기반 근거 3가지를 작성해 주세요. "
                                                                                                                              "조건은 다음과 같습니다: (1) 댓글이 찬성 또는 반대 입장일 경우 해당 입장을 지지하는 논문 근거 3가지를 작성해 주세요. "
                                                                                                                              "(2) 댓글이 중립 입장이거나 질문 형태일 경우, 분석적이거나 객관적인 관점을 제공하는 논문 근거 3가지를 작성해 주세요. "
                                                                                                                              "(3) 각 근거는 반드시 다음 3가지 요소를 포함해야 합니다: ① 간결한 요지(2문장 이내), ② 해당 논문 제목, ③ 인용 위치(가능하면 쪽수 또는 장/절 구조 등). "
                                                                                                                              "주의: 반드시 위 논문들 중에서만 인용해 주세요. 논문 외부 지식, 요약, 상식, 주관적 해석 등은 절대 사용하지 마세요. "
                                                                                                                              "출력 형식: 1. 근거 요지 문장 → 출처: 『논문 제목』, 인용 위치 / 2. 근거 요지 문장 → 출처: 『논문 제목』, 인용위치 / 3. 근거 요지 문장 → 출처: 『논문 제목』, 인용위치)"
                                                                                                                              "위 조건을 만족하는 응답이 불가능한 경우, '적절한 논문 근거를 찾을 수 없습니다.'라고만 작성해 주세요.")

    data = {
        "contents": [
            {
                "parts": [
                    {"text": check_prompt}
                ]
            }
        ],
    }
    response = requests.post(url, json=data, headers=headers)
    print(response.text)

    # 응답을 JSON으로 파싱해서 출력
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))

    response_json = response.json()
    if 'candidates' in response_json and response_json['candidates']:
        text = response_json['candidates'][0]['content']['parts'][0]['text']
        print(" Gemini 응답 내용:", text)
    else:
        print(" Gemini 응답 실패: candidates 없음")


    # 텍스트 변환
    cleaned_text = text.replace('**', '')  # 볼드 제거
    cleaned_text = cleaned_text.replace('*', '')

    return cleaned_text, links[0], links[1]


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

        #first_item = root.find('.//item')

        items = root.findall('.//item')  # 여러 item 태그 모두 찾기

        titles = ['', '']
        links = ['', '']
        i = 0
        # 첫 두 개만 슬라이싱
        for item in items[:2]:
            # title = item.find('title').text if item.find('title') is not None else "제목 없음"
            # author = item.find('author').text if item.find('author') is not None else "저자 없음"
            # year = item.find('pubyear').text if item.find('pubyear') is not None else "발행년도 없음"
            #
            # print(f"제목: {title} / 저자: {author} / 발행년도: {year}")

            if item is not None:
                title = item.findtext('title')
                title = title.replace('<!HS>', '')
                title = title.replace('<!HE>', '')
                link = item.findtext('link_url')
                if title == '' or None:
                    title = '논문 검색 결과가 없습니다.'
                    link = 'https://www.dbpia.co.kr/'
                print('title:', title)
                print('link:', link)
                titles[i] = title
                links[i] = link
                i += 1

        return titles, links

    print("API 호출 실패", response.status_code)
    return "논문 검색 결과가 없습니다.", 'https://www.dbpia.co.kr/'

def get_kosis_response(search_word):
    url = "https://kosis.kr/openapi/statisticsList.do?method=getList"
    params = {
        "method": "getList",
        "api_key": f"{KOSIS_KEY}",
        "format": "json",
        "jsonVD": "2.0",
        "orgId": "101",
        "tblId": "DT_1B040A3"

    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        try:
            data = response.json()
            print(data)
            return data
        except json.JSONDecodeError:
            print("응답 형식은 JSON이어야 합니다.", response.text)
            return {"error": "Invalid JSON response"}

def get_library_response(first, second):
    base_url = 'http://apis.data.go.kr/9720000/searchservice/basic'
    # params = {
    #     'serviceKey': LIB_KEY,
    #     'query': search_word,
    #     'pageNo': '1',
    #     'numOfRows': '5'
    # }
    # 이미 인코딩된 키이므로 작성 방식 변경

    search_word = first + " " + second
    url = f"{base_url}?serviceKey={LIB_KEY}&query={search_word}&pageNo=1&numOfRows=5"
    try:
        response = requests.get(url, verify=False)
    # response = requests.get(url, params=params, verify=False)
    # response.encoding = 'utf-8'

        if response.status_code == 200:
            root = ET.fromstring(response.text)
            # response 구조에 맞게 파싱 (예시는 일반적인 구조)
            items = root.findall('.//item')  # 'item' 태그 위치는 실제 응답 따라 달라질 수 있음
            for item in items:
                title = item.find('title').text if item.find('title') is not None else "제목 없음"
                author = item.find('author').text if item.find('author') is not None else "저자 없음"
                pub_year = item.find('pubYear').text if item.find('pubYear') is not None else "발행년도 없음"
                print(f"제목: {title}\n 저자: {author}\n 발행년도: {pub_year}\n")
                return title, author, pub_year
        print(f" 응답 실패: status={response.status_code}")
        return "응답 실패", "응답 실패", "응답 실패"
    except requests.exceptions.RequestException as e:
        print("API 요청 실패", e)
        return '실패', '실패', '실패'



