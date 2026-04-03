import { getVcpResults, getAllStockInfo, getAvailableVcpDates, getAllNewsAnalysis } from '@/lib/api';
import PortfolioPageClient from './PortfolioPageClient';

export const dynamic = 'force-dynamic';

export default async function PortfolioPage() {
    // Parallel fetch to eliminate 4-step sequential waterfall
    const [vcpResults, stockInfos, vcpDates, newsAnalysis] = await Promise.all([
        getVcpResults(),
        getAllStockInfo(),
        getAvailableVcpDates(),
        getAllNewsAnalysis()
    ]);

    return (
        <PortfolioPageClient
            vcpData={vcpResults}
            stockInfoData={stockInfos}
            availableVcpDates={vcpDates}
            newsAnalysis={newsAnalysis}
        />
    );
}
