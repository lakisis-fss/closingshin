"use client";

import { useState, useEffect, useMemo } from "react";
import { StockCard } from "@/components/vcp/StockCard";
import { Card } from "@/components/ui/Card";
import { cn } from "@/lib/utils";
import { BentoGrid, BentoItem } from "@/components/dashboard/BentoGrid";
import { VcpControls } from "@/components/dashboard/VcpControls";
import { NewsAnalysis, VcpResult, NewsItem, StockInfo, MarketStatus } from "@/lib/types";
import { FundamentalCard } from "@/components/stock/FundamentalCard";
import { SupplyDemandChart } from "@/components/stock/SupplyDemandChart";
import { VcpSmartGauge } from "@/components/vcp/VcpSmartGauge";
import { ChevronDown, Calendar, ArrowUpDown, Settings } from "lucide-react";
import { ScanManager } from "@/components/common/ScanManager";
import { VcpCalendarPicker } from "@/components/vcp/VcpCalendarPicker";
import { WeightSettingsModal, WeightPreset } from "@/components/vcp/WeightSettingsModal";
import { 
    QuantWeights, 
    calculateIntegratedQuantScore, 
    convertSentimentToScore, 
    calculateAggregatedSentimentScore,
    DEFAULT_WEIGHTS
} from "@/lib/scoreCalculator";

type SortCriteria = 'total' | 'supply' | 'sentiment' | 'fundamental' | 'vcp';

const SORT_OPTIONS: { value: SortCriteria; label: string }[] = [
    { value: 'total', label: 'Total Quant Score' },
    { value: 'supply', label: 'Supply/Demand' },
    { value: 'sentiment', label: 'AI Sentiment' },
    { value: 'fundamental', label: 'Fundamental' },
    { value: 'vcp', label: 'VCP Pattern' },
];

interface VcpDashboardProps {
    candidates: any[];
    vcpResults: VcpResult[];
    newsAnalysis: NewsAnalysis[];
    newsReports: NewsItem[];
    stockInfos: StockInfo[];
    lastScanned: string | null;
    scanDate: string | null;
    initialData?: any;
    availableDates?: string[];
    selectedDate?: string;
    onDateChange?: (date: string) => void;
    onScanComplete?: () => void;
    marketStatus: MarketStatus | null;
}

export function VcpDashboard({
    candidates,
    vcpResults,
    newsAnalysis,
    newsReports,
    stockInfos,
    lastScanned,
    scanDate,
    availableDates = [],
    selectedDate,
    onDateChange,
    onScanComplete,
    marketStatus
}: VcpDashboardProps) {
    const [selectedTicker, setSelectedTicker] = useState<string>("");
    const [timestamp, setTimestamp] = useState<number | null>(null);
    const [showDatePicker, setShowDatePicker] = useState(false);
    const [sortCriteria, setSortCriteria] = useState<SortCriteria>('total');
    const [showSortPicker, setShowSortPicker] = useState(false);

    // Pagination State
    const [visibleCount, setVisibleCount] = useState(15);

    // Reset visible count when underlying list or sort changes
    useEffect(() => {
        setVisibleCount(15);
    }, [candidates, sortCriteria]);

    // Weight Settings State
    const [showWeightSettings, setShowWeightSettings] = useState(false);

    // Modal State
    const [showSupplyModal, setShowSupplyModal] = useState(false);
    const [showChartModal, setShowChartModal] = useState(false);

    // Explicitly use weights from scoreCalculator or local state
    const [weights, setWeights] = useState<QuantWeights>(DEFAULT_WEIGHTS);
    const [weightPreset, setWeightPreset] = useState<WeightPreset>('balanced');

    // Scan Settings State (Lifted from ScanManager)
    const [scanMode, setScanMode] = useState<string>('classic');
    const [customParams, setCustomParams] = useState({
        minContractions: 2,
        maxDepth1st: 0.35,
        minDepthLast: 0.02,
        maxDepthLast: 0.15,
        strictTrend: true
    });

    // Fix hydration mismatch & Load Weights
    useEffect(() => {
        setTimestamp(Date.now());

        // Load saved weights
        const saved = localStorage.getItem('quant_weights_v1');
        if (saved) {
            try {
                const parsed = JSON.parse(saved);
                if (parsed.weights && parsed.preset) {
                    setWeights(parsed.weights);
                    setWeightPreset(parsed.preset);
                }
            } catch (e) {
                console.error("Failed to load weights", e);
            }
        }
    }, []);

    const handleSaveWeights = (newWeights: QuantWeights, newPreset: WeightPreset) => {
        setWeights(newWeights);
        setWeightPreset(newPreset);
        localStorage.setItem('quant_weights_v1', JSON.stringify({ weights: newWeights, preset: newPreset }));
    };

    // Helper: Get score for a candidate based on criteria
    const getScoreForCandidate = (code: string, criteria: SortCriteria): number => {
        const ticker = code;
        const vcp = vcpResults.find(v => String(v.ticker).padStart(6, '0') === ticker);
        const stockInfo = stockInfos.find(s => String(s.ticker).padStart(6, '0') === ticker);

        // Use aggregated score for consistency
        const aggregatedSentiment = calculateAggregatedSentimentScore(newsAnalysis, ticker);

        if (!vcp) return 0;

        // Calculate Scores
        const vcpScore = vcp.vcp_score ?? 50;
        const supplyScore = stockInfo?.supply_score;
        const sentimentScore = aggregatedSentiment;
        const fundamentalScore = stockInfo?.fundamental_score;
        const rawRs = vcp.relative_strength || 0;

        switch (criteria) {
            case 'vcp':
                return vcpScore;
            case 'supply':
                return supplyScore ?? 50;
            case 'sentiment':
                return sentimentScore ?? 50;
            case 'fundamental':
                return fundamentalScore ?? 50;
            case 'total':
            default: {
                // Use shared score calculator with dynamic weights
                const breakdown = calculateIntegratedQuantScore({
                    vcpScore,
                    supplyScore,
                    sentimentScore,
                    fundamentalScore,
                    rawRs,
                }, marketStatus || undefined, vcp.name, weights);
                return breakdown.totalScore;
            }
        }
    };

    // Sorted candidates with dynamic score
    const sortedCandidates = useMemo(() => {
        return [...candidates]
            .map(c => ({
                ...c,
                displayScore: getScoreForCandidate(c.code, sortCriteria)
            }))
            .sort((a, b) => b.displayScore - a.displayScore);
    }, [candidates, sortCriteria, vcpResults, stockInfos, newsAnalysis, weights, marketStatus]); // Added marketStatus

    // Auto-select top ranked candidate when list changes or on initial load
    useEffect(() => {
        if (sortedCandidates.length > 0) {
            const isInList = sortedCandidates.some(c => c.code === selectedTicker);
            if (!selectedTicker || !isInList) {
                setSelectedTicker(sortedCandidates[0].code);
            }
        } else {
            setSelectedTicker("");
        }
    }, [sortedCandidates, selectedTicker]);

    const selectedStock = vcpResults.find(s => String(s.ticker).padStart(6, '0') === selectedTicker);
    // Find the latest analysis for the "Reason" text
    const selectedStockAnalysis = selectedStock ? newsAnalysis.find(n => {
        const sTicker = String(selectedStock.ticker).padStart(6, '0');
        const sName = selectedStock.name.replace(/\s/g, '').toLowerCase();
        
        const nTicker = String(n.ticker || '').padStart(6, '0');
        const targetStockRaw = String(n.target_stock || '').replace(/\s/g, '').toLowerCase();
        
        const tickerMatch = nTicker === sTicker;
        const targetMatch = targetStockRaw && (
            targetStockRaw.includes(sTicker) || 
            targetStockRaw.includes(sName) || 
            sName.includes(targetStockRaw)
        );
        
        return tickerMatch || targetMatch;
    }) : null;

    // Calculate aggregated score for consistency with the list view
    const selectedStockAggregatedScore = selectedStock
        ? calculateAggregatedSentimentScore(newsAnalysis, String(selectedStock.ticker), selectedStock.name)
        : undefined;

    const selectedStockInfo = stockInfos.find(s => String(s.ticker).padStart(6, '0') === selectedTicker);

    // Derived label from aggregated score
    const getSentimentLabel = (score: number) => {
        if (score >= 80) return "STRONG POSITIVE";
        if (score >= 60) return "POSITIVE";
        if (score >= 40) return "NEUTRAL";
        if (score >= 20) return "WEAK";
        return "NEGATIVE";
    };

    const aggregatedScoreValue = selectedStockAggregatedScore ?? 50;
    const sentimentLabel = getSentimentLabel(aggregatedScoreValue);

    // Filter News for Selected Stock
    const selectedStockNews = selectedStock
        ? newsReports.filter(n => {
            const sTicker = String(selectedStock.ticker).padStart(6, '0');
            const sName = selectedStock.name.replace(/\s/g, '').toLowerCase();
            
            const nTicker = String(n.ticker || '').padStart(6, '0');
            const nNameRaw = String(n.name || '').replace(/\s/g, '').toLowerCase();
            
            const tickerMatch = nTicker === sTicker;
            const nameMatch = nNameRaw && (
                nNameRaw.includes(sTicker) || 
                nNameRaw.includes(sName) || 
                sName.includes(nNameRaw)
            );
            
            return tickerMatch || nameMatch;
        })
        : [];

    // Calculate Total Score using shared calculator for consistency
    const calculateTotalScore = (
        vcp: VcpResult | undefined,
        supply: StockInfo | undefined,
        sentiment: NewsAnalysis | undefined
    ) => {
        if (!vcp) return null;

        const vcpScore = vcp.vcp_score ?? 50;
        const supplyScore = supply?.supply_score;
        const sentimentScore = calculateAggregatedSentimentScore(newsAnalysis, String(vcp.ticker), vcp.name);
        const fundamentalScore = supply?.fundamental_score;
        const rawRs = vcp.relative_strength || 0;

        // Use shared calculator with dynamic weights
        const breakdown = calculateIntegratedQuantScore({
            vcpScore,
            supplyScore,
            sentimentScore,
            fundamentalScore,
            rawRs,
        }, marketStatus || undefined, vcp.name, weights);

        const currentSectorWeight = weights.sector || 0.1;
        const sectorRawScore = Math.round(breakdown.sectorContribution / currentSectorWeight);

        return {
            total: breakdown.totalScore,
            breakdown: [
                { label: "VCP Pattern", score: vcpScore, weight: weights.vcp, color: "bg-ink" },
                { label: "Supply/Demand", score: supplyScore ?? 50, weight: weights.supply, color: "bg-bauhaus-blue" },
                { label: "AI Sentiment", score: sentimentScore ?? 50, weight: weights.sentiment, color: "bg-bauhaus-yellow text-ink" },
                { label: "Fundamentals", score: fundamentalScore ?? 50, weight: weights.fundamental, color: "bg-gray-400" },
                { label: "Sector/RS", score: sectorRawScore, weight: weights.sector, color: "bg-bauhaus-red text-white" },
            ]
        };
    };

    const quantResult = calculateTotalScore(selectedStock, selectedStockInfo, selectedStockAnalysis ?? undefined);

    const detectedMode = useMemo(() => {
        // If we have results for the current selected date, use the mode from results
        if (vcpResults && vcpResults.length > 0 && vcpResults[0].vcp_mode) {
            return vcpResults[0].vcp_mode.toUpperCase();
        }
        // Otherwise, show the currently selected scan mode in the UI
        return scanMode.toUpperCase() + (scanMode === 'classic' ? " (정통)" : "");
    }, [vcpResults, scanMode]);

    return (
        <div className="flex flex-col h-full">
            {/* Header with Controls */}
            <div className="mb-6 flex flex-wrap items-end justify-between gap-4 border-b-4 border-ink pb-6">
                <div>
                    <h2 className="text-6xl font-black uppercase tracking-tighter leading-none flex items-center gap-3">
                        <span className="text-bauhaus-yellow drop-shadow-[2px_2px_0_rgba(0,0,0,1)]">●</span>
                        VCP CANDIDATES
                    </h2>
                    <div className="flex flex-wrap items-center gap-3 mt-2">
                        <span className="font-mono font-bold bg-ink text-white px-2 py-0.5 text-sm transform -skew-x-12">
                            {candidates.length} FOUND
                        </span>
                        {/* Scan Mode Indicator Badge */}
                        <span className={cn(
                            "font-mono font-bold px-2 py-0.5 text-[11px] transform -skew-x-12 shadow-[1px_1px_0px_0px_rgba(0,0,0,1)]",
                            detectedMode.includes("AGGRESSIVE") ? "bg-bauhaus-red text-white" :
                                detectedMode.includes("EARLYBIRD") ? "bg-bauhaus-yellow text-ink border border-ink" :
                                    detectedMode.includes("STABLE") ? "bg-bauhaus-blue text-white" :
                                        "bg-gray-100 text-gray-500 border border-ink"
                        )} title="Data generated from this scan mode">
                            {detectedMode}
                        </span>
                        <p className="text-sm font-bold text-gray-500 uppercase tracking-wide">
                            Volatility Contraction Pattern Scan Results
                        </p>
                        <span className="text-gray-300 select-none">|</span>
                        <VcpControls lastScanned={lastScanned} />
                    </div>
                </div>
                <div className="flex flex-col lg:flex-row flex-wrap items-stretch gap-6 w-full">
                    {/* VIEW SETTINGS POD */}
                    <div className="flex flex-col border-4 border-ink bg-white shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] flex-shrink-0">
                        <div className="bg-ink text-white text-[10px] font-black tracking-widest px-3 py-1 uppercase flex items-center justify-between">
                            <span>View Settings</span>
                        </div>
                        <div className="flex flex-wrap items-center gap-3 p-3 bg-gray-50 flex-1 h-full">
                            {/* Weight Settings Button */}
                            <button
                                onClick={() => setShowWeightSettings(true)}
                                className="flex items-center gap-2 px-4 h-12 bg-white border-4 border-ink shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] transition-all font-black uppercase text-sm whitespace-nowrap flex-shrink-0"
                                title="Customize Quant Weights"
                            >
                                <Settings size={16} />
                                <span>WEIGHTS</span>
                            </button>

                            {/* Sort Criteria Dropdown */}
                            <div className="relative flex-shrink-0">
                                <button
                                    onClick={() => {
                                        setShowSortPicker(!showSortPicker);
                                        setShowDatePicker(false);
                                    }}
                                    className="flex items-center gap-2 px-4 h-12 bg-bauhaus-yellow border-4 border-ink font-black uppercase text-sm shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] transition-all whitespace-nowrap"
                                >
                                    <ArrowUpDown size={16} />
                                    <span>{SORT_OPTIONS.find(o => o.value === sortCriteria)?.label || 'SORT BY'}</span>
                                    <ChevronDown size={16} className={cn("transition-transform", showSortPicker && "rotate-180")} />
                                </button>
                                {showSortPicker && (
                                    <div className="absolute left-0 top-full mt-2 z-50 bg-white border-4 border-ink shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] min-w-[200px]">
                                        {SORT_OPTIONS.map((option) => (
                                            <button
                                                key={option.value}
                                                onClick={() => {
                                                    setSortCriteria(option.value);
                                                    setShowSortPicker(false);
                                                }}
                                                className={cn(
                                                    "w-full px-4 py-3 text-left font-bold text-sm hover:bg-bauhaus-yellow transition-colors uppercase border-b-2 border-dashed border-gray-200 last:border-0",
                                                    sortCriteria === option.value ? "bg-ink text-white hover:bg-ink hover:text-bauhaus-yellow" : ""
                                                )}
                                            >
                                                {option.label}
                                            </button>
                                        ))}
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>

                    {/* DATA & SCAN ENGINE POD */}
                    <div className="flex flex-col border-4 border-ink bg-white shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] flex-1 min-w-0">
                        <div className="bg-ink text-bauhaus-yellow text-[10px] font-black tracking-widest px-3 py-1 uppercase flex items-center justify-between">
                            <span>Scan Engine & Data</span>
                        </div>
                        <div className="flex flex-wrap items-center gap-3 p-3 bg-bauhaus-yellow/10 flex-1 h-full">
                            {/* Date Picker (Calendar) */}
                            <div className="relative flex-shrink-0 w-full sm:w-auto flex-1 min-w-[200px]">
                                <button
                                    onClick={() => {
                                        setShowDatePicker(!showDatePicker);
                                        setShowSortPicker(false);
                                    }}
                                    className="flex items-center justify-center w-full gap-2 px-4 h-12 bg-white border-4 border-ink font-black uppercase text-sm shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] transition-all whitespace-nowrap"
                                >
                                    <Calendar size={16} />
                                    <span>{selectedDate ? `${selectedDate.slice(0, 4)}.${selectedDate.slice(4, 6)}.${selectedDate.slice(6, 8)}` : 'SELECT DATE'}</span>
                                    <ChevronDown size={16} className={cn("transition-transform", showDatePicker && "rotate-180")} />
                                </button>
                                {showDatePicker && (
                                    <div className="absolute left-0 top-full mt-2 z-50 min-w-[280px]">
                                        <VcpCalendarPicker
                                            availableDates={availableDates}
                                            selectedDate={selectedDate || ""}
                                            onDateChange={(date: string) => {
                                                onDateChange?.(date);
                                                setShowDatePicker(false);
                                            }}
                                        />
                                    </div>
                                )}
                            </div>

                            <ScanManager
                                onScanComplete={onScanComplete}
                                initialDate={selectedDate}
                                mode={scanMode}
                                onModeChange={setScanMode}
                                customParams={customParams}
                                onCustomParamsChange={setCustomParams}
                            />
                        </div>
                    </div>

                </div>
            </div>

            <WeightSettingsModal
                isOpen={showWeightSettings}
                onClose={() => setShowWeightSettings(false)}
                currentWeights={weights}
                currentPreset={weightPreset}
                onSave={handleSaveWeights}
            />

            <div className="flex flex-1 gap-6 min-h-[600px]">
                {/* Left Column: Stock List */}
                <div className="w-1/3 flex flex-col gap-4">
                    {(() => {
                        const isWeekend = (dateStr: string) => {
                            if (!dateStr || dateStr.length !== 8) return false;
                            const year = parseInt(dateStr.substring(0, 4), 10);
                            const month = parseInt(dateStr.substring(4, 6), 10) - 1;
                            const day = parseInt(dateStr.substring(6, 8), 10);
                            const date = new Date(year, month, day);
                            const dayOfWeek = date.getDay();
                            return dayOfWeek === 0 || dayOfWeek === 6; // 0: Sun, 6: Sat
                        };

                        if (selectedDate && isWeekend(selectedDate)) {
                            return (
                                <div className="p-12 border-4 border-ink bg-gray-50 flex flex-col items-center justify-center text-center gap-6 shadow-hard min-h-[400px]">
                                    <div className="w-20 h-20 border-4 border-ink bg-gray-200 flex items-center justify-center -rotate-3">
                                        <Calendar size={40} className="text-gray-400" />
                                    </div>
                                    <div>
                                        <h3 className="text-2xl font-black uppercase mb-2 text-gray-500">MARKET CLOSED</h3>
                                        <p className="text-sm font-bold text-gray-400 uppercase max-w-[200px] mx-auto">
                                            주말 및 휴장일에는 데이터가 제공되지 않습니다.
                                        </p>
                                    </div>
                                </div>
                            );
                        }

                        if (sortedCandidates.length > 0) {
                            return (
                                <>
                                    {sortedCandidates.slice(0, visibleCount).map((stock) => (
                                        <div
                                            key={stock.code}
                                            onClick={() => setSelectedTicker(stock.code)}
                                            className={cn(
                                                "cursor-pointer transition-all duration-200",
                                                selectedTicker === stock.code ? "ring-4 ring-bauhaus-blue" : "hover:opacity-80"
                                            )}
                                        >
                                            <StockCard
                                                {...stock}
                                                score={stock.displayScore}
                                                scoreLabel={SORT_OPTIONS.find(o => o.value === sortCriteria)?.label || 'Score'}
                                                compact={true}
                                            />
                                        </div>
                                    ))}
                                    {visibleCount < sortedCandidates.length && (
                                        <button
                                            onClick={() => setVisibleCount(prev => prev + 15)}
                                            className="w-full py-4 bg-gray-100 hover:bg-bauhaus-yellow border-4 border-ink text-ink font-black uppercase tracking-widest transition-colors shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px]"
                                        >
                                            + LOAD MORE ({visibleCount} / {sortedCandidates.length})
                                        </button>
                                    )}
                                </>
                            );
                        }

                        return (
                            <div className="p-12 border-4 border-ink bg-gray-50 flex flex-col items-center justify-center text-center gap-6 shadow-hard">
                                <div className="w-20 h-20 border-4 border-ink bg-white flex items-center justify-center rotate-3">
                                    <Calendar size={40} className="text-gray-300" />
                                </div>
                                <div>
                                    <h3 className="text-2xl font-black uppercase mb-2">NO DATA FOR THIS DATE</h3>
                                    <p className="text-sm font-bold text-gray-500 uppercase max-w-[200px] mx-auto">
                                        해당 날짜의 VCP 데이터가 없습니다. 수집을 시작하시겠습니까?
                                    </p>
                                </div>
                                <ScanManager
                                    onScanComplete={onScanComplete}
                                    initialDate={selectedDate}
                                    mode={scanMode}
                                    onModeChange={setScanMode}
                                    customParams={customParams}
                                    onCustomParamsChange={setCustomParams}
                                />
                            </div>
                        );
                    })()}
                </div>

                {/* Right Column: Detail View */}
                <div className="w-2/3">
                    {selectedStock ? (
                        <div className="h-full flex flex-col bg-white border border-ink shadow-hard p-6">
                            {/* Detail Header */}
                            <div className="mb-6 flex items-end gap-4 border-b-2 border-ink pb-4">
                                <h2 className="text-4xl font-black uppercase tracking-tighter">
                                    {selectedStock.name}
                                </h2>
                                <span className="text-xl font-mono text-gray-400 font-bold mb-1">
                                    {selectedTicker}
                                </span>
                                <div className="ml-auto flex items-end gap-4">
                                    <span className="text-3xl font-mono font-bold">
                                        {selectedStock.price?.toLocaleString() ?? "0"}
                                    </span>
                                    <span className="text-lg font-bold bg-bauhaus-yellow px-2 border-2 border-ink">
                                        {selectedStock.contractions_count}T
                                    </span>
                                </div>
                            </div>

                            {/* Bento Layout */}
                            <div className="flex-1 grid grid-cols-2 gap-4 auto-rows-min">

                                {/* Total Rank / Context Card (2x1) */}
                                {quantResult && (
                                    <div className="col-span-2 border-2 border-ink p-4 bg-white shadow-hard relative overflow-hidden mb-2">
                                        <div className="flex items-center justify-between">
                                            <div className="flex flex-col">
                                                <h3 className="text-sm font-black uppercase text-gray-500 mb-1">Total Quant Score</h3>
                                                <div className="flex items-baseline gap-3">
                                                    <span className={cn(
                                                        "text-6xl font-black tracking-tighter leading-none",
                                                        quantResult.total >= 80 ? "text-bauhaus-red" :
                                                            quantResult.total >= 60 ? "text-bauhaus-blue" : "text-gray-400"
                                                    )}>
                                                        {quantResult.total}
                                                    </span>
                                                    <div className="flex flex-col">
                                                        <span className="text-lg font-bold uppercase leading-none">
                                                            {quantResult.total >= 80 ? "STRONG BUY" :
                                                                quantResult.total >= 60 ? "WATCHLIST" : "WEAK"}
                                                        </span>
                                                        <span className="text-xs text-gray-400 font-mono">Top Tier Setup</span>
                                                    </div>
                                                </div>
                                            </div>

                                            {/* Context Breakdown */}
                                            <div className="flex gap-2">
                                                {quantResult.breakdown.map((item, idx) => (
                                                    <div key={idx} className="flex flex-col items-center w-16">
                                                        <div className="relative w-full h-16 bg-gray-100 border border-ink rounded-sm overflow-hidden flex items-end group">
                                                            <div
                                                                className={cn("w-full transition-all duration-500", item.color)}
                                                                style={{ height: `${item.score}%` }}
                                                            />
                                                            <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 bg-white/80 transition-opacity">
                                                                <span className="text-xs font-bold">{item.score}</span>
                                                            </div>
                                                        </div>
                                                        <span className="text-[9px] font-bold uppercase mt-1 text-center leading-tight text-gray-500">
                                                            {item.label}
                                                        </span>
                                                        <span className="text-sm font-bold font-mono text-gray-400 mt-0.5">
                                                            {item.weight * 100}%
                                                        </span>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    </div>
                                )}
                                {/* Smart Gauge Panel (2x1) - VCP Metrics */}
                                <VcpSmartGauge stock={selectedStock} />

                                {/* Supply Trend (Replaced with Button) */}
                                <div className="col-span-2 border-2 border-ink p-4 bg-gray-50 flex items-center justify-between group cursor-pointer hover:bg-bauhaus-yellow transition-colors" onClick={() => setShowSupplyModal(true)}>
                                    <div className="flex items-center gap-4">
                                        <h3 className="text-sm font-black uppercase text-gray-500 group-hover:text-ink">Supply / Demand Trend</h3>
                                        {selectedStockInfo?.supply_score !== undefined && selectedStockInfo.supply_score !== null && (
                                            <div className="flex items-center gap-2">
                                                <span className="text-xs font-bold text-gray-400 group-hover:text-gray-600 uppercase transition-colors">Score</span>
                                                <div className={cn(
                                                    "px-2 py-0.5 text-sm font-black border-2 border-ink shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]",
                                                    selectedStockInfo.supply_score >= 80 ? "bg-bauhaus-red text-white" :
                                                        selectedStockInfo.supply_score >= 50 ? "bg-white text-ink" :
                                                            "bg-gray-200 text-gray-500"
                                                )}>
                                                    {selectedStockInfo.supply_score}
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                    <button className="text-sm font-bold border-2 border-ink px-4 py-2 bg-white flex items-center gap-2 group-hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:-translate-y-[1px]">
                                        VIEW FULL CHART <ArrowUpDown size={14} className="rotate-90" />
                                    </button>
                                </div>

                                {/* AI Analysis (1x1) */}
                                <div className="col-span-1 bg-white text-ink p-4 border border-ink shadow-hard relative overflow-hidden flex flex-col">
                                    <h3 className="text-sm font-black uppercase mb-4 border-b-2 border-ink pb-2">AI Sentiment</h3>
                                    {selectedStockAnalysis || selectedStockAggregatedScore !== undefined ? (
                                        <div className="flex-1 flex flex-col">
                                            <div className="flex items-center gap-3 mb-3">
                                                <div className={cn(
                                                    "px-3 py-1 text-4xl font-black border-2 border-ink shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]",
                                                    aggregatedScoreValue >= 60 ? "bg-bauhaus-red text-white" :
                                                        aggregatedScoreValue >= 20 ? "bg-bauhaus-yellow text-ink" :
                                                            aggregatedScoreValue >= 0 ? "bg-gray-100 text-gray-500" :
                                                                "bg-bauhaus-blue text-white"
                                                )}>
                                                    {aggregatedScoreValue}
                                                </div>
                                                <div className="flex flex-col">
                                                    <span className="text-xs font-bold text-gray-400 uppercase leading-none mb-1">Verdict</span>
                                                    <span className="text-xl font-black uppercase leading-none tracking-tight">
                                                        {sentimentLabel}
                                                    </span>
                                                </div>
                                            </div>
                                            <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar">
                                                <p className="font-bold leading-snug text-lg text-gray-800 italic">
                                                    &quot;{selectedStockAnalysis?.reason || 'No specific analysis available.'}&quot;
                                                </p>
                                            </div>
                                        </div>
                                    ) : (
                                        <div className="flex-1 flex items-center justify-center opacity-50 text-sm text-center border border-dashed border-gray-300">
                                            해당 기간 AI 분석 내용 없음
                                        </div>
                                    )}
                                </div>

                                {/* News List (1x1) */}
                                <div className="col-span-1 border border-ink p-4 flex flex-col bg-canvas max-h-[300px]">
                                    <h3 className="text-sm font-bold uppercase text-gray-500 mb-2">Latest News</h3>
                                    <div className="flex-1 overflow-y-auto pr-1 space-y-2">
                                        {selectedStockNews.length > 0 ? (
                                            selectedStockNews.map((news, i) => (
                                                <a
                                                    key={i}
                                                    href={news.link}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    className="block p-3 border-b border-dashed border-gray-300 last:border-0 hover:bg-gray-50 transition-colors group"
                                                >
                                                    <div className="font-bold text-sm leading-snug text-ink mb-1 group-hover:text-bauhaus-blue transition-colors">
                                                        {news.title.replace(/"/g, '')}
                                                    </div>
                                                    <div className="text-[10px] text-gray-400 font-mono flex justify-between items-center">
                                                        <span>{news.pub_date?.substring(0, 10)}</span>
                                                        {news.score && (
                                                            <span className={cn(
                                                                "flex items-center justify-center min-w-[30px] h-[20px] text-[10px] font-bold border border-ink shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] transition-transform group-hover:translate-x-[-1px] group-hover:translate-y-[-1px] group-hover:shadow-[3px_3px_0px_0px_rgba(0,0,0,1)]",
                                                                news.score >= 0.7 ? "bg-bauhaus-red text-white" : "bg-bauhaus-yellow text-ink"
                                                            )}>
                                                                {news.score}
                                                            </span>
                                                        )}
                                                    </div>
                                                </a>
                                            ))
                                        ) : (
                                            <div className="text-center text-gray-400 text-xs py-8">
                                                해당 기간 뉴스 없음
                                                <br />
                                                <span className="text-[10px] text-red-300">Target: {selectedTicker}</span>
                                            </div>
                                        )}
                                    </div>
                                </div>

                                {/* Fundamentals (2x1) */}
                                <div className="col-span-2 min-h-[220px]">
                                    {selectedStockInfo ? (
                                        <FundamentalCard info={selectedStockInfo} />
                                    ) : (
                                        <div className="h-full flex items-center justify-center border border-dashed border-gray-300 text-gray-400">
                                            No Fundamental Data
                                        </div>
                                    )}
                                </div>

                                {/* Chart (Replaced with Button) */}
                                <div className="col-span-2 border-2 border-ink p-4 bg-bauhaus-blue/10 flex items-center justify-between group cursor-pointer hover:bg-bauhaus-blue transition-colors" onClick={() => setShowChartModal(true)}>
                                    <h3 className="text-sm font-black uppercase text-bauhaus-blue group-hover:text-white">Master Price Chart</h3>
                                    <button className="text-sm font-bold border-2 border-ink px-4 py-2 bg-white flex items-center gap-2 group-hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:-translate-y-[1px]">
                                        VIEW LARGE CHART
                                    </button>
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div className="h-full flex items-center justify-center border border-dashed border-gray-300 text-gray-400">
                            Select a stock to view details
                        </div>
                    )}
                </div>
            </div>

            {/* Modals for Heavy Content */}
            {/* Supply/Demand Modal */}
            {showSupplyModal && (
                <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/50 backdrop-blur-sm p-8" onClick={() => setShowSupplyModal(false)}>
                    <div className="bg-white border-4 border-ink shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] w-full max-w-4xl h-[60vh] flex flex-col" onClick={e => e.stopPropagation()}>
                        <div className="flex justify-between items-center p-4 border-b-4 border-ink bg-bauhaus-yellow">
                            <h3 className="font-black uppercase text-xl">Supply & Demand Analysis</h3>
                            <button onClick={() => setShowSupplyModal(false)} className="font-bold border-2 border-ink px-3 py-1 bg-white hover:bg-ink hover:text-white transition-colors">
                                CLOSE
                            </button>
                        </div>
                        <div className="flex-1 p-6 overflow-hidden">
                            {selectedStockInfo ? (
                                <SupplyDemandChart info={selectedStockInfo} />
                            ) : (
                                <div className="h-full flex items-center justify-center text-gray-400">No Data</div>
                            )}
                        </div>
                    </div>
                </div>
            )}

            {/* Master Chart Modal */}
            {showChartModal && (
                <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/80 backdrop-blur-sm p-12" onClick={() => setShowChartModal(false)}>
                    <div className="bg-white border-4 border-ink shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] w-full h-full flex flex-col" onClick={e => e.stopPropagation()}>
                        <div className="flex justify-between items-center p-4 border-b-4 border-ink bg-bauhaus-blue text-white">
                            <h3 className="font-black uppercase text-xl">{selectedStock?.name} VCP Master Chart</h3>
                            <button onClick={() => setShowChartModal(false)} className="font-bold border-2 border-white px-3 py-1 hover:bg-white hover:text-bauhaus-blue transition-colors">
                                CLOSE
                            </button>
                        </div>
                        <div className="flex-1 p-6 bg-gray-50 flex items-center justify-center">
                            {lastScanned && selectedStock ? (
                                (() => {
                                    const selectedCandidate = candidates.find(c => c.code === selectedTicker);
                                    if (!selectedCandidate) return <div className="text-gray-400">Stock Not Found</div>;
                                    
                                    const currentChartUrl = selectedCandidate.chartUrl;
                                    const market = selectedCandidate.market || "UNKNOWN";
                                    const name = selectedCandidate.name || "Unknown";
                                    const ticker = selectedCandidate.code || selectedTicker;
                                    const fallbackUrl = `/api/charts/${scanDate || "unknown"}/${market}_${name}_${ticker}.png${timestamp ? `?t=${timestamp}` : ""}`;
                                    
                                    return (
                                        /* eslint-disable-next-line @next/next/no-img-element */
                                        <img
                                            src={currentChartUrl || fallbackUrl}
                                            alt="VCP Master Chart"
                                            className="w-full h-full object-contain"
                                            onError={(e) => {
                                                // Fallback if DB image fails (e.g. not migrated yet)
                                                const target = e.target as HTMLImageElement;
                                                if (target.src !== fallbackUrl) {
                                                    target.src = fallbackUrl;
                                                }
                                            }}
                                        />
                                    );
                                })()
                            ) : (
                                <div className="text-gray-400">Chart Not Available</div>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
