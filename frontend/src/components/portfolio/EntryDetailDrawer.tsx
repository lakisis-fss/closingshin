'use client';

import { useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, TrendingUp, BarChart2, Activity, Cpu } from 'lucide-react';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts';

interface EntryDetailDrawerProps {
    item: any | null; // The enriched portfolio item
    onClose: () => void;
}

export function EntryDetailDrawer({ item, onClose }: EntryDetailDrawerProps) {
    // Close on Escape key press
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if (e.key === 'Escape') onClose();
        };
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [onClose]);

    // Format data for Radar Chart
    const radarData = item ? [
        { subject: 'VCP', score: item.vcpScore || 0, fullMark: 100 },
        { subject: '수급(Supply)', score: item.supplyScore || 0, fullMark: 100 },
        { subject: '펀더멘털', score: item.fundamentalScore || 0, fullMark: 100 },
        { subject: 'AI 센티멘트', score: item.sentimentScore || 50, fullMark: 100 },
        // { subject: '통합(TQ)', score: item.integratedScore || 0, fullMark: 100 },
    ] : [];

    // Animation variants for the backdrop
    const backdropVariants = {
        hidden: { opacity: 0 },
        visible: { opacity: 1 }
    };

    // Animation variants for the drawer panel
    const drawerVariants = {
        hidden: { x: '100%', opacity: 0 },
        visible: { x: 0, opacity: 1, transition: { type: 'spring' as const, damping: 25, stiffness: 200 } }
    };

    // Date formatter
    const formatDate = (dateString: string) => {
        if (!dateString) return '-';
        const d = new Date(dateString);
        if (isNaN(d.getTime())) return dateString;
        return d.toLocaleDateString('ko-KR', { year: 'numeric', month: '2-digit', day: '2-digit' }).replace(/\./g, '/').replace(/\/ $/, '').replace(/\s/g, '');
    };

    const vcp = item?.vcp;
    const stockInfo = item?.stockInfo;

    return (
        <AnimatePresence>
            {item && (
                <>
                    {/* Backdrop */}
                    <motion.div
                        className="fixed inset-0 bg-black/40 z-40 backdrop-blur-sm"
                        variants={backdropVariants}
                        initial="hidden"
                        animate="visible"
                        exit="hidden"
                        onClick={onClose}
                    />

                    {/* Drawer Panel */}
                    <motion.div
                        className="fixed top-0 right-0 h-full w-full sm:w-[500px] md:w-[600px] bg-canvas border-l-4 border-ink shadow-[-8px_0px_0px_0px_rgba(0,0,0,1)] z-50 overflow-y-auto flex flex-col"
                        variants={drawerVariants}
                        initial="hidden"
                        animate="visible"
                        exit="hidden"
                    >
                        {/* Header */}
                        <div className="bg-ink text-white p-6 flex justify-between items-start sticky top-0 z-10">
                            <div>
                                <div className="flex items-center gap-3 space-y-1 mb-1">
                                    <span className="bg-white text-ink text-xs font-black px-2 py-0.5 font-mono">
                                        {item.ticker}
                                    </span>
                                    <h2 className="text-2xl font-black">{item.name}</h2>
                                </div>
                                <div className="text-sm text-gray-300 font-mono mt-2">
                                    진입일: {formatDate(item.buyDate || item.createdAt)}
                                </div>
                                <div className="text-sm font-bold text-bauhaus-yellow mt-2 flex items-center gap-1">
                                    TQ SCORE: {item.integratedScore}
                                    {item.vcp_mode && (
                                        <span className="ml-3 text-[10px] uppercase font-black px-2 py-0.5 border-2 border-bauhaus-yellow bg-ink text-bauhaus-yellow">
                                            MODE: {item.vcp_mode}
                                        </span>
                                    )}
                                </div>
                            </div>
                            <button
                                onClick={onClose}
                                className="p-2 hover:bg-white/20 transition-colors border-2 border-transparent hover:border-white group"
                            >
                                <X size={24} className="group-hover:rotate-90 transition-transform" />
                            </button>
                        </div>

                        {/* Content Area */}
                        <div className="p-6 flex-1 flex flex-col gap-6">

                            {/* Summary / Memo Area */}
                            {item.memo && (
                                <div className="bg-white border-2 border-ink shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] p-4">
                                    <p className="text-sm font-bold mb-2 uppercase text-gray-500 border-b-2 border-gray-200 pb-1">진입 당시 코멘트</p>
                                    <p className="text-ink font-semibold whitespace-pre-wrap">{item.memo}</p>
                                </div>
                            )}

                            {/* Radar Chart Area */}
                            <div className="bg-white border-2 border-ink shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] p-4">
                                <h3 className="text-lg font-black uppercase mb-4 text-center">진입 시점 분석 밸런스</h3>
                                <div className="h-[250px] w-full">
                                    <ResponsiveContainer width="100%" height="100%">
                                        <RadarChart cx="50%" cy="50%" outerRadius="70%" data={radarData}>
                                            <PolarGrid stroke="#e5e7eb" />
                                            <PolarAngleAxis dataKey="subject" tick={{ fill: '#4b5563', fontSize: 12, fontWeight: 700 }} />
                                            <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                                            <Radar
                                                name="Score"
                                                dataKey="score"
                                                stroke="#E32636" // bauhaus-red
                                                fill="#E32636"
                                                fillOpacity={0.4}
                                            />
                                        </RadarChart>
                                    </ResponsiveContainer>
                                </div>
                            </div>

                            {/* Bento Grid layout for specific metrics */}
                            <div className="grid grid-cols-2 gap-4">
                                {/* VCP Metrics */}
                                <div className="bg-white border-2 border-ink shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] p-4 flex flex-col justify-between">
                                    <div>
                                        <div className="flex items-center gap-2 text-bauhaus-blue mb-2">
                                            <Activity size={18} />
                                            <h4 className="font-black">VCP 패턴</h4>
                                        </div>
                                        <div className="text-3xl font-black">{item.vcpScore || '-'}</div>
                                    </div>
                                    <div className="mt-4 text-xs font-mono space-y-1 text-gray-600">
                                        <div className="flex justify-between">
                                            <span>수축 횟수:</span>
                                            <span className="font-bold text-ink">{vcp?.contractions_count || '-'} T</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span>마지막 깊이:</span>
                                            <span className="font-bold text-ink">{vcp?.last_depth_pct ? `${vcp.last_depth_pct.toFixed(2)}%` : '-'}</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span>거래량 고갈:</span>
                                            <span className="font-bold text-ink">{vcp?.volume_dry_up ? 'YES' : 'NO'}</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span>볼륨 비율:</span>
                                            <span className="font-bold text-ink">{vcp?.vol_ratio ? vcp.vol_ratio.toFixed(2) : '-'}</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span>피벗 이격도:</span>
                                            <span className="font-bold text-ink">{vcp?.pivot_distance_pct ? `${vcp.pivot_distance_pct.toFixed(2)}%` : '-'}</span>
                                        </div>
                                    </div>
                                </div>

                                {/* Supply/Demand Metrics */}
                                <div className="bg-white border-2 border-ink shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] p-4 flex flex-col justify-between">
                                    <div>
                                        <div className="flex items-center gap-2 text-bauhaus-yellow mb-2 text-ink">
                                            <TrendingUp size={18} />
                                            <h4 className="font-black">수급 동향</h4>
                                        </div>
                                        <div className="text-3xl font-black">{item.supplyScore || '-'}</div>
                                    </div>
                                    <div className="mt-4 text-xs font-mono space-y-1 text-gray-600">
                                        <div className="flex justify-between">
                                            <span>외인(15일):</span>
                                            <span className={`font-bold ${stockInfo?.외인_15일 > 0 ? 'text-bauhaus-red' : stockInfo?.외인_15일 < 0 ? 'text-bauhaus-blue' : 'text-ink'}`}>
                                                {stockInfo?.외인_15일 ? stockInfo.외인_15일.toLocaleString() : '-'}
                                            </span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span>기관(15일):</span>
                                            <span className={`font-bold ${stockInfo?.기관_15일 > 0 ? 'text-bauhaus-red' : stockInfo?.기관_15일 < 0 ? 'text-bauhaus-blue' : 'text-ink'}`}>
                                                {stockInfo?.기관_15일 ? stockInfo.기관_15일.toLocaleString() : '-'}
                                            </span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span>외인(5일):</span>
                                            <span className={`font-bold ${stockInfo?.외인_5일 > 0 ? 'text-bauhaus-red' : stockInfo?.외인_5일 < 0 ? 'text-bauhaus-blue' : 'text-ink'}`}>
                                                {stockInfo?.외인_5일 ? stockInfo.외인_5일.toLocaleString() : '-'}
                                            </span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span>기관(5일):</span>
                                            <span className={`font-bold ${stockInfo?.기관_5일 > 0 ? 'text-bauhaus-red' : stockInfo?.기관_5일 < 0 ? 'text-bauhaus-blue' : 'text-ink'}`}>
                                                {stockInfo?.기관_5일 ? stockInfo.기관_5일.toLocaleString() : '-'}
                                            </span>
                                        </div>
                                    </div>
                                </div>

                                {/* Fundamental Metrics */}
                                <div className="bg-white border-2 border-ink shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] p-4 flex flex-col justify-between">
                                    <div>
                                        <div className="flex items-center gap-2 text-orange-500 mb-2">
                                            <BarChart2 size={18} />
                                            <h4 className="font-black text-ink">펀더멘털</h4>
                                        </div>
                                        <div className="text-3xl font-black">{item.fundamentalScore || '-'}</div>
                                    </div>
                                    <div className="mt-4 text-xs font-mono space-y-1 text-gray-600">
                                        <div className="flex justify-between">
                                            <span>PER:</span>
                                            <span className="font-bold text-ink">{stockInfo?.PER || '-'}</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span>PBR:</span>
                                            <span className="font-bold text-ink">{stockInfo?.PBR || '-'}</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span>EPS:</span>
                                            <span className="font-bold text-ink">{stockInfo?.EPS ? stockInfo.EPS.toLocaleString() : '-'}</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span>BPS:</span>
                                            <span className="font-bold text-ink">{stockInfo?.BPS ? stockInfo.BPS.toLocaleString() : '-'}</span>
                                        </div>
                                    </div>
                                </div>

                                {/* AI Sentiment Metrics */}
                                <div className="bg-white border-2 border-ink shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] p-4 flex flex-col justify-between">
                                    <div>
                                        <div className="flex items-center gap-2 text-purple-600 mb-2">
                                            <Cpu size={18} />
                                            <h4 className="font-black text-ink">AI 센티멘트</h4>
                                        </div>
                                        <div className="text-3xl font-black text-ink">{item.sentimentScore || '50'}</div>
                                    </div>
                                    <div className="mt-4">
                                        <p className="text-xs text-gray-500 font-bold mb-1">최근 뉴스 모멘텀</p>
                                        <div className="text-xs text-ink leading-relaxed line-clamp-4">
                                            {/* We don't have direct news text passed in easily here unless we pass it, so we rely on scores or short description if available. */}
                                            {item.sentimentScore >= 70 ? '강세 모멘텀 포착. 외인 순매수 지속 또는 호재 뉴스가 유효함을 나타냅니다.' : item.sentimentScore <= 30 ? '약세 모멘텀. 최근 부정적 뉴스 또는 매도세가 관측되었습니다.' : '중립 모멘텀. 특이할 만한 부정/긍정 뉴스 시그널이 뚜렷하지 않습니다.'}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    );
}
