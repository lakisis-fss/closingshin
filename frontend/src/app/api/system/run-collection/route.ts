export const dynamic = 'force-dynamic';

import { NextResponse } from 'next/server';
import { exec } from 'child_process';
import path from 'path';
import util from 'util';
import { fetchFromPB, postToPB, patchToPB } from '@/lib/pocketbase';

const execPromise = util.promisify(exec);

export async function POST() {
    try {
        // Initialize progress in PocketBase for UI synchronization
        const initialProgress = {
            step: 1,
            progress: 0,
            total: 100,
            percent: 5,
            message: "데이터 수집 파이프라인 시작 중...",
            status: "running",
            timestamp: new Date().toISOString()
        };

        try {
            const pbRes = await fetchFromPB("settings", { filter: 'key = "scan_progress"', limit: 1 });
            const settingsData = { key: "scan_progress", value: initialProgress };
            if (pbRes.items && pbRes.items.length > 0) {
                await patchToPB("settings", pbRes.items[0].id, settingsData);
            } else {
                await postToPB("settings", settingsData);
            }
        } catch (e) {
            console.error('Failed to init progress in PB:', e);
        }

        // Define path to the script
        // process.cwd() is e:\Downloads\Antigravity Project\ClosingSHIN\frontend
        // We need to go up to ClosingSHIN root, then to Scripts
        const SCRIPT_PATH = path.resolve(process.cwd(), '../Scripts/06_collect_stock_data.py');

        console.log(`Executing script at: ${SCRIPT_PATH}`);

        // Command to run the python script
        // Assuming 'python' is in the system PATH and has necessary packages installed
        const command = `python "${SCRIPT_PATH}"`;

        const { stdout, stderr } = await execPromise(command);

        if (stderr) {
            console.warn('Script stderr:', stderr);
        }

        console.log('Script stdout:', stdout);

        // Step 2: Run Portfolio Calculation
        const CALC_SCRIPT_PATH = path.resolve(process.cwd(), '../Scripts/07_calc_portfolio.py');
        console.log(`Executing portfolio calculation at: ${CALC_SCRIPT_PATH}`);

        const calcCommand = `python "${CALC_SCRIPT_PATH}"`;
        const { stdout: calcStdout, stderr: calcStderr } = await execPromise(calcCommand);

        if (calcStderr) {
            console.warn('Portfolio Calculation stderr:', calcStderr);
        }
        console.log('Portfolio Calculation stdout:', calcStdout);

        return NextResponse.json({
            success: true,
            message: 'Data collection completed successfully.',
            details: stdout
        });

    } catch (error: any) {
        console.error('Failed to run data collection script:', error);
        return NextResponse.json(
            { error: 'Failed to run data collection script', details: error.message },
            { status: 500 }
        );
    }
}
