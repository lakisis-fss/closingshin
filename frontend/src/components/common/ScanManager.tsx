"use client";

import { useState, useEffect, useRef } from 'react';
import { Play, X, CheckCircle, AlertTriangle, Loader2, RefreshCw } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ScanManagerProps {
    onScanComplete?: () => void;
    initialDate?: string;
    mode?: string;
    onModeChange?: (mode: string) => void;
    customParams?: any;
    onCustomParamsChange?: (params: any) => void;
}

interface ScanProgress {
    step: number;
    progress: number;
    total: number;
    percent: number;
    message: string;
    status: 'running' | 'completed' | 'error';
    timestamp: string;
}

export function ScanManager({
    onScanComplete,
    initialDate,
    mode = 'classic',
    onModeChange,
    customParams = {
        minContractions: 2,
        maxDepth1st: 0.35,
        minDepthLast: 0.02,
        maxDepthLast: 0.15,
        strictTrend: true
    },
    onCustomParamsChange
}: ScanManagerProps) {
    const [isOpen, setIsOpen] = useState(false);
    const [isScanning, setIsScanning] = useState(false);
    const [progressData, setProgressData] = useState<ScanProgress | null>(null);
    const [logs, setLogs] = useState<{ time: string; msg: string }[]>([]);
    const [error, setError] = useState<string | null>(null);

    const pollInterval = useRef<NodeJS.Timeout | null>(null);

    const startScan = async (date?: string) => {
        setIsOpen(true);
        setIsScanning(true);
        setError(null);
        setLogs([]);
        setProgressData({
            step: 0,
            progress: 0,
            total: 100,
            percent: 0,
            message: date ? `Initializing scan for ${date}...` : 'Initializing scan...',
            status: 'running',
            timestamp: new Date().toISOString()
        });

        try {
            const res = await fetch('/api/system/run-scan', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    date,
                    mode,
                    custom: mode === 'custom' ? customParams : undefined
                })
            });
            if (!res.ok) throw new Error('Failed to start scan');

            // Start polling
            startPolling();
        } catch (e: any) {
            setError(e.message);
            setIsScanning(false);
        }
    };

    const startPolling = () => {
        if (pollInterval.current) clearInterval(pollInterval.current);

        pollInterval.current = setInterval(async () => {
            try {
                const res = await fetch('/api/system/scan-progress?t=' + Date.now());
                const data: ScanProgress = await res.json();

                // Update state
                setProgressData(data);

                // Add to log if message changed
                setLogs(prev => {
                    if (prev.length > 0 && prev[prev.length - 1].msg === data.message) return prev;
                    return [...prev, { time: new Date().toLocaleTimeString(), msg: data.message }];
                });

                if (data.status === 'completed' || data.status === 'error') {
                    setIsScanning(false);
                    if (pollInterval.current) clearInterval(pollInterval.current);
                    if (data.status === 'completed' && onScanComplete) {
                        onScanComplete();
                    }
                }
            } catch (e) {
                console.error("Polling error", e);
            }
        }, 1000);
    };

    const handleClose = () => {
        setIsOpen(false);
        // Continue scanning in background (polling will resume if modal is reopened)
    };

    // Auto-scroll logs
    const logsEndRef = useRef<HTMLDivElement>(null);
    useEffect(() => {
        logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [logs]);

    // Cleanup
    useEffect(() => {
        return () => {
            if (pollInterval.current) clearInterval(pollInterval.current);
        };
    }, []);

    // Bauhaus / Brutalist Styles
    // Thick borders, distinct colors, geometric shapes

    return (
        <>
            <div className="flex flex-col gap-3 w-full">
                <div className="flex flex-wrap items-center gap-3 w-full">
                    <select
                        value={mode}
                        onChange={(e) => onModeChange?.(e.target.value)}
                        className="h-12 px-4 border-4 border-ink font-black text-sm uppercase outline-none shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] transition-all bg-white hover:bg-gray-50 cursor-pointer w-full sm:w-auto flex-1 min-w-[200px]"
                        disabled={isScanning}
                    >
                        <option value="classic">Classic (정통)</option>
                        <option value="aggressive">Aggressive (야수)</option>
                        <option value="earlybird">EarlyBird (얼리버드)</option>
                        <option value="stable">Stable (우량주 방어)</option>
                        <option value="relaxed">Relaxed (릴렉스 박스권)</option>
                        <option value="custom">Custom (커스텀 팩토리)</option>
                    </select>

                    <button
                        onClick={() => startScan(initialDate)}
                        disabled={isScanning}
                        className="
                            group relative flex items-center justify-center gap-2 h-12 px-6
                            bg-white border-4 border-ink font-black text-ink uppercase text-sm whitespace-nowrap
                            shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] hover:bg-bauhaus-yellow transition-all
                            disabled:opacity-50 disabled:cursor-not-allowed w-full sm:w-auto flex-1 min-w-[200px] flex-shrink-0
                        "
                    >
                        <Play className="w-4 h-4 fill-current" />
                        <span>START VCP SCAN</span>
                    </button>
                </div>
                {mode === 'custom' && (
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 p-4 border-4 border-black bg-white shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] max-w-xl">
                        <label className="flex flex-col text-sm font-bold">
                            최소 파동 횟수:
                            <input type="number" disabled={isScanning} value={customParams.minContractions} onChange={e => onCustomParamsChange?.({ ...customParams, minContractions: Number(e.target.value) })} className="border-2 border-black px-2 py-1 mt-1 outline-none focus:border-bauhaus-blue" />
                        </label>
                        <label className="flex flex-col text-sm font-bold">
                            1차 최대 하락폭 (비율):
                            <input type="number" step="0.01" disabled={isScanning} value={customParams.maxDepth1st} onChange={e => onCustomParamsChange?.({ ...customParams, maxDepth1st: Number(e.target.value) })} className="border-2 border-black px-2 py-1 mt-1 outline-none focus:border-bauhaus-blue" />
                        </label>
                        <label className="flex flex-col text-sm font-bold">
                            마지막 최소 하락폭 (비율):
                            <input type="number" step="0.01" disabled={isScanning} value={customParams.minDepthLast} onChange={e => onCustomParamsChange?.({ ...customParams, minDepthLast: Number(e.target.value) })} className="border-2 border-black px-2 py-1 mt-1 outline-none focus:border-bauhaus-blue" />
                        </label>
                        <label className="flex flex-col text-sm font-bold">
                            마지막 최대 하락폭 (비율):
                            <input type="number" step="0.01" disabled={isScanning} value={customParams.maxDepthLast} onChange={e => onCustomParamsChange?.({ ...customParams, maxDepthLast: Number(e.target.value) })} className="border-2 border-black px-2 py-1 mt-1 outline-none focus:border-bauhaus-blue" />
                        </label>
                        <label className="flex items-center gap-2 text-sm font-bold col-span-1 sm:col-span-2 mt-2">
                            <input type="checkbox" disabled={isScanning} checked={customParams.strictTrend} onChange={e => onCustomParamsChange?.({ ...customParams, strictTrend: e.target.checked })} className="w-5 h-5 border-2 border-black accent-bauhaus-blue" />
                            엄격한 추세 정배열 요구 (200일선 위 &amp; 50&gt;150&gt;200)
                        </label>
                    </div>
                )}
            </div>

            {isOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
                    <div className="
                        relative w-full max-w-2xl bg-white border-4 border-black 
                        shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] p-0 overflow-hidden
                    ">
                        {/* Header */}
                        <div className="flex items-center justify-between border-b-4 border-black bg-bauhaus-blue p-4">
                            <h2 className="text-xl font-black text-white flex items-center gap-2">
                                {isScanning ? <Loader2 className="animate-spin" /> : <CheckCircle />}
                                SYSTEM SCAN STATUS
                            </h2>
                            {/* Always allow closing the modal (background execution supported) */}
                            <button
                                onClick={handleClose}
                                className="p-1 hover:bg-black hover:text-white border-2 border-transparent hover:border-white transition-colors"
                                title="Close (Run in background)"
                            >
                                <X className="w-6 h-6" />
                            </button>
                        </div>

                        {/* Content */}
                        <div className="p-6 space-y-6">

                            {/* Status Bar */}
                            <div className="space-y-2">
                                <div className="flex justify-between font-mono font-bold text-sm">
                                    <span>
                                        PROGRESS
                                        {progressData?.step && progressData.step > 0 && progressData.step <= 6 ?
                                            <span className="ml-2 text-gray-500">(STEP {progressData.step}/6)</span>
                                            : null}
                                    </span>
                                    <span>{progressData?.percent}%</span>
                                </div>
                                <div className="h-8 w-full border-4 border-black bg-gray-100 p-1">
                                    <div
                                        className={cn(
                                            "h-full transition-all duration-300 ease-out",
                                            progressData?.status === 'error' ? "bg-bauhaus-red" : "bg-bauhaus-blue"
                                        )}
                                        style={{ width: `${progressData?.percent}%` }}
                                    />
                                </div>
                            </div>

                            {/* Target Date Info */}
                            <div className="flex border-4 border-black">
                                <div className="bg-black text-white px-4 py-3 flex items-center">
                                    <span className="text-[10px] font-black uppercase tracking-widest">TARGET<br />DATE</span>
                                </div>
                                <div className="flex-1 px-4 py-2 bg-white flex items-center justify-between">
                                    <span className="text-2xl font-black font-mono tracking-tight">
                                        {initialDate
                                            ? `${initialDate.slice(0, 4)}.${initialDate.slice(4, 6)}.${initialDate.slice(6, 8)}`
                                            : new Date().toLocaleDateString('ko-KR', { year: 'numeric', month: '2-digit', day: '2-digit' }).replace(/\. /g, '.').replace('.', '')
                                        }
                                    </span>
                                    <span className={cn(
                                        "text-[10px] font-black uppercase px-2 py-1 border-2 border-black",
                                        initialDate ? "bg-bauhaus-yellow text-black" : "bg-gray-100 text-gray-500"
                                    )}>
                                        {initialDate ? "HISTORICAL" : "TODAY"}
                                    </span>
                                </div>
                            </div>

                            {/* Current Action */}
                            <div className="border-4 border-black p-4 bg-gray-50 flex items-start gap-4">
                                <div className={cn(
                                    "p-2 border-2 border-black",
                                    progressData?.status === 'error' ? "bg-bauhaus-red text-white" : "bg-bauhaus-yellow text-black"
                                )}>
                                    {progressData?.status === 'error' ? <AlertTriangle className="w-6 h-6" /> : <RefreshCw className={cn("w-6 h-6", isScanning && "animate-spin")} />}
                                </div>
                                <div>
                                    <div className="font-bold text-lg mb-1">
                                        {progressData?.status === 'completed' ? 'SCAN COMPLETE' :
                                            progressData?.status === 'error' ? 'SCAN FAILED' : 'PROCESSING...'}
                                    </div>
                                    <div className="font-mono text-sm break-all">
                                        {progressData?.message || "Initializing..."}
                                    </div>
                                </div>
                            </div>

                            {/* Terminal Logs */}
                            <div className="h-48 border-4 border-black bg-black text-green-400 font-mono text-xs p-4 overflow-y-auto">
                                {logs.map((log, i) => (
                                    <div key={i} className="mb-1">
                                        <span className="text-gray-500">[{log.time}]</span> {log.msg}
                                    </div>
                                ))}
                                <div ref={logsEndRef} />
                            </div>

                            {/* Error Message */}
                            {error && (
                                <div className="bg-red-100 border-4 border-red-500 text-red-700 p-4 font-bold">
                                    ERROR: {error}
                                </div>
                            )}

                        </div>

                        {/* Footer */}
                        {progressData?.status === 'completed' && (
                            <div className="border-t-4 border-black p-4 bg-gray-100 flex justify-end">
                                <button
                                    onClick={handleClose}
                                    className="
                                        px-6 py-2 bg-black text-white font-bold border-2 border-transparent 
                                        hover:bg-bauhaus-blue hover:text-white hover:border-black transition-all
                                        shadow-[2px_2px_0px_0px_rgba(0,0,0,0.5)]
                                    "
                                >
                                    CLOSE & REFRESH
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            )}
        </>
    );
}
