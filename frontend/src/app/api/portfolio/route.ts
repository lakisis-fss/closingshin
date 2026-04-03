export const dynamic = 'force-dynamic';

import { NextResponse } from 'next/server';
import { fetchFromPB, postToPB, patchToPB, deleteFromPB } from '@/lib/pocketbase';

// GET: Read all portfolio items from PB
export async function GET() {
    try {
        const data = await fetchFromPB("portfolio", { sort: "-buyDate", limit: 200 });
        // Map PB's 'id' to the frontend's expected 'id' if needed (they are named the same)
        return NextResponse.json(data.items || []);
    } catch (error) {
        console.error('Failed to read portfolio from PB:', error);
        return NextResponse.json({ error: 'Failed to read portfolio' }, { status: 500 });
    }
}

// POST: Add a new portfolio item to PB
export async function POST(request: Request) {
    try {
        const body = await request.json();
        
        // Ensure buyDate is set properly for PB's 'date' type (YYYY-MM-DD HH:MM:SS)
        const buyDate = body.buyDate && body.buyDate.trim() !== '' 
            ? `${body.buyDate} 00:00:00.000Z` 
            : new Date().toISOString();

        const newItem = {
            ...body,
            buyDate,
        };
        
        // PB returns the record including its generated id
        const record = await postToPB("portfolio", newItem);
        return NextResponse.json(record, { status: 201 });
    } catch (error: any) {
        console.error('Failed to add portfolio item to PB:', error);
        return NextResponse.json({ error: error.message || 'Failed to add portfolio item' }, { status: 500 });
    }
}

// PUT: Update an existing portfolio item in PB
export async function PUT(request: Request) {
    try {
        const body = await request.json();
        const { id, ...updates } = body;

        if (!id) {
            return NextResponse.json({ error: 'id is required' }, { status: 400 });
        }

        if (updates.buyDate) {
            updates.buyDate = `${updates.buyDate.substring(0, 10)} 00:00:00.000Z`;
        }

        const record = await patchToPB("portfolio", id, updates);
        return NextResponse.json(record);
    } catch (error: any) {
        console.error('Failed to update portfolio item in PB:', error);
        return NextResponse.json({ error: error.message || 'Failed to update portfolio item' }, { status: 500 });
    }
}

// DELETE: Remove a portfolio item from PB
export async function DELETE(request: Request) {
    try {
        const body = await request.json();
        const { id } = body;

        if (!id) {
            return NextResponse.json({ error: 'id is required' }, { status: 400 });
        }

        await deleteFromPB("portfolio", id);
        return NextResponse.json({ success: true, id });
    } catch (error: any) {
        console.error('Failed to delete portfolio item from PB:', error);
        return NextResponse.json({ error: error.message || 'Failed to delete portfolio item' }, { status: 500 });
    }
}
