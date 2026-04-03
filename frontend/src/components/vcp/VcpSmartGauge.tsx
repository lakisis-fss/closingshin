"use client";

import { cn } from "@/lib/utils";
import { VcpResult } from "@/lib/types";

interface VcpSmartGaugeProps {
    stock: VcpResult;
}

function CompressionFunnel({ history }: { history: number[] }) {
    const displayHistory = history.length > 6 ? history.slice(-6) : history;
    const validHistory = displayHistory.filter(d => typeof d === 'number' && !isNaN(d));
    const maxDepth = validHistory.length > 0 ? Math.max(...validHistory) : 1;

    return (
        <div className="flex flex-col gap-0 justify-center items-stretch w-full h-full">
            <div className="text-[10px] font-black text-ink uppercase tracking-widest mb-2 border-b-2 border-ink pb-1">
                Compression
            </div>
            {displayHistory.map((depth, i) => {
                const isLast = i === displayHistory.length - 1;
                const widthPct = Math.max((depth / maxDepth) * 100, 15);
                const isTight = depth < 5;
                const isMedium = depth >= 5 && depth < 10;

                return (
                    <div key={i} className="w-full flex items-stretch border-b border-ink/10 last:border-b-0">
                        <div className="w-6 flex items-center justify-center bg-ink text-white text-[9px] font-black border-r border-ink/30 py-1">
                            T{i + 1}
                        </div>
                        <div className="flex-1 flex items-center py-1 px-1 bg-white">
                            <div
                                className={cn(
                                    "h-5 flex items-center justify-end pr-1.5 transition-all duration-300",
                                    isLast && isTight
                                        ? "bg-bauhaus-red border-2 border-ink"
                                        : isLast && isMedium
                                            ? "bg-bauhaus-yellow border-2 border-ink"
                                            : isLast
                                                ? "bg-gray-400 border-2 border-ink"
                                                : "bg-ink/15"
                                )}
                                style={{ width: `${widthPct}%`, minWidth: '32px' }}
                            >
                                <span
                                    className={cn(
                                        "text-[9px] font-black whitespace-nowrap font-mono",
                                        isLast && isTight ? "text-white" :
                                            isLast && isMedium ? "text-ink" :
                                                isLast ? "text-white" : "text-ink/60"
                                    )}
                                >
                                    {depth?.toFixed(1) ?? "0.0"}%
                                </span>
                            </div>
                        </div>
                    </div>
                );
            })}
        </div>
    );
}

function PivotDistanceBadge({ distance, pivotPrice }: { distance: number; pivotPrice: number }) {
    const isBreakout = distance <= 0;
    const isNear = distance > 0 && distance <= 3;
    const isApproaching = distance > 3 && distance <= 10;

    const label = isBreakout ? "BREAKOUT" : isNear ? "NEAR PIVOT" : isApproaching ? "APPROACHING" : "DEVELOPING";
    const colorClass = isBreakout
        ? "bg-bauhaus-blue text-white"
        : isNear
            ? "bg-bauhaus-red text-white"
            : isApproaching
                ? "bg-bauhaus-yellow text-ink"
                : "bg-gray-100 text-gray-500";

    return (
        <div className="flex items-center justify-between gap-2">
            <div className="flex items-center gap-2">
                <span className={cn("px-2 py-1 text-[10px] font-black border-2 border-ink shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]", colorClass)}>
                    {label}
                </span>
                <span className="text-lg font-black font-mono text-ink">
                    {distance > 0 ? `+${distance?.toFixed(1) ?? "0.0"}%` : `${distance?.toFixed(1) ?? "0.0"}%`}
                </span>
            </div>
            {pivotPrice > 0 && (
                <span className="text-[10px] font-mono text-gray-400 font-bold">
                    {pivotPrice.toLocaleString()}
                </span>
            )}
        </div>
    );
}

function VolRatioBar({ ratio, isDryUp }: { ratio: number; isDryUp: boolean }) {
    const cappedRatio = Math.min(ratio, 2.0);
    const fillPct = (cappedRatio / 2.0) * 100;
    const isDryZone = ratio < 0.5;
    const isLow = ratio >= 0.5 && ratio < 0.8;

    return (
        <div className="flex flex-col gap-1">
            <div className="flex justify-between items-center">
                <div className="flex items-center gap-2">
                    <span className="text-[10px] font-black text-ink uppercase tracking-wider">Volume</span>
                    <span className={cn(
                        "text-[9px] font-black uppercase px-1.5 py-0.5 border-2 border-ink shadow-[1px_1px_0px_0px_rgba(0,0,0,1)]",
                        isDryUp ? "bg-bauhaus-red text-white" : "bg-gray-100 text-gray-400"
                    )}>
                        {isDryUp ? "DRY UP" : "NORMAL"}
                    </span>
                </div>
                <span className="text-sm font-black font-mono text-ink">{ratio?.toFixed(2) ?? "0.00"}</span>
            </div>
            <div className="w-full h-4 bg-gray-100 border-2 border-ink relative overflow-hidden">
                <div
                    className={cn(
                        "h-full transition-all duration-500",
                        isDryZone ? "bg-bauhaus-red" : isLow ? "bg-bauhaus-yellow" : "bg-gray-400"
                    )}
                    style={{ width: `${fillPct}%` }}
                />
                <div className="absolute left-[25%] top-0 bottom-0 w-0.5 bg-ink/20" />
                <div className="absolute left-[40%] top-0 bottom-0 w-0.5 bg-ink/30" />
            </div>
            <div className="flex justify-between text-[8px] font-mono text-gray-300 font-bold">
                <span>0</span>
                <span className={isDryZone ? "text-bauhaus-red" : ""}>0.5</span>
                <span className={isLow ? "text-bauhaus-yellow" : ""}>0.8</span>
                <span>2.0</span>
            </div>
        </div>
    );
}

type ActionCondition = {
    label: string;
    met: boolean;
};

function ActionBar({ stock }: { stock: VcpResult }) {
    const conditions: ActionCondition[] = [
        { label: "VDU", met: stock.volume_dry_up },
        { label: "<5%", met: stock.last_depth_pct < 5 },
        { label: "PIVOT", met: stock.pivot_distance_pct <= 3 && stock.pivot_distance_pct >= -2 },
        { label: "3T+", met: stock.contractions_count >= 3 },
    ];

    const metCount = conditions.filter(c => c.met).length;
    const actionLabel = metCount >= 4 ? "GO" : metCount >= 3 ? "WATCH" : "WAIT";
    const barColor = metCount >= 4
        ? "bg-bauhaus-blue"
        : metCount >= 3
            ? "bg-bauhaus-yellow"
            : "bg-gray-200";
    const textColor = metCount >= 4
        ? "text-white"
        : metCount >= 3
            ? "text-ink"
            : "text-gray-500";

    return (
        <div className="border-t-2 border-ink pt-3 mt-auto">
            <div className="flex items-center gap-2">
                <div className={cn(
                    "px-4 py-1.5 font-black text-sm border-2 border-ink shadow-[3px_3px_0px_0px_rgba(0,0,0,1)]",
                    barColor, textColor
                )}>
                    {actionLabel}
                </div>
                <div className="flex gap-1 flex-1">
                    {conditions.map((c, i) => (
                        <div
                            key={i}
                            className={cn(
                                "flex items-center gap-0.5 px-2 py-1 text-[9px] font-black uppercase border-2 transition-colors",
                                c.met
                                    ? "bg-ink text-white border-ink"
                                    : "bg-white text-gray-300 border-gray-200"
                            )}
                        >
                            <span className="text-[10px]">
                                {c.met ? "\u2713" : "\u2717"}
                            </span>
                            {c.label}
                        </div>
                    ))}
                </div>
                <span className="text-[10px] font-black font-mono text-gray-400 bg-gray-100 px-2 py-1 border border-ink/10">
                    {metCount}/4
                </span>
            </div>
        </div>
    );
}

export function VcpSmartGauge({ stock }: VcpSmartGaugeProps) {
    const history = stock.contractions_history ?? [];

    return (
        <div className="col-span-2 border-2 border-ink shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] p-0 flex flex-col bg-white overflow-hidden">
            {/* Header - Heavy Brutalist Bar */}
            <div className="bg-ink text-white px-4 py-2.5 flex justify-between items-center">
                <h3 className="text-base font-black uppercase tracking-wider">
                    VCP Metrics
                </h3>
                <div className="flex items-center gap-2">
                    {stock.jump_score >= 80 && (
                        <div className="text-[10px] px-2 py-1 bg-bauhaus-red text-white border-2 border-white/30 font-black flex items-center gap-1">
                            JUMP {stock.jump_score}
                        </div>
                    )}
                    <div className={cn(
                        "text-xl px-3 py-0.5 border-2 font-black font-mono",
                        (stock.vcp_score || 0) >= 80
                            ? "bg-bauhaus-red text-white border-white/30"
                            : (stock.vcp_score || 0) >= 60
                                ? "bg-bauhaus-yellow text-ink border-ink/30"
                                : "bg-white text-ink border-white/30"
                    )}>
                        {stock.vcp_score || 0}
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="flex flex-1 min-h-0">
                {/* Left: Compression Funnel */}
                <div className="w-2/5 border-r-2 border-ink p-3">
                    {history.length > 0 ? (
                        <CompressionFunnel history={history} />
                    ) : (
                        <div className="h-full flex items-center justify-center text-[10px] text-gray-300 font-black uppercase">
                            No Data
                        </div>
                    )}
                </div>

                {/* Right: Key Metrics Stack */}
                <div className="w-3/5 flex flex-col">
                    {/* Contractions + Last Depth */}
                    <div className="grid grid-cols-2 border-b-2 border-ink">
                        <div className="flex flex-col p-3 border-r-2 border-ink">
                            <span className="text-[9px] font-black text-gray-400 uppercase tracking-wider">Contractions</span>
                            <div className="flex items-baseline gap-1 mt-1">
                                <span className="text-2xl font-black text-ink font-mono">{stock.contractions_count}</span>
                                <span className="text-[9px] font-black text-gray-300">W</span>
                            </div>
                        </div>
                        <div className="flex flex-col p-3">
                            <span className="text-[9px] font-black text-gray-400 uppercase tracking-wider">Last Depth</span>
                            <div className="flex items-baseline gap-0.5 mt-1">
                                <span className={cn(
                                    "text-2xl font-black font-mono",
                                    stock.last_depth_pct < 5 ? "text-bauhaus-red" :
                                        stock.last_depth_pct < 10 ? "text-bauhaus-yellow" : "text-ink"
                                )}>
                                    {stock.last_depth_pct?.toFixed(1) ?? "0.0"}
                                </span>
                                <span className="text-[9px] font-black text-gray-300">%</span>
                            </div>
                        </div>
                    </div>

                    {/* Volume Section */}
                    <div className="p-3 border-b-2 border-ink">
                        <VolRatioBar ratio={stock.vol_ratio} isDryUp={stock.volume_dry_up} />
                    </div>

                    {/* Pivot Distance */}
                    <div className="p-3">
                        <div className="text-[10px] font-black text-ink uppercase tracking-wider mb-1.5 border-b border-ink/10 pb-1">
                            Pivot Distance
                        </div>
                        <PivotDistanceBadge
                            distance={stock.pivot_distance_pct}
                            pivotPrice={stock.pivot_point}
                        />
                    </div>
                </div>
            </div>

            {/* Bottom: Action Bar */}
            <div className="px-4 py-3 bg-gray-50 border-t-2 border-ink">
                <ActionBar stock={stock} />
            </div>
        </div>
    );
}
