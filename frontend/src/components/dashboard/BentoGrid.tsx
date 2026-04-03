import { cn } from "@/lib/utils";

interface BentoGridProps {
    className?: string;
    children: React.ReactNode;
}

export function BentoGrid({ className, children }: BentoGridProps) {
    return (
        <div
            className={cn(
                "grid grid-cols-1 md:grid-cols-3 gap-6 auto-rows-[minmax(180px,auto)]",
                className
            )}
        >
            {children}
        </div>
    );
}

export function BentoItem({
    className,
    children,
    colSpan = 1,
    rowSpan = 1,
}: {
    className?: string;
    children: React.ReactNode;
    colSpan?: number;
    rowSpan?: number;
}) {
    return (
        <div
            className={cn(
                `col-span-1 md:col-span-${colSpan} row-span-${rowSpan}`,
                className
            )}
        >
            {children}
        </div>
    );
}
