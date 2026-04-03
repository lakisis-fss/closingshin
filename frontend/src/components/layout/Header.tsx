'use client';

import Link from "next/link";
import { cn } from "@/lib/utils";
import { Settings } from "lucide-react";

import { useMarketStatus } from "@/hooks/useMarketStatus";

export function Header() {
    // Determine market status using custom hook
    const { isMarketOpen, status } = useMarketStatus();

    const isMarketHours = isMarketOpen; // Maintain backward compatibility for styling logic

    // Status text is directly from the hook
    const statusText = status;
    const statusColor = isMarketHours ? "text-ink" : "text-gray-400";
    const decorationColor = isMarketHours ? "decoration-bauhaus-red" : "decoration-gray-400";

    return (
        <header className="mb-12 border-b-4 border-ink pb-6 flex flex-col md:flex-row justify-between items-end gap-4">
            <div>
                <Link href="/">
                    <h1 className="text-7xl font-black uppercase tracking-tighter hover:opacity-80 transition-opacity bg-ink text-white px-4 py-2 inline-block transform -skew-x-6">
                        Closing<span className="text-bauhaus-yellow">SHIN</span>
                    </h1>
                </Link>
                <nav className="flex items-center gap-6 mt-4 font-bold text-lg">
                    <Link
                        href="/"
                        className="hover:text-bauhaus-red hover:underline decoration-4 underline-offset-4"
                    >
                        DASHBOARD
                    </Link>
                    <Link
                        href="/vcp"
                        className="hover:text-bauhaus-red hover:underline decoration-4 underline-offset-4"
                    >
                        VCP CANDIDATES
                    </Link>
                    <Link
                        href="/portfolio"
                        className="hover:text-bauhaus-red hover:underline decoration-4 underline-offset-4"
                    >
                        PORTFOLIO
                    </Link>
                    <Link
                        href="/admin"
                        className="flex items-center gap-1 hover:text-bauhaus-red hover:underline decoration-4 underline-offset-4 group"
                    >
                        <Settings size={18} className="group-hover:rotate-90 transition-transform duration-500" />
                        ADMIN
                    </Link>
                </nav>
            </div>
            <div className="text-right">
                <div className="flex flex-col items-end">
                    <div className="bg-bauhaus-red text-white text-xs font-black px-3 py-1 mb-1 transform -rotate-6 border-2 border-ink shadow-[3px_3px_0px_0px_rgba(0,0,0,1)]">
                        MARKET STATUS
                    </div>
                    <div className={cn("text-5xl font-black italic underline decoration-8", statusColor, decorationColor)}>
                        {statusText}
                    </div>
                </div>
            </div>
        </header>
    );
}
