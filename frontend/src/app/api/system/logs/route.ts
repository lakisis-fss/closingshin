export const dynamic = 'force-dynamic';

import { NextResponse } from 'next/server';
import { fetchFromPB } from '@/lib/pocketbase';
import PocketBase from 'pocketbase';

export async function GET() {
    try {
        const pb = new PocketBase(process.env.PB_URL || 'http://127.0.0.1:8090');
        
        // Fetch and sort in memory to avoid PB internal 400 error on certain environments
        const data = await pb.collection("system_logs").getList(1, 500);

        const logs = data.items
            .sort((a, b) => {
                const dateA = a.created || '';
                const dateB = b.created || '';
                return dateB.localeCompare(dateA);
            })
            .map((item: any) => 
                `[${item.created}] [${item.source || 'SYS'}] [${item.level || 'INFO'}] ${item.message}`
            );

        return NextResponse.json({ logs });
    } catch (error: any) {
        console.error('Failed to fetch logs:', error);
        return NextResponse.json({ error: 'Failed to fetch logs', details: error.message }, { status: 500 });
    }
}

export async function DELETE() {
    try {
        const pb = new PocketBase(process.env.PB_URL || 'http://127.0.0.1:8090');
        await pb.collection('_superusers').authWithPassword(
            process.env.PB_EMAIL || 'admin@example.com',
            process.env.PB_PASSWORD || 'admin1234'
        );

        // Delete all records in system_logs
        // PocketBase doesn't have a truncate, so we fetch and delete or use a batch delete if available.
        // For simplicity, we'll fetch IDs and delete them.
        const all = await pb.collection('system_logs').getFullList({ fields: 'id' });
        for (const item of all) {
            await pb.collection('system_logs').delete(item.id);
        }

        return NextResponse.json({ message: 'Logs cleared successfully from PB' });
    } catch (error) {
        console.error('Failed to clear logs in PB:', error);
        return NextResponse.json(
            { error: 'Failed to clear logs: ' + (error instanceof Error ? error.message : String(error)) },
            { status: 500 }
        );
    }
}
