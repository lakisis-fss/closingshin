export const dynamic = 'force-dynamic';

import { BentoGrid, BentoItem } from "@/components/dashboard/BentoGrid";
import { MetricCard } from "@/components/dashboard/MetricCard";
import { Card } from "@/components/ui/Card";
import { Header } from "@/components/layout/Header";
import { getLatestMarketStatus, getVcpResults } from "@/lib/api";
import { MarketMomentumChart } from "@/components/dashboard/MarketMomentumChart";

import { MarketStatusBar } from "@/components/dashboard/MarketStatusBar";

export default async function Home() {
  // Parallel fetch to reduce initial page load latency (Waterfall fix)
  const [data, vcpResults] = await Promise.all([
    getLatestMarketStatus(),
    getVcpResults()
  ]);

  // Fallback if no data
  if (!data) {
    return (
      <main className="min-h-screen p-8 bg-canvas text-center">
        <Header />
        <div className="text-2xl font-bold bg-bauhaus-yellow p-4 inline-block shadow-hard">
          SYSTEM OFFLINE: No Data Found
        </div>
        <p className="mt-4">Please run the Python collection scripts first.</p>
      </main>
    );
  }

  // Formatting Helpers
  const fmtChange = (pct: number | null | undefined = 0) => {
    if (pct === null || pct === undefined) return "0.00%";
    return `${pct > 0 ? "+" : ""}${pct.toFixed(2)}%`;
  };
  const getTrend = (pct: number | null | undefined = 0) => {
    if (pct === null || pct === undefined) return "neutral";
    return pct > 0 ? "up" : pct < 0 ? "down" : "neutral";
  };

  // Bilingual Label Helper
  const Label = ({ en, kr }: { en: string; kr: string }) => (
    <span className="flex items-baseline gap-2">
      <span>{en}</span>
      <span className="text-xs font-normal text-gray-400 font-sans tracking-normal">{kr}</span>
    </span>
  );

  // --- Calculations ---
  const kospiClose = data.KOSPI?.Close || data.KOSPI_Close || 0;
  const kospiChangePct = data.KOSPI?.Change_Pct || 0;

  const kosdaqClose = data.KOSDAQ?.Close || data.KOSDAQ_Close || 0;
  const kosdaqChangePct = data.KOSDAQ?.Change_Pct || 0;

  const us10y = data.US_10Y || (data as any).US10Y;
  const wti = data.WTI_OIL || (data as any).WTI;
  const sox = data.SOX || (data as any).PHLX_SOX;

  const isKospiNetBuy = (data.KOSPI_Net?.Foreigner || 0) > 0;

  return (
    <main className="min-h-screen p-8 bg-canvas">
      <Header />

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        {/* Status Bar - Extracted to Client Component for Interactivity */}
        <MarketStatusBar data={data} />
      </div>

      <BentoGrid>
        {/* Core Indices */}
        <BentoItem colSpan={1}>
          <MetricCard
            title={<Label en="KOSPI" kr="코스피" />}
            value={kospiClose.toLocaleString(undefined, { maximumFractionDigits: 2 })}
            trend={getTrend(kospiChangePct)}
            change={fmtChange(kospiChangePct)}
          />
        </BentoItem>
        <BentoItem colSpan={1}>
          <MetricCard
            title={<Label en="KOSDAQ" kr="코스닥" />}
            value={kosdaqClose.toLocaleString(undefined, { maximumFractionDigits: 2 })}
            trend={getTrend(kosdaqChangePct)}
            change={fmtChange(kosdaqChangePct)}
          />
        </BentoItem>
        <BentoItem colSpan={1}>
          <MetricCard
            title={<Label en="Foreign Net (KOSPI)" kr="외인 수급 (코스피)" />}
            value={data.KOSPI_Net?.Foreigner ? Math.round(data.KOSPI_Net.Foreigner / 100000000).toLocaleString() + "억" : "-"}
            trend={isKospiNetBuy ? "up" : "down"}
            className={isKospiNetBuy ? "bg-bauhaus-red/10 border-bauhaus-red" : "bg-bauhaus-blue/10 border-bauhaus-blue"}
          />
        </BentoItem>
        <BentoItem colSpan={1}>
          <div className="grid grid-rows-2 gap-2 h-full">
            {/* WTI */}
            <div className="bg-white border-[4px] border-ink p-3 flex justify-between items-center shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
              <div>
                <div className="text-xs font-black text-ink uppercase flex items-center gap-1 border-b border-ink">
                  WTI Crude <span className="font-normal text-[10px] text-gray-500 font-sans">국제유가</span>
                </div>
                <div className="font-black text-2xl">{(wti?.Close ?? 0).toFixed(2)}</div>
              </div>
              <span className={`text-lg font-black ${getTrend(wti?.Change_Pct) === 'up' ? 'text-bauhaus-red' : 'text-bauhaus-blue'}`}>
                {fmtChange(wti?.Change_Pct ?? 0)}
              </span>
            </div>
            {/* US 10Y */}
            <div className="bg-white border-[4px] border-ink p-3 flex justify-between items-center shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
              <div>
                <div className="text-xs font-black text-ink uppercase flex items-center gap-1 border-b border-ink">
                  US 10Y Bond <span className="font-normal text-[10px] text-gray-500 font-sans">미 국채 10년물</span>
                </div>
                <div className="font-black text-2xl">{(us10y?.Close ?? 0).toFixed(3)}%</div>
              </div>
              <span className={`text-lg font-black ${getTrend(us10y?.Change_Pct) === 'up' ? 'text-bauhaus-red' : 'text-bauhaus-blue'}`}>
                {fmtChange(us10y?.Change_Pct ?? 0)}
              </span>
            </div>
          </div>
        </BentoItem>



        {/* Big Chart Area */}
        <BentoItem colSpan={2} rowSpan={2}>
          <Card className="h-full flex flex-col p-4">
            <h3 className="text-2xl font-bold mb-4 flex items-center gap-2">
              MARKET MOMENTUM <span className="text-sm font-normal text-gray-400 font-sans">시장 모멘텀 (30일 추세)</span>
            </h3>
            <div className="flex-1 bg-white border border-ink p-2 shadow-inner">
              {data.History && data.History.length > 0 ? (
                <MarketMomentumChart data={data.History} />
              ) : (
                <div className="h-full flex items-center justify-center text-gray-400">
                  Loading Chart Data...
                </div>
              )}
            </div>
          </Card>
        </BentoItem>

        {/* AI Insight / SOX */}
        <BentoItem colSpan={1} rowSpan={2}>
          <div className="h-full flex flex-col gap-4">
            {/* SOX Index Mini Card - More Impactful */}
            <Card className="p-4 bg-bauhaus-blue text-white border-ink shadow-[6px_6px_0px_0px_rgba(0,0,0,1)]">
              <div className="flex justify-between items-baseline border-b border-white/30 pb-1">
                <span className="text-xs font-black text-white flex items-center gap-2">
                  PHLX SOX <span className="text-[10px] font-normal font-sans opacity-70">필라델피아 반도체</span>
                </span>
                <span className="font-black text-2xl text-bauhaus-yellow">
                  {fmtChange(sox?.Change_Pct ?? 0)}
                </span>
              </div>
              <div className="font-black text-4xl mt-2 italic tracking-tighter">{(sox?.Close ?? 0).toLocaleString()}</div>
            </Card>

            <Card className="flex-1 bg-bauhaus-yellow border-ink shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] text-ink p-5 flex flex-col">
              <h3 className="text-xl font-black mb-3 uppercase border-b-4 border-ink pb-2 flex items-center justify-between">
                <span>AI Insight</span>
                <span className="text-xs font-normal opacity-60 font-sans border border-ink px-2 bg-white">REASONING</span>
              </h3>
              <p className="font-black text-lg leading-tight flex-1 italic">
                {data.AI_Insight ? (
                  `"${data.AI_Insight.summary} ${data.AI_Insight.reasoning}"`
                ) : (
                  <span className="text-gray-500 italic">"AI 데이터 분석 대기중..."</span>
                )}
              </p>
            </Card>
          </div>
        </BentoItem>
      </BentoGrid>

      {/* Sector Bar */}
      {data.Sectors && (
        <div className="mt-8">
          <h3 className="text-xl font-bold mb-4 uppercase flex items-center gap-2">
            Sector Heatmap <span className="text-sm font-normal text-gray-400 font-sans">섹터별 등락</span>
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(data.Sectors).map(([name, sec]: [string, any]) => (
              <Card key={name} className={`p-3 border-l-4 ${sec.Change_Pct > 0 ? "border-l-bauhaus-red" : "border-l-bauhaus-blue"}`}>
                <div className="flex justify-between items-center mb-1">
                  <span className="font-bold text-sm uppercase">{name}</span>
                  <span className={`font-mono font-bold text-xs ${(sec.Change_Pct ?? 0) > 0 ? "text-bauhaus-red" : "text-bauhaus-blue"}`}>
                    {fmtChange(sec.Change_Pct ?? 0)}
                  </span>
                </div>
                <div className="text-xl font-mono">{(sec.Close ?? 0).toLocaleString()}</div>
              </Card>
            ))}
          </div>
        </div>
      )}

    </main>
  );
}
