export const dynamic = 'force-dynamic';

import { NextResponse } from 'next/server';
import { spawn } from 'child_process';
import path from 'path';
import fs from 'fs';
import { fetchFromPB, postToPB, patchToPB } from '@/lib/pocketbase';

export async function POST(request: Request) {
    try {
        const { date, mode, custom } = await request.json();

        // 스크립트 경로 설정
        const projectRoot = path.resolve(process.cwd(), '..');
        const scriptPath = path.join(projectRoot, 'Scripts', '02_scan_vcp.py');
        // Use venv python to ensure dependencies are loaded
        const isWin = process.platform === 'win32';
        const venvPath = path.join(projectRoot, 'venv');
        const pythonExec = isWin
            ? path.join(venvPath, 'Scripts', 'pythonw.exe')
            : path.join(venvPath, 'bin', 'python');

        // Check if venv python exists, otherwise fallback to system python
        const pythonPath = fs.existsSync(pythonExec) ? pythonExec : (isWin ? 'pythonw' : 'python');

        // 파라미터 준비
        // -u flag for unbuffered binary stdout and stderr
        const args = ['-u', scriptPath];
        if (date) {
            args.push('--date', date);
        }
        if (mode) {
            args.push('--mode', mode);
        }
        if (mode === 'custom' && custom) {
            if (custom.minContractions !== undefined) args.push('--min_contractions', custom.minContractions.toString());
            if (custom.maxDepth1st !== undefined) args.push('--max_depth_1st', custom.maxDepth1st.toString());
            if (custom.minDepthLast !== undefined) args.push('--min_depth_last', custom.minDepthLast.toString());
            if (custom.maxDepthLast !== undefined) args.push('--max_depth_last', custom.maxDepthLast.toString());
            if (custom.strictTrend !== undefined) args.push('--strict_trend', custom.strictTrend ? 'true' : 'false');
        }

        console.log(`Executing scan: ${pythonPath} ${args.join(' ')}`);

        // 백그라운드 프로세스로 실행
        const isWindows = process.platform === 'win32';

        // 로그 파일 설정
        const scriptsDir = path.join(projectRoot, 'Scripts');
        const logDir = path.join(scriptsDir, 'data', 'logs');

        if (!fs.existsSync(logDir)) fs.mkdirSync(logDir, { recursive: true });
        const logFile = path.join(logDir, `scan_${date || 'today'}_${Date.now()}.log`);
        const out = fs.openSync(logFile, 'a');

        // Initialize progress file to prevent stale data reading
        const progressFile = path.join(scriptsDir, 'data', 'scan_progress.json');
        const initialProgress = {
            step: 0,
            progress: 0,
            total: 100,
            percent: 0,
            message: "VCP 스캔을 준비하고 있습니다 (Initializing)...",
            status: "running",
            timestamp: new Date().toISOString()
        };
        fs.writeFileSync(progressFile, JSON.stringify(initialProgress, null, 2));

        console.log(`[API] Executing background scan: ${pythonPath} ${args.join(' ')}`);
        console.log(`[API] CWD: ${scriptsDir}`);
        console.log(`[API] Logging completion to: ${logFile}`);

        // Update scriptPath to be absolute if not already (it is based on process.cwd in line 11)
        // But let's be sure.

        const child = spawn(pythonPath, args, {
            stdio: ['ignore', out, out], // stdout, stderr를 로그 파일로 리다이렉트
            detached: true,
            windowsHide: true,
            cwd: scriptsDir // Run from Scripts directory
        });

        child.unref(); // 부모 프로세스가 종료되어도 자식이 유지되도록 (Node.js 이벤트 루프에서 제외)

        // Sync with PocketBase settings for real-time UI updates
        try {
            const pbRes = await fetchFromPB("settings", { filter: 'key = "scan_progress"', limit: 1 });
            const settingsData = {
                key: "scan_progress",
                value: initialProgress
            };

            if (pbRes.items && pbRes.items.length > 0) {
                await patchToPB("settings", pbRes.items[0].id, settingsData);
            } else {
                await postToPB("settings", settingsData);
            }
            console.log('[API] PocketBase scan_progress initialized.');
        } catch (pbError) {
            console.error('[API] Failed to sync scan_progress to PB:', pbError);
        }

        return NextResponse.json({
            success: true,
            message: 'VCP Scan started in background',
            pid: child.pid
        });

    } catch (error) {
        console.error('Failed to run scan:', error);
        return NextResponse.json(
            { success: false, error: 'Failed to start VCP scan' },
            { status: 500 }
        );
    }
}
