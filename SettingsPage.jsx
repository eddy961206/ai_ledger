import React, { useState } from 'react';
import { 
  Settings, 
  User, 
  Brain, 
  Bell, 
  Shield, 
  Palette,
  Server,
  Calendar,
  Trash2,
  Save
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { useAuthStore, useAppStore } from '../lib/store';

function SettingsPage() {
  const { user, updateUser } = useAuthStore();
  const { theme, setTheme } = useAppStore();
  
  const [userSettings, setUserSettings] = useState({
    username: user?.username || '',
    email: user?.email || '',
    preferred_ai_model: user?.preferred_ai_model || 'gemini',
    ollama_server_url: user?.ollama_server_url || 'http://localhost:11434',
    notifications_enabled: true,
    email_notifications: false,
    auto_sync_enabled: true,
    sync_frequency: 'daily'
  });

  const [scheduleSettings, setScheduleSettings] = useState({
    auto_analysis: true,
    analysis_frequency: 'weekly',
    report_generation: true,
    report_frequency: 'monthly'
  });

  const handleUserSettingsChange = (key, value) => {
    setUserSettings(prev => ({ ...prev, [key]: value }));
  };

  const handleScheduleSettingsChange = (key, value) => {
    setScheduleSettings(prev => ({ ...prev, [key]: value }));
  };

  const handleSaveUserSettings = async () => {
    try {
      // API 호출로 사용자 설정 저장
      updateUser(userSettings);
      console.log('사용자 설정 저장됨');
    } catch (error) {
      console.error('설정 저장 실패:', error);
    }
  };

  const handleClearCache = async () => {
    try {
      // AI 캐시 삭제 API 호출
      console.log('캐시 삭제됨');
    } catch (error) {
      console.error('캐시 삭제 실패:', error);
    }
  };

  const handleExportData = () => {
    // 데이터 내보내기 로직
    console.log('데이터 내보내기');
  };

  return (
    <div className="space-y-6">
      {/* 헤더 */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">설정</h1>
        <p className="text-muted-foreground">
          계정, AI 모델, 알림 등 다양한 설정을 관리하세요
        </p>
      </div>

      <Tabs defaultValue="profile" className="space-y-6">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="profile">프로필</TabsTrigger>
          <TabsTrigger value="ai">AI 설정</TabsTrigger>
          <TabsTrigger value="notifications">알림</TabsTrigger>
          <TabsTrigger value="schedule">스케줄</TabsTrigger>
          <TabsTrigger value="data">데이터</TabsTrigger>
        </TabsList>

        {/* 프로필 설정 */}
        <TabsContent value="profile" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <User className="w-5 h-5 mr-2" />
                사용자 정보
              </CardTitle>
              <CardDescription>
                기본 계정 정보를 관리합니다
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="username">사용자명</Label>
                  <Input
                    id="username"
                    value={userSettings.username}
                    onChange={(e) => handleUserSettingsChange('username', e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="email">이메일</Label>
                  <Input
                    id="email"
                    type="email"
                    value={userSettings.email}
                    onChange={(e) => handleUserSettingsChange('email', e.target.value)}
                  />
                </div>
              </div>
              <Button onClick={handleSaveUserSettings}>
                <Save className="w-4 h-4 mr-2" />
                저장
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Palette className="w-5 h-5 mr-2" />
                테마 설정
              </CardTitle>
              <CardDescription>
                앱의 외관을 설정합니다
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label>다크 모드</Label>
                    <p className="text-sm text-muted-foreground">
                      어두운 테마를 사용합니다
                    </p>
                  </div>
                  <Switch
                    checked={theme === 'dark'}
                    onCheckedChange={(checked) => setTheme(checked ? 'dark' : 'light')}
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* AI 설정 */}
        <TabsContent value="ai" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Brain className="w-5 h-5 mr-2" />
                AI 모델 설정
              </CardTitle>
              <CardDescription>
                분석에 사용할 AI 모델을 선택합니다
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>기본 AI 모델</Label>
                <Select
                  value={userSettings.preferred_ai_model}
                  onValueChange={(value) => handleUserSettingsChange('preferred_ai_model', value)}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="gemini">Google Gemini</SelectItem>
                    <SelectItem value="ollama">Ollama (로컬)</SelectItem>
                    <SelectItem value="hybrid">하이브리드</SelectItem>
                  </SelectContent>
                </Select>
                <p className="text-sm text-muted-foreground">
                  Gemini는 클라우드 기반, Ollama는 로컬 실행, 하이브리드는 두 모델을 모두 사용합니다
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="ollama-url">Ollama 서버 URL</Label>
                <Input
                  id="ollama-url"
                  value={userSettings.ollama_server_url}
                  onChange={(e) => handleUserSettingsChange('ollama_server_url', e.target.value)}
                  placeholder="http://localhost:11434"
                />
                <p className="text-sm text-muted-foreground">
                  로컬 Ollama 서버의 주소를 입력하세요
                </p>
              </div>

              <div className="flex items-center space-x-2">
                <Badge variant="outline" className="bg-green-50 text-green-700">
                  ✓ Gemini 연결됨
                </Badge>
                <Badge variant="outline" className="bg-yellow-50 text-yellow-700">
                  ⚠ Ollama 연결 확인 필요
                </Badge>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Server className="w-5 h-5 mr-2" />
                성능 설정
              </CardTitle>
              <CardDescription>
                AI 분석 성능과 관련된 설정입니다
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <Label>분석 결과 캐싱</Label>
                  <p className="text-sm text-muted-foreground">
                    동일한 분석 요청에 대해 캐시된 결과를 사용합니다
                  </p>
                </div>
                <Switch defaultChecked />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label>자동 fallback</Label>
                  <p className="text-sm text-muted-foreground">
                    기본 모델 실패 시 다른 모델로 자동 전환합니다
                  </p>
                </div>
                <Switch defaultChecked />
              </div>

              <Button variant="outline" onClick={handleClearCache}>
                <Trash2 className="w-4 h-4 mr-2" />
                캐시 삭제
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 알림 설정 */}
        <TabsContent value="notifications" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Bell className="w-5 h-5 mr-2" />
                알림 설정
              </CardTitle>
              <CardDescription>
                다양한 알림을 관리합니다
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <Label>푸시 알림</Label>
                  <p className="text-sm text-muted-foreground">
                    브라우저 푸시 알림을 받습니다
                  </p>
                </div>
                <Switch
                  checked={userSettings.notifications_enabled}
                  onCheckedChange={(checked) => handleUserSettingsChange('notifications_enabled', checked)}
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label>이메일 알림</Label>
                  <p className="text-sm text-muted-foreground">
                    중요한 분석 결과를 이메일로 받습니다
                  </p>
                </div>
                <Switch
                  checked={userSettings.email_notifications}
                  onCheckedChange={(checked) => handleUserSettingsChange('email_notifications', checked)}
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label>거래 동기화 알림</Label>
                  <p className="text-sm text-muted-foreground">
                    새로운 거래가 동기화되면 알림을 받습니다
                  </p>
                </div>
                <Switch defaultChecked />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label>AI 분석 완료 알림</Label>
                  <p className="text-sm text-muted-foreground">
                    AI 분석이 완료되면 알림을 받습니다
                  </p>
                </div>
                <Switch defaultChecked />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 스케줄 설정 */}
        <TabsContent value="schedule" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Calendar className="w-5 h-5 mr-2" />
                자동 스케줄 설정
              </CardTitle>
              <CardDescription>
                자동으로 실행될 작업들을 설정합니다
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label>자동 거래 동기화</Label>
                    <p className="text-sm text-muted-foreground">
                      정기적으로 은행 거래 내역을 동기화합니다
                    </p>
                  </div>
                  <Switch
                    checked={userSettings.auto_sync_enabled}
                    onCheckedChange={(checked) => handleUserSettingsChange('auto_sync_enabled', checked)}
                  />
                </div>

                {userSettings.auto_sync_enabled && (
                  <div className="ml-6 space-y-2">
                    <Label>동기화 주기</Label>
                    <Select
                      value={userSettings.sync_frequency}
                      onValueChange={(value) => handleUserSettingsChange('sync_frequency', value)}
                    >
                      <SelectTrigger className="w-48">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="daily">매일</SelectItem>
                        <SelectItem value="weekly">매주</SelectItem>
                        <SelectItem value="monthly">매월</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                )}
              </div>

              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label>자동 AI 분석</Label>
                    <p className="text-sm text-muted-foreground">
                      정기적으로 소비 패턴을 분석합니다
                    </p>
                  </div>
                  <Switch
                    checked={scheduleSettings.auto_analysis}
                    onCheckedChange={(checked) => handleScheduleSettingsChange('auto_analysis', checked)}
                  />
                </div>

                {scheduleSettings.auto_analysis && (
                  <div className="ml-6 space-y-2">
                    <Label>분석 주기</Label>
                    <Select
                      value={scheduleSettings.analysis_frequency}
                      onValueChange={(value) => handleScheduleSettingsChange('analysis_frequency', value)}
                    >
                      <SelectTrigger className="w-48">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="daily">매일</SelectItem>
                        <SelectItem value="weekly">매주</SelectItem>
                        <SelectItem value="monthly">매월</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                )}
              </div>

              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label>자동 리포트 생성</Label>
                    <p className="text-sm text-muted-foreground">
                      정기적으로 소비 리포트를 생성합니다
                    </p>
                  </div>
                  <Switch
                    checked={scheduleSettings.report_generation}
                    onCheckedChange={(checked) => handleScheduleSettingsChange('report_generation', checked)}
                  />
                </div>

                {scheduleSettings.report_generation && (
                  <div className="ml-6 space-y-2">
                    <Label>리포트 생성 주기</Label>
                    <Select
                      value={scheduleSettings.report_frequency}
                      onValueChange={(value) => handleScheduleSettingsChange('report_frequency', value)}
                    >
                      <SelectTrigger className="w-48">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="weekly">매주</SelectItem>
                        <SelectItem value="monthly">매월</SelectItem>
                        <SelectItem value="quarterly">분기별</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 데이터 관리 */}
        <TabsContent value="data" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Shield className="w-5 h-5 mr-2" />
                데이터 관리
              </CardTitle>
              <CardDescription>
                개인 데이터를 관리하고 보호합니다
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-4">
                <div>
                  <h4 className="font-medium mb-2">데이터 내보내기</h4>
                  <p className="text-sm text-muted-foreground mb-3">
                    모든 거래 내역과 분석 결과를 JSON 형식으로 내보냅니다
                  </p>
                  <Button variant="outline" onClick={handleExportData}>
                    데이터 내보내기
                  </Button>
                </div>

                <div>
                  <h4 className="font-medium mb-2">개인정보 보호</h4>
                  <p className="text-sm text-muted-foreground mb-3">
                    모든 개인 데이터는 암호화되어 안전하게 저장됩니다
                  </p>
                  <div className="flex items-center space-x-2">
                    <Badge variant="outline" className="bg-green-50 text-green-700">
                      ✓ 데이터 암호화
                    </Badge>
                    <Badge variant="outline" className="bg-green-50 text-green-700">
                      ✓ HTTPS 통신
                    </Badge>
                    <Badge variant="outline" className="bg-green-50 text-green-700">
                      ✓ 개인정보보호법 준수
                    </Badge>
                  </div>
                </div>

                <div>
                  <h4 className="font-medium mb-2 text-red-600">위험 구역</h4>
                  <p className="text-sm text-muted-foreground mb-3">
                    아래 작업들은 되돌릴 수 없습니다. 신중하게 진행하세요.
                  </p>
                  <div className="space-y-2">
                    <Button variant="outline" className="text-red-600 border-red-200 hover:bg-red-50">
                      <Trash2 className="w-4 h-4 mr-2" />
                      모든 거래 내역 삭제
                    </Button>
                    <Button variant="outline" className="text-red-600 border-red-200 hover:bg-red-50">
                      <Trash2 className="w-4 h-4 mr-2" />
                      계정 삭제
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

export default SettingsPage;

