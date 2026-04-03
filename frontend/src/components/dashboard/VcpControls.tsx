"use client";

import { Clock, RefreshCw } from "lucide-react";
import { useRouter } from "next/navigation";
import { formatToKST } from "@/lib/utils";

interface VcpControlsProps {
    lastScanned: string | null;
}

export function VcpControls({ lastScanned }: VcpControlsProps) {
    const router = useRouter();

    return (
        <div className="flex items-center gap-4">
            {/* Timestamp Display - Subtle Text Style */}
            <div className="flex items-center gap-2 text-xs font-mono font-bold text-gray-400 uppercase tracking-widest bg-gray-50/50 px-3 py-1 rounded-sm border border-gray-200">
                <Clock size={12} />
                <span>SYS.LAST: {lastScanned ? formatToKST(lastScanned) : "N/A"}</span>
                <button
                    onClick={() => router.refresh()}
                    className="ml-2 hover:text-ink p-1 transition-colors"
                    title="Refresh Data"
                >
                    <RefreshCw size={12} className="active:rotate-180 transition-transform duration-300" />
                </button>
            </div>
        </div>
    );
}
