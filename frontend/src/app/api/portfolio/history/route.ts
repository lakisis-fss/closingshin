import { NextResponse } from 'next/server';
import pb from '@/lib/pocketbase';

export async function GET(request: Request) {
    const { searchParams } = new URL(request.url);
    const ticker = searchParams.get('ticker');
    const startDate = searchParams.get('startDate');
    const endDate = searchParams.get('endDate');

    if (!ticker || !startDate) {
        return NextResponse.json({ error: 'Ticker and startDate are required' }, { status: 400 });
    }

    try {
        // Normalize Dates for PocketBase (YYYY-MM-DD HH:MM:SS.msZ)
        // Note: The input startDate comes in 'YYYY-MM-DD' or 'YYYY-MM-DD 00:00:00.000Z'
        const normalizedStart = startDate.includes(' ') ? startDate : `${startDate} 00:00:00.000Z`;
        
        let filter = `code = "${String(ticker).padStart(6, '0')}" && date >= "${normalizedStart}"`;
        
        if (endDate) {
            const normalizedEnd = endDate.includes(' ') ? endDate : `${endDate} 23:59:59.999Z`;
            filter += ` && date <= "${normalizedEnd}"`;
        }

        // Fetch using PocketBase SDK (Fast, Internal, No Python Overhead)
        // Using getFullList ensures we don't miss records if duration > 50 days (HoldingsTable needs all)
        const records = await pb.collection('ohlcv').getFullList({
            filter: filter,
            sort: '+date', // Ascending order as required by charts/MAE calculations
            requestKey: null // Disable request cancellation for concurrent calls
        });

        // Map to expected format
        const history = records.map(record => ({
            date: String(record.date).split(' ')[0],
            open: Number(record.open || 0),
            high: Number(record.high || 0),
            low: Number(record.low || 0),
            close: Number(record.close || 0),
            volume: Number(record.volume || 0)
        }));

        return NextResponse.json({ history });

    } catch (error: any) {
        console.error('Failed to fetch price history directly from PB:', error);
        return NextResponse.json({ 
            error: 'Failed to fetch price history',
            details: error.message 
        }, { status: 500 });
    }
}
