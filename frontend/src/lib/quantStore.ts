'use client';

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { QuantWeights, DEFAULT_WEIGHTS } from './scoreCalculator';

interface QuantStore {
    weights: QuantWeights;
    setWeights: (weights: QuantWeights) => void;
}

export const useQuantStore = create<QuantStore>()(
    persist(
        (set) => ({
            weights: DEFAULT_WEIGHTS,
            setWeights: (weights) => set({ weights }),
        }),
        {
            name: 'quant-weights-storage',
        }
    )
);
