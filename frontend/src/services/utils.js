import { clsx } from "clsx";
import { twMerge } from "tailwind-merge"
import { format, parseISO, isValid } from 'date-fns';
import { ko } from 'date-fns/locale';

export function cn(...inputs) {
  return twMerge(clsx(inputs));
}

// 금액 포맷팅
export function formatCurrency(amount, currency = 'KRW') {
  if (typeof amount !== 'number') {
    amount = parseFloat(amount) || 0;
  }
  
  return new Intl.NumberFormat('ko-KR', {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}

// 숫자 포맷팅 (천 단위 구분)
export function formatNumber(number) {
  if (typeof number !== 'number') {
    number = parseFloat(number) || 0;
  }
  
  return new Intl.NumberFormat('ko-KR').format(number);
}

// 날짜 포맷팅
export function formatDate(date, formatString = 'yyyy년 MM월 dd일') {
  if (!date) return '';
  
  let dateObj = date;
  if (typeof date === 'string') {
    dateObj = parseISO(date);
  }
  
  if (!isValid(dateObj)) return '';
  
  return format(dateObj, formatString, { locale: ko });
}

// 상대적 시간 표시
export function formatRelativeTime(date) {
  if (!date) return '';
  
  let dateObj = date;
  if (typeof date === 'string') {
    dateObj = parseISO(date);
  }
  
  if (!isValid(dateObj)) return '';
  
  const now = new Date();
  const diffInSeconds = Math.floor((now - dateObj) / 1000);
  
  if (diffInSeconds < 60) {
    return '방금 전';
  } else if (diffInSeconds < 3600) {
    const minutes = Math.floor(diffInSeconds / 60);
    return `${minutes}분 전`;
  } else if (diffInSeconds < 86400) {
    const hours = Math.floor(diffInSeconds / 3600);
    return `${hours}시간 전`;
  } else if (diffInSeconds < 2592000) {
    const days = Math.floor(diffInSeconds / 86400);
    return `${days}일 전`;
  } else {
    return formatDate(dateObj, 'MM월 dd일');
  }
}

// 카테고리 색상 매핑
export function getCategoryColor(category) {
  const colorMap = {
    '식비': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
    '교통': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    '쇼핑': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    '의료': 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
    '미용': 'bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-200',
    '여가': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
    '기타': 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200',
  };
  
  return colorMap[category] || colorMap['기타'];
}

// 카테고리 아이콘 매핑
export function getCategoryIcon(category) {
  const iconMap = {
    '식비': '🍽️',
    '교통': '🚗',
    '쇼핑': '🛒',
    '의료': '🏥',
    '미용': '💄',
    '여가': '🎮',
    '기타': '📦',
  };
  
  return iconMap[category] || iconMap['기타'];
}

// 에러 메시지 추출
export function getErrorMessage(error) {
  if (error.response?.data?.detail) {
    return error.response.data.detail;
  } else if (error.message) {
    return error.message;
  } else {
    return '알 수 없는 오류가 발생했습니다.';
  }
}

// 퍼센티지 계산
export function calculatePercentage(value, total) {
  if (total === 0) return 0;
  return Math.round((value / total) * 100);
}
