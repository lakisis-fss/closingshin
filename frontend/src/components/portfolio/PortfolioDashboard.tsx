'use client';

import { useMemo } from 'react';
import { Wallet, TrendingUp, TrendingDown, Activity, Info, Lock, Unlock } from 'lucide-react';
import { PortfolioItem, VcpResult, StockInfo, NewsAnalysis } from '@/lib/types';
import { calculateIntegratedQuantScore, calculateAggregatedSentimentScore } from '@/lib/scoreCalculator';
import { isMarketOpen } from '@/lib/utils';

interface PortfolioDashboardProps {
    holdings: PortfolioItem[];
    vcpData: VcpResult[];
    stockInfoData: StockInfo[];
    newsAnalysis: NewsAnalysis[];
    statusData?: any;
}

export function PortfolioDashboard({ holdings, vcpData, stockInfoData, newsAnalysis, statusData }: PortfolioDashboardProps) {
    const stats = useMemo(() => {
        let totalCost = 0;
        let totalValue = 0;
        let integratedScoreSum = 0;
        let integratedScoreCount = 0;
        let dailyReturnSum = 0;

        // Separate tracking for realized vs unrealized
        let realizedPnl = 0;
        let realizedCost = 0;
        let unrealizedPnl = 0;
        let unrealizedCost = 0;
        let activeCount = 0;
        let closedCount = 0;

        holdings.forEach((item) => {
            const cost = item.buyPrice * item.quantity;
            totalCost += cost;

            const isClosed = item.simulation?.status === 'CLOSED';
            const simResult = item.simulation;

            if (isClosed && simResult) {
                // Closed position: use realized P&L from simulation
                closedCount++;
                realizedCost += cost;
                realizedPnl += simResult.realizedPnl || 0;
                // Use exit price for total value
                totalValue += (simResult.exitPrice || item.buyPrice) * item.quantity;
            } else {
                // Active position: calculate unrealized P&L
                activeCount++;
                unrealizedCost += cost;

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
                // Always prioritize real-time price from statusData, fallback to closePrice
                if (statusPrice > 0) {
                    currentPrice = statusPrice;
                } else {
                    currentPrice = closePrice || 0;
                }

                // Fallback to buyPrice if we still have nothing (e.g., brand new entry today)
                // but ONLY if the market is closed and we have no other data
                if (currentPrice === 0 && !marketOpen) {
                    currentPrice = item.buyPrice;
                }

                // 2. Use simulation result (very fresh from modal addition) if still 0
                if (currentPrice === 0 && item.simulation?.enabled && item.simulation.exitPrice) {
                    currentPrice = item.simulation.exitPrice;
                }

                if (currentPrice > 0) {
                    const currentValue = currentPrice * item.quantity;
                    totalValue += currentValue;
                    unrealizedPnl += currentValue - cost;
                }

                // Calculate weighted integrated score (only for active positions)
                const sentimentScore = calculateAggregatedSentimentScore(newsAnalysis, item.ticker);

                const breakdown = calculateIntegratedQuantScore({
                    vcpScore: vcp?.vcp_score,
                    supplyScore: stockInfo?.supply_score,
                    fundamentalScore: stockInfo?.fundamental_score,
                    sentimentScore: sentimentScore,
                    sectorScore: 50,
                });

                integratedScoreSum += breakdown.totalScore;
                integratedScoreCount++;

                // Calculate Daily Avg Return for Active Positions
                const buyDate = new Date(item.buyDate || item.createdAt || new Date().toISOString());
                const diffTime = Math.abs(new Date().getTime() - buyDate.getTime());
                const daysHeld = Math.max(1, Math.ceil(diffTime / (1000 * 60 * 60 * 24)));
                
                // pnlPercent for this item (active only)
                const itemCost = item.buyPrice * item.quantity;
                const itemCurrentValue = currentPrice * item.quantity;
                const itemPnlPercent = itemCost > 0 ? ((itemCurrentValue - itemCost) / itemCost) * 100 : 0;
                
                dailyReturnSum += (itemPnlPercent / daysHeld);
            }
        });

        const totalPnl = realizedPnl + unrealizedPnl;
        const pnlPercent = totalCost > 0 ? (totalPnl / totalCost) * 100 : 0;
        const realizedPnlPercent = realizedCost > 0 ? (realizedPnl / realizedCost) * 100 : 0;
        const unrealizedPnlPercent = unrealizedCost > 0 ? (unrealizedPnl / unrealizedCost) * 100 : 0;

        const avgDailyReturn = activeCount > 0 ? (dailyReturnSum / activeCount) : 0;
        const avgIntegratedScore = integratedScoreCount > 0 ? Math.round(integratedScoreSum / integratedScoreCount) : 0;

        return {
            totalCost,
            totalValue,
            totalPnl,
            pnlPercent,
            realizedPnl,
            realizedPnlPercent,
            unrealizedPnl,
            unrealizedPnlPercent,
            healthScore: avgIntegratedScore,
            avgDailyReturn: avgDailyReturn,
            stockCount: holdings.length,
            activeCount,
            closedCount,
        };
    }, [holdings, vcpData, stockInfoData, newsAnalysis, statusData]);

    const getHealthLabel = (score: number) => {
        if (score >= 80) return { label: 'EXCELLENT', color: 'text-green-600' };
        if (score >= 60) return { label: 'GOOD', color: 'text-bauhaus-blue' };
        if (score >= 40) return { label: 'FAIR', color: 'text-yellow-600' };
        return { label: 'POOR', color: 'text-bauhaus-red' };
    };

    const health = getHealthLabel(stats.healthScore);

    return (
        <div className="space-y-4 mb-8">
            {/* Main Stats Row */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">

                <div className="bg-white border-4 border-ink p-6 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
                    <div className="flex items-center gap-3 mb-2">
                        <Wallet className="text-bauhaus-blue" size={24} />
                        <span className="text-sm font-bold text-gray-600">TOTAL COST</span>
                    </div>
                    <div className="text-3xl font-black font-mono">
                        {Math.round(stats.totalCost).toLocaleString()}
                    </div>
                    <div className="text-sm text-gray-500">KRW</div>
                </div>

                <div className="bg-white border-4 border-ink p-6 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
                    <div className="flex items-center gap-3 mb-2">
                        <Activity className="text-bauhaus-yellow" size={24} />
                        <span className="text-sm font-bold text-gray-600">CURRENT VALUE</span>
                    </div>
                    <div className="text-3xl font-black font-mono">
                        {stats.totalValue > 0 ? Math.round(stats.totalValue).toLocaleString() : '-'}
                    </div>
                    <div className="text-sm text-gray-500">KRW ({stats.stockCount} stocks)</div>
                </div>

                <div className="bg-white border-4 border-ink p-6 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
                    <div className="flex items-center gap-3 mb-2">
                        {stats.totalPnl >= 0 ? (
                            <TrendingUp className="text-bauhaus-red" size={24} />
                        ) : (
                            <TrendingDown className="text-bauhaus-blue" size={24} />
                        )}
                        <span className="text-sm font-bold text-gray-600">TOTAL P&L</span>
                    </div>
                    <div
                        className={`text-3xl font-black font-mono ${stats.totalPnl >= 0 ? 'text-bauhaus-red' : 'text-bauhaus-blue'
                            }`}
                    >
                        {stats.totalPnl >= 0 ? '+' : ''}
                        {stats.pnlPercent.toFixed(2)}%
                    </div>
                    <div className={`text-sm ${stats.totalPnl >= 0 ? 'text-bauhaus-red' : 'text-bauhaus-blue'}`}>
                        {stats.totalPnl >= 0 ? '+' : ''}
                        {Math.round(stats.totalPnl).toLocaleString()} KRW
                    </div>
                </div>

                <div className="bg-white border-4 border-ink p-6 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] flex flex-col justify-between">
                    <div>
                        <div className="flex items-center gap-3 mb-2">
                            <div className="w-6 h-6 bg-ink rounded-full flex items-center justify-center text-white text-xs font-black">
                                Q
                            </div>
                            <span className="text-sm font-bold text-gray-600">AVG QUANT SCORE</span>
                            <div className="group relative">
                                <Info size={16} className="text-gray-400 cursor-help" />
                                <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-48 p-2 bg-ink text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-50 text-center">
                                    Portfolio Avg. Total Quant Score
                                    (Includes VCP + Supply + Sentiment)
                                </div>
                            </div>
                        </div>
                        <div className={`text-3xl font-black ${health.color}`}>
                            {stats.healthScore > 0 ? stats.healthScore : '-'}
                        </div>
                        <div className={`text-sm font-bold ${health.color}`}>{health.label}</div>
                    </div>
                    <div className="text-[10px] text-gray-400 mt-2 leading-tight">
                        * 보유 종목들의 Total Quant 점수 평균 (수익률 무관)
                    </div>
                </div>
            </div>

            {/* P&L Breakdown Row */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Unrealized P&L */}
                <div className="bg-white border-4 border-ink p-4 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
                    <div className="flex items-center gap-3 mb-3">
                        <Unlock className="text-bauhaus-yellow" size={20} />
                        <span className="text-sm font-bold text-gray-600">UNREALIZED P&L</span>
                        <span className="text-xs bg-bauhaus-yellow text-ink px-2 py-0.5 font-black">
                            {stats.activeCount} ACTIVE
                        </span>
                    </div>
                    <div className="flex items-baseline gap-4">
                        <div
                            className={`text-2xl font-black font-mono ${stats.unrealizedPnl >= 0 ? 'text-bauhaus-red' : 'text-bauhaus-blue'
                                }`}
                        >
                            {stats.unrealizedPnl >= 0 ? '+' : ''}
                            {stats.unrealizedPnlPercent.toFixed(2)}%
                        </div>
                        <div className={`text-sm font-mono ${stats.unrealizedPnl >= 0 ? 'text-bauhaus-red' : 'text-bauhaus-blue'}`}>
                            {stats.unrealizedPnl >= 0 ? '+' : ''}
                            {Math.round(stats.unrealizedPnl).toLocaleString()} KRW
                        </div>
                    </div>
                </div>

                {/* Realized P&L */}
                <div className="bg-white border-4 border-ink p-4 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
                    <div className="flex items-center gap-3 mb-3">
                        <Lock className="text-gray-600" size={20} />
                        <span className="text-sm font-bold text-gray-600">REALIZED P&L</span>
                        <span className="text-xs bg-gray-200 text-gray-700 px-2 py-0.5 font-black">
                            {stats.closedCount} CLOSED
                        </span>
                    </div>
                    <div className="flex items-baseline gap-4">
                        <div
                            className={`text-2xl font-black font-mono ${stats.realizedPnl >= 0 ? 'text-bauhaus-red' : 'text-bauhaus-blue'
                                }`}
                        >
                            {stats.realizedPnl >= 0 ? '+' : ''}
                            {stats.realizedPnlPercent.toFixed(2)}%
                        </div>
                        <div className={`text-sm font-mono ${stats.realizedPnl >= 0 ? 'text-bauhaus-red' : 'text-bauhaus-blue'}`}>
                            {stats.realizedPnl >= 0 ? '+' : ''}
                            {Math.round(stats.realizedPnl).toLocaleString()} KRW
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
