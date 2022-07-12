# WebSite-demo

--- 데모 사이트 실행시키기
1. 프로젝트 파일로 이동
```
  $ cd moseek
```
2. 가상환경 적용
```
  $ source ven/bin/activate
```
3. 웹사이트 서버 가동
```
  $ python3 manage.py runserver 0:8080
```
4. URL 확인
  3.35.243.113:8080 

--- SSH 닫아도 서버 가동되게 하기
1. 서버 실행 
```
  $ python3 manage.py runserver 0:8080
```
2. control + z 로 해당 프로그램 정지
3. 아래 명령어로 프로그램 백그라운드로 보내기
```
  $ bg
```
4. 아래 명령어로 ssh 연결 끊어져도 해당 프로세스 돌아가게 하기
```
  $ disown -h
```

--- 백그라운드 서버 닫기
1. 아래 명령어로 python3 manage.py runserver 실행하고 있는 프로세스 ID 찾기
```
  $ ps auxf
```
2. 찾은 PID로 프로세스 끄기
```
  $ kill -9 [PID]
```
--- (가상환경 접속상태에서, 서버 가동 명령어 입력시 라이브러리 오류가 날 때)
```
pip install -r requirements.txt
```
