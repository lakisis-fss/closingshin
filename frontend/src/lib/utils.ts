import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"
import { HOLIDAYS_2026 } from "./constants"

export function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs))
}

/**
 * 어떤 입력값이든 서울 시간(KST, UTC+9)으로 변환하여 반환합니다.
 */
export function formatToKST(timestamp: string | number | Date | null | undefined): string {
    if (!timestamp) return "-";

    try {
        const date = new Date(timestamp);
        if (isNaN(date.getTime())) return String(timestamp);

        return new Intl.DateTimeFormat('ko-KR', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: false,
            timeZone: 'Asia/Seoul'
        }).format(date).replace(/\. /g, '-').replace('.', '');
    } catch (e) {
        return String(timestamp);
    }
}

/**
 * 현재 시간이 한국 주식 시장 운영 시간(평일 09:00 ~ 15:30)인지 확인합니다.
 */
export function isMarketOpen(): boolean {
    const now = new Date();
    // KST 시간으로 변환
    const kstOffset = 9 * 60 * 60 * 1000;
    const kstTime = new Date(now.getTime() + (now.getTimezoneOffset() * 60000) + kstOffset);

    const day = kstTime.getDay(); // 0: 일, 1: 월, ..., 6: 토
    const hours = kstTime.getHours();
    const minutes = kstTime.getMinutes();

    // 주말(토, 일) 체크
    if (day === 0 || day === 6) return false;

    // 공휴일 체크
    const dateStr = kstTime.toISOString().split('T')[0];
    if (HOLIDAYS_2026.includes(dateStr)) return false;

    // 운영 시간 체크: 09:00 - 15:30
    const currentTimeMinutes = hours * 60 + minutes;
    const openTimeMinutes = 9 * 60;
    const closeTimeMinutes = 15 * 60 + 30;

    return currentTimeMinutes >= openTimeMinutes && currentTimeMinutes <= closeTimeMinutes;
}
