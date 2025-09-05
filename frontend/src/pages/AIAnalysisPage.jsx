import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  Brain, 
  TrendingUp, 
  PieChart, 
  BarChart3,
  RefreshCw,
  Settings,
  Zap,
  Target,
  AlertCircle
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { aiAPI } from '../lib/api';
import { formatCurrency, getCategoryColor } from '../lib/utils';

// 더미 AI 분석 데이터
const mockAnalysisData = {
  pattern: {
    summary: "이번 달 소비 패턴을 분석한 결과, 식비 지출이 평소보다 20% 증가했으며, 주로 외식에 집중되어 있습니다.",
    category_analysis: {
      "식비": {
        percentage: 36,
        insight: "외식 빈도가 증가했습니다. 집에서 요리하는 횟수를 늘리면 절약할 수 있습니다."
      },
      "교통": {
        percentage: 22,
        insight: "대중교통 이용이 일정합니다. 효율적인 교통비 지출을 보이고 있습니다."
      },
      "쇼핑": {
        percentage: 26,
        insight: "온라인 쇼핑 지출이 증가했습니다. 필요한 물건만 구매하도록 주의하세요."
      },
      "기타": {
        percentage: 16,
        insight: "기타 지출이 적절한 수준입니다."
      }
    },
    spending_habits: [
      "주말에 외식 지출이 집중됨",
      "온라인 쇼핑을 자주 이용함",
      "대중교통을 주로 이용함"
    ],
    recommendations: [
      "주말 외식 횟수를 줄이고 집에서 요리해보세요",
      "온라인 쇼핑 전 장바구니에 하루 이상 보관 후 구매하세요",
      "월 예산을 카테고리별로 설정해보세요"
    ]
  },
  report: {
    title: "2024년 09월 소비 리포트",
    executive_summary: "이번 달 총 소비는 125만원으로 지난 달 대비 15% 증가했습니다. 주요 증가 요인은 식비와 쇼핑 지출입니다.",
    key_metrics: {
      total_spending: 1250000,
      transaction_count: 47,
      most_spent_category: "식비"
    },
    category_breakdown: {
      "식비": {
        amount: 450000,
        percentage: 36,
        analysis: "외식비가 크게 증가했습니다. 배달음식 주문이 잦았습니다."
      },
      "교통": {
        amount: 275000,
        percentage: 22,
        analysis: "대중교통 이용이 일정하며 효율적입니다."
      },
      "쇼핑": {
        amount: 325000,
        percentage: 26,
        analysis: "온라인 쇼핑과 생필품 구매가 주를 이뤘습니다."
      },
      "기타": {
        amount: 200000,
        percentage: 16,
        analysis: "기타 지출이 적절한 수준을 유지하고 있습니다."
      }
    },
    insights: [
      "식비 지출 패턴 개선이 필요합니다",
      "쇼핑 지출에 대한 계획적 접근이 필요합니다",
      "전반적인 소비 증가 추세를 관리해야 합니다"
    ],
    next_month_goals: [
      "식비 예산을 35만원으로 설정",
      "외식 횟수를 주 2회로 제한",
      "온라인 쇼핑 전 24시간 대기 규칙 적용"
    ]
  },
  performance: {
    total_analyses: 23,
    success_rate: 0.96,
    successful_analyses: 22,
    failed_analyses: 1,
    model_usage: {
      "gemini": {
        count: 15,
        success: 15,
        error: 0
      },
      "ollama": {
        count: 8,
        success: 7,
        error: 1
      }
    },
    cache_size: 12
  }
};

function AnalysisCard({ title, content, icon: Icon, variant = "default" }) {
  return (
    <Card className={variant === "highlight" ? "border-primary" : ""}>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center text-lg">
          <Icon className="w-5 h-5 mr-2" />
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm leading-relaxed">{content}</p>
      </CardContent>
    </Card>
  );
}

function CategoryAnalysisCard({ category, data }) {
  return (
    <Card>
      <CardContent className="p-4">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2">
            <Badge className={getCategoryColor(category)}>
              {category}
            </Badge>
            <span className="font-semibold">{data.percentage}%</span>
          </div>
          <div className="text-right">
            <div className="font-bold">{formatCurrency(data.amount || 0)}</div>
          </div>
        </div>
        <p className="text-sm text-muted-foreground">{data.insight || data.analysis}</p>
      </CardContent>
    </Card>
  );
}

function AIAnalysisPage() {
  const [analysisType, setAnalysisType] = useState('pattern');
  const [selectedPeriod, setSelectedPeriod] = useState('30');
  const [selectedModel, setSelectedModel] = useState('auto');

  // 실제 API 연동 시 사용할 쿼리들
  const { data: analysisData, isLoading, refetch } = useQuery({
    queryKey: ['ai-analysis', analysisType, selectedPeriod],
    queryFn: () => aiAPI.analyze({
      analysis_type: analysisType,
      days_back: parseInt(selectedPeriod)
    }),
    enabled: false // 임시로 비활성화
  });

  const { data: performanceData } = useQuery({
    queryKey: ['ai-performance'],
    queryFn: () => aiAPI.getPerformance(),
    enabled: false // 임시로 비활성화
  });

  // 임시로 더미 데이터 사용
  const currentAnalysis = mockAnalysisData[analysisType] || mockAnalysisData.pattern;
  const performance = mockAnalysisData.performance;

  const handleRunAnalysis = async () => {
    try {
      await refetch();
    } catch (error) {
      console.error('AI 분석 실패:', error);
    }
  };

  const handleTestAnalysis = async () => {
    try {
      await aiAPI.testAnalysis(selectedModel);
    } catch (error) {
      console.error('AI 테스트 실패:', error);
    }
  };

  const periods = [
    { value: '7', label: '최근 7일' },
    { value: '30', label: '최근 30일' },
    { value: '90', label: '최근 3개월' }
  ];

  const models = [
    { value: 'auto', label: '자동 선택' },
    { value: 'gemini', label: 'Google Gemini' },
    { value: 'ollama', label: 'Ollama (로컬)' },
    { value: 'hybrid', label: '하이브리드' }
  ];

  return (
    <div className="space-y-6">
      {/* 헤더 */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">AI 분석</h1>
          <p className="text-muted-foreground">
            AI가 분석한 소비 패턴과 인사이트를 확인하세요
          </p>
        </div>
        <div className="flex space-x-2 mt-4 sm:mt-0">
          <Button variant="outline" onClick={handleTestAnalysis}>
            <Zap className="w-4 h-4 mr-2" />
            테스트
          </Button>
          <Button onClick={handleRunAnalysis}>
            <Brain className="w-4 h-4 mr-2" />
            분석 실행
          </Button>
        </div>
      </div>

      {/* 분석 설정 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Settings className="w-5 h-5 mr-2" />
            분석 설정
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <div className="space-y-2">
              <label className="text-sm font-medium">분석 기간</label>
              <Select value={selectedPeriod} onValueChange={setSelectedPeriod}>
                <SelectTrigger>
                  <SelectValue />
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
            
            <div className="space-y-2">
              <label className="text-sm font-medium">AI 모델</label>
              <Select value={selectedModel} onValueChange={setSelectedModel}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {models.map((model) => (
                    <SelectItem key={model.value} value={model.value}>
                      {model.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div className="space-y-2">
              <label className="text-sm font-medium">분석 상태</label>
              <div className="flex items-center space-x-2 h-10">
                <Badge variant="outline" className="bg-green-50 text-green-700">
                  ✓ 준비됨
                </Badge>
                <span className="text-sm text-muted-foreground">
                  {performance.cache_size}개 캐시됨
                </span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 분석 결과 탭 */}
      <Tabs value={analysisType} onValueChange={setAnalysisType}>
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="pattern">패턴 분석</TabsTrigger>
          <TabsTrigger value="report">월간 리포트</TabsTrigger>
          <TabsTrigger value="performance">성능 지표</TabsTrigger>
        </TabsList>

        <TabsContent value="pattern" className="space-y-6">
          {/* 패턴 분석 요약 */}
          <AnalysisCard
            title="소비 패턴 요약"
            content={currentAnalysis.summary}
            icon={TrendingUp}
            variant="highlight"
          />

          {/* 카테고리별 분석 */}
          <div>
            <h3 className="text-lg font-semibold mb-4">카테고리별 분석</h3>
            <div className="grid gap-4 md:grid-cols-2">
              {Object.entries(currentAnalysis.category_analysis || {}).map(([category, data]) => (
                <CategoryAnalysisCard
                  key={category}
                  category={category}
                  data={data}
                />
              ))}
            </div>
          </div>

          {/* 소비 습관 및 추천사항 */}
          <div className="grid gap-6 lg:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <BarChart3 className="w-5 h-5 mr-2" />
                  주요 소비 습관
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {(currentAnalysis.spending_habits || []).map((habit, index) => (
                    <li key={index} className="flex items-start space-x-2">
                      <span className="text-blue-500 mt-1">•</span>
                      <span className="text-sm">{habit}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Target className="w-5 h-5 mr-2" />
                  개선 추천사항
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {(currentAnalysis.recommendations || []).map((recommendation, index) => (
                    <li key={index} className="flex items-start space-x-2">
                      <span className="text-green-500 mt-1">✓</span>
                      <span className="text-sm">{recommendation}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="report" className="space-y-6">
          {/* 월간 리포트 헤더 */}
          <Card>
            <CardHeader>
              <CardTitle>{currentAnalysis.title}</CardTitle>
              <CardDescription>{currentAnalysis.executive_summary}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-3">
                <div className="text-center p-4 bg-muted rounded-lg">
                  <div className="text-2xl font-bold">
                    {formatCurrency(currentAnalysis.key_metrics?.total_spending || 0)}
                  </div>
                  <div className="text-sm text-muted-foreground">총 소비</div>
                </div>
                <div className="text-center p-4 bg-muted rounded-lg">
                  <div className="text-2xl font-bold">
                    {currentAnalysis.key_metrics?.transaction_count || 0}건
                  </div>
                  <div className="text-sm text-muted-foreground">거래 건수</div>
                </div>
                <div className="text-center p-4 bg-muted rounded-lg">
                  <div className="text-2xl font-bold">
                    {currentAnalysis.key_metrics?.most_spent_category || '식비'}
                  </div>
                  <div className="text-sm text-muted-foreground">최대 소비 카테고리</div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* 카테고리별 상세 분석 */}
          <div>
            <h3 className="text-lg font-semibold mb-4">카테고리별 상세 분석</h3>
            <div className="grid gap-4 md:grid-cols-2">
              {Object.entries(currentAnalysis.category_breakdown || {}).map(([category, data]) => (
                <CategoryAnalysisCard
                  key={category}
                  category={category}
                  data={data}
                />
              ))}
            </div>
          </div>

          {/* 인사이트 및 목표 */}
          <div className="grid gap-6 lg:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <AlertCircle className="w-5 h-5 mr-2" />
                  주요 인사이트
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {(currentAnalysis.insights || []).map((insight, index) => (
                    <li key={index} className="flex items-start space-x-2">
                      <span className="text-yellow-500 mt-1">💡</span>
                      <span className="text-sm">{insight}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Target className="w-5 h-5 mr-2" />
                  다음 달 목표
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {(currentAnalysis.next_month_goals || []).map((goal, index) => (
                    <li key={index} className="flex items-start space-x-2">
                      <span className="text-blue-500 mt-1">🎯</span>
                      <span className="text-sm">{goal}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="performance" className="space-y-6">
          {/* 성능 지표 */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">총 분석 횟수</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{performance.total_analyses}</div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">성공률</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {Math.round(performance.success_rate * 100)}%
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">성공한 분석</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">
                  {performance.successful_analyses}
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">실패한 분석</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-red-600">
                  {performance.failed_analyses}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* 모델별 사용 현황 */}
          <Card>
            <CardHeader>
              <CardTitle>AI 모델별 사용 현황</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {Object.entries(performance.model_usage).map(([model, stats]) => (
                  <div key={model} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center space-x-3">
                      <Badge variant="outline">
                        {model === 'gemini' ? 'Google Gemini' : 'Ollama'}
                      </Badge>
                      <div className="text-sm text-muted-foreground">
                        총 {stats.count}회 사용
                      </div>
                    </div>
                    <div className="flex items-center space-x-4">
                      <div className="text-sm">
                        <span className="text-green-600">성공: {stats.success}</span>
                        <span className="text-muted-foreground mx-2">|</span>
                        <span className="text-red-600">실패: {stats.error}</span>
                      </div>
                      <div className="text-sm font-medium">
                        {Math.round((stats.success / stats.count) * 100)}%
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

export default AIAnalysisPage;

