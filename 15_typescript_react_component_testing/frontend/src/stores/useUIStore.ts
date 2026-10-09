import { create } from 'zustand';
import { UIState } from '../types/state';

export const useUIStore = create<UIState>((set) => ({
  isMockNetworkDown: false,
  mockLatencyMs: 0,

  setMockNetworkDown: (down: boolean) => set({ isMockNetworkDown: down }),
  setMockLatencyMs: (ms: number) => set({ mockLatencyMs: ms }),
}));

export default useUIStore;
