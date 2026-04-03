'use client';

import { useState, useEffect, useCallback } from 'react';
import { VcpDashboard } from '@/components/vcp/VcpDashboard';
import { VcpResult, NewsAnalysis, NewsItem, StockInfo, MarketStatus } from '@/lib/types';

interface VcpPageClientProps {
    initialCandidates: any[];
    initialVcpResults: VcpResult[];
    initialNewsAnalysis: NewsAnalysis[];
    initialNewsReports: NewsItem[];
    initialStockInfos: StockInfo[];
    initialLastScanned: string | null;
    initialScanDate: string | null;
    availableDates: string[];
    initialMarketStatus: MarketStatus | null;
}

export function VcpPageClient({
    initialCandidates,
    initialVcpResults,
    initialNewsAnalysis,
    initialNewsReports,
    initialStockInfos,
    initialLastScanned,
    initialScanDate,
    availableDates: initialAvailableDates,
    initialMarketStatus,
}: VcpPageClientProps) {
    const [selectedDate, setSelectedDate] = useState<string>(initialScanDate || initialAvailableDates[0] || '');
    const [candidates, setCandidates] = useState(initialCandidates);
    const [vcpResults, setVcpResults] = useState(initialVcpResults);
    const [newsAnalysis, setNewsAnalysis] = useState(initialNewsAnalysis);
    const [newsReports, setNewsReports] = useState(initialNewsReports);
    const [stockInfos, setStockInfos] = useState(initialStockInfos);
    const [lastScanned, setLastScanned] = useState(initialLastScanned);
    const [scanDate, setScanDate] = useState(initialScanDate);
    const [availableDates, setAvailableDates] = useState<string[]>(initialAvailableDates);
    const [marketStatus, setMarketStatus] = useState<MarketStatus | null>(initialMarketStatus);
    const [isLoading, setIsLoading] = useState(false);

    const handleDateChange = useCallback(async (date: string, force: boolean = false) => {
        if (!force && date === selectedDate) return;

        setIsLoading(true);
        setSelectedDate(date);

        try {
            // If forced refresh (scan complete), update available dates
            if (force) {
                const datesRes = await fetch('/api/system/available-dates?t=' + Date.now());
                if (datesRes.ok) {
                    const newDates = await datesRes.json();
                    setAvailableDates(newDates);
                }
            }

            const fetchTime = Date.now();
            
            // 1단계: 병렬 네트워크 요청 (트럭 6대 동시 출발)
            const [
                vcpRes,
                newsAnalysisRes,
                stockInfoRes,
                newsReportsRes,
                chartsRes,
                marketStatusRes
            ] = await Promise.all([
                fetch(`/api/vcp/${date}?t=${fetchTime}`, { cache: 'no-store' }),
                fetch(`/api/news-analysis/${date}?t=${fetchTime}`, { cache: 'no-store' }),
                fetch(`/api/stock-info/${date}?t=${fetchTime}`, { cache: 'no-store' }),
                fetch(`/api/news-reports/${date}?t=${fetchTime}`, { cache: 'no-store' }),
                fetch(`/api/charts/${date}/list?t=${fetchTime}`, { cache: 'no-store' }),
                fetch(`/api/market-status?t=${fetchTime}`, { cache: 'no-store' })
            ]);

            // 2단계: 병렬 JSON 파싱 (동시 하차 및 정리)
            const [
                vcpData,
                newsAnalysisData,
                stockInfoData,
                newsReportsData,
                chartsMap,
                marketStatusData
            ] = await Promise.all([
                vcpRes.ok ? vcpRes.json() : Promise.resolve([]),
                newsAnalysisRes.ok ? newsAnalysisRes.json() : Promise.resolve([]),
                stockInfoRes.ok ? stockInfoRes.json() : Promise.resolve(initialStockInfos),
                newsReportsRes.ok ? newsReportsRes.json() : Promise.resolve([]),
                chartsRes.ok ? chartsRes.json() : Promise.resolve({}),
                marketStatusRes.ok ? marketStatusRes.json() : Promise.resolve(null)
            ]) as [
                VcpResult[],
                NewsAnalysis[],
                StockInfo[],
                NewsItem[],
                Record<string, string>,
                MarketStatus | null
            ];

            if (marketStatusData) {
                setMarketStatus(marketStatusData);
            }

            // Map to candidates
            const newCandidates = vcpData.map((stock) => {
                const score = stock.vcp_score || 0;
                const ticker = String(stock.ticker).padStart(6, '0');
                const stockInfo = stockInfoData.find(s => String(s.ticker).padStart(6, '0') === ticker);
                
                // Handle unit conversion for vcp_reports.change_pct (fraction -> %)
                const priceChange = typeof stock.change_pct === 'number' 
                    ? stock.change_pct * 100 
                    : (stockInfo?.price_change_pct ?? 0);
                
                const changeStr = typeof priceChange === 'number' 
                    ? `${priceChange > 0 ? '+' : ''}${priceChange.toFixed(2)}%` 
                    : '0.00%';

                const tags = [];
                if (stock.volume_dry_up) tags.push("Vol Dry");
                if (stock.last_depth_pct < 5) tags.push("Super Tight");
                if (stock.contractions_count >= 4) tags.push(stock.contractions_count + "T");
                if (stock.jump_score && stock.jump_score >= 80) tags.push("🚀");

                return {
                    code: ticker,
                    name: stock.name,
                    market: (stock as any).market || (stock as any).market_name || "UNKNOWN",
                    price: stock.price ?? 0,
                    change: changeStr,
                    score: Math.round(score),
                    tags: tags,
                    jumpScore: stock.jump_score,
                    chartUrl: chartsMap[ticker] || null
                };
            });

            setCandidates(newCandidates);
            setVcpResults(vcpData);
            setNewsAnalysis(newsAnalysisData);
            setNewsReports(newsReportsData);
            setStockInfos(stockInfoData);
            setScanDate(date);

        } catch (error) {
            console.error('Failed to fetch data for date:', date, error);
        } finally {
            setIsLoading(false);
        }
    }, [selectedDate, initialStockInfos]);

    return (
        <div className="relative">
            {isLoading && (
                <div className="absolute inset-0 bg-white/80 z-50 flex items-center justify-center">
                    <div className="flex items-center gap-3 px-6 py-3 bg-ink text-white font-black uppercase">
                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                        Loading...
                    </div>
                </div>
            )}
            <VcpDashboard
                candidates={candidates}
                vcpResults={vcpResults}
                newsAnalysis={newsAnalysis}
                newsReports={newsReports}
                stockInfos={stockInfos}
                lastScanned={lastScanned}
                scanDate={scanDate}
                availableDates={availableDates}
                selectedDate={selectedDate}
                onDateChange={handleDateChange}
                onScanComplete={() => handleDateChange(selectedDate, true)}
                marketStatus={marketStatus}
            />
        </div>
    );
}
