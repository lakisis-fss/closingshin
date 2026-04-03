'use client';

import { useState, useEffect, useRef } from 'react';
import { Activity, Clock, Loader2, Zap } from 'lucide-react';
import { cn } from '@/lib/utils';

interface JobStatus {
    name: string;
    lastRun: string | null;
    nextRun: string | null;
    status: 'idle' | 'running' | 'error';
    lastError?: string;
}

type SchedulerState = Record<string, JobStatus>;

export function LiveStatusCard() {
    const [status, setStatus] = useState<SchedulerState | null>(null);
    const [loading, setLoading] = useState(true);
    
    // Use refs instead of state to prevent 1-second React re-renders which trigger the Next.js dev indicator
    const statusRef = useRef<SchedulerState | null>(null);
    const marketRef = useRef<HTMLSpanElement>(null);
    const vcpRef = useRef<HTMLSpanElement>(null);

    const fetchStatus = async () => {
        try {
            const res = await fetch('/api/scheduler/status');
            if (!res.ok) throw new Error('Failed to fetch status');
            const data = await res.json();
            setStatus(data);
            statusRef.current = data;
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const getTimeRemaining = (targetDateStr: string | null, now: Date) => {
        if (!targetDateStr) return '대기 중...';

        const target = new Date(targetDateStr);
        const diff = target.getTime() - now.getTime();

        if (diff <= 0) return '처리 중...';

        const hours = Math.floor(diff / (1000 * 60 * 60));
        const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((diff % (1000 * 60)) / 1000);

        if (hours > 0) {
            return `${hours}시간 ${minutes}분 ${seconds}초`;
        }
        return `${minutes}분 ${seconds}초`;
    };

    useEffect(() => {
        fetchStatus();

        // Fetch status every 60s to sync nextRun if changed by server
        const statusInterval = setInterval(fetchStatus, 60000);

        // Update DOM manually every second to avoid re-rendering entire component
        const timerInterval = setInterval(() => {
            const now = new Date();
            if (statusRef.current) {
                if (marketRef.current) {
                    marketRef.current.innerText = getTimeRemaining(statusRef.current.marketUpdate?.nextRun, now);
                }
                if (vcpRef.current) {
                    vcpRef.current.innerText = getTimeRemaining(statusRef.current.vcpScan?.nextRun, now);
                }
            }
        }, 1000);

        return () => {
            clearInterval(statusInterval);
            clearInterval(timerInterval);
        };
    }, []);

    return (
        <div className="bg-white border-4 border-ink p-6 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] flex flex-col items-center text-center group hover:bg-bauhaus-blue hover:text-white transition-colors relative overflow-hidden">
            <div className="absolute top-2 right-2 animate-pulse">
                <div className="w-3 h-3 bg-green-500 rounded-full border border-white"></div>
            </div>

            <Activity size={48} className="mb-4 text-ink group-hover:text-white" />
            <h3 className="text-xl font-black uppercase mb-4">실시간 상태</h3>

            {loading ? (
                <Loader2 className="animate-spin text-gray-400" />
            ) : status ? (
                <div className="w-full space-y-3">
                    <div className="bg-gray-100/50 group-hover:bg-white/10 p-2 rounded flex justify-between items-center text-sm">
                        <span className="font-bold flex items-center gap-1">
                            <Zap size={14} /> 시장 데이터
                        </span>
                        <span ref={marketRef} className="font-mono font-bold text-ink group-hover:text-white">
                            {getTimeRemaining(status.marketUpdate?.nextRun, new Date())}
                        </span>
                    </div>
                    <div className="bg-gray-100/50 group-hover:bg-white/10 p-2 rounded flex justify-between items-center text-sm">
                        <span className="font-bold flex items-center gap-1">
                            <Clock size={14} /> VCP Scan
                        </span>
                        <span ref={vcpRef} className="font-mono font-bold text-ink group-hover:text-white">
                            {getTimeRemaining(status.vcpScan?.nextRun, new Date())}
                        </span>
                    </div>
                </div>
            ) : (
                <p className="text-sm font-bold text-red-500">시스템 오프라인</p>
            )}
        </div>
    );
}
