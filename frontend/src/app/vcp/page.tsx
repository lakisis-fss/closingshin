import { Header } from "@/components/layout/Header";
import {
    getLatestMarketStatus,
    getVcpResults,
    getAllNewsReports,
    getStockInfoByDate,
    getVcpScanTime,
    getVcpScanDate,
    getAllNewsAnalysis,
    getAvailableVcpDates,
    getLatestTradingDayVcpDate,
    getVcpResultsByDate
} from "@/lib/api";
import { VcpPageClient } from "./VcpPageClient";

// Force dynamic since data changes daily
export const dynamic = 'force-dynamic';

export default async function VcpPage() {
    // STAGE 1: Fetch independent data in parallel
    const [
        marketStatus,
        vcpScanDate,
        vcpLastScanned,
        newsAnalysis,
        allNewsReports,
        availableDates
    ] = await Promise.all([
        getLatestMarketStatus(),
        getLatestTradingDayVcpDate(),
        getVcpScanTime(),
        getAllNewsAnalysis(),
        getAllNewsReports(),
        getAvailableVcpDates()
    ]);

    // STAGE 2: Fetch data dependent on vcpScanDate in parallel
    const [vcpResults, stockInfos] = await Promise.all([
        vcpScanDate ? getVcpResultsByDate(vcpScanDate) : getVcpResults(),
        getStockInfoByDate(vcpScanDate || '')
    ]);

    // Map to simplified card props (Common Logic)
    const candidates = vcpResults.map((stock) => {
        // Use backend calculated scores
        const score = stock.vcp_score || 0;
        const ticker = String(stock.ticker).padStart(6, '0');
        const stockInfo = stockInfos.find(s => String(s.ticker).padStart(6, '0') === ticker);
        
        // vcp_reports.change_pct는 소수점 형태(0.0843)이므로 100을 곱해 % 단위로 변환
        // stock_infos.price_change_pct는 이미 % 단위(8.43)이므로 그대로 사용
        const priceChange = typeof stock.change_pct === 'number' 
            ? stock.change_pct * 100 
            : (stockInfo?.price_change_pct ?? 0);
            
        const changeStr = typeof priceChange === 'number' ? `${priceChange > 0 ? '+' : ''}${priceChange.toFixed(2)}%` : '0.00%';

        const tags = [];
        if (stock.volume_dry_up) tags.push("Vol Dry");
        if (stock.last_depth_pct < 5) tags.push("Super Tight");
        if (stock.contractions_count >= 4) tags.push(stock.contractions_count + "T");

        // Add Rocket icon for High Jump Score (> 80 arbitrary calculation reference)
        if (stock.jump_score && stock.jump_score >= 80) tags.push("🚀");

        return {
            code: ticker,
            name: stock.name,
            market: stock.market,
            price: stock.price ?? 0,
            change: changeStr,
            score: Math.round(score),
            tags: tags,
            jumpScore: stock.jump_score
        };
    });

    return (
        <main className="min-h-screen p-8 bg-canvas">
            <Header />
            <VcpPageClient
                initialCandidates={candidates}
                initialVcpResults={vcpResults}
                initialNewsAnalysis={newsAnalysis}
                initialNewsReports={allNewsReports}
                initialStockInfos={stockInfos}
                initialLastScanned={vcpLastScanned}
                initialScanDate={vcpScanDate}
                availableDates={availableDates}
                initialMarketStatus={marketStatus}
            />
        </main>
    );
}
