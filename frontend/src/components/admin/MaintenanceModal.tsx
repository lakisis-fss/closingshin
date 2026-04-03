'use client';

import { useState } from 'react';
import { Settings, RefreshCw, X, AlertTriangle, Database } from 'lucide-react';
import { cn } from '@/lib/utils'; // Assuming cn exists

interface MaintenanceModalProps {
    isOpen: boolean;
    onClose: () => void;
}

export function MaintenanceModal({ isOpen, onClose }: MaintenanceModalProps) {
    const [triggering, setTriggering] = useState<string | null>(null);
    const [message, setMessage] = useState<string | null>(null);

    if (!isOpen) return null;

    const handleTrigger = async (jobId: string, jobName: string) => {
        if (triggering) return;

        if (!confirm(`Are you sure you want to run "${jobName}"? This may take some time.`)) {
            return;
        }

        setTriggering(jobId);
        setMessage(`Starting ${jobName}...`);

        try {
            const res = await fetch('/api/scheduler/trigger', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ job: jobId }),
            });

            if (!res.ok) throw new Error('Failed to trigger job');

            const text = await res.text();
            setMessage(`Success: ${text}`);

            // Auto close message after 3s
            setTimeout(() => setMessage(null), 3000);
        } catch (err) {
            setMessage(`Error: ${String(err)}`);
        } finally {
            setTriggering(null);
        }
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
            <div className="bg-white border-4 border-ink w-[500px] shadow-[16px_16px_0px_0px_rgba(0,0,0,1)] max-h-[90vh] overflow-y-auto">
                <div className="bg-ink text-white p-4 flex justify-between items-center sticky top-0 z-10">
                    <h2 className="text-2xl font-black uppercase flex items-center gap-2">
                        <Settings size={28} /> System Maintenance
                    </h2>
                    <button onClick={onClose} className="hover:text-bauhaus-yellow transition-colors">
                        <X size={28} />
                    </button>
                </div>

                <div className="p-6 space-y-6">
                    <div className="bg-yellow-50 border-2 border-yellow-200 p-4 flex items-start gap-3">
                        <AlertTriangle className="text-yellow-600 shrink-0" size={24} />
                        <div>
                            <h3 className="font-bold text-yellow-800 uppercase mb-1">Caution</h3>
                            <p className="text-sm text-yellow-700">
                                Running maintenance tasks can put high load on the system and may interrupt ongoing processes. Use only when necessary.
                            </p>
                        </div>
                    </div>

                    {message && (
                        <div className={cn(
                            "p-3 text-sm font-bold text-center border-2",
                            message.startsWith("Error")
                                ? "bg-red-50 border-red-200 text-red-600"
                                : "bg-green-50 border-green-200 text-green-600"
                        )}>
                            {message}
                        </div>
                    )}

                    <div className="space-y-4">
                        <div className="border-2 border-gray-200 p-4 hover:border-ink transition-colors group">
                            <div className="flex justify-between items-start mb-3">
                                <div>
                                    <h3 className="font-black uppercase text-lg flex items-center gap-2">
                                        <Database size={20} /> Data Re-indexing
                                    </h3>
                                    <p className="text-sm text-gray-500 font-bold mt-1">
                                        Update Stock Info (Fundamental, Market Cap)
                                    </p>
                                </div>
                                <span className="bg-gray-100 text-gray-500 text-xs font-bold px-2 py-1 uppercase">
                                    ~5 Mins
                                </span>
                            </div>
                            <p className="text-sm text-gray-600 mb-4">
                                Runs <code>06_collect_stock_data.py</code>. Updates all static stock information including sector, market cap, and fundamental scores.
                            </p>
                            <button
                                onClick={() => handleTrigger('stock', 'Stock Info Update')}
                                disabled={!!triggering}
                                className="w-full bg-white border-2 border-ink py-2 uppercase font-black text-sm tracking-widest hover:bg-ink hover:text-white transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                            >
                                {triggering === 'stock' ? <RefreshCw className="animate-spin" size={16} /> : <RefreshCw size={16} />}
                                {triggering === 'stock' ? 'Running...' : 'Run Re-indexing'}
                            </button>
                        </div>

                        <div className="border-2 border-gray-200 p-4 hover:border-ink transition-colors group">
                            <div className="flex justify-between items-start mb-3">
                                <div>
                                    <h3 className="font-black uppercase text-lg flex items-center gap-2">
                                        <RefreshCw size={20} /> Force Market Status
                                    </h3>
                                    <p className="text-sm text-gray-500 font-bold mt-1">
                                        Refresh Market Data & Indices
                                    </p>
                                </div>
                                <span className="bg-gray-100 text-gray-500 text-xs font-bold px-2 py-1 uppercase">
                                    ~1 Min
                                </span>
                            </div>
                            <p className="text-sm text-gray-600 mb-4">
                                Runs <code>05_collect_market_status.py</code>. Forces a refresh of market indices, ADR, and investor trends.
                            </p>
                            <button
                                onClick={() => handleTrigger('market', 'Market Status Update')}
                                disabled={!!triggering}
                                className="w-full bg-white border-2 border-ink py-2 uppercase font-black text-sm tracking-widest hover:bg-ink hover:text-white transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                            >
                                {triggering === 'market' ? <RefreshCw className="animate-spin" size={16} /> : <RefreshCw size={16} />}
                                {triggering === 'market' ? 'Running...' : 'Run Update'}
                            </button>
                        </div>

                        <div className="border-2 border-gray-200 p-4 hover:border-ink transition-colors group">
                            <div className="flex justify-between items-start mb-3">
                                <div>
                                    <h3 className="font-black uppercase text-lg flex items-center gap-2">
                                        <Database size={20} /> Missing Data Recovery
                                    </h3>
                                    <p className="text-sm text-gray-500 font-bold mt-1">
                                        Scan & Fill Missing Daily Data (Last 7 Days)
                                    </p>
                                </div>
                                <span className="bg-gray-100 text-gray-500 text-xs font-bold px-2 py-1 uppercase">
                                    ~3 Mins
                                </span>
                            </div>
                            <p className="text-sm text-gray-600 mb-4">
                                Runs <code>regenerate_missing_data.py</code>. Checks past 7 days for missing stock data and attempts to collect it.
                            </p>
                            <button
                                onClick={() => handleTrigger('recovery', 'Missing Data Recovery')}
                                disabled={!!triggering}
                                className="w-full bg-white border-2 border-ink py-2 uppercase font-black text-sm tracking-widest hover:bg-ink hover:text-white transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                            >
                                {triggering === 'recovery' ? <RefreshCw className="animate-spin" size={16} /> : <RefreshCw size={16} />}
                                {triggering === 'recovery' ? 'Running...' : 'Run Recovery'}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
