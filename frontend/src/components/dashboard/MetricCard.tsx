import { Card } from "@/components/ui/Card";
import { cn } from "@/lib/utils";

interface MetricCardProps {
    title: React.ReactNode;
    value: string;
    trend?: "up" | "down" | "neutral";
    change?: string;
    className?: string;
}

export function MetricCard({
    title,
    value,
    trend,
    change,
    className,
}: MetricCardProps) {
    const trendColor =
        trend === "up"
            ? "text-bauhaus-red"
            : trend === "down"
                ? "text-bauhaus-blue"
                : "text-bauhaus-yellow";

    return (
        <Card className={cn("flex flex-col justify-between h-full", className)}>
            <h3 className="text-sm font-black uppercase tracking-widest text-ink mb-2 border-b-2 border-ink pb-1 inline-block">
                {title}
            </h3>
            <div className="flex items-end justify-between">
                <span className="text-4xl font-mono font-bold tracking-tighter">
                    {value}
                </span>
                {change && (
                    <span className={cn("font-black text-xl mb-1 flex items-center gap-1", trendColor)}>
                        <span className="text-2xl">{trend === "up" ? "▲" : trend === "down" ? "▼" : "●"}</span>
                        {change}
                    </span>
                )}
            </div>
        </Card>
    );
}
