"use client";

import { useState, useEffect } from 'react';
import { X, Save, RotateCcw, Settings, Check } from 'lucide-react';
import { cn } from '@/lib/utils';
import { QuantWeights, DEFAULT_WEIGHTS } from '@/lib/scoreCalculator';

// Preset Types
export type WeightPreset = 'balanced' | 'momentum' | 'value' | 'custom';

export const PRESETS: Record<Exclude<WeightPreset, 'custom'>, { titleEn: string; titleKo: string; weights: QuantWeights; desc: string }> = {
    balanced: {
        titleEn: 'BALANCED',
        titleKo: '균형',
        weights: DEFAULT_WEIGHTS,
        desc: '수급과 심리에 집중한 표준 분포'
    },
    momentum: {
        titleEn: 'MOMENTUM MASTER',
        titleKo: '모멘텀',
        weights: { vcp: 0.40, supply: 0.40, sentiment: 0.10, fundamental: 0.05, sector: 0.05 },
        desc: 'VCP 패턴과 수급 집중\n(단기 급등주 포착)'
    },
    value: {
        titleEn: 'VALUE PICKS',
        titleKo: '가치주',
        weights: { vcp: 0.10, supply: 0.10, sentiment: 0.10, fundamental: 0.60, sector: 0.10 },
        desc: '펀더멘털 비중 확대\n(PER, PBR, ROE)'
    }
};

const DISPLAY_LABELS: Record<keyof QuantWeights, { en: string; ko: string }> = {
    vcp: { en: 'VCP PATTERN', ko: '패턴' },
    supply: { en: 'SUPPLY / DEMAND', ko: '수급' },
    sentiment: { en: 'AI SENTIMENT', ko: '심리' },
    fundamental: { en: 'FUNDAMENTALS', ko: '실적' },
    sector: { en: 'SECTOR / RS', ko: '주도주' }
};

interface WeightSettingsModalProps {
    isOpen: boolean;
    onClose: () => void;
    currentWeights: QuantWeights;
    currentPreset: WeightPreset;
    onSave: (weights: QuantWeights, preset: WeightPreset) => void;
}

export function WeightSettingsModal({ isOpen, onClose, currentWeights, currentPreset, onSave }: WeightSettingsModalProps) {
    const [preset, setPreset] = useState<WeightPreset>(currentPreset);
    const [weights, setWeights] = useState<QuantWeights>(currentWeights);
    const [sliderValues, setSliderValues] = useState<Record<keyof QuantWeights, number>>({
        vcp: Math.round(currentWeights.vcp * 100),
        supply: Math.round(currentWeights.supply * 100),
        sentiment: Math.round(currentWeights.sentiment * 100),
        fundamental: Math.round(currentWeights.fundamental * 100),
        sector: Math.round(currentWeights.sector * 100),
    });

    useEffect(() => {
        if (isOpen) {
            setPreset(currentPreset);
            setWeights(currentWeights);
            setSliderValues({
                vcp: Math.round(currentWeights.vcp * 100),
                supply: Math.round(currentWeights.supply * 100),
                sentiment: Math.round(currentWeights.sentiment * 100),
                fundamental: Math.round(currentWeights.fundamental * 100),
                sector: Math.round(currentWeights.sector * 100),
            });
        }
    }, [isOpen, currentPreset, currentWeights]);

    const handlePresetChange = (newPreset: WeightPreset) => {
        setPreset(newPreset);
        if (newPreset !== 'custom') {
            const newWeights = PRESETS[newPreset].weights;
            setWeights(newWeights);
            setSliderValues({
                vcp: Math.round(newWeights.vcp * 100),
                supply: Math.round(newWeights.supply * 100),
                sentiment: Math.round(newWeights.sentiment * 100),
                fundamental: Math.round(newWeights.fundamental * 100),
                sector: Math.round(newWeights.sector * 100),
            });
        }
    };

    const handleSliderChange = (key: keyof QuantWeights, val: number) => {
        setPreset('custom');
        setSliderValues(prev => ({ ...prev, [key]: val }));
    };

    const totalWeight = Object.values(sliderValues).reduce((a, b) => a + b, 0);
    const isValid = totalWeight === 100;

    const handleSave = () => {
        if (!isValid) return;

        const finalWeights: QuantWeights = {
            vcp: sliderValues.vcp / 100,
            supply: sliderValues.supply / 100,
            sentiment: sliderValues.sentiment / 100,
            fundamental: sliderValues.fundamental / 100,
            sector: sliderValues.sector / 100,
        };
        onSave(finalWeights, preset);
        onClose();
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
            <div className="relative w-full max-w-2xl bg-white border-[6px] border-ink shadow-[12px_12px_0px_0px_rgba(0,0,0,1)] flex flex-col max-h-[90vh]">

                {/* Header */}
                <div className="flex items-center justify-between border-b-[6px] border-ink bg-bauhaus-yellow p-6">
                    <h2 className="text-3xl font-black uppercase flex items-center gap-3 tracking-tighter">
                        <Settings className="w-8 h-8" strokeWidth={3} />
                        <div>
                            QUANT WEIGHTS
                            <span className="block text-sm font-bold opacity-100 text-ink/70 tracking-normal mt-1">가중치 설정</span>
                        </div>
                    </h2>
                    <button onClick={onClose} className="p-2 hover:bg-black hover:text-white border-4 border-transparent hover:border-white transition-colors">
                        <X className="w-8 h-8" strokeWidth={3} />
                    </button>
                </div>

                <div className="p-8 overflow-y-auto flex-1 bg-white">

                    {/* Preset Selector */}
                    <div className="mb-10 grid grid-cols-1 md:grid-cols-2 gap-6">
                        {(Object.keys(PRESETS) as Array<keyof typeof PRESETS>).map(key => (
                            <button
                                key={key}
                                onClick={() => handlePresetChange(key)}
                                className={cn(
                                    "relative p-6 border-4 text-left transition-all group overflow-hidden min-h-[140px] flex flex-col justify-between",
                                    preset === key
                                        ? "border-ink bg-ink text-white shadow-[8px_8px_0px_0px_rgba(0,0,0,0.5)] translate-x-[2px] translate-y-[2px]"
                                        : "border-gray-300 hover:border-ink hover:bg-gray-50 text-gray-500 hover:shadow-[8px_8px_0px_0px_rgba(200,200,200,1)] hover:-translate-y-1"
                                )}
                            >
                                <div>
                                    <div className="text-2xl font-black uppercase tracking-tighter leading-none mb-1">
                                        {PRESETS[key].titleEn}
                                    </div>
                                    <div className={cn("text-lg font-bold mb-3", preset === key ? "text-bauhaus-yellow" : "text-gray-400 group-hover:text-ink")}>
                                        {PRESETS[key].titleKo}
                                    </div>
                                </div>
                                <div className={cn("text-sm font-medium leading-snug whitespace-pre-wrap", preset === key ? "text-gray-300" : "text-gray-400 group-hover:text-gray-600")}>
                                    {PRESETS[key].desc}
                                </div>
                                {preset === key && <div className="absolute top-4 right-4 w-4 h-4 bg-bauhaus-yellow rounded-full animate-pulse" />}
                            </button>
                        ))}
                        <button
                            onClick={() => handlePresetChange('custom')}
                            className={cn(
                                "relative p-6 border-4 text-left transition-all group overflow-hidden min-h-[140px] flex flex-col justify-between",
                                preset === 'custom'
                                    ? "border-ink bg-ink text-white shadow-[8px_8px_0px_0px_rgba(0,0,0,0.5)] translate-x-[2px] translate-y-[2px]"
                                    : "border-gray-300 hover:border-ink hover:bg-gray-50 text-gray-500 hover:shadow-[8px_8px_0px_0px_rgba(200,200,200,1)] hover:-translate-y-1"
                            )}
                        >
                            <div>
                                <div className="text-2xl font-black uppercase tracking-tighter leading-none mb-1">
                                    CUSTOM
                                </div>
                                <div className={cn("text-lg font-bold mb-3", preset === 'custom' ? "text-bauhaus-yellow" : "text-gray-400 group-hover:text-ink")}>
                                    사용자 설정
                                </div>
                            </div>
                            <div className={cn("text-sm font-medium leading-snug whitespace-pre-wrap", preset === 'custom' ? "text-gray-300" : "text-gray-400 group-hover:text-gray-600")}>
                                직접 가중치를 조절하여<br />나만의 점수 산출
                            </div>
                            {preset === 'custom' && <div className="absolute top-4 right-4 w-4 h-4 bg-bauhaus-yellow rounded-full animate-pulse" />}
                        </button>
                    </div>

                    {/* Sliders */}
                    <div className="space-y-6">
                        {Object.keys(DEFAULT_WEIGHTS).map((key) => {
                            const k = key as keyof QuantWeights;
                            return (
                                <div key={k} className="flex flex-col gap-2">
                                    <div className="flex justify-between items-end border-b-2 border-gray-100 pb-1">
                                        <div className="flex flex-col">
                                            <span className="text-sm font-black uppercase text-ink">{DISPLAY_LABELS[k].en}</span>
                                            <span className="text-xs font-bold text-gray-400">{DISPLAY_LABELS[k].ko}</span>
                                        </div>
                                        <span className={cn(
                                            "text-2xl font-black font-mono",
                                            sliderValues[k] > 0 ? "text-ink" : "text-gray-300"
                                        )}>
                                            {sliderValues[k]}%
                                        </span>
                                    </div>
                                    <input
                                        type="range"
                                        min="0"
                                        max="100"
                                        step="5"
                                        value={sliderValues[k]}
                                        onChange={(e) => handleSliderChange(k, parseInt(e.target.value))}
                                        className={cn(
                                            "w-full h-6 bg-gray-200 rounded-none appearance-none cursor-pointer border-2 border-transparent focus:outline-none focus:border-ink accent-ink hover:bg-gray-300 transition-colors",
                                            preset !== 'custom' && "opacity-50 pointer-events-none grayscale"
                                        )}
                                    />
                                </div>
                            );
                        })}
                    </div>

                    {/* Total Indicator */}
                    <div className={cn(
                        "mt-10 p-4 border-4 font-mono font-black text-center transition-colors flex justify-between items-center text-xl shadow-[4px_4px_0px_0px_rgba(0,0,0,0.1)]",
                        isValid
                            ? "border-green-600 bg-green-50 text-green-700"
                            : "border-red-500 bg-red-50 text-red-700 animate-pulse"
                    )}>
                        <span className="uppercase tracking-tight">TOTAL WEIGHT <span className="text-sm font-bold opacity-70 ml-2">(합계)</span></span>
                        <span className="text-3xl">{totalWeight}%</span>
                    </div>
                </div>

                {/* Footer */}
                <div className="border-t-[6px] border-ink p-6 bg-gray-100 flex justify-end gap-4">
                    <button
                        onClick={() => handlePresetChange('balanced')}
                        className="px-6 py-3 border-4 border-gray-400 text-gray-500 font-black hover:bg-white hover:text-ink hover:border-ink transition-all flex items-center gap-2 uppercase tracking-wide"
                    >
                        <RotateCcw size={20} strokeWidth={3} />
                        <div>
                            RESET <span className="text-xs font-bold block leading-none opacity-60">초기화</span>
                        </div>
                    </button>
                    <button
                        onClick={handleSave}
                        disabled={!isValid}
                        className={cn(
                            "px-8 py-3 border-4 text-white font-black shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] transition-all flex items-center gap-3 uppercase tracking-wide",
                            isValid
                                ? "bg-bauhaus-blue border-ink hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:bg-blue-600"
                                : "bg-gray-400 border-gray-400 cursor-not-allowed shadow-none opacity-50"
                        )}
                    >
                        <Save size={20} strokeWidth={3} />
                        <div className="text-left">
                            SAVE SETTINGS
                            <span className="text-xs font-bold block leading-none opacity-80 mt-0.5">설정 저장</span>
                        </div>
                    </button>
                </div>

            </div>
        </div>
    );
}

