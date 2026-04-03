# PocketBase 0.23 다운로드 및 설치 안내

이 문서는 PocketBase 0.23 최신 버전을 다운로드하고 설치하는 방법을 고등학생도 이해할 수 있도록 쉽게 설명한 가이드입니다.

## 1. 공식 다운로드 경로

PocketBase는 공식 홈페이지나 GitHub에서 안전하게 다운로드할 수 있습니다.

- **GitHub 릴리스 페이지 (가장 추천)**: [https://github.com/pocketbase/pocketbase/releases](https://github.com/pocketbase/pocketbase/releases)
- **공식 홈페이지**: [https://pocketbase.io/docs/](https://pocketbase.io/docs/)

## 2. Windows에서 어떤 파일을 받아야 하나요?

Windows를 사용 중이라면 파일 목록에서 자신의 컴퓨터 사양에 맞는 것을 골라야 합니다.

- **64비트 컴퓨터 (대부분의 경우)**: `pocketbase_0.23.0_windows_amd64.zip`
- **ARM64 (일부 노트북 등)**: `pocketbase_0.23.0_windows_arm64.zip`

## 3. 설치 및 버전 교체 방법 (매우 중요!)

단순히 파일을 덮어쓰기 전에 다음 순서를 꼭 지켜주세요.

1.  **기존 파일 백업**: 현재 프로젝트의 `pocketbase.exe` 파일과 `pb_data` 폴더를 다른 곳에 복사해 두세요. (문제가 생겼을 때 되돌리기 위함)
2.  **압축 풀기**: 다운로드한 `.zip` 파일의 압축을 풉니다.
3.  **파일 교체**: 새로 압축을 푼 `pocketbase.exe` 파일을 프로젝트 폴더에 넣습니다.
4.  **마이그레이션 확인**: 0.22에서 0.23으로 변경 시 내부 코드가 바뀔 수 있으므로, 실행 후 에러 메시지가 나오는지 꼭 확인해야 합니다.

---
> [!IMPORTANT]
> **주의**: 0.23 버전은 '대규모 업데이트'이므로, 실행만 한다고 해서 바로 이전 작업들이 완벽하게 작동하지 않을 수 있습니다. 반드시 데이터 백업 후 진행하세요.

---
*작성일: 2026-03-20*
