import { NewsAnalysis, MarketStatus } from './types';

export interface ScoreInputs {
    vcpScore?: number;
    supplyScore?: number;
    sentimentScore?: number;
    fundamentalScore?: number;
    sectorScore?: number;
    rawRs?: number; // Added for RS calculation
}

export interface ScoreBreakdown {
    vcpContribution: number;
    supplyContribution: number;
    sentimentContribution: number;
    fundamentalContribution: number;
    sectorContribution: number;
    totalScore: number;
    grade: 'STRONG_BUY' | 'WATCHLIST' | 'NEUTRAL' | 'WEAK';
    gradeColor: string;
}

export interface QuantWeights {
    vcp: number;
    supply: number;
    sentiment: number;
    fundamental: number;
    sector: number;
}

export const DEFAULT_WEIGHTS: QuantWeights = {
    vcp: 0.20,
    supply: 0.30,
    sentiment: 0.30,
    fundamental: 0.10,
    sector: 0.10,
};

export const SCORE_WEIGHTS = DEFAULT_WEIGHTS;

export const GRADE_THRESHOLDS = {
    STRONG_BUY: 80,
    WATCHLIST: 60,
    NEUTRAL: 40,
} as const;

/**
 * 종목명을 기반으로 섹터 카테고리를 판별합니다.
 * 사용자가 제공한 8대 섹터 히트맵 항목과 매칭됩니다.
 */
export function getSectorCategory(stockName: string): string {
    const name = stockName.toUpperCase();
    if (name.includes('전자') || name.includes('하이닉스') || name.includes('반도체') || name.includes('삼성')) return 'SEMICON';
    if (name.includes('에너지') || name.includes('배터리') || name.includes('셀') || name.includes('소재') || name.includes('에코')) return 'BATTERY';
    if (name.includes('기아') || name.includes('현대차') || name.includes('모비스') || name.includes('자동차') || name.includes('부품')) return 'AUTO';
    if (name.includes('포스코') || name.includes('POSCO') || name.includes('철강') || name.includes('금속') || name.includes('제철')) return 'STEEL';
    if (name.includes('은행') || name.includes('금융지주') || name.includes('KB') || name.includes('신한') || name.includes('금융')) return 'BANK';
    if (name.includes('증권') || name.includes('미래에셋') || name.includes('키움') || name.includes('투자')) return 'SECURITIES';
    if (name.includes('네이버') || name.includes('카카오') || name.includes('IT') || name.includes('NAVER') || name.includes('소프트')) return 'IT';
    return 'KOSPI200'; // 기본값
}

/**
 * Raw RS 값(Minervini Style, 약 50~150 범위)을 0~100 스케일로 정규화합니다.
 * 100점(시장평균)을 약 75점으로 맵핑하여 강세 종목을 우대합니다.
 */
export function normalizeRsScore(rawRs: number): number {
    if (!rawRs || rawRs <= 0) return 50;
    
    // 130 이상: 100점 (초강세)
    if (rawRs >= 130) return 100;
    // 50 이하: 0~30점 (최약세)
    if (rawRs <= 50) return Math.max(0, rawRs - 20);
    
    // 구간별 선형 보간
    // 50(30점) -> 100(75점) -> 130(100점)
    if (rawRs <= 100) {
        return 30 + (rawRs - 50) * (45 / 50);
    } else {
        return 75 + (rawRs - 100) * (25 / 30);
    }
}

/**
 * 섹터 등락률을 0~100 스케일 점수로 변환합니다.
 * 0%를 50점으로 기준 삼아 1%당 10점씩 가중치를 둡니다.
 */
export function calculateSectorPerformanceScore(changePct: number): number {
    const score = 50 + (changePct * 10);
    return Math.max(0, Math.min(100, Math.round(score)));
}

/**
 * 가중치 기반 Total Quant Score 계산
 */
export function calculateIntegratedQuantScore(
    inputs: ScoreInputs, 
    marketStatus?: MarketStatus,
    stockName?: string,
    weights: QuantWeights = DEFAULT_WEIGHTS
): ScoreBreakdown {
    const vcp = inputs.vcpScore ?? 50;
    const supply = inputs.supplyScore ?? 50;
    const sentiment = inputs.sentimentScore ?? 50;
    const fundamental = inputs.fundamentalScore ?? 50;
    
    // Sector/RS Score 자동 계산 로직
    let finalSectorRsScore = 50;
    
    // RS 점수 산출 (Minervini Raw RS -> 0~100)
    const rsScore = normalizeRsScore(inputs.rawRs || 0);
    
    // 섹터 등락 점수 산출
    let sectorPerfScore = 50;
    if (marketStatus && stockName) {
        const category = getSectorCategory(stockName);
        const sectorChange = marketStatus.Sectors?.[category]?.Change_Pct;
        if (sectorChange !== undefined) {
            sectorPerfScore = calculateSectorPerformanceScore(sectorChange);
        } else {
            // 섹터 정보가 없으면 시장 지수 등락률(KOSPI/KOSDAQ 평균)을 폴백으로 사용
            const marketChange = (marketStatus.KOSPI?.Change_Pct || marketStatus.KOSDAQ?.Change_Pct || 0);
            sectorPerfScore = calculateSectorPerformanceScore(marketChange);
        }
    }
    
    // 최종 Sector/RS 점수 결합 (종목 RS 70% : 섹터 분위기 30%)
    finalSectorRsScore = Math.round(rsScore * 0.7 + sectorPerfScore * 0.3);

    const vcpContribution = Math.round(vcp * weights.vcp);
    const supplyContribution = Math.round(supply * weights.supply);
    const sentimentContribution = Math.round(sentiment * weights.sentiment);
    const fundamentalContribution = Math.round(fundamental * weights.fundamental);
    const sectorContribution = Math.round(finalSectorRsScore * weights.sector);

    const totalScore = vcpContribution + supplyContribution + sentimentContribution + fundamentalContribution + sectorContribution;

    let grade: ScoreBreakdown['grade'];
    let gradeColor: string;

    if (totalScore >= GRADE_THRESHOLDS.STRONG_BUY) {
        grade = 'STRONG_BUY';
        gradeColor = 'bauhaus-red';
    } else if (totalScore >= GRADE_THRESHOLDS.WATCHLIST) {
        grade = 'WATCHLIST';
        gradeColor = 'bauhaus-blue';
    } else if (totalScore >= GRADE_THRESHOLDS.NEUTRAL) {
        grade = 'NEUTRAL';
        gradeColor = 'bauhaus-yellow';
    } else {
        grade = 'WEAK';
        gradeColor = 'gray-400';
    }

    return {
        vcpContribution,
        supplyContribution,
        sentimentContribution,
        fundamentalContribution,
        sectorContribution,
        totalScore,
        grade,
        gradeColor,
    };
}

/**
 * -1~1 범위의 sentiment_score를 0~100 스케일로 변환
 */
export function convertSentimentToScore(rawSentiment: number): number {
    const amplified = rawSentiment * 1.5;
    const score = Math.round((amplified + 1) * 50);
    return Math.max(0, Math.min(100, score));
}

/**
 * Buy Reason 포맷 생성
 */
export function formatScoreBreakdown(
    breakdown: ScoreBreakdown,
    inputs: ScoreInputs,
    vcpDetails?: { contractions: number; lastDepth: number; volumeDryUp: boolean; jumpScore: number }
): string {
    // Sector/RS 원점수 역산
    const sectorRaw = Math.round(breakdown.sectorContribution / DEFAULT_WEIGHTS.sector);

    const lines = [
        `[Total Quant Score]`,
        `Total Score: ${breakdown.totalScore} (${breakdown.grade.replace('_', ' ')})`,
        ``,
        `[Score Breakdown]`,
        `- VCP (20%): ${inputs.vcpScore ?? 'N/A'} → +${breakdown.vcpContribution}`,
        `- Supply (30%): ${inputs.supplyScore ?? 'N/A'} → +${breakdown.supplyContribution}`,
        `- Sentiment (30%): ${inputs.sentimentScore ?? 'N/A'} → +${breakdown.sentimentContribution}`,
        `- Fundamental (10%): ${inputs.fundamentalScore ?? 'N/A'} → +${breakdown.fundamentalContribution}`,
        `- Sector/RS (10%): ${sectorRaw} → +${breakdown.sectorContribution}`,
    ];

    if (vcpDetails) {
        lines.push(
            ``,
            `[VCP Pattern Details]`,
            `Pattern: ${vcpDetails.contractions}T, Last Depth ${vcpDetails.lastDepth}%`,
            `Volume Dry-Up: ${vcpDetails.volumeDryUp ? 'YES' : 'NO'}`,
            `Jump Score: ${vcpDetails.jumpScore}`
        );
    }

    return lines.join('\n');
}

/**
 * 뉴스 분석 목록에서 특정 종목의 통합 심리 점수를 계산합니다.
 */
export function calculateAggregatedSentimentScore(newsList: NewsAnalysis[], ticker: string, stockName?: string): number | undefined {
    const targetTicker = String(ticker).padStart(6, '0');
    const sName = stockName ? String(stockName).replace(/\s/g, '').toLowerCase() : '';
    
    const relevantNews = newsList.filter(n => {
        const itemTicker = String(n.ticker || '').padStart(6, '0');
        const tickerMatch = itemTicker === targetTicker;
        
        // 종목명 매칭 (보조 수단)
        let nameMatch = false;
        const targetStockRaw = String(n.target_stock || '').replace(/\s/g, '').toLowerCase();
        
        if (targetStockRaw) {
            // 1. target_stock 필드에 티커가 들어있는 경우
            const tickerInTarget = !!targetStockRaw.includes(targetTicker);
            
            // 2. 종목명이 상호 포함되는 경우
            const nameContainsTarget = !!(sName && targetStockRaw.includes(sName));
            const targetContainsName = !!(sName && sName.includes(targetStockRaw));
            
            nameMatch = tickerInTarget || nameContainsTarget || targetContainsName;
        }
        
        return tickerMatch || nameMatch;
    });

    if (relevantNews.length === 0) return undefined;

    const sum = relevantNews.reduce((acc, curr) => acc + (curr.sentiment_score || 0), 0);
    const avg = sum / relevantNews.length;

    return convertSentimentToScore(avg);
}
