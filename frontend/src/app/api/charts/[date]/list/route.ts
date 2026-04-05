import { NextRequest, NextResponse } from 'next/server';
import { fetchFromPB } from '@/lib/pocketbase';

export async function GET(
    request: NextRequest,
    { params }: { params: Promise<{ date: string }> }
) {
    const { date } = await params;
    
    // date here is usually YYYYMMDD, PB expects ISO-ish date
    const isoDate = `${date.substring(0, 4)}-${date.substring(4, 6)}-${date.substring(6, 8)} 00:00:00.000Z`;
    
    try {
        const data = await fetchFromPB("vcp_charts", {
            filter: `date = "${isoDate}"`,
            limit: 500
        });
        
        const chartMap: Record<string, string> = {};
        
        data.items.forEach((item: any) => {
            // Encode filename to handle special characters correctly
            const market = item.market || "UNKNOWN";
            const name = item.name || "UNKNOWN";
            const ticker = item.ticker || "";
            const filename = encodeURIComponent(`${market}_${name}_${ticker}.png`);
            
            // Return internal proxy URL instead of direct PB URL
            chartMap[ticker] = `/api/charts/${date}/${filename}`;
        });
        
        return NextResponse.json(chartMap);
    } catch (error) {
        console.error(`[API] Charts List Error for ${date}:`, error);
        return NextResponse.json({}, { status: 500 });
    }
}
