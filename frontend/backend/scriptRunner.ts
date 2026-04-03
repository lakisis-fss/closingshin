import { spawn } from 'child_process';
import path from 'path';
import fs from 'fs';
import PocketBase from 'pocketbase';
import dotenv from 'dotenv';

// Constants
// process.cwd() is expected to be '.../frontend' when running 'npm run scheduler'
const FRONTEND_ROOT = process.cwd();
const PROJECT_ROOT = path.resolve(FRONTEND_ROOT, '..'); // '.../ClosingSHIN'
const SCRIPTS_DIR = path.resolve(PROJECT_ROOT, 'Scripts');

/**
 * Detects the Python executable path.
 * Prioritizes the virtual environment in the project root.
 */
function getPythonPath(): string {
    // Docker 환경: /app/venv/bin/python3
    const dockerVenvPython = '/app/venv/bin/python3';

    // Windows 로컬: ClosingSHIN/venv/Scripts/python.exe
    const venvPythonWin = path.join(PROJECT_ROOT, 'venv', 'Scripts', 'python.exe');

    // Unix 로컬: ClosingSHIN/venv/bin/python
    const venvPythonUnix = path.join(PROJECT_ROOT, 'venv', 'bin', 'python');

    if (fs.existsSync(dockerVenvPython)) return dockerVenvPython;
    if (fs.existsSync(venvPythonWin)) return venvPythonWin;
    if (fs.existsSync(venvPythonUnix)) return venvPythonUnix;

    return 'python'; // Fallback to system python
}

interface ScriptResult {
    success: boolean;
    output: string;
    error?: string;
    code: number | null;
}

/**
 * Runs a Python script located in the Scripts directory.
 * @param scriptName The filename of the script (e.g., '04_market_status.py')
 * @param args Optional arguments for the script
 */
export function runPythonScript(scriptName: string, args: string[] = []): Promise<ScriptResult> {
    return new Promise((resolve) => {
        const pythonPath = getPythonPath();
        const scriptPath = path.join(SCRIPTS_DIR, scriptName);

        if (!fs.existsSync(scriptPath)) {
            resolve({
                success: false,
                output: '',
                error: `Script not found: ${scriptPath}`,
                code: -1
            });
            return;
        }

        console.log(`[ScriptRunner] Executing: ${pythonPath} ${scriptPath} ${args.join(' ')}`);

        const pythonProcess = spawn(pythonPath, [scriptPath, ...args], {
            cwd: SCRIPTS_DIR, // Run in Scripts directory context
            env: { ...process.env, PYTHONIOENCODING: 'utf-8' },
        });

        let stdout = '';
        let stderr = '';

// Load environment variables from .env
dotenv.config({ path: path.resolve(FRONTEND_ROOT, '.env') });

const pb = new PocketBase(process.env.PB_URL || 'http://127.0.0.1:8090');
pb.autoCancellation(false);

let initPromise: Promise<void> | null = null;

async function initPB() {
    if (pb.authStore.token) return;
    if (initPromise) return initPromise;

    initPromise = (async () => {
        try {
            await pb.collection('_superusers').authWithPassword(
                process.env.PB_EMAIL || 'admin@example.com',
                process.env.PB_PASSWORD || 'admin1234'
            );
        } catch (e) {
            console.error('[ScriptRunner] PB Auth Failed:', e);
            throw e;
        } finally {
            initPromise = null;
        }
    })();

    return initPromise;
}

let logQueue: Promise<any> = Promise.resolve();

async function appendLog(message: string, scriptName: string, level: string = 'INFO') {
    // Sequential processing to avoid parallel request spam
    logQueue = logQueue.then(async () => {
        try {
            await initPB();
            await pb.collection('system_logs').create({
                message: message,
                source: scriptName,
                level: level
            });
        } catch (e) {
            // Don't log to console about failed logs too often to avoid noise
            // unless it's an auth error
            if (e instanceof Error && e.message.includes('autocancelled')) return;
            console.error('[ScriptRunner] Failed to log to PB:', e);
        }
    });
    
    return logQueue;
}

        pythonProcess.stdout.on('data', (data) => {
            const chunk = data.toString();
            stdout += chunk;
            // Trim whitespace to avoid excessive newlines in log file if chunk is just newline
            if (chunk.trim()) {
                appendLog(chunk.trim(), scriptName, 'INFO');
            }
        });

        pythonProcess.stderr.on('data', (data) => {
            const chunk = data.toString();
            stderr += chunk;
            console.error(`[${scriptName} ERROR] ${chunk.trim()}`);
            appendLog(chunk.trim(), scriptName, 'ERROR');
        });

        pythonProcess.on('close', (code) => {
            console.log(`[ScriptRunner] ${scriptName} exited with code ${code}`);
            resolve({
                success: code === 0,
                output: stdout,
                error: code !== 0 ? stderr : undefined,
                code
            });
        });

        pythonProcess.on('error', (err) => {
            console.error(`[ScriptRunner] Failed to start subprocess: ${err.message}`);
            resolve({
                success: false,
                output: stdout,
                error: err.message,
                code: -1
            });
        });
    });
}
