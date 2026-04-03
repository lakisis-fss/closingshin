import { BentoGrid, BentoItem } from "@/components/dashboard/BentoGrid";
import { Header } from "@/components/layout/Header";
import { Card } from "@/components/ui/Card";
import { cn } from "@/lib/utils";
import { 
    getVcpResultByTicker, 
    getNewsAnalysis, 
    getNewsReport, 
    getStockInfo, 
    getVcpScanDate, 
    getVcpChartUrl 
} from "@/lib/api";
import { FundamentalCard } from "@/components/stock/FundamentalCard";
import { SupplyDemandChart } from "@/components/stock/SupplyDemandChart";

// Force dynamic since data changes daily
export const dynamic = 'force-dynamic';

export default async function StockDetailPage({
    params,
}: {
    params: Promise<{ code: string }>;
}) {
    const { code } = await params;
    const ticker = code.padStart(6, '0');

    // 1. Get latest scan date first
    const latestDate = await getVcpScanDate();
    
    if (!latestDate) {
        return (
            <main className="min-h-screen p-8 bg-canvas text-center">
                <Header />
                <div className="text-xl font-bold mt-10 p-8 border-2 border-dashed border-ink inline-block">
                    NO SCAN DATA AVAILABLE
                </div>
            </main>
        );
    }

    // 2. Fetch all required data in parallel for high performance
    const [stock, stockInfo, newsAnalysis, newsReport, chartUrl] = await Promise.all([
        getVcpResultByTicker(ticker, latestDate),
        getStockInfo(ticker),
        getNewsAnalysis(""), // We will filter by stock.name after fetching stock
        getNewsReport(ticker),
        getVcpChartUrl(ticker, latestDate)
    ]);

    // Handle case where stock is not in candidates
    if (!stock) {
        return (
            <main className="min-h-screen p-8 bg-canvas text-center">
                <Header />
                <div className="text-xl font-bold mt-10 p-8 border-2 border-dashed border-ink inline-block uppercase">
                    Stock Not Found in Candidates<br />
                    <span className="text-bauhaus-red font-mono">{ticker}</span>
                    <p className="text-sm font-bold text-gray-400 mt-4 normal-case">
                        최근 VCP 스캔 결과({latestDate})에 포함되지 않은 종목입니다.
                    </p>
                </div>
            </main>
        );
    }

    // Secondary fetch for news analysis because it needs stock.name (usually very fast after Stage 1)
    const specificNewsAnalysis = await getNewsAnalysis(stock.name);
    const latestAnalysis = specificNewsAnalysis.length > 0 ? specificNewsAnalysis[0] : null;

    return (
        <main className="min-h-screen p-8 bg-canvas">
            <Header />

            <div className="mb-8 flex items-end gap-4">
                <h2 className="text-5xl font-black uppercase tracking-tighter">
                    {stock.name}
                </h2>
                <span className="text-2xl font-mono text-gray-400 font-bold mb-2">
                    {ticker}
                </span>
                <div className="ml-auto flex items-end gap-4">
                    <span className="text-4xl font-mono font-bold">
                        {(stock.close ?? stock.price).toLocaleString()}
                    </span>
                    <span className="text-xl font-bold bg-white px-2 border-2 border-ink">
                        {stock.contractions_count}T
                    </span>
                </div>
            </div>

            <BentoGrid>
                {/* Chart Area (2x2) */}
                <BentoItem colSpan={2} rowSpan={2}>
                    <Card className="h-full min-h-[400px] flex flex-col p-0 overflow-hidden border-4 border-ink shadow-hard">
                        <div className="bg-ink text-white px-4 py-2 font-bold uppercase flex justify-between items-center">
                            <span>VCP Analysis Chart</span>
                            <span className="text-[10px] bg-bauhaus-yellow text-ink px-2 py-0.5 rounded-sm">DATE: {latestDate}</span>
                        </div>
                        <div className="flex-1 bg-white flex items-center justify-center relative bg-[url('/grid.png')] bg-repeat">
                            {chartUrl ? (
                                <img 
                                    src={chartUrl} 
                                    alt={`${stock.name} VCP Chart`} 
                                    className="w-full h-full object-contain p-2 hover:scale-[1.02] transition-transform duration-500"
                                />
                            ) : (
                                <div className="text-center">
                                    <div className="mb-4 opacity-20 transform -rotate-12">
                                        <svg width="120" height="120" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round">
                                            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                                            <circle cx="8.5" cy="8.5" r="1.5"/>
                                            <polyline points="21 15 16 10 5 21"/>
                                        </svg>
                                    </div>
                                    <p className="font-mono text-gray-400 font-bold">
                                        NO ANALYSIS CHART GENERATED<br />
                                        <span className="text-xs">스케줄러에서 차트 생성을 대기 중입니다.</span>
                                    </p>
                                </div>
                            )}
                        </div>
                    </Card>
                </BentoItem>

                {/* AI Analysis (1x1) */}
                <BentoItem colSpan={1} rowSpan={1}>
                    <Card className="h-full bg-bauhaus-blue text-white border-none shadow-hard relative overflow-hidden flex flex-col justify-center min-h-[250px]">
                        <h3 className="text-lg font-black uppercase mb-4 opacity-80 border-b border-white/20 pb-2">AI Sentiment</h3>

                        {latestAnalysis ? (
                            <>
                                <div className="flex items-center gap-4 mb-4">
                                    <div className="text-6xl font-black">{latestAnalysis.sentiment_score ? (latestAnalysis.sentiment_score * 100).toFixed(0) : "N/A"}</div>
                                    <div className="text-sm font-bold uppercase leading-tight bg-white text-bauhaus-blue px-2 py-1">
                                        {latestAnalysis.sentiment_label || "NEUTRAL"}
                                    </div>
                                </div>
                                <p className="font-bold opacity-100 leading-snug text-lg line-clamp-4 italic">
                                    "{latestAnalysis.reason}"
                                </p>
                            </>
                        ) : (
                            <div className="text-center opacity-70 font-bold">
                                해당 종목의 AI 분석 리포트가 없습니다.
                            </div>
                        )}

                        <div className="absolute -bottom-4 -right-4 w-24 h-24 bg-bauhaus-yellow rounded-full opacity-20" />
                    </Card>
                </BentoItem>

                {/* News List (1x1) */}
                <BentoItem colSpan={1} rowSpan={1}>
                    <Card className="h-full flex flex-col min-h-[250px] overflow-hidden">
                        <h3 className="text-lg font-black uppercase text-ink mb-2 px-1 border-b-4 border-bauhaus-yellow pb-1">Latest News</h3>
                        <div className="flex-1 overflow-y-auto pr-1 space-y-2 custom-scrollbar">
                            {newsReport.length > 0 ? (
                                newsReport.map((news, i) => (
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
                                                    "flex items-center justify-center min-w-[30px] h-[20px] text-[10px] font-bold border border-ink shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]",
                                                    news.score >= 0.7 ? "bg-bauhaus-red text-white" : "bg-bauhaus-yellow text-ink"
                                                )}>
                                                    {news.score}
                                                </span>
                                            )}
                                        </div>
                                    </a>
                                ))
                            ) : (
                                <div className="text-center text-gray-400 text-sm py-8 font-bold">
                                    최근 뉴스가 존재하지 않습니다.
                                </div>
                            )}
                        </div>
                    </Card>
                </BentoItem>

                {/* Supply Trend (2x1) */}
                <BentoItem colSpan={2} rowSpan={1}>
                    {stockInfo ? (
                        <SupplyDemandChart info={stockInfo} />
                    ) : (
                        <Card className="h-full flex items-center justify-center text-gray-400 border-2 border-dashed border-gray-200">
                           <p className="font-bold uppercase tracking-widest">No Supply Data Available</p>
                        </Card>
                    )}
                </BentoItem>

                {/* Fundamentals (1x1) */}
                <BentoItem colSpan={1} rowSpan={1}>
                    {stockInfo ? (
                        <FundamentalCard info={stockInfo} />
                    ) : (
                        <Card className="h-full flex items-center justify-center text-gray-400 border-2 border-dashed border-gray-200">
                            <p className="font-bold uppercase tracking-widest">No Fundamental Data</p>
                        </Card>
                    )}
                </BentoItem>

                {/* VCP Metrics (3x1) - Bottom Detail Panel */}
                <BentoItem colSpan={3} rowSpan={1}>
                    <Card className="h-full flex flex-col justify-center bg-gray-50 border-4 border-ink shadow-hard">
                        <div className="flex flex-col md:flex-row items-center gap-8 px-8 py-6">
                            <div className="flex items-center gap-3 w-48">
                                <span className="w-4 h-4 bg-bauhaus-red rounded-full" />
                                <h3 className="text-2xl font-black uppercase text-ink">VCP Metrics</h3>
                            </div>

                            <div className="flex-1 w-full grid grid-cols-2 md:grid-cols-4 gap-8">
                                <div className="flex flex-col border-l-4 border-bauhaus-yellow pl-4">
                                    <span className="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">Contractions</span>
                                    <span className="font-black text-3xl text-ink">{stock.contractions_count}<span className="text-sm ml-1 opacity-50">WAVES</span></span>
                                </div>
                                <div className="flex flex-col border-l-4 border-bauhaus-blue pl-4">
                                    <span className="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">Last Depth</span>
                                    <span className="font-black text-3xl text-ink">{(stock.last_depth_pct).toFixed(1)}<span className="text-sm ml-1 opacity-50">%</span></span>
                                </div>
                                <div className="flex flex-col border-l-4 border-bauhaus-red pl-4">
                                    <span className="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">Volume Status</span>
                                    <span className={cn("font-black text-3xl uppercase", stock.volume_dry_up ? "text-bauhaus-red" : "text-gray-400")}>
                                        {stock.volume_dry_up ? "Dry Up" : "Normal"}
                                    </span>
                                </div>
                                <div className="flex flex-col border-l-4 border-ink pl-4">
                                    <span className="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">Volatility Ratio</span>
                                    <span className="font-black text-3xl text-ink">{stock.vol_ratio?.toFixed(2) || "N/A"}</span>
                                </div>
                            </div>
                        </div>
                    </Card>
                </BentoItem>
            </BentoGrid>
        </main>
    );
}
