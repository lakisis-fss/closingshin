'use client';

import { useMemo, useEffect, useState } from 'react';
import { TrendingUp, TrendingDown, AlertTriangle, CheckCircle, Target, Timer, Shield, BarChart2, Activity } from 'lucide-react';
import { PortfolioItem, VcpResult, StockInfo, NewsAnalysis } from '@/lib/types';
import { calculateIntegratedQuantScore, calculateAggregatedSentimentScore } from '@/lib/scoreCalculator';
import { isMarketOpen } from '@/lib/utils';

interface HoldingsTableProps {
    holdings: PortfolioItem[];
    vcpData: VcpResult[];
    stockInfoData: StockInfo[];
    newsAnalysis: NewsAnalysis[];
    statusData?: any;
    onEdit: (item: PortfolioItem) => void;
    onRemove: (id: string) => void;
    onRowClick: (item: any) => void;
    onClosePosition: (item: any) => void;
}

export function HoldingsTable({ holdings, vcpData, stockInfoData, newsAnalysis, statusData, onEdit, onRemove, onRowClick, onClosePosition }: HoldingsTableProps) {
    // State to store fetched historical metrics per ticker
    const [historyMetrics, setHistoryMetrics] = useState<Record<string, { peakPrice: number, mdd: number, minPrice: number, mae: number, lastClose: number }>>({});

    // Fetch historical data for open positions
    useEffect(() => {
        const fetchHistories = async () => {
            const newMetrics: Record<string, { peakPrice: number, mdd: number, minPrice: number, mae: number, lastClose: number }> = { ...historyMetrics };
            let hasUpdates = false;

            const fetchPromises = holdings.map(async (item) => {
                // Skip if we already have it or if position is closed
                // Skip if we already have it
                if (newMetrics[item.id]) {
                    return;
                }

                try {
                    const buyDate = item.buyDate || new Date().toISOString().split('T')[0];
                    const isClosed = item.simulation?.enabled && item.simulation?.status === 'CLOSED';
                    const exitDate = isClosed ? item.simulation?.exitDate : null;
                    
                    let url = `/api/portfolio/history?ticker=${item.ticker}&startDate=${buyDate}`;
                    if (exitDate) url += `&endDate=${exitDate}`;
                    
                    const res = await fetch(url);
                    if (res.ok) {
                        const data = await res.json();
                        if (data.history && data.history.length > 0) {
                            // Find Peak Price from historical 'high's and current price
                            let peakPrice = item.buyPrice;
                            let minPrice = item.buyPrice;
                            for (const candle of data.history) {
                                if (candle.high > peakPrice) peakPrice = candle.high;
                                if (candle.low > 0 && candle.low < minPrice) minPrice = candle.low;
                            }

                            // Get current price based on market status
                            const normalizedItemTicker = String(item.ticker).padStart(6, '0');
                            const marketOpen = isMarketOpen();
                            const vcp = vcpData.find((v) => String(v.ticker).padStart(6, '0') === normalizedItemTicker);
                            const stockInfo = stockInfoData.find((s) => String(s.ticker).padStart(6, '0') === normalizedItemTicker);
                            const closePrice = vcp?.close || stockInfo?.close || 0;

                            let currentPrice = item.buyPrice;
                            let statusPrice = 0;

                            if (statusData?.items) {
                                const statusItem = statusData.items.find((s: any) => String(s.ticker).padStart(6, '0') === normalizedItemTicker);
                                if (statusItem && statusItem.currentPrice > 0) statusPrice = statusItem.currentPrice;
                            }

                             // Market-based logic: 
                             // Always prioritize real-time statusPrice if available
                             const isClosedPos = item.simulation?.enabled && item.simulation?.status === 'CLOSED';
                             
                             if (isClosedPos) {
                                 currentPrice = item.simulation?.exitPrice || statusPrice || closePrice || item.buyPrice;
                             } else if (statusPrice > 0) {
                                 currentPrice = statusPrice;
                             } else {
                                 currentPrice = closePrice || item.buyPrice;
                             }

                            if (currentPrice > peakPrice) peakPrice = currentPrice;
                            if (currentPrice > 0 && currentPrice < minPrice) minPrice = currentPrice;

                            // Calculate MDD and MAE
                            const mdd = peakPrice > 0 ? ((currentPrice - peakPrice) / peakPrice) * 100 : 0;
                            const mae = ((minPrice - item.buyPrice) / item.buyPrice) * 100;

                            const lastClose = data.history[data.history.length - 1].close || closePrice || item.buyPrice;

                            newMetrics[item.id] = { peakPrice, mdd, minPrice, mae, lastClose };
                            hasUpdates = true;
                        }
                    }
                } catch (err) {
                    console.error('Failed to fetch history for', item.ticker, err);
                }
            });

            await Promise.all(fetchPromises);

            if (hasUpdates) {
                setHistoryMetrics(newMetrics);
            }
        };

        fetchHistories();
    }, [holdings, statusData]); // re-run if holdings or statusData changes

    const enrichedHoldings = useMemo(() => {
        // 1. Calculate total portfolio value first for weight calculation
        let totalPortfolioValue = 0;
        const tempHoldings = holdings.map((item) => {
            const normalizedItemTicker = String(item.ticker).padStart(6, '0');
            const vcp = vcpData.find((v) => String(v.ticker).padStart(6, '0') === normalizedItemTicker);
            const stockInfo = stockInfoData.find((s) => String(s.ticker).padStart(6, '0') === normalizedItemTicker);
            let currentPrice = 0;
            const marketOpen = isMarketOpen();
            const closePrice = vcp?.close || stockInfo?.close || 0;

            // Initialize with statusData price if available
            let statusPrice = 0;
            if (statusData?.items) {
                const statusItem = statusData.items.find((s: any) => String(s.ticker).padStart(6, '0') === normalizedItemTicker);
                if (statusItem && statusItem.currentPrice > 0) {
                    statusPrice = statusItem.currentPrice;
                }
            }

            // Market-based logic:
            // P1: Always prioritize real-time price from statusData (Market Hours)
            // P2: Fallback to the most recent closing price from history (After Hours / Weekend)
            // P3: Fallback to the dashboard's closePrice (Static data)
            if (statusPrice > 0) {
                currentPrice = statusPrice;
            } else if (historyMetrics[item.id]?.lastClose > 0) {
                currentPrice = historyMetrics[item.id].lastClose;
            } else {
                currentPrice = closePrice || 0;
            }

            // Final fallback to buyPrice if we still have absolutely nothing
            if (currentPrice === 0) {
                currentPrice = item.buyPrice;
            }

            // Fallback to simulation result if still 0
            if (currentPrice === 0 && item.simulation?.enabled && item.simulation.exitPrice) {
                currentPrice = item.simulation.exitPrice;
            }

            const currentValue = currentPrice * item.quantity;
            totalPortfolioValue += currentValue;
            return { ...item, currentValue, vcp, currentPrice };
        });

        // 2. Map enriched data
        return tempHoldings.map((item) => {
            const vcp = item.vcp;
            const normalizedItemTicker = String(item.ticker).padStart(6, '0');
            const stockInfo = stockInfoData.find((s) => String(s.ticker).padStart(6, '0') === normalizedItemTicker);

            const currentPrice = item.currentPrice || 0;
            const totalCost = item.buyPrice * item.quantity;
            const currentValue = currentPrice * item.quantity;
            const pnl = currentValue - totalCost;
            const pnlPercent = totalCost > 0 ? ((currentValue - totalCost) / totalCost) * 100 : 0;

            // Calculate Weight
            const weight = totalPortfolioValue > 0 ? (currentValue / totalPortfolioValue) * 100 : 0;

            // Calculate Days Held
            const buyDateStr = item.buyDate || item.createdAt || new Date().toISOString();
            const buyDate = new Date(buyDateStr);
            
            // For closed positions, use exitDate if available, otherwise today
            const isClosedPos = item.simulation?.enabled && item.simulation?.status === 'CLOSED';
            const endDateStr = (isClosedPos && item.simulation?.exitDate) 
                ? item.simulation.exitDate 
                : new Date().toISOString();
            const endDate = new Date(endDateStr);
            
            let daysHeld = 0;
            if (!isNaN(buyDate.getTime()) && !isNaN(endDate.getTime())) {
                const diffTime = Math.abs(endDate.getTime() - buyDate.getTime());
                daysHeld = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
            }

            // Ensure daysHeld is at least 1 for average calculation
            const calculationDays = daysHeld === 0 ? 1 : daysHeld;
            
            // Use simulation realizedPnlPercent for closed positions, or calculated pnlPercent for active
            const targetPnlPercent = isClosedPos ? (item.simulation?.realizedPnlPercent || 0) : pnlPercent;
            // Requirement: Apply dailyAvgReturn logic to all positions (Active & Realized)
            // Realized trades are calculated based on their exit date
            const dailyAvgReturn = targetPnlPercent / calculationDays;

            // DETERMINE SCORES
            let finalScores: {
                totalScore: number;
                vcpScore?: number;
                supplyScore?: number;
                fundamentalScore?: number;
                sentimentScore?: number;
            };

            // Strategy 1: Use Title-saved Initial Scores (Best)
            if (item.initialScores) {
                finalScores = item.initialScores;
            } else {
                // Strategy 2: Fallback - Try to parse TQ Score from Memo
                // Memo format: "Total Score: 78" or previously "Total Score:78"
                const memoMatch = item.memo?.match(/Total Score:\s*(\d+)/);

                // Strategy 3: Real-time Calculation (Last Resort)
                // If memo parsing failed, we calculate from CURRENT data
                const sentimentScore = calculateAggregatedSentimentScore(newsAnalysis, item.ticker);
                const currentBreakdown = calculateIntegratedQuantScore({
                    vcpScore: vcp?.vcp_score,
                    supplyScore: stockInfo?.supply_score,
                    fundamentalScore: stockInfo?.fundamental_score,
                    sentimentScore: sentimentScore,
                    sectorScore: 50,
                });

                if (memoMatch) {
                    // If we found a score in memo, use it for Total Score
                    // But we might lack component scores, so we mix best effort
                    finalScores = {
                        totalScore: parseInt(memoMatch[1], 10),
                        vcpScore: vcp?.vcp_score, // Still showing current component scores if we can't parse them
                        supplyScore: stockInfo?.supply_score,
                        fundamentalScore: stockInfo?.fundamental_score,
                        sentimentScore: sentimentScore // And current sentiment
                    };
                } else {
                    // Fully computed real-time score
                    finalScores = {
                        totalScore: currentBreakdown.totalScore,
                        vcpScore: vcp?.vcp_score,
                        supplyScore: stockInfo?.supply_score,
                        fundamentalScore: stockInfo?.fundamental_score,
                        sentimentScore: sentimentScore
                    };
                }
            }

            // Calculate grade color for final score
            let gradeColor = 'gray-400';
            const { totalScore } = finalScores;
            if (totalScore >= 80) gradeColor = 'bauhaus-red';
            else if (totalScore >= 60) gradeColor = 'bauhaus-yellow';
            else if (totalScore >= 40) gradeColor = 'bauhaus-blue';

            return {
                ...item,
                currentPrice,
                totalCost,
                currentValue,
                pnl,
                pnlPercent,
                weight,
                daysHeld,
                dailyAvgReturn,
                vcpScore: finalScores.vcpScore,
                fundamentalScore: finalScores.fundamentalScore,
                supplyScore: finalScores.supplyScore,
                stockInfo,
                vcp: (item as any).vcp,
                integratedScore: totalScore,
                scoreGradeColor: gradeColor,
                peakPrice: historyMetrics[item.id]?.peakPrice || Math.max(currentPrice, item.buyPrice),
                mdd: historyMetrics[item.id]?.mdd || 0,
                mae: historyMetrics[item.id]?.mae || 0,
            };
        });
    }, [holdings, vcpData, stockInfoData, newsAnalysis, statusData, historyMetrics]);

    const { activeHoldings, closedHoldings } = useMemo(() => {
        const active = enrichedHoldings.filter(item => !(item.simulation?.enabled && item.simulation?.status === 'CLOSED'));
        const closed = enrichedHoldings.filter(item => item.simulation?.enabled && item.simulation?.status === 'CLOSED');
        return { activeHoldings: active, closedHoldings: closed };
    }, [enrichedHoldings]);

    if (holdings.length === 0) {
        return (
            <div className="bg-white border-4 border-ink p-12 text-center">
                <p className="text-gray-500 font-bold text-lg">No stocks in portfolio</p>
                <p className="text-gray-400 mt-2">Click the button above to add your first stock</p>
            </div>
        );
    }

    const renderTable = (items: typeof enrichedHoldings, title: string, titleColor: string, count: number) => {
        if (items.length === 0) return null;

        // Calculate statistics for this group
        const totalCost = items.reduce((sum, item) => sum + item.totalCost, 0);
        const totalValue = items.reduce((sum, item) => {
            const isClosed = item.simulation?.enabled && item.simulation?.status === 'CLOSED';
            const price = isClosed ? (item.simulation?.exitPrice || 0) : item.currentPrice;
            return sum + (price * item.quantity);
        }, 0);
        const totalPnl = totalValue - totalCost;
        const totalPnlPercent = totalCost > 0 ? (totalPnl / totalCost) * 100 : 0;
        const avgDailyReturn = items.length > 0 
            ? items.reduce((sum, item: any) => sum + (item.dailyAvgReturn || 0), 0) / items.length 
            : 0;

        return (
            <div className="mb-12 last:mb-0">
                <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-6 border-b-4 border-ink pb-2">
                    <div className="flex items-center gap-3">
                        <h3 className={`text-4xl font-black uppercase ${titleColor}`}>{title}</h3>
                        <span className="bg-ink text-white px-3 py-1 text-sm font-black border-2 border-ink">
                            {count} {count === 1 ? 'ITEM' : 'ITEMS'}
                        </span>
                    </div>

                    <div className="flex items-center gap-6 font-mono">
                        {(avgDailyReturn !== 0) && (
                            <div className="flex flex-col items-end">
                                <span className="text-[10px] uppercase font-black text-gray-400">Avg. Daily Return</span>
                                <div className={`text-xl font-black flex items-center gap-1 ${avgDailyReturn >= 0 ? 'text-bauhaus-red' : 'text-bauhaus-blue'}`}>
                                    <span>{avgDailyReturn >= 0 ? '+' : ''}{avgDailyReturn.toFixed(3)}%</span>
                                    <span className="text-[10px] font-black opacity-50">/DAY</span>
                                </div>
                            </div>
                        )}
                        <div className="flex flex-col items-end">
                            <span className="text-[10px] uppercase font-black text-gray-500">Total Investment</span>
                            <span className="text-xl font-black">{Math.round(totalCost).toLocaleString()} KRW</span>
                        </div>
                        <div className="flex flex-col items-end">
                            <span className="text-[10px] uppercase font-black text-gray-500">
                                {title.includes('Active') ? 'Unrealized P&L' : 'Realized P&L'}
                            </span>
                            <div className={`text-xl font-black flex items-center gap-2 ${totalPnl >= 0 ? 'text-bauhaus-red' : 'text-bauhaus-blue'}`}>
                                <span>{totalPnl >= 0 ? '+' : ''}{Math.round(totalPnl).toLocaleString()}</span>
                                <span className={`text-sm px-2 py-0.5 border-2 ${totalPnl >= 0 ? 'bg-bauhaus-red text-white border-bauhaus-red' : 'bg-bauhaus-blue text-white border-bauhaus-blue'}`}>
                                    {totalPnlPercent.toFixed(2)}%
                                </span>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="bg-white border-4 border-ink shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] overflow-hidden">
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead className="bg-ink text-white">
                                <tr>
                                    <th className="p-3 text-left font-black">STOCK</th>
                                    <th className="p-3 text-right font-black">BUY</th>
                                    <th className="p-3 text-right font-black">
                                        {title.includes('Active') ? 'CURRENT' : 'EXIT'}
                                    </th>
                                    <th className="p-3 text-right font-black">P&L</th>
                                    <th className="p-3 text-center font-black">SCORES</th>
                                    <th className="p-3 text-center font-black">EXIT PLAN / RESULT</th>
                                    <th className="p-3 text-center font-black">ACTIONS</th>
                                </tr>
                            </thead>
                            <tbody>
                                {items.map((item, idx) => {
                                    const isSimulated = item.simulation?.enabled;
                                    const isClosed = isSimulated && item.simulation?.status === 'CLOSED';
                                    const simResult = item.simulation;

                                    const displayPrice = isClosed ? (simResult?.exitPrice || 0) : item.currentPrice;
                                    const displayValue = isClosed ? (displayPrice * item.quantity) : item.currentValue;
                                    const displayPnl = isClosed ? (simResult?.realizedPnl || 0) : item.pnl;
                                    const displayPnlPercent = isClosed ? (simResult?.realizedPnlPercent || 0) : item.pnlPercent;

                                    return (
                                        <tr
                                            key={item.id}
                                            onClick={() => onRowClick(item)}
                                            className={`border-b-2 border-gray-200 hover:bg-gray-50 transition-colors cursor-pointer group ${isClosed ? 'bg-gray-100 hover:bg-gray-200' : (idx % 2 === 1 ? 'bg-gray-50' : '')
                                                }`}
                                        >
                                            <td className="p-3">
                                                <div className="flex items-center gap-2">
                                                    <span className={`text-xs px-2 py-0.5 font-mono ${isClosed ? 'bg-gray-300 text-gray-600' : 'bg-gray-200'}`}>
                                                        {item.ticker}
                                                    </span>
                                                    <span className={`font-bold ${isClosed ? 'text-gray-600' : ''}`}>{item.name}</span>
                                                    {item.vcp_mode && (
                                                        <span className={`text-[10px] font-black uppercase px-1.5 py-0.5 border-2 ${isClosed ? 'border-gray-400 text-gray-500 bg-gray-200' : 'border-ink bg-bauhaus-yellow text-ink'}`}>
                                                            {item.vcp_mode}
                                                        </span>
                                                    )}

                                                    <a
                                                        href={`https://finance.naver.com/item/main.naver?code=${item.ticker}`}
                                                        target="_blank"
                                                        rel="noopener noreferrer"
                                                        onClick={(e) => e.stopPropagation()}
                                                        className="p-1 bg-white border-2 border-ink shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:bg-bauhaus-yellow hover:shadow-none hover:translate-x-[1px] hover:translate-y-[1px] transition-all cursor-pointer"
                                                        title="네이버 차트 보기"
                                                    >
                                                        <BarChart2 size={12} className="text-ink" />
                                                    </a>
                                                    {isSimulated && (
                                                        <span className={`text-[10px] font-black px-1.5 py-0.5 border ${isClosed ? 'bg-gray-300 text-gray-600 border-gray-400' : 'bg-blue-100 text-blue-600 border-blue-200'
                                                            }`}>
                                                            {isClosed ? 'SIM:CLOSED' : 'SIM:ACTIVE'}
                                                        </span>
                                                    )}
                                                </div>
                                                <div className="text-xs text-gray-500 mt-1 flex items-center gap-2">
                                                    <span>{item.market}</span>
                                                    {!isClosed && (
                                                        <>
                                                            <span className="text-gray-300">|</span>
                                                            <span className="font-bold text-bauhaus-blue">Weight {item.weight.toFixed(1)}%</span>
                                                        </>
                                                    )}
                                                    <span className="text-gray-300">|</span>
                                                    <span className="font-mono text-gray-600">
                                                        D+{item.daysHeld}
                                                        {item.buyDate && !isNaN(new Date(item.buyDate).getTime()) && (
                                                            <span className="text-[10px] text-gray-400 ml-1">
                                                                ({new Date(item.buyDate).toLocaleDateString('ko-KR', { year: '2-digit', month: '2-digit', day: '2-digit' }).replace(/\./g, '/').replace(/\/ $/, '').replace(/\s/g, '')})
                                                            </span>
                                                        )}
                                                    </span>
                                                </div>
                                            </td>
                                            <td className="p-3 text-right font-mono">
                                                <div className="font-bold">{item.totalCost.toLocaleString()}</div>
                                                <div className="text-xs text-gray-500 font-mono mt-1">
                                                    @{item.buyPrice.toLocaleString()} x {item.quantity.toLocaleString()}
                                                </div>
                                            </td>
                                            <td className="p-3 text-right font-mono">
                                                {displayPrice > 0 ? (
                                                    <>
                                                        <div className={`font-bold ${isClosed ? 'text-gray-600' : ''}`}>
                                                            {Math.round(displayValue).toLocaleString()}
                                                        </div>
                                                        <div className="text-xs text-gray-500">
                                                            @{Math.round(displayPrice).toLocaleString()}
                                                            {isClosed && (
                                                                <>
                                                                    <span className="ml-1 text-[10px] text-gray-400">(EXIT)</span>
                                                                    {simResult?.exitDate && !isNaN(new Date(simResult.exitDate).getTime()) && (
                                                                        <div className="text-[10px] text-gray-400 mt-0.5 leading-none">
                                                                            ({new Date(simResult.exitDate).toLocaleDateString('ko-KR', { year: '2-digit', month: '2-digit', day: '2-digit' }).replace(/\./g, '/').replace(/\/ $/, '').replace(/\s/g, '')})
                                                                        </div>
                                                                    )}
                                                                </>
                                                            )}
                                                        </div>
                                                    </>
                                                ) : (
                                                    <span className="text-gray-400">-</span>
                                                )}
                                                {!isClosed && displayPrice > 0 && Number(item.peakPrice) > 0 && (
                                                    <div className="flex items-center justify-end gap-1 mt-1 text-[10px]">
                                                        <span className="bg-gray-200 text-gray-600 px-1 py-0.5 border border-gray-300 rounded-sm font-bold" title={`고점: ${Number(item.peakPrice).toLocaleString()}`}>
                                                            <Activity size={10} className="inline mr-0.5" />
                                                            고점 {Number(item.peakPrice).toLocaleString()} {Number(item.mdd) < 0 ? `(MDD ${Number(item.mdd).toFixed(1)}%)` : ''}
                                                        </span>
                                                    </div>
                                                )}
                                            </td>
                                            <td className="p-3 text-right">
                                                <div className="flex flex-col items-end">
                                                    <div
                                                        className={`text-lg font-black font-mono flex flex-col items-end ${displayPnlPercent >= 0 ? 'text-bauhaus-red' : 'text-bauhaus-blue'
                                                            }`}
                                                    >
                                                        <div className="text-[12px] font-bold leading-none mb-1">
                                                            {displayPnl >= 0 ? '+' : ''}{Math.round(displayPnl).toLocaleString()}
                                                        </div>
                                                        <div className="flex items-center gap-1">
                                                            {displayPnlPercent >= 0 ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
                                                            {displayPnlPercent >= 0 ? '+' : ''}
                                                            {displayPnlPercent.toFixed(2)}%
                                                        </div>
                                                        <div className="text-[10px] font-bold opacity-80">
                                                            {((item.dailyAvgReturn || 0)).toFixed(2)}%/day
                                                        </div>
                                                    </div>

                                                    {item.mae < 0 && (() => {
                                                        const mae = item.mae;
                                                        const cur = displayPnlPercent;
                                                        const max = Math.max(cur, 0.1);
                                                        const range = max - mae;
                                                        if (range === 0) return null;
                                                        const zeroPct = (Math.abs(mae) / range) * 100;
                                                        const curPct = ((cur - mae) / range) * 100;
                                                        return (
                                                            <div className="w-[110px] flex flex-col mt-1" title="MAE: 진입 후 최대 하락 우회폭">
                                                                <div className="flex justify-between items-center text-[9px] font-mono text-gray-500 mb-0.5 px-0.5">
                                                                    <span>MAE <span className="text-bauhaus-blue font-bold">{mae.toFixed(1)}%</span></span>
                                                                </div>
                                                                <div className="w-full h-1.5 bg-gray-200 relative overflow-hidden border border-gray-300">
                                                                    <div className="absolute top-0 bottom-0 bg-blue-200/50" style={{ left: 0, right: `${100 - zeroPct}%` }} />
                                                                    {cur <= 0 && <div className="absolute top-0 bottom-0 bg-bauhaus-blue" style={{ left: `${curPct}%`, right: `${100 - zeroPct}%` }} />}
                                                                    {cur > 0 && <div className="absolute top-0 bottom-0 bg-bauhaus-red" style={{ left: `${zeroPct}%`, right: `${100 - curPct}%` }} />}
                                                                    <div className="absolute top-0 bottom-0 w-[1.5px] bg-ink z-10" style={{ left: `calc(${zeroPct}% - 0.75px)` }} />
                                                                </div>
                                                            </div>
                                                        );
                                                    })()}
                                                </div>
                                            </td>
                                            <td className="p-3">
                                                <div className="flex flex-col items-center gap-1">
                                                    <div
                                                        className={`text-sm font-black px-3 py-1 border-2 ${item.integratedScore >= 80
                                                            ? 'bg-bauhaus-red text-white border-bauhaus-red'
                                                            : item.integratedScore >= 60
                                                                ? 'bg-bauhaus-yellow text-ink border-ink'
                                                                : item.integratedScore >= 40
                                                                    ? 'bg-bauhaus-blue text-white border-bauhaus-blue'
                                                                    : 'bg-gray-200 text-gray-600 border-gray-400'
                                                            }`}
                                                    >
                                                        TQ {item.integratedScore}
                                                    </div>
                                                    <div className="flex gap-1 text-[10px] text-gray-500">
                                                        {item.vcpScore !== undefined && <span>V:{item.vcpScore}</span>}
                                                        {item.supplyScore !== undefined && <span>S:{item.supplyScore}</span>}
                                                        {item.fundamentalScore !== undefined && <span>F:{item.fundamentalScore}</span>}
                                                    </div>
                                                </div>
                                            </td>
                                            <td className="p-3">
                                                {isClosed ? (
                                                    <div className="flex flex-col items-end gap-1 text-right">
                                                        <span className="text-xs font-black uppercase text-gray-700 bg-gray-200 px-2 py-0.5 rounded-sm">
                                                            {simResult?.exitReason || 'Closed'}
                                                        </span>
                                                        {simResult?.exitDate && !isNaN(new Date(simResult.exitDate).getTime()) && (
                                                            <span className="text-[10px] text-gray-500 font-mono mt-0.5">
                                                                {new Date(simResult.exitDate).toLocaleDateString('ko-KR', { year: '2-digit', month: '2-digit', day: '2-digit' }).replace(/\./g, '/').replace(/\/ $/, '').replace(/\s/g, '')}
                                                            </span>
                                                        )}
                                                    </div>
                                                ) : (
                                                    (item.exitConditions && Object.keys(item.exitConditions).filter(k => k !== 'alertEnabled').length > 0) ? (
                                                        <div className="flex flex-col gap-1 text-xs">
                                                            <div className="flex items-center justify-center gap-1">
                                                                {item.exitConditions.stopLossPercent && (
                                                                    <span className={`px-2 py-0.5 font-mono font-bold border-2 ${item.pnlPercent <= -(item.exitConditions.stopLossPercent || 0)
                                                                        ? 'bg-bauhaus-blue text-white border-bauhaus-blue' : 'bg-white text-bauhaus-blue border-bauhaus-blue'}`}>
                                                                        <Shield size={10} className="inline mr-0.5" />
                                                                        -{Math.abs(item.exitConditions.stopLossPercent)}%
                                                                    </span>
                                                                )}
                                                                {item.exitConditions.takeProfitPercent && (
                                                                    <span className={`px-2 py-0.5 font-mono font-bold border-2 ${item.pnlPercent >= (item.exitConditions.takeProfitPercent || 0)
                                                                        ? 'bg-bauhaus-red text-white border-bauhaus-red' : 'bg-white text-bauhaus-red border-bauhaus-red'}`}>
                                                                        <Target size={10} className="inline mr-0.5" />
                                                                        +{item.exitConditions.takeProfitPercent}%
                                                                    </span>
                                                                )}
                                                            </div>
                                                        </div>
                                                    ) : (
                                                        <div className="flex justify-center">
                                                            <span className="px-3 py-1 font-black text-xs uppercase border-2 border-bauhaus-yellow bg-bauhaus-yellow text-ink">
                                                                OPEN
                                                            </span>
                                                        </div>
                                                    )
                                                )}
                                            </td>
                                            <td className="p-3 text-center">
                                                <div className="flex justify-center gap-2">
                                                    <button onClick={(e) => { e.stopPropagation(); onEdit(item); }}
                                                        className="text-xs font-bold px-3 py-1 border-2 border-ink hover:bg-ink hover:text-white transition-colors">EDIT</button>
                                                    {!isClosed && (
                                                        <button onClick={(e) => { e.stopPropagation(); onClosePosition(item); }}
                                                            className="text-xs font-bold px-3 py-1 border-2 border-bauhaus-red text-bauhaus-red hover:bg-bauhaus-red hover:text-white transition-colors uppercase">Close</button>
                                                    )}
                                                    <button onClick={(e) => { e.stopPropagation(); onRemove(item.id); }}
                                                        className="text-xs font-bold px-3 py-1 border-2 border-red-500 text-red-500 hover:bg-red-500 hover:text-white transition-colors">DEL</button>
                                                </div>
                                            </td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        );
    };

    return (
        <div className="space-y-12">
            {renderTable(activeHoldings, "Active Positions", "text-ink", activeHoldings.length)}
            {renderTable(closedHoldings, "Realized Trades", "text-gray-400", closedHoldings.length)}
        </div>
    );
}
