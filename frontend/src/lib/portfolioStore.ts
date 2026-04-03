'use client';

import { create } from 'zustand';
import { PortfolioItem } from './types';

interface PortfolioState {
    portfolio: PortfolioItem[];
    isLoading: boolean;
    fetchPortfolio: () => Promise<void>;
    addStock: (item: Omit<PortfolioItem, 'id' | 'createdAt' | 'updatedAt'>) => Promise<void>;
    removeStock: (id: string) => Promise<void>;
    updateStock: (id: string, updates: Partial<PortfolioItem>) => Promise<void>;
    updateMemo: (id: string, memo: string, exitPlan: string) => Promise<void>;
    clearPortfolio: () => void;
}

export const usePortfolioStore = create<PortfolioState>()((set, get) => ({
    portfolio: [],
    isLoading: false,

    fetchPortfolio: async () => {
        set({ isLoading: true });
        try {
            const res = await fetch('/api/portfolio');
            if (res.ok) {
                const data = await res.json();
                set({ portfolio: Array.isArray(data) ? data : [] });
            }
        } catch (error) {
            console.error('Failed to fetch portfolio:', error);
        } finally {
            set({ isLoading: false });
        }
    },

    addStock: async (item) => {
        try {
            const res = await fetch('/api/portfolio', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(item),
            });
            if (res.ok) {
                const newItem = await res.json();
                set((state) => ({ portfolio: [...state.portfolio, newItem] }));
            }
        } catch (error) {
            console.error('Failed to add stock:', error);
        }
    },

    removeStock: async (id) => {
        try {
            const res = await fetch('/api/portfolio', {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id }),
            });
            if (res.ok) {
                set((state) => ({
                    portfolio: state.portfolio.filter((item) => item.id !== id),
                }));
            }
        } catch (error) {
            console.error('Failed to remove stock:', error);
        }
    },

    updateStock: async (id, updates) => {
        try {
            const res = await fetch('/api/portfolio', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id, ...updates }),
            });
            if (res.ok) {
                const updatedItem = await res.json();
                set((state) => ({
                    portfolio: state.portfolio.map((item) =>
                        item.id === id ? updatedItem : item
                    ),
                }));
            }
        } catch (error) {
            console.error('Failed to update stock:', error);
        }
    },

    updateMemo: async (id, memo, exitPlan) => {
        const { updateStock } = get();
        await updateStock(id, { memo, exitPlan });
    },

    clearPortfolio: () => set({ portfolio: [] }),
}));
