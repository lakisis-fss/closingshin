export const dynamic = 'force-dynamic';

import { NextResponse } from 'next/server';
import { fetchFromPB } from '@/lib/pocketbase';

export async function GET() {
    try {
        const data = await fetchFromPB("settings", { 
            filter: 'key = "portfolio_status"', 
            limit: 1 
        });

        if (!data.items || data.items.length === 0) {
            return NextResponse.json({ error: 'Settings not found in PB' }, { status: 404 });
        }

        const record = data.items[0];
        // settings 컬렉션의 value 필드에 저장된 포트폴리오 상태 데이터를 반환합니다.
        return NextResponse.json(record.value || {});
    } catch (error) {
        console.error('Failed to read portfolio status from PB:', error);
        return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
    }
}
