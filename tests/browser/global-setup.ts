import { spawn, ChildProcess } from "child_process";

const SERVER_URL = "http://localhost:8000";

let serverProcess: ChildProcess | null = null;

async function isServerRunning(): Promise<boolean> {
  try {
    const response = await fetch(`${SERVER_URL}/tools`, { signal: AbortSignal.timeout(1000) });
    return response.ok;
  } catch {
    return false;
  }
}

async function startServer(): Promise<ChildProcess> {
  return new Promise((resolve, reject) => {
    const proc = spawn("pnpm", ["run", "server"], {
      cwd: process.cwd(),
      detached: true,
      stdio: "pipe",
    });

    let started = false;
    const timeout = globalThis.setTimeout(() => {
      if (!started) {
        reject(new Error("Server failed to start within 30 seconds"));
      }
    }, 30000);

    proc.stdout?.on("data", (data) => {
      const output = data.toString();
      if (output.includes("Application startup complete") && !started) {
        started = true;
        globalThis.clearTimeout(timeout);
        resolve(proc);
      }
    });

    proc.stderr?.on("data", (data) => {
      const output = data.toString();
      if (output.includes("Application startup complete") && !started) {
        started = true;
        globalThis.clearTimeout(timeout);
        resolve(proc);
      }
    });

    proc.on("error", (err) => {
      globalThis.clearTimeout(timeout);
      reject(err);
    });
  });
}

async function globalSetup() {
  if (!(await isServerRunning())) {
    serverProcess = await startServer();
    // Store PID for teardown
    process.env.TEST_SERVER_PID = String(serverProcess.pid);
  }
}

export default globalSetup;
