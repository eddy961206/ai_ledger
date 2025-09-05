import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  Search, 
  Filter, 
  Download, 
  RefreshCw,
  Calendar,
  MapPin,
  CreditCard
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { transactionAPI } from '../lib/api';
import { formatCurrency, formatDate, getCategoryColor, getCategoryIcon } from '../lib/utils';

// 더미 거래 데이터
const mockTransactions = [
  {
    id: 1,
    merchant_name: '스타벅스 강남점',
    original_merchant_name: '스타벅스강남점',
    amount: 15000,
    category: '식비',
    transaction_type: '결제',
    transaction_date: '2024-09-05T10:30:00Z',
    memo: '',
    merchant: {
      address: '서울시 강남구 테헤란로 123',
      category: 'cafe'
    }
  },
  {
    id: 2,
    merchant_name: '지하철 교통카드',
    original_merchant_name: '서울교통공사',
    amount: 8000,
    category: '교통',
    transaction_type: '결제',
    transaction_date: '2024-09-05T08:15:00Z',
    memo: '2호선 강남역',
    merchant: {
      address: '서울시 강남구',
      category: 'transportation'
    }
  },
  {
    id: 3,
    merchant_name: '이마트 트레이더스',
    original_merchant_name: '이마트트레이더스월드컵점',
    amount: 85000,
    category: '쇼핑',
    transaction_type: '결제',
    transaction_date: '2024-09-04T19:45:00Z',
    memo: '생필품 구매',
    merchant: {
      address: '서울시 마포구 월드컵로 123',
      category: 'grocery'
    }
  },
  {
    id: 4,
    merchant_name: '올리브영 홍대점',
    original_merchant_name: '올리브영홍대점',
    amount: 32000,
    category: '미용',
    transaction_type: '결제',
    transaction_date: '2024-09-04T16:20:00Z',
    memo: '',
    merchant: {
      address: '서울시 마포구 홍익로 456',
      category: 'beauty'
    }
  },
  {
    id: 5,
    merchant_name: '맥도날드 신촌점',
    original_merchant_name: '맥도날드신촌점',
    amount: 12000,
    category: '식비',
    transaction_type: '결제',
    transaction_date: '2024-09-04T12:30:00Z',
    memo: '',
    merchant: {
      address: '서울시 서대문구 신촌로 789',
      category: 'restaurant'
    }
  }
];

function TransactionCard({ transaction }) {
  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardContent className="p-4">
        <div className="flex items-start justify-between">
          <div className="flex items-start space-x-3 flex-1">
            <div className="mt-1">
              <span className="text-2xl">{getCategoryIcon(transaction.category)}</span>
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center space-x-2 mb-1">
                <h3 className="font-semibold truncate">{transaction.merchant_name}</h3>
                <Badge variant="outline" className={getCategoryColor(transaction.category)}>
                  {transaction.category}
                </Badge>
              </div>
              
              <div className="space-y-1 text-sm text-muted-foreground">
                <div className="flex items-center space-x-1">
                  <Calendar className="w-3 h-3" />
                  <span>{formatDate(transaction.transaction_date, 'yyyy년 MM월 dd일 HH:mm')}</span>
                </div>
                
                {transaction.merchant?.address && (
                  <div className="flex items-center space-x-1">
                    <MapPin className="w-3 h-3" />
                    <span className="truncate">{transaction.merchant.address}</span>
                  </div>
                )}
                
                <div className="flex items-center space-x-1">
                  <CreditCard className="w-3 h-3" />
                  <span>{transaction.transaction_type}</span>
                </div>
                
                {transaction.memo && (
                  <div className="text-xs bg-muted p-2 rounded">
                    {transaction.memo}
                  </div>
                )}
              </div>
            </div>
          </div>
          
          <div className="text-right ml-4">
            <div className="text-lg font-bold">
              {formatCurrency(transaction.amount)}
            </div>
            <div className="text-xs text-muted-foreground">
              {transaction.original_merchant_name}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function TransactionsPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedPeriod, setSelectedPeriod] = useState('30');

  // 실제 API 연동 시 사용할 쿼리
  const { data: transactions, isLoading, refetch } = useQuery({
    queryKey: ['transactions', searchTerm, selectedCategory, selectedPeriod],
    queryFn: () => transactionAPI.getTransactions({
      search: searchTerm,
      category: selectedCategory === 'all' ? undefined : selectedCategory,
      days_back: parseInt(selectedPeriod)
    }),
    enabled: false // 임시로 비활성화
  });

  // 임시로 더미 데이터 사용
  const transactionData = mockTransactions;

  // 필터링된 거래 내역
  const filteredTransactions = transactionData.filter(transaction => {
    const matchesSearch = transaction.merchant_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         transaction.original_merchant_name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || transaction.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const handleSyncTransactions = async () => {
    try {
      await transactionAPI.syncTransactions(parseInt(selectedPeriod));
      refetch();
    } catch (error) {
      console.error('거래 내역 동기화 실패:', error);
    }
  };

  const handleExport = () => {
    // CSV 내보내기 로직
    console.log('거래 내역 내보내기');
  };

  const categories = ['all', '식비', '교통', '쇼핑', '의료', '미용', '여가', '기타'];
  const periods = [
    { value: '7', label: '최근 7일' },
    { value: '30', label: '최근 30일' },
    { value: '90', label: '최근 3개월' },
    { value: '365', label: '최근 1년' }
  ];

  return (
    <div className="space-y-6">
      {/* 헤더 */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">거래 내역</h1>
          <p className="text-muted-foreground">
            모든 거래 내역을 확인하고 관리하세요
          </p>
        </div>
        <div className="flex space-x-2 mt-4 sm:mt-0">
          <Button variant="outline" onClick={handleExport}>
            <Download className="w-4 h-4 mr-2" />
            내보내기
          </Button>
          <Button onClick={handleSyncTransactions}>
            <RefreshCw className="w-4 h-4 mr-2" />
            동기화
          </Button>
        </div>
      </div>

      {/* 필터 및 검색 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Filter className="w-5 h-5 mr-2" />
            필터 및 검색
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <div className="space-y-2">
              <label className="text-sm font-medium">검색</label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <Input
                  placeholder="가맹점명으로 검색..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            
            <div className="space-y-2">
              <label className="text-sm font-medium">카테고리</label>
              <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                <SelectTrigger>
                  <SelectValue placeholder="카테고리 선택" />
                </SelectTrigger>
                <SelectContent>
                  {categories.map((category) => (
                    <SelectItem key={category} value={category}>
                      {category === 'all' ? '전체' : category}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div className="space-y-2">
              <label className="text-sm font-medium">기간</label>
              <Select value={selectedPeriod} onValueChange={setSelectedPeriod}>
                <SelectTrigger>
                  <SelectValue placeholder="기간 선택" />
                </SelectTrigger>
                <SelectContent>
                  {periods.map((period) => (
                    <SelectItem key={period.value} value={period.value}>
                      {period.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 거래 내역 요약 */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">총 거래 건수</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{filteredTransactions.length}건</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">총 소비 금액</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatCurrency(filteredTransactions.reduce((sum, t) => sum + t.amount, 0))}
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">평균 거래 금액</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatCurrency(
                filteredTransactions.length > 0 
                  ? filteredTransactions.reduce((sum, t) => sum + t.amount, 0) / filteredTransactions.length
                  : 0
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 거래 내역 목록 */}
      <div className="space-y-4">
        {filteredTransactions.length > 0 ? (
          filteredTransactions.map((transaction) => (
            <TransactionCard key={transaction.id} transaction={transaction} />
          ))
        ) : (
          <Card>
            <CardContent className="p-8 text-center">
              <div className="text-muted-foreground">
                <CreditCard className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p className="text-lg font-medium mb-2">거래 내역이 없습니다</p>
                <p className="text-sm">
                  검색 조건을 변경하거나 거래 내역을 동기화해보세요.
                </p>
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* 페이지네이션 (추후 구현) */}
      {filteredTransactions.length > 0 && (
        <div className="flex justify-center">
          <Button variant="outline">
            더 보기
          </Button>
        </div>
      )}
    </div>
  );
}

export default TransactionsPage;

