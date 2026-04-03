import { cn } from "@/lib/utils";
import { ButtonHTMLAttributes, forwardRef } from "react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: "primary" | "secondary" | "outline";
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
    ({ className, variant = "primary", ...props }, ref) => {
        const variants = {
            primary: "bg-bauhaus-blue text-white hover:bg-opacity-90 shadow-hard",
            secondary: "bg-bauhaus-yellow text-ink hover:bg-opacity-90 shadow-hard",
            outline: "border-2 border-ink text-ink hover:bg-gray-100",
        };

        return (
            <button
                ref={ref}
                className={cn(
                    "px-6 py-3 font-bold transition-all active:translate-x-[2px] active:translate-y-[2px] active:shadow-none",
                    variants[variant],
                    className
                )}
                {...props}
            />
        );
    }
);
Button.displayName = "Button";

export { Button };
