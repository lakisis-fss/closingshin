'use client';

import { useState, useEffect } from 'react';
import { RefreshCw } from 'lucide-react';
import { formatToKST } from '@/lib/utils';

interface MarketData {
    timestamp: string;
    NASDAQ?: {
        Change_Pct: number;
    };
    USD_KRW?: {
        Close: number;
        Change_Pct: number;
    };
}

interface MarketStatusBarProps {
    data: MarketData;
}

export function MarketStatusBar({ data }: MarketStatusBarProps) {
    const [isUpdating, setIsUpdating] = useState(false);

    const runTask = async (endpoint: string, label: string) => {
        if (isUpdating) return;
        setIsUpdating(true);
        try {
            const res = await fetch(`/api/system/${endpoint}`, { method: 'POST' });
            if (!res.ok) throw new Error('Task failed');
            alert(`${label} Completed!`);
            window.location.reload();
        } catch (err: any) {
            alert(`Failed: ${err.message}`);
        } finally {
            setIsUpdating(false);
        }
    };

    return (
        <div className="md:col-span-4 bg-ink text-white p-4 flex flex-col gap-4 border-[4px] border-ink shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">
            <div className="flex flex-col md:flex-row justify-between items-center gap-4">
                <div className="flex wrap gap-4 items-center">
                    <span className="font-black text-xl text-bauhaus-yellow italic tracking-tighter uppercase">STAY ANALYTICAL.</span>
                    <span className="font-mono bg-white text-ink px-2 font-bold text-xs">{formatToKST(data.timestamp)}</span>

                    <div className="flex gap-2">
                        {/* Task: Market Index - Only keeping this one */}
                        <button
                            onClick={() => runTask('update-market', 'Market Sync')}
                            disabled={isUpdating}
                            className={`flex items-center gap-2 bg-bauhaus-red text-white text-[13px] font-black px-3 py-1.5 hover:bg-white hover:text-bauhaus-red transition-all border-2 border-transparent hover:border-bauhaus-red ${isUpdating ? 'opacity-50' : ''}`}
                        >
                            <RefreshCw size={12} className={isUpdating ? "animate-spin" : ""} />
                            MARKET UPDATE
                        </button>
                    </div>
                </div>

                <div className="flex gap-6 font-mono text-[15px] uppercase">
                    <div className="flex items-center gap-2">
                        <span className="text-gray-400 font-black">NASDAQ:</span>
                        <span className={`font-black ${(data.NASDAQ?.Change_Pct ?? 0) > 0 ? "text-bauhaus-red" : "text-white"}`}>
                            {data.NASDAQ?.Change_Pct ? `${data.NASDAQ.Change_Pct > 0 ? '+' : ''}${data.NASDAQ.Change_Pct.toFixed(2)}%` : '-'}
                        </span>
                    </div>
                    <div className="flex items-center gap-2">
                        <span className="text-gray-400 font-black">USD/KRW:</span>
                        <span className="font-black text-bauhaus-red">
                            {(data.USD_KRW?.Close ?? 0).toLocaleString()}
                            {data.USD_KRW?.Change_Pct ? ` (${data.USD_KRW.Change_Pct > 0 ? '+' : ''}${data.USD_KRW.Change_Pct.toFixed(2)}%)` : ''}
                        </span>
                    </div>
                </div>
            </div>
        </div>
    );
}
