import { create } from 'zustand';
import { persist } from 'zustand/middleware';

// 인증 상태 관리
export const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      
      login: (user, token) => {
        localStorage.setItem('access_token', token);
        set({ user, token, isAuthenticated: true });
      },
      
      logout: () => {
        localStorage.removeItem('access_token');
        set({ user: null, token: null, isAuthenticated: false });
      },
      
      updateUser: (userData) => {
        set((state) => ({ user: { ...state.user, ...userData } }));
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ 
        user: state.user, 
        token: state.token, 
        isAuthenticated: state.isAuthenticated 
      }),
    }
  )
);

// 거래 내역 상태 관리
export const useTransactionStore = create((set, get) => ({
  transactions: [],
  currentTransaction: null,
  loading: false,
  error: null,
  
  setTransactions: (transactions) => set({ transactions }),
  
  addTransaction: (transaction) => 
    set((state) => ({ 
      transactions: [transaction, ...state.transactions] 
    })),
  
  updateTransaction: (id, updatedTransaction) =>
    set((state) => ({
      transactions: state.transactions.map((t) =>
        t.id === id ? { ...t, ...updatedTransaction } : t
      ),
    })),
  
  setCurrentTransaction: (transaction) => set({ currentTransaction: transaction }),
  
  setLoading: (loading) => set({ loading }),
  
  setError: (error) => set({ error }),
  
  clearError: () => set({ error: null }),
}));

// AI 분석 상태 관리
export const useAIStore = create((set, get) => ({
  analysisResults: {},
  currentAnalysis: null,
  availableModels: {},
  performance: null,
  loading: false,
  error: null,
  
  setAnalysisResult: (type, result) =>
    set((state) => ({
      analysisResults: { ...state.analysisResults, [type]: result },
    })),
  
  setCurrentAnalysis: (analysis) => set({ currentAnalysis: analysis }),
  
  setAvailableModels: (models) => set({ availableModels: models }),
  
  setPerformance: (performance) => set({ performance }),
  
  setLoading: (loading) => set({ loading }),
  
  setError: (error) => set({ error }),
  
  clearError: () => set({ error: null }),
  
  clearCache: () => set({ analysisResults: {} }),
}));

// 스케줄 상태 관리
export const useScheduleStore = create((set, get) => ({
  schedules: [],
  loading: false,
  error: null,
  
  setSchedules: (schedules) => set({ schedules }),
  
  addSchedule: (schedule) =>
    set((state) => ({ schedules: [...state.schedules, schedule] })),
  
  removeSchedule: (id) =>
    set((state) => ({
      schedules: state.schedules.filter((s) => s.id !== id),
    })),
  
  setLoading: (loading) => set({ loading }),
  
  setError: (error) => set({ error }),
  
  clearError: () => set({ error: null }),
}));

// 앱 전역 상태 관리
export const useAppStore = create((set, get) => ({
  theme: 'light',
  sidebarOpen: false,
  notifications: [],
  
  toggleTheme: () =>
    set((state) => ({ theme: state.theme === 'light' ? 'dark' : 'light' })),
  
  setTheme: (theme) => set({ theme }),
  
  toggleSidebar: () =>
    set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  
  addNotification: (notification) =>
    set((state) => ({
      notifications: [...state.notifications, { ...notification, id: Date.now() }],
    })),
  
  removeNotification: (id) =>
    set((state) => ({
      notifications: state.notifications.filter((n) => n.id !== id),
    })),
  
  clearNotifications: () => set({ notifications: [] }),
}));

