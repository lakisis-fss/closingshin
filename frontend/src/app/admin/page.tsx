'use client';

import { useState } from 'react';
import { Header } from '@/components/layout/Header';
import { SchedulerStatus } from '@/components/admin/SchedulerStatus';
import { LiveStatusCard } from '@/components/admin/LiveStatusCard';
import { MaintenanceModal } from '@/components/admin/MaintenanceModal';
import { LogViewer } from '@/components/admin/LogViewer'; // NEW
import { Settings, ShieldCheck, Activity } from 'lucide-react';

export default function AdminPage() {
    const [isMaintenanceOpen, setIsMaintenanceOpen] = useState(false);

    return (
        <main className="min-h-screen p-8 bg-canvas">
            <Header />

            <div className="max-w-6xl mx-auto">
                <div className="mb-12">
                    <div className="flex items-center gap-4 mb-2">
                        <div className="p-3 bg-ink text-white">
                            <Settings size={32} />
                        </div>
                        <h2 className="text-5xl font-black uppercase tracking-tighter">시스템 제어</h2>
                    </div>
                    <p className="text-xl text-gray-600 font-medium">백엔드 작업, 데이터 동기화 및 시스템 상태를 관리합니다.</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
                    <div className="bg-white border-4 border-ink p-6 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] flex flex-col items-center text-center group hover:bg-bauhaus-yellow transition-colors">
                        <ShieldCheck size={48} className="mb-4 text-ink" />
                        <h3 className="text-xl font-black uppercase mb-2">시스템 보안</h3>
                        <p className="text-sm text-gray-500 font-bold">모든 백그라운드 프로세스가 모니터링되고 안전하게 보호됩니다.</p>
                    </div>
                    <LiveStatusCard />
                    <button
                        onClick={() => setIsMaintenanceOpen(true)}
                        className="bg-white border-4 border-ink p-6 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] flex flex-col items-center text-center group hover:bg-bauhaus-red hover:text-white transition-colors"
                    >
                        <Settings size={48} className="mb-4 text-ink group-hover:text-white" />
                        <h3 className="text-xl font-black uppercase mb-2">유지 보수</h3>
                        <p className="text-sm text-gray-500 group-hover:text-white/80 font-bold">수동 제어 및 데이터 재색인 도구입니다.</p>
                    </button>
                </div>

                <div className="mb-12">
                    <div className="inline-block bg-ink text-white px-4 py-1 text-sm font-black uppercase mb-4 tracking-widest">
                        작업 오케스트레이션
                    </div>
                    <SchedulerStatus />
                </div>

                <div className="mb-8">
                    <div className="inline-block bg-ink text-white px-4 py-1 text-sm font-black uppercase mb-4 tracking-widest">
                        시스템 로그
                    </div>
                    <LogViewer />
                </div>

                <div className="mt-16 pt-8 border-t-4 border-ink text-center">
                    <p className="font-black uppercase tracking-widest text-gray-400">ClosingSHIN OS v1.0.4 - 관리자 터미널</p>
                </div>
            </div>

            <MaintenanceModal isOpen={isMaintenanceOpen} onClose={() => setIsMaintenanceOpen(false)} />
        </main>
    );
}
