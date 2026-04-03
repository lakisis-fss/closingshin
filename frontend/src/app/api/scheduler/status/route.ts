export const dynamic = 'force-dynamic';

import { NextResponse } from 'next/server';

const SCHEDULER_URL = 'http://127.0.0.1:3001';

export async function GET() {
    try {
        const response = await fetch(`${SCHEDULER_URL}/status`, {
            cache: 'no-store',
            headers: { 'Content-Type': 'application/json' },
        });

        if (!response.ok) {
            throw new Error(`Scheduler returned ${response.status}`);
        }

        const data = await response.json();
        return NextResponse.json(data);
    } catch (error) {
        console.error('Failed to fetch scheduler status:', error);
        return NextResponse.json(
            { error: 'Scheduler is unreachable', details: String(error) },
            { status: 503 }
        );
    }
}
