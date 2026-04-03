export const dynamic = 'force-dynamic';

import { NextRequest, NextResponse } from 'next/server';
import { spawn } from 'child_process';
import path from 'path';

export async function GET(
    request: NextRequest,
    { params }: { params: Promise<{ ticker: string }> }
) {
    try {
        const { ticker } = await params;
        const searchParams = request.nextUrl.searchParams;
        const date = searchParams.get('date'); // YYYYMMDD optional

        if (!ticker || ticker.length !== 6) {
            return NextResponse.json({ error: 'Invalid ticker format' }, { status: 400 });
        }

        const scriptPath = path.resolve(process.cwd(), '../Scripts/get_price.py');
        const args = [ticker];
        if (date) args.push(date);

        const pythonProcess = spawn('python', [scriptPath, ...args]);

        let resultData = '';
        let errorData = '';

        pythonProcess.stdout.on('data', (data) => { resultData += data.toString(); });
        pythonProcess.stderr.on('data', (data) => { errorData += data.toString(); });

        const exitCode = await new Promise((resolve) => {
            pythonProcess.on('close', resolve);
        });

        if (exitCode !== 0) {
            console.error('get_price.py Error:', errorData);
            return NextResponse.json({ error: 'Failed to fetch price', details: errorData }, { status: 500 });
        }

        try {
            const result = JSON.parse(resultData);
            return NextResponse.json(result);
        } catch (e) {
            console.error('JSON Parse Error:', resultData);
            return NextResponse.json({ error: 'Invalid response from backend', raw: resultData }, { status: 500 });
        }
    } catch (error) {
        console.error('API Error:', error);
        return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
    }
}
