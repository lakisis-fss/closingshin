"use client";

import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
} from "recharts";

interface MarketMomentumChartProps {
    data: {
        date: string;
        KOSPI: number;
        KOSDAQ: number;
    }[];
}

export function MarketMomentumChart({ data }: MarketMomentumChartProps) {
    // Normalize data for dual-axis effect (Indexed to 100 at start)
    const baseKOSPI = data[0]?.KOSPI || 1;
    const baseKOSDAQ = data[0]?.KOSDAQ || 1;

    const normalizedData = data.map((d) => ({
        ...d,
        KOSPI_Norm: ((d.KOSPI / baseKOSPI) * 100).toFixed(2),
        KOSDAQ_Norm: ((d.KOSDAQ / baseKOSDAQ) * 100).toFixed(2),
    }));

    return (
        <div className="w-full h-full min-h-[200px]">
            <ResponsiveContainer width="100%" height="100%">
                <LineChart data={normalizedData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" vertical={false} />
                    <XAxis
                        dataKey="date"
                        tick={{ fontSize: 10 }}
                        interval={5}
                        tickFormatter={(val) => (typeof val === 'string' ? val.slice(5) : '')} // Show MM-DD
                    />
                    <YAxis hide domain={['auto', 'auto']} />
                    <Tooltip
                        contentStyle={{
                            backgroundColor: "#FFFFFF",
                            border: "4px solid #121212",
                            borderRadius: "0px",
                            boxShadow: "4px 4px 0px 0px rgba(0,0,0,1)"
                        }}
                        itemStyle={{ fontSize: "12px", fontWeight: "bold" }}
                        formatter={(value: any, name: any) => {
                            const n = String(name);
                            if (n === "KOSPI_Norm") return [value, "KOSPI(%)"];
                            if (n === "KOSDAQ_Norm") return [value, "KOSDAQ(%)"];
                            return [value, n];
                        }}
                        labelStyle={{ fontWeight: "bold", marginBottom: "5px" }}
                    />
                    <Line
                        type="monotone"
                        dataKey="KOSPI_Norm"
                        stroke="#E03C31" // Bauhaus Red
                        strokeWidth={4}
                        dot={false}
                    />
                    <Line
                        type="monotone"
                        dataKey="KOSDAQ_Norm"
                        stroke="#005698" // Bauhaus Blue
                        strokeWidth={4}
                        dot={false}
                    />
                </LineChart>
            </ResponsiveContainer>
            <div className="flex justify-center gap-4 mt-2 text-xs font-bold">
                <div className="flex items-center gap-1">
                    <div className="w-3 h-3 bg-bauhaus-red"></div> KOSPI
                </div>
                <div className="flex items-center gap-1">
                    <div className="w-3 h-3 bg-bauhaus-blue"></div> KOSDAQ
                </div>
            </div>
        </div>
    );
}
