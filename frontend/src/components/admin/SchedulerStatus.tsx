'use client';

import { useState, useEffect } from 'react';
import { RefreshCw, Play, AlertCircle, CheckCircle2, Clock } from 'lucide-react';
import { cn, formatToKST } from '@/lib/utils';
// If cn doesn't exist, we can define a simple one or use template literals.
// Checking previous files, cn is used.

interface JobStatus {
    name: string;
    lastRun: string | null;
    status: 'idle' | 'running' | 'error';
    lastError?: string;
}

type SchedulerState = Record<string, JobStatus>;

export function SchedulerStatus() {
    const [status, setStatus] = useState<SchedulerState | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [triggering, setTriggering] = useState<string | null>(null);
    const [progressData, setProgressData] = useState<{ percent: number; message: string; status: string } | null>(null);

    const fetchStatus = async () => {
        try {
            const res = await fetch('/api/scheduler/status');
            if (!res.ok) {
                const errorData = await res.json().catch(() => ({}));
                throw new Error(errorData.details || errorData.error || 'Failed to fetch status');
            }
            const data = await res.json();
            setStatus(data);
            setError(null);
        } catch (err) {
            setError(String(err));
            setStatus(null);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchStatus();
        const interval = setInterval(fetchStatus, 5000); // Poll every 5s
        return () => clearInterval(interval);
    }, []);

    // Poll progress for Missing Data Recovery
    useEffect(() => {
        let interval: NodeJS.Timeout | undefined; // Initialize as undefined
        const isRecoveryRunning = status?.['missingDataRecovery']?.status === 'running';

        if (isRecoveryRunning) {
            const fetchProg = async () => {
                try {
                    const res = await fetch('/api/system/scan-progress');
                    if (res.ok) {
                        const data = await res.json();
                        setProgressData(data);
                    }
                } catch (e) {
                    console.error('Failed to fetch progress', e);
                }
            };
            fetchProg(); // Fetch immediately
            interval = setInterval(fetchProg, 1000);
        } else {
            setProgressData(null);
        }

        return () => {
            if (interval) {
                clearInterval(interval);
            }
        };
    }, [status]); // Depend on status updates to start/stop polling

    const handleTrigger = async (jobId: string) => {
        if (triggering) return;

        // Map internal job IDs to server trigger endpoints
        let serverJobName = '';
        let confirmMessage = '';

        if (jobId === 'marketUpdate') {
            serverJobName = 'market';
            confirmMessage = '시장 데이터를 업데이트하시겠습니까?';
        } else if (jobId === 'vcpScan') {
            serverJobName = 'vcp';
            confirmMessage = 'VCP 스캔을 시작하시겠습니까?';
        } else if (jobId === 'stockInfoUpdate') {
            serverJobName = 'stock';
            confirmMessage = '주식 정보를 업데이트(재색인)하시겠습니까? 약 5분 정도 소요됩니다.';
        } else if (jobId === 'missingDataRecovery') {
            serverJobName = 'recovery';
            confirmMessage = '누락 데이터 복구를 실행하시겠습니까? 약 3분 정도 소요됩니다.';
        } else if (jobId === 'exitMonitor') {
            serverJobName = 'exit';
            confirmMessage = '장중 감시를 시작하시겠습니까?';
        } else if (jobId === 'portfolioCalc') {
            serverJobName = 'portfolio';
            confirmMessage = '포트폴리오 계산을 실행하시겠습니까?';
        } else {
            alert(`알 수 없는 작업 ID: ${jobId}`);
            return;
        }

        if (!confirm(confirmMessage)) return;

        setTriggering(jobId);
        try {
            const res = await fetch('/api/scheduler/trigger', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ job: serverJobName }),
            });

            if (!res.ok) throw new Error('Failed to trigger job');

            // Refresh status immediately and then after a delay
            fetchStatus();
            setTimeout(fetchStatus, 2000);
        } catch (err) {
            alert('작업 실행 오류: ' + String(err));
        } finally {
            setTriggering(null);
        }
    };

    if (loading && !status) return <div className="p-4 text-center">스케줄러 상태 불러오는 중...</div>;
    if (error) return (
        <div className="p-4 border-2 border-red-500 bg-red-50 text-red-700 flex items-center gap-2">
            <AlertCircle size={20} />
            <span>스케줄러 접속 불가: {error}</span>
            <span className="text-xs ml-2">(backend/scheduler.ts가 실행 중인가요?)</span>
        </div>
    );

    return (
        <div className="border-4 border-ink bg-white shadow-[8px_8px_0px_0px_rgba(0,0,0,0.2)]">
            <div className="bg-ink text-white p-3 flex justify-between items-center">
                <h3 className="font-black uppercase flex items-center gap-2">
                    <Clock size={20} /> 시스템 스케줄러
                </h3>
                <button
                    onClick={fetchStatus}
                    className="p-1 hover:bg-white/20 rounded transition-colors"
                    title="새로고침"
                >
                    <RefreshCw size={16} />
                </button>
            </div>

            <div className="divide-y-2 divide-gray-100">
                {status && Object.entries(status).map(([id, job], index) => {
                    const isRecoveryRunning = id === 'missingDataRecovery' && job.status === 'running' && progressData;
                    
                    // Bauhaus primary colors rotation
                    const accentColors = ['bg-bauhaus-red', 'bg-bauhaus-blue', 'bg-bauhaus-yellow'];
                    const accentColor = accentColors[index % 3];

                    return (
                        <div key={id} className="relative pl-6 p-4 flex items-center justify-between hover:bg-gray-50 transition-colors gap-4 group">
                            {/* Bauhaus Vertical Accent Bar */}
                            <div className={cn("absolute left-0 top-0 bottom-0 w-2 transition-all group-hover:w-3", accentColor)} />
                            
                            <div className="min-w-[200px]">
                                <div className="font-bold text-lg leading-none mb-1 flex items-center gap-2 text-ink uppercase tracking-tight">
                                    {job.name}
                                    {job.status === 'running' && (
                                        <span className="text-[10px] bg-bauhaus-blue text-white px-2 py-0.5 font-black uppercase animate-pulse border-2 border-ink shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]">
                                            RUNNING
                                        </span>
                                    )}
                                    {job.status === 'error' && (
                                        <span className="text-[10px] bg-bauhaus-red text-white px-2 py-0.5 font-black uppercase border-2 border-ink shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]">
                                            ERROR
                                        </span>
                                    )}
                                </div>
                                <div className="text-[11px] text-ink/60 font-medium mb-1.5 leading-tight max-w-sm">
                                    {id === 'marketUpdate' && '환율, 유가, 지수 등 기초 시황 정보를 수집하여 대시보드에 표시합니다.'}
                                    {id === 'portfolioCalc' && '내 주식의 현재 가치와 수익률을 계산하여 포트폴리오 화면에 실시간으로 반영합니다.'}
                                    {id === 'vcpScan' && '차트 패턴을 분석해 급등 가능성이 있는 종목을 찾아 리스트와 차트로 보여줍니다.'}
                                    {id === 'stockInfoUpdate' && '개별 종목의 재무 상태와 외국인/기관의 수급을 정밀 분석해 점수를 매깁니다.'}
                                    {id === 'missingDataRecovery' && '오류나 전원 꺼짐으로 비어 있는 과거 데이터를 채워 분석의 연속성을 유지합니다.'}
                                    {id === 'exitMonitor' && '장중에 실시간으로 가격을 체크하여 내가 설정한 손절/익절 조건이 오면 알림을 줍니다.'}
                                </div>
                                <div className="text-[11px] text-gray-500 font-mono font-bold flex items-center gap-2">
                                    <span>마지막 실행: {formatToKST(job.lastRun)}</span>
                                    <span className="text-[9px] bg-gray-100 text-gray-500 px-1.5 py-0.5 border border-gray-300 rounded uppercase tracking-tighter">
                                        PB: {
                                            id === 'marketUpdate' ? 'market_status, ohlcv' :
                                            id === 'portfolioCalc' ? 'portfolio' :
                                            id === 'vcpScan' ? 'vcp_reports, ohlcv' :
                                            id === 'stockInfoUpdate' ? 'stock_infos' :
                                            id === 'missingDataRecovery' ? 'stock_infos' :
                                            id === 'exitMonitor' ? 'portfolio' : 'N/A'
                                        }
                                    </span>
                                </div>
                                {job.lastError && (
                                    <div className="text-[10px] text-bauhaus-red mt-1 font-mono bg-bauhaus-red/5 p-1 border-l-2 border-bauhaus-red">
                                        {job.lastError}
                                    </div>
                                )}
                            </div>

                            {/* Middle Area: Progress Bar for Recovery */}
                            {isRecoveryRunning ? (
                                <div className="flex-1 max-w-md mx-4">
                                    <div className="flex justify-between text-xs mb-1 font-mono text-gray-500 font-bold">
                                        <span className="truncate mr-2">{progressData.message || '처리 중...'}</span>
                                        <span>{progressData.percent}%</span>
                                    </div>
                                    <div className="h-3 bg-gray-100 rounded-full overflow-hidden border border-gray-300 shadow-inner relative">
                                        <div
                                            className="h-full bg-bauhaus-blue transition-all duration-300 relative overflow-hidden"
                                            style={{ width: `${progressData.percent}%` }}
                                        >
                                            <div className="absolute inset-0 bg-white/20 animate-[shimmer_2s_infinite] skew-x-[-20deg]" />
                                        </div>
                                    </div>
                                </div>
                            ) : (
                                <div className="flex-1" /> /* Spacer */
                            )}

                            <button
                                onClick={() => handleTrigger(id)}
                                disabled={triggering === id || job.status === 'running'}
                                className={cn(
                                    "flex items-center gap-2 px-3 py-1 font-bold text-xs uppercase tracking-wider border-2 transition-all",
                                    triggering === id || job.status === 'running'
                                        ? "bg-gray-100 border-gray-300 text-gray-400 cursor-not-allowed"
                                        : "bg-white border-ink hover:bg-ink hover:text-white shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[1px] hover:translate-y-[1px] hover:shadow-none active:translate-x-[2px] active:translate-y-[2px]"
                                )}
                            >
                                {triggering === id || job.status === 'running' ? <RefreshCw className="animate-spin" size={14} /> : <Play size={14} />}
                                {triggering === id ? '시작 중' : '실행'}
                            </button>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}

// Ensure cn is imported correctly or define it if missing.
// Checking previous source code: VcpDashboard.tsx uses 'cn' from '@/lib/utils'.
// So the import should be fine.
