# sparta-games
팀 스파르타 AI 6기 최종 팀 프로젝트

## 프로젝트 명: Sparta Games
Sparta NEWS에서 최신 정보를 확인하세요
(reference 1: [itch.io](https://itch.io/))  
(reference 2: [io games](https://iogames.space/))


## 개요
 
### 주요 기능
- Unity의 WebGL 빌드 파일을 사이트에 업로드하고 이를 플레이할 수 있는 서비스를 제공
- 유저가 플레이하고 싶은 게임을 추천해줄 수 있는 대화형 추천 서비스 기능 제공

### 컨셉 및 목표
- 주니어 게임 개발자의 공간 제공
- 유저로부터 피드백
- 한글화된 사이트를 서비스
- 협업 기능을 제공, 주니어 개발자들의 커뮤니티 형성에 도움

## 개발 기간
- 2024-05-08 ~ 2024-06-12


## ERD

![ERD](https://private-user-images.githubusercontent.com/159861706/339225776-ae24f902-327f-44d2-9d8c-c11394e05766.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3MTgyNTc0NDcsIm5iZiI6MTcxODI1NzE0NywicGF0aCI6Ii8xNTk4NjE3MDYvMzM5MjI1Nzc2LWFlMjRmOTAyLTMyN2YtNDRkMi05ZDhjLWMxMTM5NGUwNTc2Ni5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjQwNjEzJTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI0MDYxM1QwNTM5MDdaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT0xZmZkNWYzOTZkZmZjNGEyMGVmMGQ1YTI3MDdjNjEzOWM4ZGY1ZWQzNDZmN2MwYmZmZDE4NDUzMjc3ZmFkNTFhJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCZhY3Rvcl9pZD0wJmtleV9pZD0wJnJlcG9faWQ9MCJ9.qcjbDSEoygfe6jYxXwdDyaW46t6W-4_6JtTE3t2zgcc)


## Service Architecture

![Service Architecture](https://private-user-images.githubusercontent.com/159861706/339234770-3fa8fb1e-d104-4807-9d76-fb7cbb810840.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3MTgyNTk3NjMsIm5iZiI6MTcxODI1OTQ2MywicGF0aCI6Ii8xNTk4NjE3MDYvMzM5MjM0NzcwLTNmYThmYjFlLWQxMDQtNDgwNy05ZDc2LWZiN2NiYjgxMDg0MC5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjQwNjEzJTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI0MDYxM1QwNjE3NDNaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT1jNGJlOTNjYTdmZjk2NmE0Y2U2Y2NlOGFiOWMxMDUxOTEyYjNiYzUxNzQ3YjVhMTBhZGIwOGU5ODk1NmJmNmNhJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCZhY3Rvcl9pZD0wJmtleV9pZD0wJnJlcG9faWQ9MCJ9.NfLPJ9bYwOVKN4mNqZibsE_y4nLjMk-ZbrzU2CrHp9k)


## API 명세

- Accounts

| Method                                 | Authorization | endpoint                     | Success | Fail       | Description   |
|----------------------------------------|---------------|------------------------------|---------|------------|---------------|
| <span style="color:yellow">POST</span> | `Anonymous`     | `/accounts/api/signup/` | 201,회원가입 성공       | 400,잘못된 사항 | 회원가입          |
| <span style="color:yellow">POST</span> | `Anonymous`     | `/accounts/api/login/` |    202,로그인 성공    |     401,Unauthorized       | 로그인           |
| <span style="color:yellow">POST</span> | `User`     | `/accounts/api/refresh/` |    200,OK     |    401,Unauthorized        | Refresh Token |
| <span style="color:yellow">POST</span>   | `User`     | `/accounts/api/logout/` |    200,로그아웃 완료    |     403, 로그아웃 실패       | 로그아웃          |

- Games

| Method                                 | Authorization | endpoint                      | Success                | Fail                           | Description      |
|----------------------------------------|---------------|-------------------------------|------------------------|--------------------------------|------------------|
| <span style="color:green">GET</span>   | `Anonymous`   | `/games/api/list/` | 200, 게임 리스트            | 404, 목록X                       | 게임 목록            |
| <span style="color:green">GET</span>   | `Anonymous`   | `/games/api/list/<int:game_pk>/` | 200, 게임 상세 정보          | 404, 목록X                       | 게임 상세페이지 / 댓글 조회 |
| <span style="color:yellow">POST</span> | `User`        | `/games/api/list/`              | 201, 게임 상세 정보          | 403 (회원이 아닙니다), 400 (필요한 정보)   | 게임 생성            |
| <span style="color:yellow">POST</span> | `Admin`       | `/games/api/list/<int:game_pk>/register/`          | 200, game_id, gamepath | 403 (권한이 없습니다)                 | 게임 등록            |
| <span style="color:yellow">POST</span> | `Admin`       | `/games/api/list/<int:game_pk>/deny/` | 200                    | 403 (권한이 없습니다)                 | 게임 등록 거부         |
| <span style="color:yellow">POST</span> | `Admin`       | `/games/api/list/<int:game_pk>/dzip/` | 200, 게임 zip 파일         | 403 (권한이 없습니다)                 | 게임 파일 다운         |
| <span style="color:skyblue">PUT</span> | `User`        | `/games/api/list/<int:game_pk>/` | 200, 게임 상세 정보          | 403 (작성자가 아닙니다)                | 게임 수정            |
| <span style="color:red">DELETE</span>  | `User`        | `/games/api/list/<int:game_pk>/` | 204, 삭제완료              | 403 (작성자가 아닙니다)                | 게임 삭제            |
| <span style="color:yellow">POST</span> | `User`        | `/games/api/list/<int:game_pk>/like/` | 200, like 정보           | 403 (회원이 아닙니다)                 | 게임 즐겨찾기          |
| <span style="color:yellow">POST</span> | `User`        | `/games/api/list/<int:game_pk>/star/` | 200, 별점 정보             | 403 (회원이 아닙니다)                 | 게임 별점 매기기        |
| <span style="color:yellow">POST</span> | `User`        | `/games/api/list/<int:game_pk>/comments/` | 200, 댓글 정보             | 403 (회원이 아닙니다), 400 (필요한것이있습니다) | 댓글 작성            |
| <span style="color:skyblue">PUT</span> | `User`        | `/games/api/comment/<int:comment:_id>/` | 201, 댓글 정보             | 403(작성자가 아닙니다)                 | 댓글 수정            |
| <span style="color:red">DELETE</span>  | `User`        | `/games/api/comment/<int:comment:_id>/` | 204, 삭제 완료             | 403(작성자가 아닙니다)                 | 댓글 삭제            |
| <span style="color:green">GET</span>   | `Admin`       | `/games/api/tags` | 200                    | 403(권한이 없습니다)                  | 태그 조회            |
| <span style="color:yellow">POST</span> | `Admin`        | `/games/api/tags` | 200                    | 403(권한이 없습니다)                  | 태그 생성            |
| <span style="color:red">DELETE</span>  | `Admin`        | `/games/api/tags` | 200                    | 403(권한이 없습니다)                  | 태그 삭제            |

- Users

| Method                                 | Authorization | endpoint                     | Success | Fail                          | Description       |
|----------------------------------------|---------------|------------------------------|---------|-------------------------------|-------------------|
| <span style="color:red">DELETE</span>  | `User`        | `/user/api/<int:user_pk>/` | 200,탈퇴 완료                   | 403 (회원이 아닙니다), 400 (비밀번호 틀림) | 회원 탈퇴             |
| <span style="color:skyblue">PUT</span> | `User`        | `/user/api/<int:user_pk>/password/` | 202,수정 완료          | 403 (회원이 아닙니다), 400 (비밀번호 틀림) | 패스워드 수정           |
| <span style="color:skyblue">PUT</span> | `User`        | `/user/api/<int:user_pk>/` | 202, 수정 완료          | 403 (회원이 아닙니다), 400 (비밀번호 틀림) | 프로필 수정 (이메일, 이미지) |
| <span style="color:green">GET</span>   | `Anonymous`   | `/user/api/<int:user_pk>/` | 200, 정보            | 404 목록X                       | 프로필 조회            |
| <span style="color:green">GET</span>   | `Anonymous`   | `/user/api/<int:user_pk>/games/` | 200, 정보            | 404 목록X                       | 내가 등록한 게임 목록      |
| <span style="color:green">GET</span>   | `User`   | `/user/api/<int:user_pk>/likes/` | 200, 정보            | 404 목록X                       | 내가 즐겨찾기한 게임 목록    |

- Qnas

| Method                                 | Authorization | endpoint                     | Success     | Fail                            | Description  |
|----------------------------------------|---------------|------------------------------|-------------|---------------------------------|--------------|
| <span style="color:green">GET</span>   | `Anonymous`   | `/qnas/api/post/` | 200, 리스트    | 404 (목록X)                       | QnA 목록 조회    |
| <span style="color:yellow">POST</span> | `Admin`        | `/qnas/api/post/` | 201, 문의내용   | 403 (회원이 아닙니다), 400 (필요한것이있습니다) | QnA 작성       |
| <span style="color:green">GET</span>   | `Anonymous`   | `/qnas/api/post/<int:post_pk>/` | 200, 리스트 상세 | 404 (목록 X)                      | QnA 상세페이지 조회 |
| <span style="color:skyblue">PUT</span> | `Admin`        | `/qnas/api/post/<int:post_pk>/` | 201, 문의 내용  | 403 (회원이 아닙니다), 400 (필요한 정보)    | QnA 수정       |
| <span style="color:red">DELETE</span>  | `Admin`        | `/qnas/api/post/<int:post_pk>/` | 204, 삭제 완료  | 404(목록X)  | QnA 삭제       |



## 역할 분담

- 정해진: 전체 일정 조정, 기능(Users, Accounts 위주) 구현, AWS 구조 구축

- 한진용: 세부 일정 조정, 기능(Users, Accounts 위주) 구현, AWS 구조 구축

- 전관: 유효성 검증 등 기능 정밀화, 기능(Games, Qnas 위주) 구현, 사용자 맞춤 태그 추천 서비스

- 박성현: 프로젝트 관리 보조, 기능(Games, Qnas 위주) 구현, 사용자 맞춤 태그 추천 서비스

- 임우재 튜터님: S.A. 피드백, 프로젝트 방향성 피드백, 프로젝트 기술 질의 응답
    

## 사용하는 기술
- Python
- Python Django
- Python Django Rest Framework
- AWS
  - EC2
  - RDS
  - S3
  - Route53
  - ACM
- gunicorn
- Nginx


## 설치 필요 패키지
- requirements.txt에 명시
- `pip install -r requirements.txt` 로 설치