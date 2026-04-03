export const dynamic = 'force-dynamic';

import { NextResponse } from 'next/server';
import { getNewsReportsByDate } from '@/lib/api';

export async function GET(
    request: Request,
    { params }: { params: Promise<{ date: string }> }
) {
    const { date } = await params;

    if (!date || !/^\d{8}$/.test(date)) {
        return NextResponse.json({ error: 'Invalid date format. Use YYYYMMDD.' }, { status: 400 });
    }

    const results = await getNewsReportsByDate(date);
    return NextResponse.json(results);
}
