export const dynamic = 'force-dynamic';

import { NextRequest, NextResponse } from "next/server";

export async function GET(
    request: NextRequest,
    { params }: { params: Promise<{ date: string; filename: string }> }
) {
    const { date, filename } = await params;
    
    // Decode filename to handle Korean characters correctly
    const decodedFilename = decodeURIComponent(filename);

    // Security: Prevent directory traversal
    const safeDate = date.replace(/[^0-9]/g, ""); // Allow only numbers
    const safeFilename = decodedFilename.replace(/[^a-zA-Z0-9._\-가-힣]/g, ""); // Allow alphanumeric, dots, dashes, underscores, and Korean characters

    // If filename was malformed or traversal attempted
    if (safeDate !== date || (!decodedFilename.includes(safeFilename) && safeFilename !== "")) {
        return new NextResponse("Invalid path", { status: 400 });
    }

    try {
        // --- Directly Fetch from PocketBase ---
        console.log(`[API] Fetching chart from PocketBase: ${decodedFilename}`);
        
        // Extract ticker from filename (format: market_name_ticker.png)
        const parts = decodedFilename.replace('.png', '').split('_');
        if (parts.length >= 3) {
            const ticker = parts[parts.length - 1];
            const isoDate = `${date.substring(0, 4)}-${date.substring(4, 6)}-${date.substring(6, 8)} 00:00:00.000Z`;
            
            const pbUrl = process.env.PB_URL || process.env.NEXT_PUBLIC_PB_URL || 'http://127.0.0.1:8090';
            const filter = `date = "${isoDate}" && ticker = "${ticker}"`;
            const checkUrl = `${pbUrl}/api/collections/vcp_charts/records?filter=${encodeURIComponent(filter)}&limit=1`;
            
            console.log(`[API Proxy] Querying PB: ${checkUrl}`);
            const pbRes = await fetch(checkUrl, { cache: 'no-store' });
            if (pbRes.ok) {
                const data = await pbRes.json();
                if (data.totalItems > 0) {
                    const record = data.items[0];
                    if (record.file) {
                        const pbFileUrl = `${pbUrl}/api/files/${record.collectionId}/${record.id}/${record.file}`;
                        console.log(`[API Proxy] Fetching image: ${pbFileUrl}`);
                        
                        // Proxy the actual image content
                        const imageRes = await fetch(pbFileUrl, { cache: 'no-store' });
                        if (imageRes.ok) {
                            const blob = await imageRes.blob();
                            const headers = new Headers();
                            headers.set("Content-Type", "image/png");
                            headers.set("Cache-Control", "public, s-maxage=3600");
                            return new NextResponse(blob, { headers });
                        }
                    }
                }
            }
        }

        console.error(`[API Error] Chart Not Found in PB: ${decodedFilename}`);
        return NextResponse.json({ error: 'Chart not found' }, { status: 404 });
    } catch (error) {
        console.error('[API Error] Chart access error:', error);
        return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
    }
}
