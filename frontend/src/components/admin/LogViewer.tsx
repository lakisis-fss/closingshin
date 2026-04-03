'use client';

import { useState, useEffect, useRef } from 'react';
import { Terminal, RefreshCw, Trash2, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

export function LogViewer() {
    const [logs, setLogs] = useState<string[]>([]);
    const [loading, setLoading] = useState(false);
    const logContainerRef = useRef<HTMLDivElement>(null);

    const fetchLogs = async () => {
        setLoading(true);
        try {
            const res = await fetch('/api/system/logs');
            if (res.ok) {
                const data = await res.json();
                setLogs(data.logs || []);
                // Scroll to bottom after update
                setTimeout(() => {
                    if (logContainerRef.current) {
                        logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
                    }
                }, 100);
            }
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const clearLogs = async () => {
        if (!confirm('Are you sure you want to clear all system logs?')) return;

        setLoading(true);
        try {
            const res = await fetch('/api/system/logs', { method: 'DELETE' });
            if (res.ok) {
                setLogs([]);
            } else {
                const data = await res.json();
                alert(`Failed to clear logs: ${data.error || 'Unknown error'}`);
            }
        } catch (err) {
            console.error(err);
            alert('An error occurred while trying to clear the logs.');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchLogs();
    }, []);

    return (
        <div className="bg-white border-4 border-ink p-6 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">
            <div className="flex justify-between items-center mb-4">
                <h3 className="text-xl font-black uppercase flex items-center gap-2">
                    <Terminal size={24} /> System Logs
                </h3>
                <div className="flex gap-2">
                    <button
                        onClick={fetchLogs}
                        disabled={loading}
                        className={cn(
                            "p-2 border-2 border-ink transition-colors",
                            loading ? "opacity-50 cursor-not-allowed" : "hover:bg-ink hover:text-white"
                        )}
                        title="Refresh Logs"
                    >
                        <RefreshCw size={16} className={cn(loading && "animate-spin")} />
                    </button>
                    <button
                        onClick={clearLogs}
                        disabled={loading}
                        className={cn(
                            "p-2 border-2 border-ink transition-colors",
                            loading ? "opacity-50 cursor-not-allowed" : "hover:bg-red-600 hover:text-white hover:border-red-600 font-bold"
                        )}
                        title="Clear Logs"
                    >
                        <Trash2 size={16} />
                    </button>
                </div>
            </div>

            <div
                ref={logContainerRef}
                className="bg-ink text-green-400 font-mono text-sm p-4 h-[400px] overflow-y-auto border-2 border-ink custom-scrollbar"
            >
                {logs.length > 0 ? (
                    logs.map((line, i) => (
                        <div key={i} className="whitespace-pre-wrap break-all border-b border-gray-800 pb-1 mb-1 last:border-0">
                            {line}
                        </div>
                    ))
                ) : (
                    <div className="h-full flex flex-col items-center justify-center text-gray-500">
                        {loading ? (
                            <>
                                <Loader2 className="animate-spin mb-4" size={32} />
                                <p className="font-bold">Loading system logs...</p>
                            </>
                        ) : (
                            <>
                                <Terminal className="mb-4 opacity-20" size={48} />
                                <p className="font-bold text-gray-600 italic">No log records found.</p>
                                <button
                                    onClick={fetchLogs}
                                    className="mt-4 px-4 py-2 border-2 border-gray-700 hover:bg-gray-800 hover:text-green-400 transition-all text-xs uppercase tracking-widest font-black"
                                >
                                    Try Refreshing
                                </button>
                            </>
                        )}
                    </div>
                )}
            </div>
            <p className="text-xs text-gray-500 mt-2 font-bold text-right">
                Showing last {logs.length} lines • Auto-scroll enabled
            </p>
        </div>
    );
}
