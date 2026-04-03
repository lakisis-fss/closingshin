export const dynamic = 'force-dynamic';

import { NextRequest, NextResponse } from 'next/server';
import { spawn } from 'child_process';
import path from 'path';

export async function POST(req: NextRequest) {
    try {
        const body = await req.json();

        // Path to python script
        const scriptPath = path.resolve(process.cwd(), '../Scripts/simulate_trade.py');

        // Spawn python process
        // Ensure 'python' is in PATH or use specific path if needed. 
        // In this environment, 'python' usually refers to the active env.
        const pythonProcess = spawn('python', [scriptPath]);

        let resultData = '';
        let errorData = '';

        // Write data to stdin
        pythonProcess.stdin.write(JSON.stringify(body));
        pythonProcess.stdin.end();

        // Collect stdout
        pythonProcess.stdout.on('data', (data) => {
            resultData += data.toString();
        });

        // Collect stderr
        pythonProcess.stderr.on('data', (data) => {
            errorData += data.toString();
        });

        // Wait for process to close
        const exitCode = await new Promise((resolve) => {
            pythonProcess.on('close', resolve);
        });

        if (exitCode !== 0) {
            console.error('Simulation Script Error:', errorData);
            return NextResponse.json(
                { error: 'Simulation failed', details: errorData },
                { status: 500 }
            );
        }

        try {
            // resultData might contain other print outputs if not careful, 
            // but our script only prints JSON at the end. 
            // Better to robustly parse the last line or ensure script is clean.
            // Our script currently prints exactly one JSON string.
            const simulationResult = JSON.parse(resultData);
            return NextResponse.json(simulationResult);
        } catch (e) {
            console.error('JSON Parse Error:', e, resultData);
            return NextResponse.json(
                { error: 'Invalid response from simulation engine', output: resultData },
                { status: 500 }
            );
        }

    } catch (error) {
        console.error('API Error:', error);
        return NextResponse.json(
            { error: 'Internal Server Error' },
            { status: 500 }
        );
    }
}
