"use client";

import { useState } from 'react';
import { ChevronLeft, ChevronRight, Calendar as CalendarIcon } from 'lucide-react';
import { cn } from '@/lib/utils';

interface VcpCalendarPickerProps {
    availableDates: string[]; // YYYYMMDD format
    selectedDate: string;     // YYYYMMDD format
    onDateChange: (date: string) => void;
}

export function VcpCalendarPicker({ availableDates, selectedDate, onDateChange }: VcpCalendarPickerProps) {
    const today = new Date();
    const [currentMonth, setCurrentMonth] = useState(new Date(
        parseInt(selectedDate.slice(0, 4)),
        parseInt(selectedDate.slice(4, 6)) - 1
    ));

    const daysInMonth = (year: number, month: number) => new Date(year, month + 1, 0).getDate();
    const firstDayOfMonth = (year: number, month: number) => new Date(year, month, 1).getDay();

    const year = currentMonth.getFullYear();
    const month = currentMonth.getMonth();
    const totalDays = daysInMonth(year, month);
    const startDay = firstDayOfMonth(year, month);

    const prevMonth = () => setCurrentMonth(new Date(year, month - 1));
    const nextMonth = () => setCurrentMonth(new Date(year, month + 1));

    const formatDate = (d: number) => {
        const mm = String(month + 1).padStart(2, '0');
        const dd = String(d).padStart(2, '0');
        return `${year}${mm}${dd}`;
    };

    const isToday = (dateStr: string) => {
        const todayStr = `${today.getFullYear()}${String(today.getMonth() + 1).padStart(2, '0')}${String(today.getDate()).padStart(2, '0')}`;
        return dateStr === todayStr;
    };

    const hasData = (dateStr: string) => {
        // 주말(토, 일)은 데이터가 있어도 없는 것으로 간주 (휴장일)
        const year = parseInt(dateStr.slice(0, 4));
        const month = parseInt(dateStr.slice(4, 6)) - 1;
        const day = parseInt(dateStr.slice(6, 8));
        const date = new Date(year, month, day);
        const dayOfWeek = date.getDay();
        if (dayOfWeek === 0 || dayOfWeek === 6) return false;

        return availableDates.includes(dateStr);
    };

    return (
        <div className="w-full bg-white border-4 border-ink font-mono text-xs shadow-hard">
            {/* Header */}
            <div className="flex items-center justify-between border-b-4 border-ink p-2 bg-gray-50">
                <button onClick={prevMonth} className="p-1 hover:bg-bauhaus-yellow border-2 border-transparent hover:border-ink transition-all">
                    <ChevronLeft size={16} />
                </button>
                <div className="font-black uppercase tracking-tighter text-sm flex items-center gap-2">
                    <CalendarIcon size={14} />
                    {year}.{String(month + 1).padStart(2, '0')}
                </div>
                <button onClick={nextMonth} className="p-1 hover:bg-bauhaus-yellow border-2 border-transparent hover:border-ink transition-all">
                    <ChevronRight size={16} />
                </button>
            </div>

            {/* Weekdays */}
            <div className="grid grid-cols-7 border-b-2 border-ink bg-white">
                {['SU', 'MO', 'TU', 'WE', 'TH', 'FR', 'SA'].map((day, i) => (
                    <div key={day} className={cn(
                        "p-2 text-center font-black border-r last:border-0 border-ink/10",
                        i === 0 ? "text-bauhaus-red" : i === 6 ? "text-bauhaus-blue" : "text-gray-400"
                    )}>
                        {day}
                    </div>
                ))}
            </div>

            {/* Days Grid */}
            <div className="grid grid-cols-7 border-ink/10">
                {Array.from({ length: startDay }).map((_, i) => (
                    <div key={`empty-${i}`} className="p-2 aspect-square border-r border-b border-ink/10 bg-gray-50/50" />
                ))}
                {Array.from({ length: totalDays }).map((_, i) => {
                    const day = i + 1;
                    const dateStr = formatDate(day);
                    const isSelected = dateStr === selectedDate;
                    const dayHasData = hasData(dateStr);
                    const isNow = isToday(dateStr);

                    return (
                        <button
                            key={day}
                            onClick={() => onDateChange(dateStr)}
                            className={cn(
                                "p-2 aspect-square border-r border-b border-ink/10 flex flex-col items-center justify-center relative transition-all group",
                                isSelected ? "bg-ink text-white font-black z-10" : "hover:bg-bauhaus-yellow/30",
                                !dayHasData && !isSelected && "text-gray-300"
                            )}
                        >
                            <span className="relative z-10">{day}</span>

                            {/* Bauhaus Data Indicator */}
                            {dayHasData && !isSelected && (
                                <div className="absolute inset-0 bg-bauhaus-blue/10 pointer-events-none" />
                            )}

                            {/* Today Indicator */}
                            {isNow && !isSelected && (
                                <div className="absolute top-1 right-1 w-1.5 h-1.5 bg-bauhaus-yellow border border-ink rounded-full" />
                            )}

                            {/* Has Data Mark */}
                            {dayHasData && !isSelected && (
                                <div className="mt-1 w-full h-1 bg-bauhaus-blue" style={{ height: '2px' }} />
                            )}
                        </button>
                    );
                })}
            </div>

            {/* Legend */}
            <div className="p-3 border-t-2 border-ink flex gap-4 bg-gray-50 font-bold text-[10px] uppercase">
                <div className="flex items-center gap-1">
                    <div className="w-2 h-2 bg-bauhaus-blue" />
                    <span>Scanned</span>
                </div>
                <div className="flex items-center gap-1">
                    <div className="w-2 h-2 bg-bauhaus-yellow" />
                    <span>Today</span>
                </div>
                <div className="flex items-center gap-1">
                    <div className="w-2 h-2 bg-ink" />
                    <span>Selected</span>
                </div>
            </div>
        </div>
    );
}
