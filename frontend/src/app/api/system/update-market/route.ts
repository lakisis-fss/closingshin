export const dynamic = 'force-dynamic';

import { NextResponse } from 'next/server';
import { exec } from 'child_process';
import path from 'path';
import util from 'util';

const execPromise = util.promisify(exec);

export async function POST() {
    try {
        // Define path to the script
        // process.cwd() is e:\Downloads\Antigravity Project\ClosingSHIN\frontend
        const SCRIPT_PATH = path.resolve(process.cwd(), '../Scripts/05_collect_market_status.py');

        console.log(`Executing market update script at: ${SCRIPT_PATH}`);

        // Create path to venv python
        const projectRoot = path.resolve(process.cwd(), '..');
        const isWin = process.platform === 'win32';
        const venvPath = path.join(projectRoot, 'venv');
        const pythonExec = isWin
            ? path.join(venvPath, 'Scripts', 'pythonw.exe')
            : path.join(venvPath, 'bin', 'python');

        // Use venv python if explicitly exists, otherwise fallback to system python (though likely to fail if deps missing)
        // For simple scripts, 'python' might be 'python.exe' in venv/Scripts, but 'pythonw' is safer for no-console in logs if needed.
        // However, exec() captures stdout anyway. python.exe is fine.
        // Let's use the same logic as VCP scan for consistency.
        // Actually, for exec(), 'python.exe' is better than 'pythonw.exe' to capture stdout consistently?
        // 'pythonw' does NOT print to stdout/stderr in some cases. 
        // VCP scan uses spawn and file redirect. Here we use exec and capture stdout. 
        // We MUST use 'python.exe' (or just 'python') for exec() to capture output, UNLESS we want to run background invisible.
        // But here we await execPromise, so we want output. 'python.exe' is correct.
        const pythonCmd = isWin
            ? path.join(venvPath, 'Scripts', 'python.exe')
            : path.join(venvPath, 'bin', 'python');

        console.log(`Executing market update script at: ${SCRIPT_PATH} using ${pythonCmd}`);

        const command = `"${pythonCmd}" "${SCRIPT_PATH}"`;

        const { stdout, stderr } = await execPromise(command);

        if (stderr) {
            console.warn('Script stderr:', stderr);
        }

        console.log('Script stdout:', stdout);

        return NextResponse.json({
            success: true,
            message: 'Market data updated successfully.',
            details: stdout
        });

    } catch (error: any) {
        console.error('Failed to update market data:', error);
        return NextResponse.json(
            { error: 'Failed to update market data', details: error.message },
            { status: 500 }
        );
    }
}
