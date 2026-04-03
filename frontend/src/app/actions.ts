"use server";

import { exec } from "child_process";
import path from "path";
import { revalidatePath } from "next/cache";

interface VcpScanOptions {
    date?: string;
}

export async function runVcpScan(options?: VcpScanOptions) {
    const scriptPath = path.join(process.cwd(), "..", "Scripts", "02_scan_vcp.py");
    const dateArg = options?.date ? `--date ${options.date}` : "";

    return new Promise<{ success: boolean; message: string }>((resolve) => {
        const scanCmd = `python "${scriptPath}" ${dateArg}`;

        exec(scanCmd, (error, stdout, stderr) => {
            if (error) {
                console.error("Scan Error:", stderr || error.message);
                resolve({ success: false, message: `Scan failed: ${stderr || error.message}` });
                return;
            }
            console.log("Scan Output:", stdout);

            console.log("Scan complete, starting visualization...");
            const vizScript = path.join(process.cwd(), "..", "Scripts", "03_visualize_vcp.py");
            const vizCmd = `python "${vizScript}" ${dateArg}`;

            exec(vizCmd, (vError, vStdout, vStderr) => {
                if (vError) {
                    console.error(`Viz error: ${vError}`);
                    revalidatePath("/");
                    revalidatePath("/vcp");
                    resolve({ success: true, message: `Scan complete, but Chart gen failed: ${vStderr || vError.message}` });
                    return;
                }
                console.log("Viz Output:", vStdout);

                revalidatePath("/");
                revalidatePath("/vcp");
                resolve({ success: true, message: "Scan and Chart Generation Complete!" });
            });
        });
    });
}
