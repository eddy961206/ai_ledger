import googlemaps
from typing import Dict, Any, Optional, List
from tenacity import retry, stop_after_attempt, wait_exponential
from ..core.config import settings
import logging

logger = logging.getLogger(__name__)

class GooglePlacesService:
    """Google Places API 연동 서비스"""
    
    def __init__(self):
        self.api_key = settings.google_places_api_key
        self.client = None
        if self.api_key:
            try:
                self.client = googlemaps.Client(key=self.api_key)
            except Exception as e:
                import logging
                logging.warning(f"Google Places API 클라이언트 초기화 실패: {e}")
    
    def is_available(self) -> bool:
        """Google Places API 사용 가능 여부 확인"""
        return self.client is not None
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def search_place_by_name(self, merchant_name: str, location: str = None) -> Optional[Dict[str, Any]]:
        """가맹점명으로 장소 검색"""
        if not self.client:
            logger.warning("Google Places API 키가 설정되지 않았습니다.")
            return None
        
        try:
            # 텍스트 검색 수행
            search_query = merchant_name
            if location:
                search_query += f" {location}"
            
            places_result = self.client.places(
                query=search_query,
                language="ko"
            )
            
            if places_result.get("results"):
                place = places_result["results"][0]  # 첫 번째 결과 사용
                
                # 장소 세부 정보 조회
                place_details = self.get_place_details(place["place_id"])
                
                return {
                    "place_id": place["place_id"],
                    "name": place.get("name", merchant_name),
                    "address": place_details.get("formatted_address", ""),
                    "latitude": place["geometry"]["location"]["lat"],
                    "longitude": place["geometry"]["location"]["lng"],
                    "category": self._extract_category(place.get("types", [])),
                    "rating": place.get("rating"),
                    "phone_number": place_details.get("formatted_phone_number"),
                    "website": place_details.get("website"),
                    "opening_hours": place_details.get("opening_hours", {}).get("weekday_text", [])
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Google Places 검색 실패: {e}")
            return None
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def get_place_details(self, place_id: str) -> Dict[str, Any]:
        """Place ID로 장소 세부 정보 조회"""
        if not self.client:
            return {}
        
        try:
            place_details = self.client.place(
                place_id=place_id,
                fields=[
                    "formatted_address", "formatted_phone_number", 
                    "website", "opening_hours", "rating", "reviews"
                ],
                language="ko"
            )
            
            return place_details.get("result", {})
            
        except Exception as e:
            logger.error(f"Google Places 세부 정보 조회 실패: {e}")
            return {}
    
    def search_nearby_places(
        self, 
        latitude: float, 
        longitude: float, 
        radius: int = 1000,
        place_type: str = None
    ) -> List[Dict[str, Any]]:
        """좌표 기반 주변 장소 검색"""
        if not self.client:
            return []
        
        try:
            nearby_result = self.client.places_nearby(
                location=(latitude, longitude),
                radius=radius,
                type=place_type,
                language="ko"
            )
            
            places = []
            for place in nearby_result.get("results", []):
                places.append({
                    "place_id": place["place_id"],
                    "name": place.get("name", ""),
                    "address": place.get("vicinity", ""),
                    "latitude": place["geometry"]["location"]["lat"],
                    "longitude": place["geometry"]["location"]["lng"],
                    "category": self._extract_category(place.get("types", [])),
                    "rating": place.get("rating"),
                    "price_level": place.get("price_level")
                })
            
            return places
            
        except Exception as e:
            logger.error(f"주변 장소 검색 실패: {e}")
            return []
    
    def _extract_category(self, types: List[str]) -> str:
        """Google Places 타입을 한국어 카테고리로 변환"""
        category_mapping = {
            "restaurant": "음식점",
            "food": "음식점",
            "cafe": "카페",
            "gas_station": "주유소",
            "hospital": "병원",
            "pharmacy": "약국",
            "bank": "은행",
            "atm": "ATM",
            "shopping_mall": "쇼핑몰",
            "supermarket": "마트",
            "convenience_store": "편의점",
            "clothing_store": "의류매장",
            "electronics_store": "전자제품매장",
            "book_store": "서점",
            "movie_theater": "영화관",
            "gym": "헬스장",
            "beauty_salon": "미용실",
            "car_wash": "세차장",
            "parking": "주차장",
            "subway_station": "지하철역",
            "bus_station": "버스정류장",
            "taxi_stand": "택시승강장",
            "school": "학교",
            "university": "대학교",
            "library": "도서관",
            "post_office": "우체국",
            "police": "경찰서",
            "fire_station": "소방서"
        }
        
        for place_type in types:
            if place_type in category_mapping:
                return category_mapping[place_type]
        
        # 기본 카테고리 반환
        if "establishment" in types:
            return "기타"
        
        return "미분류"
    
    def categorize_merchant(self, merchant_name: str) -> str:
        """가맹점명 기반 카테고리 자동 분류"""
        # 키워드 기반 분류 규칙
        food_keywords = ["식당", "음식점", "카페", "커피", "치킨", "피자", "햄버거", "중국집", "일식", "한식", "양식", "분식", "베이커리", "빵집"]
        transport_keywords = ["주유소", "GS칼텍스", "SK에너지", "현대오일뱅크", "S-OIL", "지하철", "버스", "택시", "톨게이트", "주차"]
        shopping_keywords = ["마트", "편의점", "쇼핑", "백화점", "아울렛", "홈플러스", "이마트", "롯데마트", "CU", "GS25", "세븐일레븐"]
        medical_keywords = ["병원", "의원", "약국", "치과", "한의원", "동물병원"]
        beauty_keywords = ["미용실", "헤어샵", "네일샵", "피부과", "성형외과", "마사지"]
        entertainment_keywords = ["영화관", "노래방", "PC방", "볼링장", "당구장", "게임", "오락"]
        
        merchant_lower = merchant_name.lower()
        
        for keyword in food_keywords:
            if keyword in merchant_lower:
                return "식비"
        
        for keyword in transport_keywords:
            if keyword in merchant_lower:
                return "교통"
        
        for keyword in shopping_keywords:
            if keyword in merchant_lower:
                return "쇼핑"
        
        for keyword in medical_keywords:
            if keyword in merchant_lower:
                return "의료"
        
        for keyword in beauty_keywords:
            if keyword in merchant_lower:
                return "미용"
        
        for keyword in entertainment_keywords:
            if keyword in merchant_lower:
                return "여가"
        
        return "기타"
    
    def enrich_merchant_info(self, merchant_name: str, location: str = None) -> Dict[str, Any]:
        """가맹점 정보 보강"""
        # Google Places에서 검색
        place_info = self.search_place_by_name(merchant_name, location)
        
        # 기본 정보 설정
        enriched_info = {
            "name": merchant_name,
            "google_place_id": None,
            "address": "",
            "latitude": None,
            "longitude": None,
            "category": "",
            "manual_category": self.categorize_merchant(merchant_name)
        }
        
        # Google Places 정보로 업데이트
        if place_info:
            enriched_info.update({
                "google_place_id": place_info["place_id"],
                "address": place_info["address"],
                "latitude": place_info["latitude"],
                "longitude": place_info["longitude"],
                "category": place_info["category"]
            })
        
        return enriched_info

# 싱글톤 인스턴스 (API 키가 없어도 생성됨)
try:
    google_places_service = GooglePlacesService()
except Exception as e:
    import logging
    logging.warning(f"Google Places 서비스 초기화 실패: {e}")
    google_places_service = None

