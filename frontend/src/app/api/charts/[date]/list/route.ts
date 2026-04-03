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
        const PB_URL = process.env.NEXT_PUBLIC_PB_URL || "http://127.0.0.1:8090";
        
        data.items.forEach((item: any) => {
            chartMap[item.ticker] = `${PB_URL}/api/files/vcp_charts/${item.id}/${item.file}`;
        });
        
        return NextResponse.json(chartMap);
    } catch (error) {
        console.error(`[API] Charts List Error for ${date}:`, error);
        return NextResponse.json({}, { status: 500 });
    }
}
