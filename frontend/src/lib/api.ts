import { MarketStatus, VcpResult, NewsAnalysis, NewsItem, StockInfo, PortfolioItem } from "./types";
import { fetchFromPB, getFullListFromPB } from "./pocketbase";

export type { MarketStatus, VcpResult, NewsAnalysis, NewsItem, StockInfo, PortfolioItem };

// --- Market Status ---

export async function getLatestMarketStatus(): Promise<MarketStatus | null> {
    try {
        const data = await fetchFromPB("market_status", {
            sort: "-date",
            limit: 1,
            fields: "data,date"
        });
        if (!data.items || data.items.length === 0) return null;

        const item = data.items[0];
        return {
            ...(item.data as MarketStatus),
            timestamp: item.date // Use the record's main date as timestamp
        } as MarketStatus;
    } catch (e) {
        console.error("Failed to read market status from PB", e);
        return null;
    }
}

// --- VCP Results ---

export async function getVcpResults(): Promise<VcpResult[]> {
    try {
        // Fetch the latest scan date first
        const latestDate = await getVcpScanDate();
        if (!latestDate) return [];
        return await getVcpResultsByDate(latestDate);
    } catch (e) {
        console.error("Failed to read VCP results from PB", e);
        return [];
    }
}

/**
 * VCP 스캔 데이터가 존재하는 모든 날짜 목록을 가져옵니다.
 * getFullListFromPB를 사용하여 데이터 누락을 방지합니다.
 */
export async function getAvailableVcpDates(): Promise<string[]> {
    try {
        // vcp_reports는 종목당 1개 레코드이므로 대량 조회가 필요함
        // fields: "date"만 요청하여 성능 최적화
        const { items } = await getFullListFromPB("vcp_reports", {
            sort: "-date",
            fields: "date"
        });

        if (!items || items.length === 0) return [];

        const dates = items.map((item: any) => {
            const d = new Date(item.date);
            return d.getFullYear() + String(d.getMonth() + 1).padStart(2, '0') + String(d.getDate()).padStart(2, '0');
        });

        // 중복 제거 및 명시적 타입 지정 정렬
        return Array.from(new Set(dates)).sort((a: string, b: string) => b.localeCompare(a));
    } catch (e) {
        console.error("Failed to get VCP dates", e);
        return [];
    }
}

export async function getLatestTradingDayVcpDate(): Promise<string | null> {
    const dates = await getAvailableVcpDates();
    if (dates.length === 0) return null;

    for (const dateStr of dates) {
        const year = parseInt(dateStr.substring(0, 4));
        const month = parseInt(dateStr.substring(4, 6)) - 1;
        const day = parseInt(dateStr.substring(6, 8));
        const date = new Date(year, month, day);
        if (date.getDay() !== 0 && date.getDay() !== 6) return dateStr;
    }
    return dates[0];
}

export async function getVcpResultsByDate(dateStr: string): Promise<VcpResult[]> {
    try {
        const isoDateStart = `${dateStr.substring(0, 4)}-${dateStr.substring(4, 6)}-${dateStr.substring(6, 8)} 00:00:00.000Z`;
        const data = await fetchFromPB("vcp_reports", {
            filter: `date = "${isoDateStart}"`,
            sort: "-relative_strength",
            limit: 200, // Increase limit for candidate lists
            fields: "id,ticker,name,market,price,change_pct,vcp_score,jump_score,volume_dry_up,last_depth_pct,contractions_count,contractions_history,vol_ratio,relative_strength,pivot_point,pivot_distance_pct,note,consolidation_weeks,date,vcp_mode"
        });
        if (!data.items) return [];

        return data.items.map((item: any) => ({
            ...item,
            market: item.market || item.market_name || "UNKNOWN",
            history: Array.isArray(item.contractions_history) ? item.contractions_history : []
        } as unknown as VcpResult));
    } catch (e) {
        console.error(`Failed to read VCP results for ${dateStr}`, e);
        return [];
    }
}

/**
 * Fetch a single VCP result by ticker and date.
 * Crucial for the Stock Detail Page to avoid missing items due to list limits.
 */
export async function getVcpResultByTicker(ticker: string, dateStr: string): Promise<VcpResult | null> {
    try {
        const isoDateStart = `${dateStr.substring(0, 4)}-${dateStr.substring(4, 6)}-${dateStr.substring(6, 8)} 00:00:00.000Z`;
        const data = await fetchFromPB("vcp_reports", {
            filter: `ticker = "${ticker.padStart(6, '0')}" && date = "${isoDateStart}"`,
            limit: 1,
            fields: "id,ticker,name,market,price,change_pct,vcp_score,jump_score,volume_dry_up,last_depth_pct,contractions_count,contractions_history,vol_ratio,relative_strength,pivot_point,pivot_distance_pct,note,consolidation_weeks,date,vcp_mode"
        });

        if (!data.items || data.items.length === 0) return null;

        const item = data.items[0];
        return {
            ...item,
            market: item.market || item.market_name || "UNKNOWN",
            history: Array.isArray(item.contractions_history) ? item.contractions_history : []
        } as unknown as VcpResult;
    } catch (e) {
        console.error(`Failed to read VCP result for ${ticker} on ${dateStr}`, e);
        return null;
    }
}

export async function getVcpScanTime(): Promise<string | null> {
    try {
        const data = await fetchFromPB("vcp_reports", { sort: "-date", limit: 1 });
        if (!data.items || data.items.length === 0) return null;
        return data.items[0].updated;
    } catch (e) { return null; }
}

export async function getVcpScanDate(): Promise<string | null> {
    try {
        const data = await fetchFromPB("vcp_reports", { sort: "-date", limit: 1, fields: "date" });
        if (!data.items || data.items.length === 0) return null;
        const d = new Date(data.items[0].date);
        return d.getFullYear() + String(d.getMonth() + 1).padStart(2, '0') + String(d.getDate()).padStart(2, '0');
    } catch (e) { return null; }
}

// --- News Analysis ---

export async function getNewsAnalysis(targetStock: string): Promise<NewsAnalysis[]> {
    try {
        const data = await fetchFromPB("news_analysis", {
            filter: `target_stock = "${targetStock}"`,
            sort: "-date",
            limit: 50
        });
        return (data.items || []) as unknown as NewsAnalysis[];
    } catch (e) { return []; }
}

export async function getAllNewsAnalysis(): Promise<NewsAnalysis[]> {
    try {
        const latestDate = await getVcpScanDate();
        if (!latestDate) return [];
        return await getNewsAnalysisByDate(latestDate);
    } catch (e) { return []; }
}

export async function getNewsAnalysisByDate(dateStr: string): Promise<NewsAnalysis[]> {
    try {
        const formattedDate = `${dateStr.substring(0, 4)}-${dateStr.substring(4, 6)}-${dateStr.substring(6, 8)}`;
        const filter = `date ~ "${formattedDate}"`;
        const data = await fetchFromPB("news_analysis", {
            filter: filter,
            limit: 500
        });
        return (data.items || []) as unknown as NewsAnalysis[];
    } catch (e) { return []; }
}

// --- News Reports ---

export async function getNewsReport(ticker: string): Promise<NewsItem[]> {
    try {
        const data = await fetchFromPB("news_reports", {
            filter: `ticker = "${ticker.padStart(6, '0')}"`,
            sort: "-pub_date",
            limit: 50
        });
        return (data.items || []) as unknown as NewsItem[];
    } catch (e) { return []; }
}

export async function getAllNewsReports(): Promise<NewsItem[]> {
    try {
        const latestDate = await getVcpScanDate();
        if (!latestDate) return [];
        return await getNewsReportsByDate(latestDate);
    } catch (e) { return []; }
}

export async function getNewsReportsByDate(dateStr: string): Promise<NewsItem[]> {
    try {
        const formattedDate = `${dateStr.substring(0, 4)}-${dateStr.substring(4, 6)}-${dateStr.substring(6, 8)}`;
        const filter = `date ~ "${formattedDate}"`;
        const data = await fetchFromPB("news_reports", {
            filter: filter,
            limit: 500
        });
        return (data.items || []) as unknown as NewsItem[];
    } catch (e) { return []; }
}

// --- Stock Info ---

export async function getStockInfo(ticker: string): Promise<StockInfo | null> {
    try {
        const data = await fetchFromPB("stock_infos", {
            filter: `ticker = "${ticker.padStart(6, '0')}"`,
            sort: "-date",
            limit: 1
        });
        if (!data.items || data.items.length === 0) return null;

        const item = data.items[0];
        return {
            ...item,
            "기관_5일": item.inst_net_5d,
            "외인_5일": item.foreign_net_5d,
            "개인_5일": item.indiv_net_5d,
            "기관_15일": item.inst_net_15d,
            "외인_15일": item.foreign_net_15d,
            "개인_15일": item.indiv_net_15d,
            "기관_30일": item.inst_net_30d,
            "외인_30일": item.foreign_net_30d,
            "개인_30일": item.indiv_net_30d,
            "기관_50일": item.inst_net_50d,
            "외인_50일": item.foreign_net_50d,
            "개인_50일": item.indiv_net_50d,
            "기관_100일": item.inst_net_100d,
            "외인_100일": item.foreign_net_100d,
            "개인_100일": item.indiv_net_100d,
        } as unknown as StockInfo;
    } catch (e) { return null; }
}

export async function getAllStockInfo(): Promise<StockInfo[]> {
    try {
        const latestDate = await getVcpScanDate();
        if (!latestDate) return [];
        return await getStockInfoByDate(latestDate);
    } catch (e) { return []; }
}

export async function getStockInfoByDate(dateStr: string): Promise<StockInfo[]> {
    try {
        const isoDateStart = `${dateStr.substring(0, 4)}-${dateStr.substring(4, 6)}-${dateStr.substring(6, 8)} 00:00:00.000Z`;
        const data = await fetchFromPB("stock_infos", {
            filter: `date = "${isoDateStart}"`,
            limit: 300,
            fields: "ticker,name,market,sector,market_cap,price_change_pct,close,PER,PBR,EPS,BPS,DIV,DPS,inst_net_5d,foreign_net_5d,indiv_net_5d,inst_net_15d,foreign_net_15d,indiv_net_15d,inst_net_30d,foreign_net_30d,indiv_net_30d,inst_net_50d,foreign_net_50d,indiv_net_50d,inst_net_100d,foreign_net_100d,indiv_net_100d,supply_score,fundamental_score"
        });
        return (data.items || []).map((item: any) => ({
            ...item,
            "기관_5일": item.inst_net_5d,
            "외인_5일": item.foreign_net_5d,
            "개인_5일": item.indiv_net_5d,
            "기관_15일": item.inst_net_15d,
            "외인_15일": item.foreign_net_15d,
            "개인_15일": item.indiv_net_15d,
            "기관_30일": item.inst_net_30d,
            "외인_30일": item.foreign_net_30d,
            "개인_30일": item.indiv_net_30d,
            "기관_50일": item.inst_net_50d,
            "외인_50일": item.foreign_net_50d,
            "개인_50일": item.indiv_net_50d,
            "기관_100일": item.inst_net_100d,
            "외인_100일": item.foreign_net_100d,
            "개인_100일": item.indiv_net_100d,
        })) as StockInfo[];
    } catch (e) { return []; }
}

// --- Portfolio ---

export async function getPortfolioItems(): Promise<PortfolioItem[]> {
    try {
        const data = await fetchFromPB("portfolio", { limit: 200, sort: "-buyDate" });
        return (data.items || []) as unknown as PortfolioItem[];
    } catch (e) { return []; }
}
export async function getVcpChartUrl(ticker: string, dateStr: string): Promise<string | null> {
    try {
        const isoDate = `${dateStr.substring(0, 4)}-${dateStr.substring(4, 6)}-${dateStr.substring(6, 8)} 00:00:00.000Z`;
        const data = await fetchFromPB("vcp_charts", {
            filter: `date = "${isoDate}" && ticker = "${ticker}"`,
            limit: 1
        });

        if (data.items.length > 0) {
            const record = data.items[0];
            const PB_URL = process.env.NEXT_PUBLIC_PB_URL || "http://127.0.0.1:8090";
            return `${PB_URL}/api/files/vcp_charts/${record.id}/${record.file}`;
        }
        return null;
    } catch (e) {
        console.error("[API] getVcpChartUrl Error:", e);
        return null;
    }
}
