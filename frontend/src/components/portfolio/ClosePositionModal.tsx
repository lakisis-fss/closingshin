'use client';

import { useState, useEffect } from 'react';
import { X, Target, Save } from 'lucide-react';
import { PortfolioItem } from '@/lib/types';
import { usePortfolioStore } from '@/lib/portfolioStore';

interface ClosePositionModalProps {
    isOpen: boolean;
    onClose: () => void;
    item: (PortfolioItem & { currentPrice?: number, currentValue?: number, pnlPercent?: number }) | null;
}

export function ClosePositionModal({ isOpen, onClose, item }: ClosePositionModalProps) {
    const { updateStock } = usePortfolioStore();

    const [exitPrice, setExitPrice] = useState<number>(0);
    const [exitDate, setExitDate] = useState<string>('');
    const [exitMemo, setExitMemo] = useState<string>('수동 청산');
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [priceData, setPriceData] = useState<{ high: number | null, low: number | null, close: number | null } | null>(null);
    const [isLoadingPrice, setIsLoadingPrice] = useState(false);
    const [priceError, setPriceError] = useState<string | null>(null);

    useEffect(() => {
        if (item && isOpen) {
            setExitPrice(item.currentPrice || item.buyPrice);
            setExitDate(new Date().toISOString().split('T')[0]); // Default to today
            setExitMemo('수익 달성 / 수동 청산');
            setPriceData(null);
            setPriceError(null);
        }
    }, [item, isOpen]);

    // Fetch price data when date changes
    useEffect(() => {
        if (!item || !exitDate || !isOpen) return;

        const fetchPriceData = async () => {
            setIsLoadingPrice(true);
            try {
                const formattedDate = exitDate.replace(/-/g, '');
                const res = await fetch(`/api/stock-price/${item.ticker}?date=${formattedDate}`);
                if (res.ok) {
                    const data = await res.json();
                    setPriceData(data);
                }
            } catch (err) {
                console.error("Failed to fetch price data", err);
            } finally {
                setIsLoadingPrice(false);
            }
        };

        fetchPriceData();
    }, [item?.ticker, exitDate, isOpen]);

    // Validate exit price range
    useEffect(() => {
        if (priceData && exitPrice > 0) {
            if (priceData.high !== null && priceData.low !== null) {
                if (exitPrice > priceData.high || exitPrice < priceData.low) {
                    setPriceError(`청산가가 해당 날짜의 가격 범위 (${priceData.low.toLocaleString()} ~ ${priceData.high.toLocaleString()})를 벗어납니다.`);
                } else {
                    setPriceError(null);
                }
            } else {
                setPriceError(null);
            }
        } else {
            setPriceError(null);
        }
    }, [exitPrice, priceData]);

    if (!isOpen || !item) return null;

    const estimatedPnl = exitPrice > 0 ? ((exitPrice - item.buyPrice) / item.buyPrice) * 100 : 0;
    const realizedValue = exitPrice * item.quantity;
    const realizedProfit = realizedValue - (item.buyPrice * item.quantity);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsSubmitting(true);

        try {
            // Prepare the manual close simulation block
            const manualSimulation = {
                enabled: true,
                status: 'CLOSED' as const,
                exitDate: exitDate ? `${exitDate}T00:00:00.000Z` : new Date().toISOString(),
                exitPrice: Number(exitPrice),
                exitReason: `MANUAL_CLOSE (${exitMemo})`,
                realizedPnlPercent: estimatedPnl,
                realizedPnl: realizedProfit,
                lastUpdate: new Date().toISOString()
            };

            // Update store
            await updateStock(item.id, {
                simulation: manualSimulation
            });

            onClose();
        } catch (error) {
            console.error("Failed to close position", error);
            alert("청산 처리 중 오류가 발생했습니다.");
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <div
                className="absolute inset-0 bg-ink/50 backdrop-blur-sm"
                onClick={() => !isSubmitting && onClose()}
            ></div>

            <div className="bg-white border-4 border-ink shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] w-full max-w-lg relative z-10 flex flex-col max-h-[90vh]">
                {/* Header */}
                <div className="bg-bauhaus-yellow border-b-4 border-ink p-4 flex justify-between items-center shrink-0">
                    <div className="flex items-center gap-3">
                        <Target className="text-ink" size={24} />
                        <h2 className="text-xl font-black text-ink uppercase tracking-tight">
                            Manual Close: {item.name}
                        </h2>
                    </div>
                    <button
                        onClick={onClose}
                        disabled={isSubmitting}
                        className="p-1 hover:bg-ink hover:text-white transition-colors border-2 border-transparent disabled:opacity-50"
                    >
                        <X size={20} />
                    </button>
                </div>

                {/* Content */}
                <div className="p-6 overflow-y-auto">
                    <div className="mb-6 bg-gray-50 p-4 border-2 border-ink">
                        <div className="flex justify-between items-end">
                            <div>
                                <p className="text-xs font-bold text-gray-500 mb-1">BUY PRICE</p>
                                <p className="text-lg font-mono font-black">{item.buyPrice.toLocaleString()} 원</p>
                            </div>
                            <div className="text-right">
                                <p className="text-xs font-bold text-gray-500 mb-1">QUANTITY</p>
                                <p className="text-lg font-mono font-black">{item.quantity.toLocaleString()} 주</p>
                            </div>
                        </div>
                    </div>

                    <form onSubmit={handleSubmit} className="space-y-6">
                        <div>
                            <label className="block text-xs font-black text-ink mb-2">
                                EXIT PRICE (청산 체결가) <span className="text-bauhaus-red">*</span>
                            </label>
                            <div className="relative">
                                <input
                                    type="number"
                                    required
                                    min="0"
                                    step="1"
                                    value={exitPrice}
                                    onChange={(e) => setExitPrice(Math.round(Number(e.target.value)))}
                                    className={`w-full text-lg font-mono font-bold bg-white border-4 p-3 outline-none transition-colors ${priceError ? 'border-bauhaus-red bg-red-50' : 'border-ink focus:bg-gray-50'}`}
                                />
                                <div className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 font-bold">
                                    KRW
                                </div>
                            </div>
                            
                            {/* Price range info & validation error */}
                            <div className="mt-2 flex flex-col gap-1">
                                {isLoadingPrice ? (
                                    <p className="text-[10px] font-bold text-gray-400 animate-pulse">가격 데이터 확인 중...</p>
                                ) : priceData && priceData.high ? (
                                    <p className="text-[10px] font-bold text-gray-500">
                                        해당일 가격 범위: <span className="text-ink">{priceData.low?.toLocaleString()}</span> ~ <span className="text-ink">{priceData.high?.toLocaleString()}</span> KRW
                                    </p>
                                ) : (
                                    <p className="text-[10px] font-bold text-gray-400">데이터가 없는 경우 장중 고가/저가 기준으로 검증됩니다.</p>
                                )}
                                
                                {priceError && (
                                    <p className="text-xs font-black text-bauhaus-red bg-red-100 p-2 border-2 border-bauhaus-red animate-pulse">
                                        ⚠️ {priceError}
                                    </p>
                                )}
                            </div>
                        </div>

                        <div>
                            <label className="block text-xs font-black text-ink mb-2">
                                EXIT DATE (청산 일자) <span className="text-bauhaus-red">*</span>
                            </label>
                            <input
                                type="date"
                                required
                                value={exitDate}
                                onChange={(e) => setExitDate(e.target.value)}
                                className="w-full text-base font-bold bg-white border-4 border-ink p-3 outline-none focus:bg-gray-50 transition-colors"
                            />
                        </div>

                        <div>
                            <label className="block text-xs font-black text-ink mb-2">
                                MEMO / REASON (청산 사유)
                            </label>
                            <input
                                type="text"
                                value={exitMemo}
                                onChange={(e) => setExitMemo(e.target.value)}
                                placeholder="예: +50% 목표 수익 달성으로 전량 매도"
                                className="w-full text-sm font-bold bg-white border-4 border-ink p-3 outline-none focus:bg-gray-50 transition-colors"
                            />
                        </div>

                        {/* Summary Box */}
                        <div className={`p-4 border-4 border-ink ${estimatedPnl >= 0 ? 'bg-bauhaus-red/10' : 'bg-bauhaus-blue/10'}`}>
                            <div className="flex justify-between items-end mb-2">
                                <span className="text-xs font-black text-ink">Est. Return</span>
                                <span className={`text-2xl font-mono font-black ${estimatedPnl >= 0 ? 'text-bauhaus-red' : 'text-bauhaus-blue'}`}>
                                    {estimatedPnl >= 0 ? '+' : ''}{estimatedPnl.toFixed(2)}%
                                </span>
                            </div>
                            <div className="flex justify-between items-end">
                                <span className="text-xs font-black text-ink">Realized P&L</span>
                                <span className={`text-lg font-mono font-black ${realizedProfit >= 0 ? 'text-bauhaus-red' : 'text-bauhaus-blue'}`}>
                                    {realizedProfit >= 0 ? '+' : ''}{realizedProfit.toLocaleString()} 원
                                </span>
                            </div>
                        </div>

                        <button
                            type="submit"
                            disabled={isSubmitting || !!priceError || isLoadingPrice}
                            className="w-full bg-bauhaus-red hover:bg-red-700 text-white border-4 border-ink p-4 font-black uppercase text-lg tracking-widest transition-colors flex justify-center items-center gap-2 group disabled:opacity-50 disabled:cursor-not-allowed disabled:grayscale"
                        >
                            {isSubmitting ? (
                                'Processing...'
                            ) : (
                                <>
                                    <Save size={24} className="group-hover:scale-110 transition-transform" />
                                    Confirm Close Position
                                </>
                            )}
                        </button>
                    </form>
                </div>
            </div>
        </div>
    );
}
