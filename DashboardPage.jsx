import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  TrendingUp, 
  TrendingDown, 
  CreditCard, 
  Brain,
  RefreshCw,
  Calendar,
  DollarSign
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { transactionAPI, aiAPI } from '../lib/api';
import { formatCurrency, formatDate, getCategoryColor, getCategoryIcon } from '../lib/utils';

// 더미 데이터 (실제 API 연동 전까지 사용)
const mockDashboardData = {
  totalSpending: 1250000,
  monthlyChange: 15.2,
  transactionCount: 47,
  topCategories: [
    { category: '식비', amount: 450000, percentage: 36 },
    { category: '교통', amount: 280000, percentage: 22 },
    { category: '쇼핑', amount: 320000, percentage: 26 },
    { category: '기타', amount: 200000, percentage: 16 }
  ],
  recentTransactions: [
    {
      id: 1,
      merchant_name: '스타벅스 강남점',
      amount: 15000,
      category: '식비',
      date: '2024-09-05T10:30:00Z'
    },
    {
      id: 2,
      merchant_name: '지하철 교통카드',
      amount: 8000,
      category: '교통',
      date: '2024-09-05T08:15:00Z'
    },
    {
      id: 3,
      merchant_name: '이마트 트레이더스',
      amount: 85000,
      category: '쇼핑',
      date: '2024-09-04T19:45:00Z'
    }
  ]
};

function StatCard({ title, value, change, icon: Icon, trend }) {
  const isPositive = change > 0;
  const TrendIcon = isPositive ? TrendingUp : TrendingDown;
  
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <Icon className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        <div className="flex items-center text-xs text-muted-foreground">
          <TrendIcon className={`mr-1 h-3 w-3 ${isPositive ? 'text-red-500' : 'text-green-500'}`} />
          <span className={isPositive ? 'text-red-500' : 'text-green-500'}>
            {Math.abs(change)}%
          </span>
          <span className="ml-1">지난 달 대비</span>
        </div>
      </CardContent>
    </Card>
  );
}

function CategoryCard({ category, amount, percentage }) {
  return (
    <div className="flex items-center justify-between p-3 border rounded-lg">
      <div className="flex items-center space-x-3">
        <span className="text-lg">{getCategoryIcon(category)}</span>
        <div>
          <p className="font-medium">{category}</p>
          <p className="text-sm text-muted-foreground">{percentage}%</p>
        </div>
      </div>
      <div className="text-right">
        <p className="font-semibold">{formatCurrency(amount)}</p>
        <Badge variant="secondary" className={getCategoryColor(category)}>
          {category}
        </Badge>
      </div>
    </div>
  );
}

function TransactionItem({ transaction }) {
  return (
    <div className="flex items-center justify-between p-3 border-b last:border-b-0">
      <div className="flex items-center space-x-3">
        <span className="text-lg">{getCategoryIcon(transaction.category)}</span>
        <div>
          <p className="font-medium">{transaction.merchant_name}</p>
          <p className="text-sm text-muted-foreground">
            {formatDate(transaction.date, 'MM월 dd일 HH:mm')}
          </p>
        </div>
      </div>
      <div className="text-right">
        <p className="font-semibold">{formatCurrency(transaction.amount)}</p>
        <Badge variant="outline" className={getCategoryColor(transaction.category)}>
          {transaction.category}
        </Badge>
      </div>
    </div>
  );
}

function DashboardPage() {
  // 실제 API 연동 시 사용할 쿼리들
  const { data: transactions, isLoading: transactionsLoading } = useQuery({
    queryKey: ['transactions', 'recent'],
    queryFn: () => transactionAPI.getTransactions({ limit: 10 }),
    enabled: false // 임시로 비활성화
  });

  const { data: aiAnalysis, isLoading: aiLoading } = useQuery({
    queryKey: ['ai-analysis', 'dashboard'],
    queryFn: () => aiAPI.analyze({ analysis_type: 'pattern', days_back: 30 }),
    enabled: false // 임시로 비활성화
  });

  // 임시로 더미 데이터 사용
  const dashboardData = mockDashboardData;

  const handleSyncTransactions = async () => {
    try {
      await transactionAPI.syncTransactions(7);
      // 성공 시 데이터 새로고침
      window.location.reload();
    } catch (error) {
      console.error('거래 내역 동기화 실패:', error);
    }
  };

  return (
    <div className="space-y-6">
      {/* 헤더 */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">대시보드</h1>
          <p className="text-muted-foreground">
            이번 달 소비 현황과 AI 분석 결과를 확인하세요
          </p>
        </div>
        <div className="flex space-x-2 mt-4 sm:mt-0">
          <Button variant="outline" onClick={handleSyncTransactions}>
            <RefreshCw className="w-4 h-4 mr-2" />
            거래 동기화
          </Button>
          <Button>
            <Brain className="w-4 h-4 mr-2" />
            AI 분석
          </Button>
        </div>
      </div>

      {/* 통계 카드 */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="이번 달 총 소비"
          value={formatCurrency(dashboardData.totalSpending)}
          change={dashboardData.monthlyChange}
          icon={DollarSign}
          trend="up"
        />
        <StatCard
          title="거래 건수"
          value={dashboardData.transactionCount.toString()}
          change={-5.2}
          icon={CreditCard}
          trend="down"
        />
        <StatCard
          title="일평균 소비"
          value={formatCurrency(Math.round(dashboardData.totalSpending / 30))}
          change={8.1}
          icon={Calendar}
          trend="up"
        />
        <StatCard
          title="AI 분석 점수"
          value="85점"
          change={12.3}
          icon={Brain}
          trend="up"
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* 카테고리별 소비 */}
        <Card>
          <CardHeader>
            <CardTitle>카테고리별 소비</CardTitle>
            <CardDescription>
              이번 달 주요 소비 카테고리
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {dashboardData.topCategories.map((item, index) => (
              <CategoryCard
                key={index}
                category={item.category}
                amount={item.amount}
                percentage={item.percentage}
              />
            ))}
          </CardContent>
        </Card>

        {/* 최근 거래 내역 */}
        <Card>
          <CardHeader>
            <CardTitle>최근 거래 내역</CardTitle>
            <CardDescription>
              최근 거래 내역을 확인하세요
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-0">
              {dashboardData.recentTransactions.map((transaction) => (
                <TransactionItem
                  key={transaction.id}
                  transaction={transaction}
                />
              ))}
            </div>
            <div className="mt-4">
              <Button variant="outline" className="w-full">
                전체 거래 내역 보기
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* AI 인사이트 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Brain className="w-5 h-5 mr-2" />
            AI 소비 인사이트
          </CardTitle>
          <CardDescription>
            AI가 분석한 당신의 소비 패턴
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
              <h4 className="font-semibold text-blue-900 dark:text-blue-100 mb-2">
                💡 소비 패턴 분석
              </h4>
              <p className="text-sm text-blue-800 dark:text-blue-200">
                이번 달 식비 지출이 평소보다 20% 증가했습니다. 
                외식 빈도를 줄이면 월 10만원 절약이 가능합니다.
              </p>
            </div>
            <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
              <h4 className="font-semibold text-green-900 dark:text-green-100 mb-2">
                📊 예산 추천
              </h4>
              <p className="text-sm text-green-800 dark:text-green-200">
                현재 소비 패턴을 기준으로 다음 달 예산을 120만원으로 
                설정하는 것을 추천합니다.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

export default DashboardPage;

