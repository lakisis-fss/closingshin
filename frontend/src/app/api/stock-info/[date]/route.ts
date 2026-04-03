export const dynamic = 'force-dynamic';

import { NextResponse } from 'next/server';
import { getStockInfoByDate } from '@/lib/api';

export async function GET(
    request: Request,
    { params }: { params: Promise<{ date: string }> }
) {
    const { date } = await params;

    if (!date || !/^\d{8}$/.test(date)) {
        return NextResponse.json({ error: 'Invalid date format. Use YYYYMMDD.' }, { status: 400 });
    }

    const fs = require('fs');
    const path = require('path');
    const logFile = path.resolve(process.cwd(), '..', 'Scripts', 'data', 'logs', 'debug_stock_info_route.log');

    try {
        const logMsg = `[${new Date().toISOString()}] [API Debug] Fetching stock info for date: ${date}\n`;
        fs.appendFileSync(logFile, logMsg);

        const results = await getStockInfoByDate(date);

        const logMsg2 = `[${new Date().toISOString()}] [API Debug] Found ${results.length} results for ${date}. First Item: ${JSON.stringify(results[0] || {})}\n`;
        fs.appendFileSync(logFile, logMsg2);

        return NextResponse.json(results);
    } catch (e: any) {
        const logErr = `[${new Date().toISOString()}] [API Debug] Error: ${e.message}\n`;
        if (fs.existsSync(logFile)) fs.appendFileSync(logFile, logErr);
        throw e;
    }
}
