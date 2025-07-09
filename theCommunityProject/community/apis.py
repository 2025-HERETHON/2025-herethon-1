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

def get_gemini_response(content, prompt):
    """
    GEMINI AI
    """

    #1. 키워드 추출
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

    #키워드 분리
    words = cleaned_text.split(',', 1)
    first = words[0].strip() if len(words) > 0 else ""
    second = words[1].strip() if len(words) > 1 else ""

    # KOSIS 통계
    kosis_data = get_kosis_response(first)
    # 만약 kosis_data가 dict이면 문자열로 변환
    if isinstance(kosis_data, dict):
        # 예: JSON 문자열로 변환
        kosis_data = json.dumps(kosis_data, ensure_ascii=False)
    else:
        kosis_data = str(kosis_data)
    check_prompt = "다음은 kosis 통계 자료입니다:" + kosis_data + ',' + "그리고 다음은 어떤 주제에 대한 사용자의 글입니다." + content + (
        "글 전문을 기반으로, 글에서 드러난 핵심 키워드 1순위와 입장(찬성, 반대, 중립), "
        "질문 여부를 직접 파악하여 해당 입장을 지지하거나 분석적으로 설명할 수 있는 자료 기반 근거 1가지를 작성해 주세요. "
        "조건은 다음과 같습니다: (1) 댓글이 찬성 또는 반대 입장일 경우 해당 입장을 지지하는 근거 1가지를 작성해 주세요. "
        "(2) 댓글이 중립 입장이거나 질문 형태일 경우, 분석적이거나 객관적인 관점을 제공하는 근거 1가지를 작성해 주세요. "
        "(3) 각 근거는 반드시 다음 3가지 요소를 포함해야 합니다: ① 간결한 요지(2문장 이내), ② 해당 자료 제목 "
        "주의: 반드시 위 자료를 기반으로만 인용해 주세요. 외부 지식, 요약, 상식, 주관적 해석 등은 절대 사용하지 마세요. "
        "출력 형식: 1. 근거 요지 문장 → 출처: 『자료 제목』"
        "위 조건을 만족하는 응답이 불가능한 경우, '적절한 근거를 찾을 수 없습니다.'라고만 작성해 주세요.")

    data = {
        "contents": [
            {
                "parts": [
                    {"text": check_prompt}
                ]
            }
        ],
    }

    # 근거 문장 받기
    kosis_response = requests.post(url, json=data, headers=headers)
    kosis_response_json = kosis_response.json()

    if 'candidates' in kosis_response_json and kosis_response_json['candidates']:
        text = kosis_response_json['candidates'][0]['content']['parts'][0]['text']
        print(" Gemini 응답 내용:", text)
    else:
        print(" Gemini 응답 실패: candidates 없음")

    # 텍스트 변환
    kosis_response = text.replace('**', '')  # 볼드 제거
    kosis_response = kosis_response.replace('*', '')


    # 국회도서관 검색
    lib_title, lib_author, lib_year, lib_link = get_library_response(first, second)

    print(lib_title, lib_author, lib_year, lib_link)

    check_prompt = "다음은 국회도서관 자료입니다:" + lib_title + ',' + lib_author + ',' +  "그리고 다음은 어떤 주제에 대한 사용자의 글입니다." + content + ("글 전문을 기반으로, 글에서 드러난 핵심 키워드 1순위와 입장(찬성, 반대, 중립), "
                                                        "질문 여부를 직접 파악하여 해당 입장을 지지하거나 분석적으로 설명할 수 있는 자료 기반 근거 1가지를 작성해 주세요. "
                                                        "조건은 다음과 같습니다: (1) 댓글이 찬성 또는 반대 입장일 경우 해당 입장을 지지하는 근거 1가지를 작성해 주세요. "
                                                        "(2) 댓글이 중립 입장이거나 질문 형태일 경우, 분석적이거나 객관적인 관점을 제공하는 근거 1가지를 작성해 주세요. "
                                                        "(3) 각 근거는 반드시 다음 3가지 요소를 포함해야 합니다: ① 간결한 요지(2문장 이내), ② 해당 자료 제목 "
                                                        "주의: 반드시 위 자료를 기반으로만 인용해 주세요. 외부 지식, 요약, 상식, 주관적 해석 등은 절대 사용하지 마세요. "
                                                        "출력 형식: 1. 근거 요지 문장 → 출처: 『자료 제목』"
                                                        "위 조건을 만족하는 응답이 불가능한 경우, '적절한 근거를 찾을 수 없습니다.'라고만 작성해 주세요.")

    data = {
        "contents": [
            {
                "parts": [
                    {"text": check_prompt}
                ]
            }
        ],
    }

    # 근거 문장 받기
    lib_response = requests.post(url, json=data, headers=headers)
    lib_response_json = lib_response.json()

    if 'candidates' in lib_response_json and lib_response_json['candidates']:
        text = lib_response_json['candidates'][0]['content']['parts'][0]['text']
        print(" Gemini 응답 내용:", text)
    else:
        print(" Gemini 응답 실패: candidates 없음")

    # 텍스트 변환
    lib_response = text.replace('**', '')  # 볼드 제거
    lib_response = lib_response.replace('*', '')

    # 논문에 대한 Gemini 논거 생성용 프롬프트 구성
    papers, links = get_dbpia_response(cleaned_text)
    check_prompt = "다음은 최대 3개 이하의 DBpia 논문 제목입니다:" + papers[0] + ',' + papers[1] + ',' + papers[2] + "그리고 다음은 어떤 주제에 대한 사용자의 글입니다." + content + ("글 전문을 기반으로, 글에서 드러난 핵심 키워드 1순위와 입장(찬성, 반대, 중립), "
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

    #dbpia 근거 문장 받기
    dbpia_response = requests.post(url, json=data, headers=headers)
    dbpia_response_json = dbpia_response.json()

    if 'candidates' in dbpia_response_json and dbpia_response_json['candidates']:
        text = dbpia_response_json['candidates'][0]['content']['parts'][0]['text']
        print(" Gemini 응답 내용:", text)
    else:
        print(" Gemini 응답 실패: candidates 없음")


    # 텍스트 변환
    dbpia_response = text.replace('**', '')  # 볼드 제거
    dbpia_response = dbpia_response.replace('*', '')

    total_text = dbpia_response + lib_response + kosis_response

    return total_text, links[0], links[1], links[2], lib_link


def get_dbpia_response(search_word):
    """
    DBpia
    """
    # 논문 DBPia 접근
    url = f"http://api.dbpia.co.kr/v2/search/search.xml?key={DBPIA_KEY}&target=se&searchall={search_word}"

    response = requests.get(url)
    if response.status_code == 200:
        root = ET.fromstring(response.content)  # XML 파싱

        items = root.findall('.//item')  # 여러 item 태그 모두 찾기

        titles = ['', '', '']
        links = ['', '', '']
        i = 0
        # 첫 세 개만 슬라이싱
        for item in items[:3]:

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
    """
    KOSIS API
    """
    url = "https://kosis.kr/openapi/statisticsSearch.do"
    params = {
        "method":"getList",
        "apiKey": KOSIS_KEY,
        "vwCd": "MT_ZTITLE",
        "format": "json",
        "parentListId": "A_4",
        "jsonVD": "Y",
        "searchWord": search_word,
    }

    response = requests.get(url, params=params)
    print("응답 내용:", response.text)

    if response.status_code == 200:
        try:
            data = response.json()
            print("검색 결과:", data)
            return data
        except json.JSONDecodeError:
            print("JSON 파싱 실패:", response.text)
            return {"error": "Invalid JSON response"}
    else:
        print("응답 실패:", response.status_code)
        return {"error": f"Status code {response.status_code}"}

def get_library_response(first, second):
    """
    공공도서관 api
    """
    base_url = 'http://apis.data.go.kr/9720000/searchservice/basic'
    params = {
        'serviceKey': LIB_KEY,
        'pageNo': '1',
        'displayLine': '10',
        'search': '자료명,' + second,
    }

    try:
        response = requests.get(base_url, params=params, verify=False)
        response.encoding = 'utf-8'
        if response.status_code == 200:
            root = ET.fromstring(response.text)
            recode = root.find('recode')
            if recode is not None:
                items = recode.findall('item')
            else:
                items = []

            # name-value 구조를 dict로 변환
            parsed = {}
            for item in items:
                name = item.findtext('name')
                value = item.findtext('value')
                parsed[name] = value

            title = parsed.get("자료명", "제목 없음")
            author = parsed.get("저자명", "저자 없음")
            pub = parsed.get("발행자", "발행자 없음")
            isbn = parsed.get("ISBN", "ISBN 없음")

            # 링크 구성 예: ISBN으로 추정 주소 구성
            link = f"https://www.dlibrary.go.kr/search/DetailView.do?isbn={isbn}" if isbn != "ISBN 없음" else "https://www.dlibrary.go.kr"

            return title, author, pub, link

        return "응답 실패", "응답 실패", "응답 실패", "https://www.dlibrary.go.kr"
    except requests.exceptions.RequestException as e:
        print("API 요청 실패", e)
        return '실패', '실패', '실패'



