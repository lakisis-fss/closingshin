'use client';

import { useState, useEffect, useMemo } from 'react';
import { X, ChevronDown, ChevronUp } from 'lucide-react';
import { PortfolioItem, VcpResult, StockInfo, NewsAnalysis, ExitConditions } from '@/lib/types';
import { usePortfolioStore } from '@/lib/portfolioStore';
import { calculateIntegratedQuantScore, convertSentimentToScore, formatScoreBreakdown, calculateAggregatedSentimentScore } from '@/lib/scoreCalculator';
import { useQuantStore } from '@/lib/quantStore';

interface AddStockModalProps {
    isOpen: boolean;
    onClose: () => void;
    existingItem?: PortfolioItem | null;
    vcpData?: VcpResult[];
    stockInfoData?: StockInfo[];
    newsAnalysis?: NewsAnalysis[];
    availableVcpDates?: string[];
    onFetchVcpByDate?: (date: string) => Promise<VcpResult[]>;
    onFetchNewsAnalysisByDate?: (date: string) => Promise<NewsAnalysis[]>;
    onFetchStockInfoByDate?: (date: string) => Promise<StockInfo[]>;
    onFetchMarketStatusByDate?: (date: string) => Promise<any>;
}

export function AddStockModal({
    isOpen,
    onClose,
    existingItem,
    vcpData = [],
    stockInfoData = [],
    newsAnalysis = [],
    availableVcpDates = [],
    onFetchVcpByDate,
    onFetchNewsAnalysisByDate,
    onFetchStockInfoByDate,
    onFetchMarketStatusByDate
}: AddStockModalProps) {
    const { addStock, updateStock } = usePortfolioStore();
    const { weights } = useQuantStore();

    const [ticker, setTicker] = useState('');
    const [name, setName] = useState('');
    const [market, setMarket] = useState<'KOSPI' | 'KOSDAQ'>('KOSPI');
    const [buyDate, setBuyDate] = useState('');
    const [buyPrice, setBuyPrice] = useState('');
    const [quantity, setQuantity] = useState('');
    const [memo, setMemo] = useState('');
    const [exitPlan, setExitPlan] = useState('');
    const [vcpMode, setVcpMode] = useState<string | undefined>(undefined);

    // Exit Conditions state
    const [stopLossPercent, setStopLossPercent] = useState('');
    const [takeProfitPercent, setTakeProfitPercent] = useState('');
    const [trailingStopPercent, setTrailingStopPercent] = useState('');
    const [timeCutDays, setTimeCutDays] = useState('');
    const [timeCutHours, setTimeCutHours] = useState('');
    const [timeCutMinutes, setTimeCutMinutes] = useState('');
    const [alertEnabled, setAlertEnabled] = useState(true);

    const [showVcpPicker, setShowVcpPicker] = useState(false);
    const [selectedVcpDate, setSelectedVcpDate] = useState('');
    const [dateVcpData, setDateVcpData] = useState<VcpResult[]>([]);
    const [dateNewsAnalysisData, setDateNewsAnalysisData] = useState<NewsAnalysis[]>([]);
    const [dateStockInfoData, setDateStockInfoData] = useState<StockInfo[]>([]);
    const [dateMarketStatus, setDateMarketStatus] = useState<any>(null);
    const [loadingVcp, setLoadingVcp] = useState(false);

    const [calculatedScores, setCalculatedScores] = useState<PortfolioItem['initialScores']>();

    const [simulationEnabled, setSimulationEnabled] = useState(false);
    const [isSimulating, setIsSimulating] = useState(false);
    const [lastAutoFetchedPrice, setLastAutoFetchedPrice] = useState<string | null>(null);

    useEffect(() => {
        if (existingItem) {
            setTicker(existingItem.ticker);
            setName(existingItem.name);
            setMarket(existingItem.market);
            setBuyDate(existingItem.buyDate);
            setBuyPrice(String(existingItem.buyPrice));
            setQuantity(String(existingItem.quantity));
            setMemo(existingItem.memo);
            setExitPlan(existingItem.exitPlan);
            setVcpMode(existingItem.vcp_mode);
            setCalculatedScores(existingItem.initialScores);
            setSimulationEnabled(existingItem.simulation?.enabled ?? false);

            const ec = existingItem.exitConditions;
            if (ec) {
                setStopLossPercent(ec.stopLossPercent ? String(Math.abs(ec.stopLossPercent)) : '');
                setTakeProfitPercent(ec.takeProfitPercent ? String(ec.takeProfitPercent) : '');
                setTrailingStopPercent(ec.trailingStopPercent ? String(Math.abs(ec.trailingStopPercent)) : '');
                setTimeCutDays(ec.timeCutDays ? String(ec.timeCutDays) : '');
                setTimeCutHours(ec.timeCutHours ? String(ec.timeCutHours) : '');
                setTimeCutMinutes(ec.timeCutMinutes ? String(ec.timeCutMinutes) : '');
                setAlertEnabled(ec.alertEnabled ?? true);
            }
        } else {
            resetForm();
            // Default select the latest available VCP date if present
            if (availableVcpDates.length > 0) {
                setSelectedVcpDate(availableVcpDates[0]);
            }
        }
    }, [existingItem, isOpen, availableVcpDates]);

    const resetForm = () => {
        setTicker('');
        setName('');
        setMarket('KOSPI');
        setBuyDate('');
        setBuyPrice('');
        setQuantity('');
        setMemo('');
        setExitPlan('');
        setVcpMode(undefined);
        setCalculatedScores(undefined);
        setSimulationEnabled(false);
        // Reset exit conditions
        setStopLossPercent('');
        setTakeProfitPercent('');
        setTrailingStopPercent('');
        setTimeCutDays('');
        setTimeCutHours('');
        setTimeCutMinutes('');
        setAlertEnabled(true);
    };

    useEffect(() => {
        if (!selectedVcpDate) {
            setDateVcpData([]);
            setDateNewsAnalysisData([]);
            setDateStockInfoData([]);
            return;
        }

        const fetchData = async () => {
            setLoadingVcp(true);
            try {
                const [vcp, news, info, market] = await Promise.all([
                    onFetchVcpByDate ? onFetchVcpByDate(selectedVcpDate) : Promise.resolve([]),
                    onFetchNewsAnalysisByDate ? onFetchNewsAnalysisByDate(selectedVcpDate) : Promise.resolve([]),
                    onFetchStockInfoByDate ? onFetchStockInfoByDate(selectedVcpDate) : Promise.resolve([]),
                    onFetchMarketStatusByDate ? onFetchMarketStatusByDate(selectedVcpDate) : Promise.resolve(null),
                ]);
                setDateVcpData(vcp);
                setDateNewsAnalysisData(news);
                setDateStockInfoData(info);
                setDateMarketStatus(market);
            } catch (error) {
                console.error("Failed to fetch VCP data for date", selectedVcpDate, error);
            } finally {
                setLoadingVcp(false);
            }
        };

        fetchData();
    }, [selectedVcpDate, onFetchVcpByDate, onFetchNewsAnalysisByDate, onFetchStockInfoByDate]);

    // Update selectedVcpDate when buyDate changes (if valid format)
    useEffect(() => {
        if (buyDate && /^\d{4}-\d{2}-\d{2}$/.test(buyDate)) {
            const dateStr = buyDate.replace(/-/g, '');
            if (dateStr !== selectedVcpDate) {
                setSelectedVcpDate(dateStr);
            }
        }
    }, [buyDate, selectedVcpDate]);

    // Auto-fetch Buy Price when ticker or buyDate changes
    useEffect(() => {
        if (!ticker || ticker.length !== 6 || !buyDate) return;

        const dateStr = buyDate.replace(/-/g, '');
        const todayStr = new Date().toISOString().split('T')[0].replace(/-/g, '');

        const fetchPrice = async () => {
            try {
                // First, check if we already have it in dateStockInfoData (fetched via selectedVcpDate)
                const storedInfo = dateStockInfoData.find(s => String(s.ticker).padStart(6, '0') === ticker);
                if (storedInfo && storedInfo.close) {
                    const price = String(storedInfo.close);
                    if (!buyPrice || buyPrice === lastAutoFetchedPrice) {
                        setBuyPrice(price);
                        setLastAutoFetchedPrice(price);
                    }
                    return;
                }

                // If not found in stored data or it's today, fetch from API
                const response = await fetch(`/api/stock-price/${ticker}?date=${dateStr}`);
                if (response.ok) {
                    const data = await response.json();
                    if (data.price) {
                        const price = String(data.price);
                        // Only auto-update if buyPrice is empty or matches previous auto-fetch (user hasn't manually overridden yet)
                        if (!buyPrice || buyPrice === lastAutoFetchedPrice) {
                            setBuyPrice(price);
                            setLastAutoFetchedPrice(price);
                        }
                    }
                }
            } catch (e) {
                console.error("Failed to auto-fetch buy price", e);
            }
        };

        const timer = setTimeout(fetchPrice, 500); // Debounce
        return () => clearTimeout(timer);
    }, [ticker, buyDate, dateStockInfoData, lastAutoFetchedPrice]);

    const formatDateLabel = (dateStr: string) => {
        if (dateStr.length !== 8) return dateStr;
        return `${dateStr.slice(0, 4)}-${dateStr.slice(4, 6)}-${dateStr.slice(6, 8)}`;
    };

    const displayVcpData = useMemo(() => {
        // If a date is selected, strictly use that date's data (even if empty) to avoid showing default list
        const data = selectedVcpDate ? dateVcpData : vcpData;

        const enrichedData = data.map((vcp) => {
            let vcpScore = vcp.vcp_score;

            if (vcpScore === undefined || vcpScore === null) {
                let estimatedScore = 40;
                if (vcp.contractions_count >= 4) estimatedScore += 20;
                else if (vcp.contractions_count >= 3) estimatedScore += 10;
                if (vcp.volume_dry_up) estimatedScore += 15;
                if (vcp.last_depth_pct !== undefined && vcp.last_depth_pct < 10) estimatedScore += 10;
                if (vcp.last_depth_pct !== undefined && vcp.last_depth_pct < 5) estimatedScore += 5;
                vcpScore = Math.min(estimatedScore, 100);
            }

            const tickerPadded = String(vcp.ticker).padStart(6, '0');

            // Determine which stock info list to use
            // If a date is selected, strictly use that date's stock info
            const sourceStockInfo = selectedVcpDate ? dateStockInfoData : stockInfoData;

            const stockInfo = sourceStockInfo.find(
                (s) => String(s.ticker).padStart(6, '0') === tickerPadded
            );

            const supplyScore = stockInfo?.supply_score;
            const fundamentalScore = stockInfo?.fundamental_score;

            // Find sentiment score from news analysis data
            // If a VCP date is selected, STRICTLY use that date's news (even if empty).
            // Do NOT fall back to global newsAnalysis (which is latest) because that leads to data leakage.
            const sourceNews = selectedVcpDate ? dateNewsAnalysisData : newsAnalysis;
            const sentimentScore = calculateAggregatedSentimentScore(sourceNews, vcp.ticker);

            // Calculate Weighted Integrated Quant Score
            const scoreBreakdown = calculateIntegratedQuantScore({
                vcpScore,
                supplyScore,
                sentimentScore,
                fundamentalScore,
                rawRs: vcp.relative_strength,
            }, (selectedVcpDate ? dateMarketStatus : null), vcp.name, weights);

            return {
                ...vcp,
                vcp_score: vcpScore,
                total_quant_score: scoreBreakdown.totalScore,
                supply_score: supplyScore,
                fundamental_score: fundamentalScore,
                sentiment_score: sentimentScore,
                score_breakdown: scoreBreakdown,
            };
        });

        return [...enrichedData].sort((a, b) => (b.total_quant_score || 0) - (a.total_quant_score || 0));
    }, [dateVcpData, vcpData, stockInfoData, dateNewsAnalysisData, dateStockInfoData, newsAnalysis, selectedVcpDate, dateMarketStatus, weights]);

    const handleSelectVcp = (vcp: VcpResult) => {
        const tickerPadded = String(vcp.ticker).padStart(6, '0');
        setTicker(tickerPadded);
        setName(vcp.name);
        setMarket(vcp.market as 'KOSPI' | 'KOSDAQ');
        const price = String(vcp.price || vcp.close || "");
        setBuyPrice(price);
        setLastAutoFetchedPrice(price);
        setVcpMode(vcp.vcp_mode);

        if (selectedVcpDate) {
            // Convert YYYYMMDD to YYYY-MM-DD for the HTML date input
            const formattedDate = `${selectedVcpDate.slice(0, 4)}-${selectedVcpDate.slice(4, 6)}-${selectedVcpDate.slice(6, 8)}`;
            setBuyDate(formattedDate);
        }

        // Get enriched data with pre-calculated scores
        const enrichedVcp = displayVcpData.find(
            (v) => String(v.ticker).padStart(6, '0') === tickerPadded
        ) as any;

        const vcpScore = vcp.vcp_score || 0;
        const supplyScore = enrichedVcp?.supply_score;
        const sentimentScore = enrichedVcp?.sentiment_score;
        const fundamentalScore = enrichedVcp?.fundamental_score;

        // Calculate weighted score using shared utility
        const breakdown = calculateIntegratedQuantScore({
            vcpScore,
            supplyScore,
            sentimentScore,
            fundamentalScore,
            rawRs: vcp.relative_strength,
        }, (selectedVcpDate ? dateMarketStatus : null), vcp.name, weights);

        // Save Calculated Scores
        setCalculatedScores({
            totalScore: breakdown.totalScore,
            vcpScore,
            supplyScore,
            sentimentScore,
            fundamentalScore,
            sectorScore: 50
        });

        const memoText = formatScoreBreakdown(
            breakdown,
            { vcpScore, supplyScore, sentimentScore, fundamentalScore, sectorScore: 50 },
            {
                contractions: vcp.contractions_count,
                lastDepth: vcp.last_depth_pct,
                volumeDryUp: vcp.volume_dry_up,
                jumpScore: vcp.jump_score || 0,
            }
        );

        setMemo(memoText);
        setShowVcpPicker(false);
    };

    const handleTickerChange = (value: string) => {
        setTicker(value);
        const found = vcpData.find((v) => v.ticker === value) || stockInfoData.find((s) => s.ticker === value);
        if (found) {
            setName(found.name);
            if ('market' in found) {
                setMarket(found.market as 'KOSPI' | 'KOSDAQ');
            }
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!ticker || !buyPrice || !quantity) return;

        // Build exit conditions object
        const exitConditions: ExitConditions = {};
        if (stopLossPercent) exitConditions.stopLossPercent = parseFloat(stopLossPercent);
        if (takeProfitPercent) exitConditions.takeProfitPercent = parseFloat(takeProfitPercent);
        if (trailingStopPercent) exitConditions.trailingStopPercent = parseFloat(trailingStopPercent);
        if (timeCutDays) exitConditions.timeCutDays = parseInt(timeCutDays, 10);
        if (timeCutHours) exitConditions.timeCutHours = parseInt(timeCutHours, 10);
        if (timeCutMinutes) exitConditions.timeCutMinutes = parseInt(timeCutMinutes, 10);
        exitConditions.alertEnabled = alertEnabled;

        let simulationResult = existingItem?.simulation;

        if (simulationEnabled) {
            setIsSimulating(true);
            try {
                const simResponse = await fetch('/api/simulation', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        ticker,
                        buyDate,
                        buyPrice: parseFloat(buyPrice),
                        quantity: parseInt(quantity, 10),
                        exitConditions
                    })
                });

                if (simResponse.ok) {
                    const simData = await simResponse.json();
                    simulationResult = {
                        enabled: true,
                        ...simData,
                        lastUpdate: new Date().toISOString()
                    };
                } else {
                    console.error('Simulation Failed');
                }
            } catch (error) {
                console.error('Simulation Error', error);
            } finally {
                setIsSimulating(false);
            }
        } else {
            // If disabled, remove or set enabled false
            simulationResult = undefined;
        }

        const data = {
            ticker,
            name,
            market,
            buyDate,
            buyPrice: parseFloat(buyPrice),
            quantity: parseInt(quantity, 10),
            memo,
            exitPlan,
            vcp_mode: vcpMode,
            exitConditions,
            initialScores: calculatedScores,
            simulation: simulationResult
        };

        if (existingItem) {
            await updateStock(existingItem.id, data);
        } else {
            await addStock(data);
        }
        onClose();
        resetForm();
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-ink/50">
            <div className="bg-white border-4 border-ink shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] p-8 w-full max-w-6xl mx-4 max-h-[95vh] overflow-y-auto">
                {/* ... Header ... */}
                <div className="flex justify-between items-center mb-6">
                    <h2 className="text-2xl font-black uppercase">
                        {existingItem ? 'Edit Stock' : 'Add Stock'}
                    </h2>
                    <button
                        onClick={onClose}
                        className="p-2 hover:bg-gray-100 border-2 border-ink"
                    >
                        <X size={20} />
                    </button>
                </div>

                <div className="mb-6">
                    {/* ... VCP Picker ... */}
                    <button
                        type="button"
                        onClick={() => setShowVcpPicker(!showVcpPicker)}
                        className="w-full flex items-center justify-between bg-bauhaus-yellow text-ink font-bold px-4 py-3 border-2 border-ink hover:bg-yellow-400 transition-colors"
                    >
                        <span>{selectedVcpDate ? `VCP CANDIDATES (${formatDateLabel(selectedVcpDate)})` : 'SELECT VCP DATE'}</span>
                        {showVcpPicker ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                    </button>
                    {/* ... VCP List ... */}
                    {showVcpPicker && (
                        <div className="border-2 border-t-0 border-ink bg-gray-50">
                            {/* ... select ... */}
                            {availableVcpDates.length > 1 && (
                                <div className="p-3 border-b-2 border-gray-200">
                                    <label className="block text-xs font-bold uppercase mb-1 text-gray-600">Select Date</label>
                                    <select
                                        value={selectedVcpDate}
                                        onChange={(e) => setSelectedVcpDate(e.target.value)}
                                        className="w-full px-3 py-2 font-bold border-2 border-ink bg-white text-ink focus:outline-none focus:ring-2 focus:ring-bauhaus-yellow cursor-pointer appearance-none"
                                        style={{
                                            backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E")`,
                                            backgroundRepeat: 'no-repeat',
                                            backgroundPosition: 'right 12px center',
                                            paddingRight: '40px'
                                        }}
                                    >
                                        {availableVcpDates.map((d) => (
                                            <option key={d} value={d}>
                                                {formatDateLabel(d)}
                                            </option>
                                        ))}
                                    </select>
                                </div>
                            )}

                            <div className="max-h-48 overflow-y-auto">
                                {loadingVcp ? (
                                    <div className="p-4 text-center text-gray-500">Loading...</div>
                                ) : displayVcpData.length === 0 ? (
                                    <div className="p-4 text-center text-gray-500">No VCP candidates</div>
                                ) : (
                                    displayVcpData.map((vcp, idx) => (
                                        <button
                                            key={`${vcp.ticker}-${idx}`}
                                            type="button"
                                            onClick={() => handleSelectVcp(vcp)}
                                            className="w-full flex items-center justify-between px-4 py-3 hover:bg-bauhaus-yellow/30 border-b border-gray-200 last:border-b-0 text-left transition-colors"
                                        >
                                            <div className="flex items-center gap-2">
                                                <div className={`w-10 h-10 flex items-center justify-center font-black text-lg border-2 ${(vcp as any).total_quant_score >= 80
                                                    ? 'bg-bauhaus-red text-white border-bauhaus-red'
                                                    : (vcp as any).total_quant_score >= 60
                                                        ? 'bg-bauhaus-yellow text-ink border-ink'
                                                        : (vcp as any).total_quant_score >= 40
                                                            ? 'bg-bauhaus-blue text-white border-bauhaus-blue'
                                                            : 'bg-gray-200 text-gray-600 border-gray-400'
                                                    }`}>
                                                    {(vcp as any).total_quant_score || 0}
                                                </div>
                                                <div>
                                                    <div className="flex items-center gap-2">
                                                        <span className="font-mono text-sm bg-gray-200 px-2 py-0.5">
                                                            {String(vcp.ticker).padStart(6, '0')}
                                                        </span>
                                                        <span className="font-bold">{vcp.name}</span>
                                                    </div>
                                                    <div className="text-xs text-gray-500">{vcp.market} | {vcp.close?.toLocaleString()}원</div>
                                                </div>
                                            </div>
                                            <div className="text-xs text-gray-400">#{idx + 1}</div>
                                        </button>
                                    ))
                                )}
                            </div>
                        </div>
                    )}
                </div>

                <form onSubmit={handleSubmit} className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {/* Left Column: Stock Info */}
                    <div className="space-y-4">
                        <div className="grid grid-cols-12 gap-4">
                            <div className="col-span-4">
                                <label className="block font-bold mb-1 text-sm">Ticker</label>
                                <input
                                    type="text"
                                    value={ticker}
                                    onChange={(e) => handleTickerChange(e.target.value)}
                                    placeholder="005930"
                                    className="w-full border-2 border-ink p-2 font-mono text-lg"
                                    required
                                />
                            </div>
                            <div className="col-span-8">
                                <label className="block font-bold mb-1 text-sm">Name</label>
                                <input
                                    type="text"
                                    value={name}
                                    onChange={(e) => setName(e.target.value)}
                                    placeholder="Samsung"
                                    className="w-full border-2 border-ink p-2"
                                />
                            </div>
                        </div>

                        <div className="grid grid-cols-3 gap-4">
                            <div>
                                <label className="block font-bold mb-1 text-sm">Market</label>
                                <select
                                    value={market}
                                    onChange={(e) => setMarket(e.target.value as 'KOSPI' | 'KOSDAQ')}
                                    className="w-full border-2 border-ink p-2"
                                >
                                    <option value="KOSPI">KOSPI</option>
                                    <option value="KOSDAQ">KOSDAQ</option>
                                </select>
                            </div>
                            <div>
                                <label className="block font-bold mb-1 text-sm">Buy Date</label>
                                <input
                                    type="date"
                                    value={buyDate}
                                    onChange={(e) => setBuyDate(e.target.value)}
                                    className="w-full border-2 border-ink p-2"
                                />
                            </div>
                            <div>
                                <label className="block font-bold mb-1 text-sm">Quantity</label>
                                <input
                                    type="number"
                                    value={quantity}
                                    onChange={(e) => setQuantity(e.target.value)}
                                    placeholder="100"
                                    className="w-full border-2 border-ink p-2 font-mono"
                                    required
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block font-bold mb-1 text-sm">Buy Price (KRW)</label>
                            <input
                                type="number"
                                value={buyPrice}
                                onChange={(e) => setBuyPrice(e.target.value)}
                                placeholder="50000"
                                className="w-full border-2 border-ink p-2 font-mono text-lg"
                                required
                            />
                        </div>

                        <div>
                            <label className="block font-bold mb-1 text-sm">Buy Reason (Memo)</label>
                            <textarea
                                value={memo}
                                onChange={(e) => setMemo(e.target.value)}
                                placeholder="VCP pattern detected, strong fundamentals..."
                                className="w-full border-2 border-ink p-2 h-32 resize-none"
                            />
                        </div>
                    </div>

                    {/* Right Column: Exit Strategy & Actions */}
                    <div className="space-y-4">
                        {/* Exit Plan Section */}
                        <div className="border-4 border-ink shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] bg-white">
                            <div className="bg-ink text-white px-4 py-2">
                                <span className="font-black text-sm uppercase tracking-widest">Exit Conditions</span>
                            </div>

                            <div className="p-4">
                                {/* ... price grid ... */}
                                <div className="grid grid-cols-2 gap-4 mb-4">
                                    {/* Stop Loss */}
                                    <div className="border-l-4 border-bauhaus-red pl-3">
                                        <label className="block text-xs font-black uppercase tracking-wide text-bauhaus-red mb-2">
                                            Stop Loss
                                        </label>
                                        <div className="flex items-center gap-2">
                                            <span className="text-bauhaus-red font-black text-lg">-</span>
                                            <input
                                                type="number"
                                                value={stopLossPercent}
                                                onChange={(e) => setStopLossPercent(e.target.value)}
                                                placeholder="7"
                                                className="flex-1 border-2 border-ink p-2 font-mono text-lg bg-red-50 focus:bg-white focus:outline-none"
                                                min="0"
                                                max="100"
                                                step="0.5"
                                            />
                                            <span className="font-black text-ink">%</span>
                                        </div>
                                    </div>

                                    {/* Take Profit */}
                                    <div className="border-l-4 border-green-600 pl-3">
                                        <label className="block text-xs font-black uppercase tracking-wide text-green-600 mb-2">
                                            Take Profit
                                        </label>
                                        <div className="flex items-center gap-2">
                                            <span className="text-green-600 font-black text-lg">+</span>
                                            <input
                                                type="number"
                                                value={takeProfitPercent}
                                                onChange={(e) => setTakeProfitPercent(e.target.value)}
                                                placeholder="15"
                                                className="flex-1 border-2 border-ink p-2 font-mono text-lg bg-green-50 focus:bg-white focus:outline-none"
                                                min="0"
                                                max="1000"
                                                step="0.5"
                                            />
                                            <span className="font-black text-ink">%</span>
                                        </div>
                                    </div>
                                </div>

                                {/* ... Trailing & Time ... */}
                                <div className="grid grid-cols-2 gap-4 mb-4">
                                    {/* Trailing Stop */}
                                    <div className="border-l-4 border-bauhaus-yellow pl-3">
                                        <label className="block text-xs font-black uppercase tracking-wide text-amber-600 mb-2">
                                            Trailing Stop
                                        </label>
                                        <div className="flex items-center gap-2">
                                            <span className="text-amber-600 font-black text-lg">-</span>
                                            <input
                                                type="number"
                                                value={trailingStopPercent}
                                                onChange={(e) => setTrailingStopPercent(e.target.value)}
                                                placeholder="10"
                                                className="flex-1 border-2 border-ink p-2 font-mono text-lg bg-amber-50 focus:bg-white focus:outline-none"
                                                min="0"
                                                max="100"
                                                step="0.5"
                                            />
                                            <span className="font-black text-ink">%</span>
                                        </div>
                                        <p className="text-[10px] text-gray-500 mt-1 font-bold">고점 대비 하락률</p>
                                    </div>

                                    {/* Time Cut */}
                                    <div className="border-l-4 border-bauhaus-blue pl-3 min-w-0">
                                        <label className="block text-xs font-black uppercase tracking-wide text-bauhaus-blue mb-2">
                                            Time Cut
                                        </label>
                                        <div className="flex items-center gap-1 flex-wrap">
                                            <input
                                                type="number"
                                                value={timeCutDays}
                                                onChange={(e) => setTimeCutDays(e.target.value)}
                                                placeholder="30"
                                                className="w-12 min-w-0 border-2 border-ink p-1.5 font-mono text-base text-center bg-blue-50 focus:bg-white focus:outline-none"
                                                min="0"
                                                max="365"
                                            />
                                            <span className="font-bold text-xs text-ink shrink-0">일</span>
                                            <input
                                                type="number"
                                                value={timeCutHours}
                                                onChange={(e) => setTimeCutHours(e.target.value)}
                                                placeholder="14"
                                                className="w-10 min-w-0 border-2 border-ink p-1.5 font-mono text-base text-center bg-blue-50 focus:bg-white focus:outline-none"
                                                min="0"
                                                max="23"
                                            />
                                            <span className="font-bold text-xs text-ink shrink-0">시</span>
                                            <input
                                                type="number"
                                                value={timeCutMinutes}
                                                onChange={(e) => setTimeCutMinutes(e.target.value)}
                                                placeholder="30"
                                                className="w-10 min-w-0 border-2 border-ink p-1.5 font-mono text-base text-center bg-blue-50 focus:bg-white focus:outline-none"
                                                min="0"
                                                max="59"
                                            />
                                            <span className="font-bold text-xs text-ink shrink-0">분</span>
                                        </div>
                                        <p className="text-[10px] text-gray-500 mt-1 font-bold">보유 기간 제한</p>
                                    </div>
                                </div>

                                {/* Alert Toggle */}
                                <div className="flex items-center gap-3 pt-3 border-t-2 border-ink">
                                    <button
                                        type="button"
                                        onClick={() => setAlertEnabled(!alertEnabled)}
                                        className={`w-6 h-6 border-2 border-ink flex items-center justify-center transition-colors ${alertEnabled ? 'bg-bauhaus-blue' : 'bg-white'
                                            }`}
                                    >
                                        {alertEnabled && <span className="text-white font-black text-sm">✓</span>}
                                    </button>
                                    <label className="text-sm font-bold uppercase tracking-wide cursor-pointer" onClick={() => setAlertEnabled(!alertEnabled)}>
                                        조건 충족 시 알림 받기
                                    </label>
                                </div>
                            </div>
                        </div>

                        <div className="border-t-2 border-ink bg-gray-50 p-4">
                            <label className="block text-xs font-black uppercase tracking-wide text-gray-600 mb-2">
                                Exit Memo (Optional)
                            </label>
                            <textarea
                                value={exitPlan}
                                onChange={(e) => setExitPlan(e.target.value)}
                                placeholder="추가 청산 계획 메모..."
                                className="w-full border-2 border-ink p-3 h-20 resize-none font-mono text-sm focus:outline-none"
                            />
                        </div>

                        {/* Simulation Toggle - NEW */}
                        <div className="border-4 border-ink bg-gray-100 p-4 flex items-center justify-between">
                            <div>
                                <h3 className="font-black uppercase text-sm">Simulation Mode (Backtest)</h3>
                                <p className="text-xs text-gray-600">
                                    Apply exit conditions to historical data to determine if position is already closed.
                                </p>
                            </div>
                            <button
                                type="button"
                                onClick={() => setSimulationEnabled(!simulationEnabled)}
                                className={`relative w-14 h-8 rounded-full border-2 border-ink transition-colors ${simulationEnabled ? 'bg-bauhaus-blue' : 'bg-gray-300'
                                    }`}
                            >
                                <div
                                    className={`absolute top-1 left-1 w-5 h-5 bg-white border-2 border-ink rounded-full transition-transform ${simulationEnabled ? 'translate-x-6' : 'translate-x-0'
                                        }`}
                                />
                            </button>
                        </div>

                        <button
                            type="submit"
                            disabled={isSimulating}
                            className="w-full bg-ink text-white font-black py-4 uppercase text-lg hover:bg-bauhaus-blue transition-colors disabled:bg-gray-400 disabled:cursor-wait shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-none hover:translate-x-1 hover:translate-y-1"
                        >
                            {isSimulating ? 'Running Simulation...' : (existingItem ? 'Update Portfolio' : 'Add to Portfolio')}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
