import schedule
import requests
from bs4 import BeautifulSoup
import pymysql
from urllib import parse
import smtplib
from email.mime.text import MIMEText

def job():
    # mysql과 연동
    conn = pymysql.connect(host='호스트', user='root', password='패스워드',
                           db='study', charset='utf8')
    # mysql 바라본다
    curs = conn.cursor()

    # url
    url = 'https://search.shopping.naver.com/detail/lite.nhn?nv_mid=14033883241&cat_id=50001763&frm=NVSCPRO&query=%EC%BD%94%EB%A1%9C%EB%A1%9C+%EC%A0%A4%EB%A6%AC&NaPm=ct%3Dk32kn2k0%7Cci%3Dbce1619b183d130daba0a61d7905ab38a69829ee%7Ctr%3Dslsl%7Csn%3D95694%7Chk%3D9b9288fbb37f5e192542d49961cbb2ff0ef2f4c5'
    url_parse = parse.urlparse(url)
    # parse_qs는 리스트를 묶어서 딕셔너리로 변환
    url_parse_qs = parse.parse_qs(url_parse.query)
    # nv_mid의 0번째 값을 저장
    nv_mid = url_parse_qs['nv_mid'][0]

    # http get 요청
    res = requests.get(url)

    # html 가져오기
    soup = BeautifulSoup(res.text, 'html.parser')

    # mainSummaryPrice만 빼와서 soup2에 넣기
    soup2 = soup.find('div', id="_mainSummaryPrice")

    # tbody만 빼와서 tbody_tag에 넣기
    tbody_tag = soup2.find('tbody')

    # 샵이름을 저장하기 위한 변수
    shop_names = []
    prices = []
    product_name = []

    # 샵이름 가져오기
    for tr in tbody_tag.find_all('tr'):
        # 이미지가 존재하는 경우의 샵이름
        if tr.img != None:
            shop_name = tr.img.get('alt')
        # 이미지가 존재하지 않는 경우의 샵이름
        else:
            span_html = tr.find('span', class_='mall')
            shop_name = span_html.text.strip()  # strip() ->양쪽공백제거
        # shop_names 리스트에 추가
        shop_names.append(shop_name)

        # 가격 가져오기
        price = tr.find('td', class_='price')
        # prices 리스트에 추가
        prices.append(price.text.replace('최저', '').strip())  # replace() ->문자열 치환

    # 상품명 가져오기
    product_name = soup.find_all('h2')[3].text.replace('해외', '')

    # 여기서 delete
    sql = "delete from price where prod_no = " + nv_mid + ""
    curs.execute(sql)
    result = curs.fetchall()

    # 여기서 db에 insert
    count = 0
    # shop_names수 만큼 반복
    for i in shop_names:
        # mysql price 데이터베이스에 값 insert
        sql = "insert price(name,price,product_name,url,prod_no) values (%s, %s, %s, %s, %s)"
        curs.execute(sql, (shop_names[count], prices[count], product_name, url, nv_mid))
        count = count + 1

    # insert
    conn.commit()
    # 연결 닫기
    conn.close()

    # 여기서 이메일 보내기
    # 세션 생성, 지메일의 경우 포트번호 587
    smtp = smtplib.SMTP('smtp.gmail.com', 587)
    # TLS(전송계층 보안) 사용시 필요
    smtp.starttls()
    # 로그인 인증
    smtp.login('이메일', '패스워드')
    # 보낼 메시지 설정
    msg = MIMEText('완료되었습니다')
    msg['Subject'] = '테스트'
    # 메일 보내기
    smtp.sendmail('이메일', '이메일', msg.as_string())
    # 세션 종료
    smtp.quit()

    print('성공')


# 60초에 한번씩 실행, 매개변수에 실행시키고싶은 함수명 넣기
schedule.every(60).seconds.do(job)

while True:
    schedule.run_pending() # run_pending이 무한반복시켜줌

