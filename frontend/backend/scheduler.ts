import cron from 'node-cron';
import { runPythonScript } from './scriptRunner';

interface JobStatus {
    name: string;
    lastRun: string | null;
    nextRun: string | null;
    status: 'idle' | 'running' | 'error';
    lastError?: string;
}

function getNextMarketUpdateTime(): Date {
    const now = new Date();
    const next = new Date(now);
    const minutes = next.getUTCMinutes();
    const remainder = minutes % 10;
    const addMinutes = 10 - remainder;

    next.setUTCMinutes(minutes + addMinutes);
    next.setUTCSeconds(0);
    next.setUTCMilliseconds(0);

    return next;
}

function getNextVcpScanTime(): Date {
    const now = new Date();
    // 15:40 KST is 06:40 UTC.
    const next = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate(), 6, 40, 0, 0));

    if (next <= now) {
        next.setUTCDate(next.getUTCDate() + 1);
    }
    return next;
}

const jobs: Record<string, JobStatus> = {
    marketUpdate: {
        name: '시장 데이터 업데이트',
        lastRun: null,
        nextRun: getNextMarketUpdateTime().toISOString(),
        status: 'idle'
    },
    portfolioCalc: {
        name: '포트폴리오 계산',
        lastRun: null,
        nextRun: null, // Dependent on Market Update
        status: 'idle'
    },
    vcpScan: {
        name: 'VCP 스캔',
        lastRun: null,
        nextRun: getNextVcpScanTime().toISOString(),
        status: 'idle'
    },
    stockInfoUpdate: {
        name: '주식 정보 업데이트',
        lastRun: null,
        nextRun: null, // Manual trigger only
        status: 'idle'
    },
    missingDataRecovery: {
        name: '누락 데이터 복구',
        lastRun: null,
        nextRun: null, // Manual trigger only
        status: 'idle'
    },
    exitMonitor: {
        name: '장중 감시',
        lastRun: null,
        nextRun: null,
        status: 'idle'
    },
};

async function runMarketUpdate() {
    console.log('[Scheduler] Starting Market Data Update...');
    jobs.marketUpdate.status = 'running';

    // 1. Fetch Market Status
    const result = await runPythonScript('05_collect_market_status.py');
    jobs.marketUpdate.lastRun = new Date().toISOString();
    jobs.marketUpdate.nextRun = getNextMarketUpdateTime().toISOString();

    if (result.success) {
        jobs.marketUpdate.status = 'idle';
        console.log('[Scheduler] Market Data Update Completed.');

        // 2. Trigger Portfolio Calculation (Dependency)
        await runPortfolioCalc();
    } else {
        jobs.marketUpdate.status = 'error';
        jobs.marketUpdate.lastError = result.error;
        console.error('[Scheduler] Market Data Update Failed:', result.error);
    }
}

async function runPortfolioCalc() {
    console.log('[Scheduler] Starting Portfolio Calculation...');
    jobs.portfolioCalc.status = 'running';

    // TODO: Create/Verify this script exists. If not, we might need to implement logic here or in python.
    // For now assuming a script named 'calc_portfolio.py' or similar logic will be implemented.
    // Ideally this should use the same logic as frontend portfolio calculation but in backend.
    // Since frontend logic is complex (fetching prices then manual calc), maybe we need a dedicated python script.
    // Let's use a placeholder script name for now and I will create it next.
    const result = await runPythonScript('07_calc_portfolio.py');

    jobs.portfolioCalc.lastRun = new Date().toISOString();

    if (result.success) {
        jobs.portfolioCalc.status = 'idle';
        console.log('[Scheduler] Portfolio Calculation Completed.');
    } else {
        jobs.portfolioCalc.status = 'error';
        jobs.portfolioCalc.lastError = result.error;
        console.error('[Scheduler] Portfolio Calculation Failed:', result.error);
    }
}

async function runVcpScan() {
    console.log('[Scheduler] Starting Daily VCP Scan...');
    jobs.vcpScan.status = 'running';

    // 1. Run VCP Scan
    const result = await runPythonScript('02_scan_vcp.py');
    
    if (result.success) {
        console.log('[Scheduler] VCP Scan Completed. Starting Chart Visualization...');
        
        // 2. Run Chart Visualization (Dependency)
        const vizResult = await runPythonScript('03_visualize_vcp.py');
        
        jobs.vcpScan.lastRun = new Date().toISOString();
        jobs.vcpScan.nextRun = getNextVcpScanTime().toISOString();

        if (vizResult.success) {
            jobs.vcpScan.status = 'idle';
            console.log('[Scheduler] VCP Scan & Visualization Completed.');
        } else {
            jobs.vcpScan.status = 'error';
            jobs.vcpScan.lastError = `Scan OK, but Visualization Failed: ${vizResult.error}`;
            console.error('[Scheduler] VCP Visualization Failed:', vizResult.error);
        }
    } else {
        jobs.vcpScan.status = 'error';
        jobs.vcpScan.lastError = result.error;
        jobs.vcpScan.lastRun = new Date().toISOString();
        jobs.vcpScan.nextRun = getNextVcpScanTime().toISOString();
        console.error('[Scheduler] VCP Scan Failed:', result.error);
    }
}

async function runStockInfoUpdate() {
    console.log('[Scheduler] Starting Stock Info Update...');
    jobs.stockInfoUpdate.status = 'running';

    const result = await runPythonScript('06_collect_stock_data.py');
    jobs.stockInfoUpdate.lastRun = new Date().toISOString();

    if (result.success) {
        jobs.stockInfoUpdate.status = 'idle';
        console.log('[Scheduler] Stock Info Update Completed.');
    } else {
        jobs.stockInfoUpdate.status = 'error';
        jobs.stockInfoUpdate.lastError = result.error;
        console.error('[Scheduler] Stock Info Update Failed:', result.error);
    }
}

async function runMissingDataRecovery() {
    console.log('[Scheduler] Starting Missing Data Recovery...');
    jobs.missingDataRecovery.status = 'running';

    const result = await runPythonScript('regenerate_missing_data.py');
    jobs.missingDataRecovery.lastRun = new Date().toISOString();

    if (result.success) {
        jobs.missingDataRecovery.status = 'idle';
        console.log('[Scheduler] Missing Data Recovery Completed.');
    } else {
        jobs.missingDataRecovery.status = 'error';
        jobs.missingDataRecovery.lastError = result.error;
        console.error('[Scheduler] Missing Data Recovery Failed:', result.error);
    }
}

async function runExitMonitor() {
    console.log('[Scheduler] Starting Exit Monitor...');
    jobs.exitMonitor.status = 'running';

    const result = await runPythonScript('exit_monitor.py');
    jobs.exitMonitor.lastRun = new Date().toISOString();

    if (result.success) {
        jobs.exitMonitor.status = 'idle';
        console.log('[Scheduler] Exit Monitor Completed.');
    } else {
        jobs.exitMonitor.status = 'error';
        jobs.exitMonitor.lastError = result.error;
        console.error('[Scheduler] Exit Monitor Failed:', result.error);
    }
}

export function startScheduler() {
    console.log('[Scheduler] Initializing Cron Jobs...');

    cron.schedule('*/10 * * * *', () => {
        if (jobs.marketUpdate.status !== 'running') {
            runMarketUpdate();
        } else {
            console.log('[Scheduler] Market Update skipped (already running)');
        }
    }, {
        timezone: "Asia/Seoul"
    });

    cron.schedule('40 15 * * *', () => {
        if (jobs.vcpScan.status !== 'running') {
            runVcpScan();
        }
    }, {
        timezone: "Asia/Seoul"
    });

    cron.schedule('*/10 9-15 * * 1-5', () => {
        if (jobs.exitMonitor.status !== 'running') {
            runExitMonitor();
        }
    }, {
        timezone: "Asia/Seoul"
    });

    cron.schedule('0 18 * * 1-5', () => {
        if (jobs.exitMonitor.status !== 'running') {
            runExitMonitor();
        }
    }, {
        timezone: "Asia/Seoul"
    });

    console.log('[Scheduler] Scheduler Started.');
}

// Keep the process alive
if (require.main === module) {
    startScheduler();

    // Optional: Simple HTTP server to expose status
    const http = require('http');
    const port = 3001; // Separate port from Next.js

    const server = http.createServer((req: any, res: any) => {
        if (req.url === '/status') {
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify(jobs));
        } else if (req.url?.startsWith('/trigger/')) {
            const jobName = req.url.split('/trigger/')[1];
            if (jobName === 'market') {
                runMarketUpdate();
                res.end('Triggered Market Update');
            } else if (jobName === 'vcp') {
                runVcpScan();
                res.end('Triggered VCP Scan');
            } else if (jobName === 'stock') {
                runStockInfoUpdate();
                res.end('Triggered Stock Info Update');
            } else if (jobName === 'recovery') {
                runMissingDataRecovery();
                res.end('Triggered Missing Data Recovery');
            } else if (jobName === 'exit') {
                runExitMonitor();
                res.end('Triggered Exit Monitor');
            } else if (jobName === 'portfolio') {
                runPortfolioCalc();
                res.end('Triggered Portfolio Calculation');
            } else {
                res.writeHead(404);
                res.end('Job not found');
            }
        } else {
            res.writeHead(404);
            res.end('Not Found');
        }
    });

    server.listen(port, () => {
        console.log(`[Scheduler] Status API running on http://localhost:${port}`);
    });
}
