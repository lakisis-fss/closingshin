"use client";

import { useState, useEffect } from "react";
import { Card } from "@/components/ui/Card";
import { StockInfo } from "@/lib/types";
import { cn } from "@/lib/utils";
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, CartesianGrid, ReferenceLine } from "recharts";

export function SupplyDemandChart({ info }: { info: StockInfo }) {
    const [isMounted, setIsMounted] = useState(false);

    useEffect(() => {
        setIsMounted(true);
    }, []);

    // SSR Guard: Recharts requires client-side only rendering
    if (!isMounted) return (
        <Card className="h-full border-ink shadow-hard p-4 flex flex-col bg-white">
            <h3 className="text-lg font-black uppercase mb-4 border-b-2 border-ink pb-2">Supply / Demand Trend (Net Buy)</h3>
            <div className="flex-1 min-h-[300px] flex items-center justify-center">
                <span className="animate-pulse text-gray-400 font-mono">Loading Chart...</span>
            </div>
        </Card>
    );

    if (!info) return (
        <Card className="h-full border-ink shadow-hard p-4 flex flex-col bg-white">
            <h3 className="text-lg font-black uppercase mb-4 border-b-2 border-ink pb-2">Supply / Demand Trend (Net Buy)</h3>
            <div className="flex-1 min-h-[300px] flex items-center justify-center border-dashed border-gray-300">
                <span className="text-gray-400 font-mono">No Data</span>
            </div>
        </Card>
    );

    const periods = [5, 15, 30, 50, 100];
    const data = periods.map(p => ({
        period: `${p}D`,
        Institution: info[`기관_${p}일` as keyof StockInfo] as number,
        Foreigner: info[`외인_${p}일` as keyof StockInfo] as number,
        Individual: info[`개인_${p}일` as keyof StockInfo] as number,
    }));

    const supplyScore = info.supply_score !== undefined ? info.supply_score : null;

    return (
        <Card className="h-full border-ink shadow-hard p-4 flex flex-col bg-white">
            <div className="flex items-center justify-between mb-4 border-b-2 border-ink pb-2">
                <h3 className="text-lg font-black uppercase">Supply / Demand</h3>
                {supplyScore !== null && (
                    <div className="flex items-center gap-2">
                        <span className="text-xs font-bold text-gray-400 uppercase">Score</span>
                        <div className={cn(
                            "px-2 py-0.5 text-lg font-black border-2 border-ink shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]",
                            supplyScore >= 80 ? "bg-bauhaus-red text-white" :
                                supplyScore >= 50 ? "bg-bauhaus-yellow text-ink" :
                                    "bg-gray-100 text-gray-500"
                        )}>
                            {supplyScore}
                        </div>
                    </div>
                )}
            </div>
            <div className="flex-1 min-h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E7EB" />
                        <XAxis
                            dataKey="period"
                            tick={{ fill: '#1F2937', fontSize: 12, fontWeight: 'bold' }}
                            axisLine={{ stroke: '#1F2937', strokeWidth: 2 }}
                        />
                        <YAxis
                            tick={{ fill: '#6B7280', fontSize: 10, fontFamily: 'monospace' }}
                            axisLine={{ stroke: '#E5E7EB' }}
                        />
                        <Tooltip
                            contentStyle={{
                                backgroundColor: '#FFFFF0',
                                border: '2px solid #1F2937',
                                boxShadow: '4px 4px 0px 0px #000000',
                                borderRadius: '0px'
                            }}
                            cursor={{ fill: '#F3F4F6' }}
                        />
                        <Legend wrapperStyle={{ paddingTop: '10px', fontSize: '12px', fontWeight: 'bold' }} />
                        <ReferenceLine y={0} stroke="#000" strokeWidth={1} />

                        {/* Institution: Bauhaus Blue */}
                        <Bar dataKey="Institution" fill="#195395" name="기관 (Institution)" />

                        {/* Foreigner: Bauhaus Red */}
                        <Bar dataKey="Foreigner" fill="#D24040" name="외인 (Foreigner)" />

                        {/* Individual: Bauhaus Yellow (Darkened for visibility) OR Gray */}
                        <Bar dataKey="Individual" fill="#EBB600" name="개인 (Individual)" />
                    </BarChart>
                </ResponsiveContainer>
            </div>
            <div className="mt-2 text-[10px] text-center text-gray-400 font-mono">
                * Unit: Million KRW (Cumulative Net Purchase)
            </div>
        </Card>
    );
}
