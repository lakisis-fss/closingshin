"use client";

import { Card } from "@/components/ui/Card";
import { StockInfo } from "@/lib/types";

export function FundamentalCard({ info }: { info: StockInfo }) {
    if (!info) return null;

    const formatValue = (val: number | undefined | null, precision: number = 2, isLocale: boolean = false) => {
        if (val === undefined || val === null || isNaN(val)) return "N/A";
        return isLocale ? val.toLocaleString() : val.toFixed(precision);
    };

    const metrics = [
        { label: "PER", value: formatValue(info.PER), unit: "x" },
        { label: "EPS", value: formatValue(info.EPS, 0, true), unit: "₩" },
        { label: "PBR", value: formatValue(info.PBR), unit: "x" },
        { label: "BPS", value: formatValue(info.BPS, 0, true), unit: "₩" },
        { label: "DIV", value: formatValue(info.DIV), unit: "%" },
        { label: "DPS", value: formatValue(info.DPS, 0, true), unit: "₩" },
    ];

    const fundamentalScore = info.fundamental_score !== undefined ? info.fundamental_score : null;

    return (
        <Card className="h-full border-ink shadow-hard p-4 flex flex-col bg-white">
            <div className="flex items-center justify-between mb-4 border-b-2 border-ink pb-2">
                <h3 className="text-lg font-black uppercase">Fundamentals</h3>
                {fundamentalScore !== null && (
                    <div className="flex items-center gap-2">
                        <span className="text-xs font-bold text-gray-400 uppercase">Score</span>
                        <div className={`px-2 py-0.5 text-lg font-black border-2 border-ink shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] ${fundamentalScore >= 80 ? "bg-bauhaus-red text-white" :
                            fundamentalScore >= 50 ? "bg-bauhaus-yellow text-ink" :
                                "bg-gray-100 text-gray-500"
                            }`}>
                            {fundamentalScore}
                        </div>
                    </div>
                )}
            </div>
            <div className="grid grid-cols-2 gap-4 flex-1">
                {metrics.map((m, i) => (
                    <div key={i} className="flex flex-col justify-center border border-gray-200 p-2 hover:bg-gray-50 transition-colors">
                        <span className="text-xs font-bold text-gray-500 uppercase">{m.label}</span>
                        <div className="flex items-baseline gap-1">
                            <span className="text-2xl font-mono font-bold text-ink">{m.value}</span>
                            <span className="text-xs font-mono text-gray-400">{m.unit}</span>
                        </div>
                    </div>
                ))}
            </div>
        </Card>
    );
}
