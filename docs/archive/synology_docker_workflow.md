# 시놀로지 NAS 도커 배포 워크플로우 (로컬 빌드 방식)

이 문서는 프로젝트 이미지를 **로컬 PC에서 빌드**하여 시놀로지(Synology) NAS로 옮겨 배포하는 효율적인 과정을 안내합니다. 특히 외부 접속을 위한 포트 설정과 역방향 프록시 설정을 포함하고 있습니다.

## 1. 로컬 PC에서 이미지 빌드 및 내보내기
먼저 본인의 PC(Windows/Mac)에서 Docker를 사용해 이미지를 만듭니다.
1. 터미널(PowerShell 또는 CMD)에서 프로젝트 루트 폴더로 이동합니다.
2. 다음 명령어를 입력하여 이미지를 빌드합니다.
   ```bash
   docker build -t closingshin:latest .
   ```
3. 빌드가 완료되면 이미지를 파일(`.tar`)로 저장합니다.
   ```bash
   docker save -o closingshin.tar closingshin:latest
   ```
   이제 폴더에 `closingshin.tar` 파일이 생성됩니다.

## 2. 파일 업로드
시놀로지 NAS로 필요한 파일들을 복사합니다.
1. NAS의 **File Station**에서 `docker/ClosingSHIN` 폴더를 만듭니다.
2. 다음 파일들을 업로드합니다.
   - `closingshin.tar` (빌드된 이미지 파일)
   - `docker-compose.yml`
   - `.env` (환경 설정 파일)

## 3. 시놀로지에서 이미지 가져오기 (Import)
1. NAS에서 **Container Manager**를 실행합니다.
2. **이미지** 탭으로 이동하여 **가져오기(Import)** 버튼을 누릅니다.
3. **파일에서 추가**를 선택하고 업로드한 `closingshin.tar` 파일을 선택하여 가져옵니다.

## 4. 접속 포트 및 외부 주소 설정
외부에서 `drspike.synology.me:4443`과 같은 주소로 접속하려는 경우, 다음 두 가지 방법 중 하나를 선택할 수 있습니다.

### 방법 A: docker-compose.yml 직접 수정 (간편함)
1. `docker-compose.yml` 파일을 열어 `closingshin` 서비스의 `ports` 설정을 변경합니다.
   ```yaml
   closingshin:
     image: closingshin:latest
     ports:
       - "4443:3000"  # NAS의 4443 포트를 컨테이너의 3000 포트와 연결
   ```
2. 공유기 설정에서 4443 포트를 NAS의 IP로 포트 포위딩하고, NAS 방화벽에서 4443 포트를 허용해야 합니다.

### 방법 B: 시놀로지 역방향 프록시 사용 (권장 - HTTPS 사용 가능)
이 방식은 도커 설정은 그대로 두고 NAS의 시스템 설정을 이용하는 방식입니다. 보안과 주소 관리가 훨씬 편리합니다.
1. **도커 설정**: `docker-compose.yml`에서는 포트를 `"3000:3000"`으로 둡니다.
2. **NAS 설정**: 제어판 -> 로그인 포털 -> 고급 -> **역방향 프록시** 클릭.
3. **생성** 클릭 후 다음과 같이 입력:
   - **소스**: 프로토콜 `HTTPS`, 호스트 이름 `drspike.synology.me`, 포트 `4443`
   - **대상**: 프로토콜 `HTTP`, 호스트 이름 `localhost`, 포트 `3000`
4. 이제 외부에서 `https://drspike.synology.me:4443`으로 접속하면 자동으로 도커의 앱으로 연결됩니다.

## 5. 프로젝트 생성 및 실행
1. **Container Manager** -> **프로젝트** -> **생성**을 클릭합니다.
2. 프로젝트 이름을 `closingshin`으로 정하고, 파일 경로를 선택합니다.
3. 수정된 `docker-compose.yml`을 사용하여 프로젝트를 생성하면 컨테이너가 실행됩니다.

## 6. 서비스 확인
- **웹 서비스**: `http://<NAS_IP>:3000` (또는 설정한 4443 포트)
- **PocketBase**: `http://<NAS_IP>:8090/_/`

---
**작성일**: 2026-03-23 (최종 수정)
**작성자**: Antigravity AI Assistant
