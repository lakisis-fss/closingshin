export interface MarketStatus {
    timestamp: string;
    KOSPI?: {
        Close: number;
        Change_Pct: number;
    };
    KOSDAQ?: {
        Close: number;
        Change_Pct: number;
    };
    NASDAQ?: {
        Close: number;
        Change_Pct: number;
    };
    SOX?: {
        Close: number;
        Change_Pct: number;
    };
    USD_KRW?: {
        Close: number;
        Change_Pct: number;
    };
    US10Y?: {
        Close: number;
        Change_Pct: number;
    };
    US_10Y?: {
        Close: number;
        Change_Pct: number;
    };
    WTI_OIL?: {
        Close: number;
        Change_Pct: number;
    };
    KOSPI_Close?: number;
    KOSDAQ_Close?: number;
    ADR: {
        KOSPI: number;
        KOSDAQ: number;
        Counts?: {
            KOSPI_Up: number;
            KOSPI_Down: number;
            KOSDAQ_Up: number;
            KOSDAQ_Down: number;
        };
    };
    KOSPI_Net?: {
        Foreigner: number;
        Institution: number;
        Individual: number;
    };
    KOSDAQ_Net?: {
        Foreigner: number;
        Institution: number;
        Individual: number;
    };
    Sectors?: Record<string, { Change_Pct: number; Close: number; Ticker: string }>;
    History?: {
        date: string;
        KOSPI: number;
        KOSDAQ: number;
    }[];
    AI_Insight?: {
        sentiment: string;
        summary: string;
        reasoning: string;
    };
}

export interface VcpResult {
    ticker: string;
    name: string;
    market: string;
    price: number;
    close?: number;
    contractions_count: number;
    contractions_history: number[];
    last_depth_pct: number;
    volume_dry_up: boolean;
    vol_ratio: number;
    vcp_score: number;
    jump_score: number;
    pivot_point: number;
    pivot_distance_pct: number;
    note: string;
    relative_strength: number;
    consolidation_weeks: number;
    vcp_mode?: string;
    change_pct?: number;
}



export interface NewsItem {
    ticker: string;
    name: string;
    title: string;
    pub_date: string;
    link: string;
    description: string;
    score: number;
}

export interface StockInfo {
    ticker: string;
    name: string;
    collection_date: string;
    PER: number;
    PBR: number;
    EPS: number;
    BPS: number;
    DIV: number;
    DPS: number;
    "기관_5일": number;
    "외인_5일": number;
    "개인_5일": number;
    "기관_15일": number;
    "외인_15일": number;
    "개인_15일": number;
    "기관_30일": number;
    "외인_30일": number;
    "개인_30일": number;
    "기관_50일": number;
    "외인_50일": number;
    "개인_50일": number;
    "기관_100일": number;
    "외인_100일": number;
    "개인_100일": number;
    supply_score?: number;
    fundamental_score?: number;
    market_cap?: number;
    price_change_pct?: number;
    close?: number;
}

/**
 * Exit Plan 조건 정의
 * Phase 1: 기본 조건 (손절/익절/타임컷)
 */
export interface ExitConditions {
    // 가격 기반 (필수)
    stopLossPercent?: number;      // 예: -7 (매수가 대비 %)
    takeProfitPercent?: number;    // 예: +15 (매수가 대비 %)
    trailingStopPercent?: number;  // 예: -10 (고점 대비 %)

    // 시간 기반 (타임컷)
    timeCutDays?: number;          // 예: 30 (보유일수)
    timeCutHours?: number;         // 예: 14 (시)
    timeCutMinutes?: number;       // 예: 30 (분)

    // 알림 설정
    alertEnabled?: boolean;        // 조건 충족 시 알림 여부
}

export interface PortfolioItem {
    id: string;
    ticker: string;
    name: string;
    market: 'KOSPI' | 'KOSDAQ';
    buyDate: string;
    buyPrice: number;
    quantity: number;
    memo: string;
    exitPlan: string;              // 기존 텍스트 메모 유지
    exitConditions?: ExitConditions;  // 구조화된 조건 추가
    vcp_mode?: string;             // VCP 감지 모드
    initialScores?: {
        totalScore: number;
        vcpScore?: number;
        supplyScore?: number;
        sentimentScore?: number;
        fundamentalScore?: number;
        sectorScore?: number;
    };
    simulation?: SimulationResult;
    createdAt: string;
    updatedAt: string;
}

export interface SimulationResult {
    enabled: boolean;
    status: 'OPEN' | 'CLOSED';
    exitDate?: string;
    exitPrice?: number;
    exitReason?: string;
    realizedPnl?: number;
    realizedPnlPercent?: number;
    lastUpdate: string;
}

export interface PortfolioStats {
    totalValue: number;
    totalCost: number;
    totalPnL: number;
    totalPnLPercent: number;
    healthScore: number;
}

export interface NewsAnalysis {
    ticker: string;
    name: string;
    title: string;
    pub_date: string;
    link: string;
    description: string;
    score: number;
    target_stock: string;
    sentiment_score: number;
    sentiment_label: string;
    impact_intensity: string;
    time_horizon: string;
    news_type: string;
    key_drivers: string;
    trading_signal: string;
    reason: string;
}
