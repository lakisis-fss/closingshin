'use client';

import { useState, useEffect } from 'react';
import { HOLIDAYS_2026 } from '@/lib/constants';

interface MarketStatus {
    isMarketOpen: boolean;
    status: 'OPEN' | 'CLOSED';
    message?: string;
}

export function useMarketStatus(): MarketStatus {
    const [status, setStatus] = useState<MarketStatus>({
        isMarketOpen: false,
        status: 'CLOSED',
    });

    useEffect(() => {
        const checkMarketStatus = () => {
            const now = new Date();
            const year = now.getFullYear();
            const month = String(now.getMonth() + 1).padStart(2, '0');
            const date = String(now.getDate()).padStart(2, '0');
            const day = now.getDay(); // 0: Sun, 6: Sat
            const hour = now.getHours();
            const minute = now.getMinutes();
            const currentTime = hour * 100 + minute;

            const todayString = `${year}-${month}-${date}`;

            // 1. Check Weekend
            if (day === 0 || day === 6) {
                setStatus({ isMarketOpen: false, status: 'CLOSED', message: 'Weekend' });
                return;
            }

            // 2. Check Holiday
            if (HOLIDAYS_2026.includes(todayString)) {
                setStatus({ isMarketOpen: false, status: 'CLOSED', message: 'Holiday' });
                return;
            }

            // 3. Check Market Hours (09:00 - 15:30)
            if (currentTime >= 900 && currentTime < 1530) {
                setStatus({ isMarketOpen: true, status: 'OPEN' });
            } else {
                setStatus({ isMarketOpen: false, status: 'CLOSED', message: 'Market Closed' });
            }
        };

        // Initial check
        checkMarketStatus();

        // Update every minute
        const interval = setInterval(checkMarketStatus, 60000);

        return () => clearInterval(interval);
    }, []);

    return status;
}
