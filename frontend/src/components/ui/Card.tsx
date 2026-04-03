import { cn } from "@/lib/utils";

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
    children: React.ReactNode;
}

export function Card({ className, children, ...props }: CardProps) {
    return (
        <div
            className={cn(
                "bg-white border-[4px] border-ink p-6 shadow-[6px_6px_0px_0px_rgba(0,0,0,1)]",
                className
            )}
            {...props}
        >
            {children}
        </div>
    );
}
