export const dynamic = 'force-dynamic';

import { NextResponse } from "next/server";
import { fetchFromPB } from "@/lib/pocketbase";

export async function GET() {
    try {
        const data = await fetchFromPB("market_status", { sort: "-date", limit: 1 });
        if (!data.items || data.items.length === 0) {
            return NextResponse.json({ error: "No market status found in PB" }, { status: 404 });
        }
        return NextResponse.json(data.items[0].data);
    } catch (error) {
        console.error("Error fetching market status from PB:", error);
        return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
    }
}
