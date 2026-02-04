async function globalTeardown() {
  const pid = process.env.TEST_SERVER_PID;
  if (pid) {
    try {
      process.kill(-Number(pid), "SIGTERM");
    } catch {
      // Server already stopped
    }
  }
}

export default globalTeardown;
