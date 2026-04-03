export const dynamic = 'force-dynamic';

import { NextResponse } from 'next/server';

const SCHEDULER_URL = 'http://localhost:3001';

export async function POST(request: Request) {
    try {
        const { job } = await request.json();

        if (!job) {
            return NextResponse.json({ error: 'Job name is required' }, { status: 400 });
        }

        const response = await fetch(`${SCHEDULER_URL}/trigger/${job}`, {
            method: 'POST',
        });

        if (!response.ok) {
            throw new Error(`Scheduler returned ${response.status}`);
        }

        const text = await response.text();
        return NextResponse.json({ message: text });
    } catch (error) {
        console.error('Failed to trigger scheduler job:', error);
        return NextResponse.json(
            { error: 'Scheduler is unreachable', details: String(error) },
            { status: 503 }
        );
    }
}
