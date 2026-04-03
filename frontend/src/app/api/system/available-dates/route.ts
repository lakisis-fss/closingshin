export const dynamic = 'force-dynamic';

import { NextResponse } from 'next/server';
import { getAvailableVcpDates } from '@/lib/api';

export async function GET() {
    const dates = await getAvailableVcpDates();
    return NextResponse.json(dates);
}
