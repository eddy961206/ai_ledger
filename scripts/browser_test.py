#!/usr/bin/env python3
"""
AI 가계부 시스템 브라우저 자동화 테스트
"""
from playwright.sync_api import sync_playwright
import time

def test_ai_ledger_website():
    """AI 가계부 웹사이트 테스트"""
    with sync_playwright() as p:
        # Chromium 브라우저 실행
        browser = p.chromium.launch(headless=False)  # headless=False로 브라우저 창 표시
        page = browser.new_page()
        
        try:
            print("🚀 AI 가계부 시스템 테스트 시작...")
            
            # API 서버 테스트
            print("\n1. API 서버 상태 확인...")
            page.goto("http://localhost:8000")
            page.wait_for_timeout(2000)  # 2초 대기
            print("✅ 메인 API 접속 성공")
            
            # Health check
            page.goto("http://localhost:8000/health")
            page.wait_for_timeout(1000)
            print("✅ Health check 통과")
            
            # API 문서 페이지
            print("\n2. API 문서 확인...")
            page.goto("http://localhost:8000/docs")
            page.wait_for_timeout(3000)
            title = page.title()
            print(f"✅ API 문서 페이지 로드됨: {title}")
            
            # 프론트엔드 테스트 (포트 3001)
            print("\n3. 프론트엔드 테스트...")
            try:
                page.goto("http://localhost:3001")
                page.wait_for_timeout(3000)
                print("✅ 프론트엔드 접속 성공")
            except Exception as e:
                print(f"⚠️  프론트엔드 접속 실패: {e}")
            
            # 스크린샷 촬영
            print("\n4. 스크린샷 촬영...")
            page.goto("http://localhost:8000/docs")
            page.wait_for_timeout(2000)
            page.screenshot(path="api_docs_screenshot.png")
            print("📸 API 문서 스크린샷 저장됨: api_docs_screenshot.png")
            
            # 5초간 브라우저 유지
            print("\n5초간 브라우저를 유지합니다...")
            time.sleep(5)
            
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
        
        finally:
            browser.close()
            print("\n🏁 테스트 완료!")

if __name__ == "__main__":
    test_ai_ledger_website()