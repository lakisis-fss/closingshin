import { Card } from "@/components/ui/Card";
import { cn } from "@/lib/utils";
import { BarChart2 } from "lucide-react";


interface StockCardProps {
    code: string;
    name: string;
    market: string;
    price: number;
    change: string;
    score: number;
    scoreLabel?: string;
    tags?: string[];
    compact?: boolean;
}

export function StockCard({
    code,
    name,
    market,
    price,
    change,
    score,
    scoreLabel = "SCORE",
    tags = [],
    compact = false,
}: StockCardProps) {
    const isUp = change.startsWith("+");

    if (compact) {
        return (
            <Card className="hover:translate-x-1 hover:-translate-y-1 hover:shadow-none transition-all cursor-pointer flex items-center justify-between p-3 relative overflow-hidden group border-2 border-ink active:scale-[0.98]">
                {/* Score Indicator (Left side minimal) */}
                <div className={cn(
                    "absolute left-0 top-0 bottom-0 w-2 flex flex-col justify-center items-center text-transparent group-hover:text-white font-black text-[10px]",
                    score >= 90 ? "bg-bauhaus-red" : score >= 80 ? "bg-bauhaus-yellow" : "bg-bauhaus-blue"
                )}>
                </div>

                {/* Left: Name & Code */}
                <div className="flex flex-col pl-4">
                    <div className="flex items-center gap-2 mb-0.5">
                        <span className="text-xs font-black uppercase truncate max-w-[120px]">
                            {name}
                        </span>
                        <a
                            href={`https://finance.naver.com/item/main.naver?code=${code}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            onClick={(e) => e.stopPropagation()}
                            className="p-1 bg-white border border-ink shadow-[1px_1px_0px_0px_rgba(0,0,0,1)] hover:bg-bauhaus-yellow hover:translate-x-[1px] hover:translate-y-[1px] hover:shadow-none transition-all cursor-pointer group flex-shrink-0"
                            title="네이버 차트"
                        >
                            <BarChart2 size={10} className="text-ink" />
                        </a>
                    </div>
                    <div className="flex items-center gap-2">
                        <span className="text-[10px] font-mono text-gray-400">{code}</span>
                    </div>
                </div>

                {/* Right: Price & Score */}
                <div className="flex items-center gap-4 text-right">
                    <div className="flex flex-col">
                        <span className="text-sm font-mono font-bold tracking-tighter">
                            {price?.toLocaleString() ?? "0"}
                        </span>
                        <span className={cn(
                            "text-[10px] font-bold",
                            isUp ? "text-bauhaus-red" : "text-bauhaus-blue"
                        )}>
                            {change}
                        </span>
                    </div>
                    {/* Compact Score Badge */}
                    <div className="flex flex-col items-center justify-center bg-ink text-white w-8 h-8 font-black rounded-sm relative">
                        <span className="text-sm">{score}</span>
                    </div>
                </div>
            </Card>
        );
    }

    return (
        <Card className="hover:translate-x-1 hover:-translate-y-1 hover:shadow-none transition-all cursor-pointer h-full flex flex-col relative overflow-hidden group active:scale-95 active:shadow-inner">
            {/* Geometric Accent based on Score */}
            <div
                className={cn(
                    "absolute top-0 right-0 w-16 h-16 rounded-bl-full transition-transform group-hover:scale-110",
                    score >= 90
                        ? "bg-bauhaus-red"
                        : score >= 80
                            ? "bg-bauhaus-yellow"
                            : "bg-bauhaus-blue"
                )}
            >
                <span className="absolute top-3 right-3 text-white font-black text-lg">
                    {score}
                </span>
            </div>
            {/* Score Label - Bauhaus Style */}
            <div className="absolute top-14 right-0 bg-ink text-white text-[7px] font-black uppercase px-1.5 py-0.5 tracking-wider">
                {scoreLabel}
            </div>

            <div className="mb-4">
                <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-mono text-gray-400">
                        {code}
                    </span>
                    <span className={cn(
                        "text-[10px] font-bold px-1.5 py-0.5 rounded-sm",
                        market === "KOSPI" ? "bg-gray-100 text-gray-600" : "bg-gray-100 text-bauhaus-blue"
                    )}>
                        {market}
                    </span>
                </div>
                <div className="flex items-center gap-2 pr-12">
                    <h3 className="text-2xl font-black uppercase truncate">
                        {name}
                    </h3>
                    <a
                        href={`https://finance.naver.com/item/main.naver?code=${code}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        onClick={(e) => e.stopPropagation()}
                        className="p-1 bg-white border-2 border-ink shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:bg-bauhaus-yellow hover:shadow-none hover:translate-x-[1px] hover:translate-y-[1px] transition-all cursor-pointer group flex-shrink-0"
                        title="네이버 차트 보기"
                    >
                        <BarChart2 size={12} className="text-ink group-hover:text-ink" />
                    </a>
                </div>
            </div>

            <div className="mt-auto">
                <div className="flex justify-between items-end mb-2">
                    <span className="text-3xl font-mono font-bold tracking-tighter">
                        {price?.toLocaleString() ?? "0"}
                    </span>
                    <span
                        className={cn(
                            "font-bold text-lg py-1 px-2 border-2 border-ink bg-white",
                            isUp ? "text-bauhaus-red" : "text-bauhaus-blue"
                        )}
                    >
                        {change}
                    </span>
                </div>

                <div className="flex flex-wrap gap-2 mt-3">
                    {tags.map((tag) => (
                        <span
                            key={tag}
                            className={cn(
                                "text-[10px] font-bold uppercase px-2 py-1",
                                tag === "🚀" ? "bg-transparent text-xl !p-0 ml-1 shadow-none" : "bg-ink text-white"
                            )}
                        >
                            {tag}
                        </span>
                    ))}
                </div>
            </div>
        </Card>
    );
}
