import requests
import cloudscraper
from bs4 import BeautifulSoup
import time

# 1. Make.com 웹훅 URL (나중에 Make.com 세팅 후 입력)
WEBHOOK_URL = "https://hook.us2.make.com/gfcwphb8yb44dcresg5tiexklg7j1bej"

def crawl_fontsquirrel():
    url = "https://www.fontsquirrel.com/"
    print(f"[{url}] 데이터 수집을 시작합니다...")
    
    # 💡 핵심: 단순 requests 대신 Cloudflare 우회에 특화된 cloudscraper 사용
    # 실제 사람이 크롬 브라우저를 쓰는 것처럼 행동 패턴을 완벽히 위장합니다.
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False})
    
    try:
        response = scraper.get(url)
    except Exception as e:
        print(f"접속 에러 발생: {e}")
        return []
    
    # 200(정상)이 아니면 차단된 것
    if response.status_code != 200:
        print(f"접속 에러 발생: {response.status_code} (방어벽이 너무 높습니다.)")
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    font_list = []
    
    # 폰트스쿼럴의 진짜 폰트 리스트 박스 이름
    fonts = soup.find_all('div', class_='fontlistitem') 
    
    for font in fonts[:5]: # 테스트를 위해 상위 5개만 추출
        try:
            link_tag = font.find('a')
            if not link_tag: continue
            font_link = link_tag['href']
            
            img_tag = font.find('img')
            if not img_tag: continue
            image_url = img_tag['src']
            
            raw_name = font_link.split('/')[-1]
            font_name = raw_name.replace('-', ' ').title()
            
            font_data = {
                "font_name": font_name,
                "font_url": font_link,
                "image_url": image_url,
                "license": "100% Free for Commercial Use"
            }
            font_list.append(font_data)
            print(f"✅ 추출 성공: {font_name}")
            
        except AttributeError as e:
            continue
            
    return font_list

def send_to_make(font_data):
    if WEBHOOK_URL == "YOUR_MAKE_COM_WEBHOOK_URL_HERE":
        print("\n💡 데이터가 성공적으로 추출되었습니다. (Make.com 연동 대기 중)")
        return
        
    for data in font_data:
        try:
            # Make.com으로 보낼 때는 원래대로 requests 사용
            res = requests.post(WEBHOOK_URL, json=data)
            if res.status_code == 200:
                print(f"🚀 Make.com 전송 완료: {data['font_name']}")
            time.sleep(2) 
        except Exception as e:
            print(f"❌ 전송 실패: {e}")

if __name__ == "__main__":
    extracted_fonts = crawl_fontsquirrel()
    
    if extracted_fonts:
        print(f"\n🎉 총 {len(extracted_fonts)}개의 폰트 정보를 성공적으로 찾았습니다.")
        send_to_make(extracted_fonts)
    else:
        print("추출된 데이터가 없습니다. 봇 차단이 해제되지 않았거나 HTML 구조 분석이 추가로 필요합니다.")