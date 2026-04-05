'use client';

import { useState, useEffect, useCallback } from 'react';
import { Plus, Download, FileSpreadsheet } from 'lucide-react';
import Papa from 'papaparse';
import * as XLSX from 'xlsx';
import { Header } from '@/components/layout/Header';
import { PortfolioDashboard, HoldingsTable, AddStockModal, EntryDetailDrawer, ClosePositionModal } from '@/components/portfolio';
import { usePortfolioStore } from '@/lib/portfolioStore';
import { isMarketOpen } from '@/lib/utils';
import { PortfolioItem, VcpResult, StockInfo, NewsAnalysis } from '@/lib/types';

interface PortfolioPageClientProps {
    vcpData: VcpResult[];
    stockInfoData: StockInfo[];
    availableVcpDates: string[];
    newsAnalysis: NewsAnalysis[];
}

async function fetchVcpByDate(date: string): Promise<VcpResult[]> {
    const res = await fetch(`/api/vcp/${date}`);
    if (!res.ok) return [];
    return res.json();
}

async function fetchNewsAnalysisByDate(date: string): Promise<NewsAnalysis[]> {
    const res = await fetch(`/api/news-analysis/${date}`);
    if (!res.ok) return [];
    return res.json();
}

async function fetchStockInfoByDate(date: string): Promise<StockInfo[]> {
    const res = await fetch(`/api/stock-info/${date}`);
    if (!res.ok) return [];
    return res.json();
}

export default function PortfolioPageClient({ vcpData, stockInfoData, availableVcpDates, newsAnalysis }: PortfolioPageClientProps) {
    const { portfolio, isLoading, fetchPortfolio, removeStock } = usePortfolioStore();
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [editingItem, setEditingItem] = useState<PortfolioItem | null>(null);
    const [isCloseModalOpen, setIsCloseModalOpen] = useState(false);
    const [selectedItemForClose, setSelectedItemForClose] = useState<any | null>(null);
    const [mounted, setMounted] = useState(false);
    const [isUpdating, setIsUpdating] = useState(false);
    const [statusData, setStatusData] = useState<any>(null);
    const [selectedDrawerItem, setSelectedDrawerItem] = useState<any>(null);

    useEffect(() => {
        setMounted(true);
        fetchPortfolio();
        fetchStatusData();
    }, []);

    const fetchStatusData = async () => {
        try {
            const res = await fetch('/api/portfolio/status');
            if (res.ok) {
                const data = await res.json();
                setStatusData(data);
            }
        } catch (error) {
            console.error('Failed to fetch status data:', error);
        }
    };

    const handleEdit = (item: PortfolioItem) => {
        setEditingItem(item);
        setIsModalOpen(true);
    };

    const handleCloseModal = () => {
        setIsModalOpen(false);
        setEditingItem(null);
    };

    const handleClosePosition = (item: PortfolioItem) => {
        setSelectedItemForClose(item);
        setIsCloseModalOpen(true);
    };

    const handleClosePositionModalClose = () => {
        setIsCloseModalOpen(false);
        setSelectedItemForClose(null);
        fetchPortfolio(); // Refresh the portfolio after closing
    };

    const handleRemove = async (id: string) => {
        if (confirm('Are you sure you want to remove this stock from your portfolio?')) {
            await removeStock(id);
        }
    };

    const handleFetchVcpByDate = useCallback(async (date: string): Promise<VcpResult[]> => {
        return fetchVcpByDate(date);
    }, []);

    const handleFetchNewsAnalysisByDate = useCallback(async (date: string): Promise<NewsAnalysis[]> => {
        return fetchNewsAnalysisByDate(date);
    }, []);
    
    const handleFetchMarketStatusByDate = useCallback(async (date: string): Promise<any> => {
        const res = await fetch(`/api/market-status?date=${date}`);
        if (!res.ok) return null;
        return res.json();
    }, []);

    const handleFetchStockInfoByDate = useCallback(async (date: string): Promise<StockInfo[]> => {
        return fetchStockInfoByDate(date);
    }, []);

    const getExportData = () => {
        return portfolio.map(item => {
            const normalizedTicker = String(item.ticker).padStart(6, '0');
            const vcp = vcpData.find(v => String(v.ticker).padStart(6, '0') === normalizedTicker);
            const stockInfo = stockInfoData.find(s => String(s.ticker).padStart(6, '0') === normalizedTicker);

            let currentPrice = 0;
            const marketOpen = isMarketOpen();
            const closePrice = vcp?.close || stockInfo?.close || 0;

            let statusPrice = 0;
            if (statusData?.items) {
                const statusItem = statusData.items.find((s: any) => String(s.ticker).padStart(6, '0') === normalizedTicker);
                if (statusItem && statusItem.currentPrice > 0) statusPrice = statusItem.currentPrice;
            }

            // Market-based logic:
            if (statusPrice > 0) {
                currentPrice = statusPrice;
            } else {
                currentPrice = closePrice || 0;
            }

            const isClosed = item.simulation?.status === 'CLOSED';
            const displayPrice = isClosed ? (item.simulation?.exitPrice || 0) : (currentPrice || 0);

            const totalCost = item.buyPrice * item.quantity;
            const currentValue = displayPrice * item.quantity;
            const pnl = isClosed ? (item.simulation?.realizedPnl || 0) : (currentValue - totalCost);
            const pnlPercent = isClosed ? (item.simulation?.realizedPnlPercent || 0) : (totalCost > 0 ? (pnl / totalCost) * 100 : 0);

            return {
                'Ticker': item.ticker,
                'Name': item.name,
                'Market': item.market,
                'Status': isClosed ? 'CLOSED' : 'ACTIVE',
                'Quantity': item.quantity,
                'Buy Date': item.buyDate,
                'Buy Price': item.buyPrice,
                'Total Cost': totalCost,
                'Current/Exit Price': displayPrice,
                'Current/Exit Value': currentValue,
                'P&L': Math.round(pnl),
                'P&L %': pnlPercent.toFixed(2) + '%',
                'Exit Reason': item.simulation?.exitReason || '',
                'TQ Score': item.initialScores?.totalScore || '',
                'VCP Mode': item.vcp_mode || '',
                'Memo': item.memo || ''
            };
        });
    };

    const handleExportCSV = () => {
        if (!portfolio || portfolio.length === 0) {
            alert('보유 종목이 없습니다.');
            return;
        }

        const exportData = getExportData();
        const csv = Papa.unparse(exportData);
        // UTF-8 BOM for Excel compatibility in Korean
        const blob = new Blob(["\ufeff" + csv], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);

        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `closingshin_portfolio_${new Date().toISOString().split('T')[0]}.csv`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    const handleExportXLSX = () => {
        if (!portfolio || portfolio.length === 0) {
            alert('보유 종목이 없습니다.');
            return;
        }

        const exportData = getExportData();
        const worksheet = XLSX.utils.json_to_sheet(exportData);
        const workbook = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(workbook, worksheet, "Portfolio");

        // Fit column width
        const wscols = Object.keys(exportData[0]).map(k => ({ wch: Math.max(k.length * 1.5, 12) }));
        worksheet['!cols'] = wscols;

        XLSX.writeFile(workbook, `closingshin_portfolio_${new Date().toISOString().split('T')[0]}.xlsx`);
    };

    const handleSyncData = async () => {
        if (isUpdating) return;

        setIsUpdating(true);
        try {
            const res = await fetch('/api/system/run-collection', { method: 'POST' });
            if (!res.ok) throw new Error('Failed to sync data');

            const result = await res.json();
            console.log(result);

            alert('Data sync completed successfully! Page will reload.');
            window.location.reload();
        } catch (error) {
            console.error(error);
            alert('Failed to sync data. Check console for details.');
        } finally {
            setIsUpdating(false);
        }
    };

    if (!mounted) {
        return (
            <main className="min-h-screen p-8 bg-canvas">
                <Header />
                <div className="flex items-center justify-center h-64">
                    <div className="text-lg font-bold text-gray-500">Loading portfolio...</div>
                </div>
            </main>
        );
    }

    return (
        <main className="min-h-screen p-8 bg-canvas">
            <Header />

            <div className="flex items-center justify-between mb-8">
                <div>
                    <h2 className="text-4xl font-black uppercase">My Portfolio</h2>
                    <p className="text-gray-600 mt-1">Track your investments with VCP & Fundamental insights</p>
                </div>
                <div className="flex items-center gap-4">
                    <button
                        onClick={handleSyncData}
                        disabled={isUpdating}
                        className={`flex items-center gap-2 bg-paper text-ink font-bold px-6 py-3 border-4 border-ink shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all ${isUpdating ? 'opacity-50 cursor-not-allowed' : ''}`}
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={isUpdating ? "animate-spin" : ""}>
                            <path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
                            <path d="M3 3v5h5" />
                            <path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16" />
                            <path d="M16 21h5v-5" />
                        </svg>
                        {isUpdating ? 'UPDATING...' : 'SYNC DATA'}
                    </button>
                    <button
                        onClick={handleExportCSV}
                        className="flex items-center gap-2 bg-paper text-ink font-bold px-6 py-3 border-4 border-ink shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all"
                    >
                        <Download size={20} />
                        CSV
                    </button>
                    <button
                        onClick={handleExportXLSX}
                        className="flex items-center gap-2 bg-paper text-ink font-bold px-6 py-3 border-4 border-ink shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all"
                    >
                        <FileSpreadsheet size={20} />
                        XLSX
                    </button>
                    <button
                        onClick={() => setIsModalOpen(true)}
                        className="flex items-center gap-2 bg-ink text-white font-bold px-6 py-3 border-4 border-ink shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all"
                    >
                        <Plus size={20} />
                        ADD STOCK
                    </button>
                </div>
            </div>

            <PortfolioDashboard
                holdings={portfolio}
                vcpData={vcpData}
                stockInfoData={stockInfoData}
                newsAnalysis={newsAnalysis}
                statusData={statusData}
            />

            <HoldingsTable
                holdings={portfolio}
                vcpData={vcpData}
                stockInfoData={stockInfoData}
                newsAnalysis={newsAnalysis}
                statusData={statusData}
                onEdit={handleEdit}
                onRemove={handleRemove}
                onRowClick={setSelectedDrawerItem}
                onClosePosition={handleClosePosition}
            />

            <AddStockModal
                isOpen={isModalOpen}
                onClose={handleCloseModal}
                existingItem={editingItem}
                vcpData={vcpData}
                stockInfoData={stockInfoData}
                newsAnalysis={newsAnalysis}
                availableVcpDates={availableVcpDates}
                onFetchVcpByDate={handleFetchVcpByDate}
                onFetchNewsAnalysisByDate={handleFetchNewsAnalysisByDate}
                onFetchStockInfoByDate={handleFetchStockInfoByDate}
                onFetchMarketStatusByDate={handleFetchMarketStatusByDate}
            />

            <EntryDetailDrawer
                item={selectedDrawerItem}
                onClose={() => setSelectedDrawerItem(null)}
            />

            <ClosePositionModal
                isOpen={isCloseModalOpen}
                onClose={handleClosePositionModalClose}
                item={selectedItemForClose}
            />
        </main>
    );
}
