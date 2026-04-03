import { NextResponse } from 'next/server';
import { fetchFromPB } from '@/lib/pocketbase';

export const dynamic = 'force-dynamic';

export async function GET() {
    try {
        const data = await fetchFromPB("settings", { 
            filter: 'key = "scan_progress"', 
            limit: 1 
        });

        if (!data.items || data.items.length === 0) {
            return NextResponse.json({
                status: 'idle',
                message: 'No scan history found in PB.',
                percent: 0
            });
        }

        const record = data.items[0];
        // settings 컬렉션의 value 필드에 저장된 진행률 데이터를 반환합니다.
        return NextResponse.json(record.value || {});

    } catch (error) {
        console.error('Failed to fetch progress from PB:', error);
        return NextResponse.json(
            { error: 'Failed to fetch progress' },
            { status: 500 }
        );
    }
}
