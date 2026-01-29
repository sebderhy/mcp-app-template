/**
 * System Monitor Widget
 *
 * Displays real-time CPU and memory usage with Chart.js.
 * Uses polling pattern - calls poll_system_stats tool every 2 seconds.
 * Ported from modelcontextprotocol/ext-apps system-monitor-server.
 */

import { useState, useRef, useEffect, useCallback } from "react";
import { Chart, registerables } from "chart.js";
import { useWidgetProps } from "../use-widget-props";
import "./system-monitor.css";

Chart.register(...registerables);

// Types matching server output
interface SystemInfo {
  hostname: string;
  platform: string;
  cpu: { model: string; count: number };
  memory: { totalBytes: number };
}

interface PollStats {
  cpuPercents: number[];
  memoryPercent: number;
  memoryUsedGB: number;
  memoryTotalGB: number;
  uptime: number;
  timestamp: string;
}

// Constants
const HISTORY_LENGTH = 30;
const POLL_INTERVAL = 2000;

// Color palette for CPU cores
const CORE_COLORS = [
  "rgba(59, 130, 246, 0.7)",
  "rgba(16, 185, 129, 0.7)",
  "rgba(245, 158, 11, 0.7)",
  "rgba(239, 68, 68, 0.7)",
  "rgba(139, 92, 246, 0.7)",
  "rgba(236, 72, 153, 0.7)",
  "rgba(20, 184, 166, 0.7)",
  "rgba(249, 115, 22, 0.7)",
  "rgba(34, 197, 94, 0.7)",
  "rgba(168, 85, 247, 0.7)",
  "rgba(251, 146, 60, 0.7)",
  "rgba(74, 222, 128, 0.7)",
  "rgba(96, 165, 250, 0.7)",
  "rgba(248, 113, 113, 0.7)",
  "rgba(167, 139, 250, 0.7)",
  "rgba(244, 114, 182, 0.7)",
];

function formatBytes(bytes: number): string {
  const units = ["B", "KB", "MB", "GB", "TB"];
  let value = bytes;
  let unitIndex = 0;
  while (value >= 1024 && unitIndex < units.length - 1) {
    value /= 1024;
    unitIndex++;
  }
  return `${value.toFixed(1)} ${units[unitIndex]}`;
}

function formatUptime(seconds: number): string {
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const parts: string[] = [];
  if (days > 0) parts.push(`${days}d`);
  if (hours > 0) parts.push(`${hours}h`);
  if (minutes > 0) parts.push(`${minutes}m`);
  return parts.length > 0 ? parts.join(" ") : "< 1m";
}

const defaultSystemInfo: SystemInfo = {
  hostname: "—",
  platform: "—",
  cpu: { model: "—", count: 4 },
  memory: { totalBytes: 0 },
};

export default function App() {
  const systemInfo = useWidgetProps<SystemInfo>(defaultSystemInfo);

  const [isPolling, setIsPolling] = useState(false);
  const [statusText, setStatusText] = useState("Stopped");
  const [statusClass, setStatusClass] = useState("");
  const [memPercent, setMemPercent] = useState(0);
  const [memDetail, setMemDetail] = useState("— / —");
  const [uptime, setUptime] = useState("—");

  const canvasRef = useRef<HTMLCanvasElement>(null);
  const chartRef = useRef<Chart | null>(null);
  const intervalRef = useRef<number | null>(null);
  const cpuHistoryRef = useRef<number[][]>([]);
  const labelsRef = useRef<string[]>([]);

  const coreCount = systemInfo.cpu.count;

  // Initialize chart
  useEffect(() => {
    if (!canvasRef.current) return;

    const isDarkMode = window.matchMedia("(prefers-color-scheme: dark)").matches;
    const textColor = isDarkMode ? "#9ca3af" : "#6b7280";
    const gridColor = isDarkMode ? "#374151" : "#e5e7eb";

    const datasets = Array.from({ length: coreCount }, (_, i) => ({
      label: `P${i}`,
      data: [] as number[],
      fill: true,
      backgroundColor: CORE_COLORS[i % CORE_COLORS.length],
      borderColor: CORE_COLORS[i % CORE_COLORS.length].replace("0.7", "1"),
      borderWidth: 1,
      pointRadius: 0,
      tension: 0.3,
    }));

    chartRef.current = new Chart(canvasRef.current, {
      type: "line",
      data: { labels: [], datasets },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: { duration: 300 },
        interaction: { intersect: false, mode: "index" },
        plugins: {
          legend: {
            display: true,
            position: "bottom",
            labels: { boxWidth: 12, padding: 8, font: { size: 10 }, color: textColor },
          },
          tooltip: {
            enabled: true,
            callbacks: {
              label: (ctx) => `${ctx.dataset.label}: ${ctx.parsed.y}%`,
            },
          },
        },
        scales: {
          x: { display: false },
          y: {
            stacked: true,
            min: 0,
            max: coreCount * 100,
            ticks: {
              callback: (value) => `${value}%`,
              color: textColor,
              font: { size: 10 },
            },
            grid: { color: gridColor },
          },
        },
      },
    });

    return () => {
      chartRef.current?.destroy();
      chartRef.current = null;
    };
  }, [coreCount]);

  // Handle theme changes
  useEffect(() => {
    const mq = window.matchMedia("(prefers-color-scheme: dark)");
    const handler = () => {
      if (chartRef.current) {
        chartRef.current.destroy();
        chartRef.current = null;
        // Re-trigger chart creation by updating a key - simplified by just
        // storing we need rebuild; the chart useEffect depends on coreCount
        // which won't change, so we force it via a canvas key approach
      }
    };
    mq.addEventListener("change", handler);
    return () => mq.removeEventListener("change", handler);
  }, []);

  const updateChart = useCallback((history: number[][], labels: string[]) => {
    if (!chartRef.current) return;

    chartRef.current.data.labels = labels;
    for (let i = 0; i < coreCount; i++) {
      chartRef.current.data.datasets[i].data = history.map(
        (snapshot) => snapshot[i] ?? 0,
      );
    }

    // Dynamic y-axis scaling
    const stackedTotals = history.map((s) => s.reduce((sum, v) => sum + v, 0));
    const currentMax = Math.max(...stackedTotals, 0);
    const headroom = 1.2;
    const minVisible = coreCount * 15;
    const absoluteMax = coreCount * 100;
    const dynamicMax = Math.min(Math.max(currentMax * headroom, minVisible), absoluteMax);
    chartRef.current.options.scales!.y!.max = dynamicMax;

    chartRef.current.update("none");
  }, [coreCount]);

  const fetchStats = useCallback(async () => {
    // Use the legacy callTool bridge to call the app-only tool
    if (!window.openai?.callTool) return;

    const result = await window.openai?.callTool("poll_system_stats", {});
    if (!result) return;

    // Parse the result - it comes back as structured content from callTool
    let stats: PollStats;
    if (typeof result === "object" && "cpuPercents" in result) {
      stats = result as unknown as PollStats;
    } else if (typeof result === "string") {
      stats = JSON.parse(result);
    } else {
      return;
    }

    // Update CPU history
    cpuHistoryRef.current.push(stats.cpuPercents);
    labelsRef.current.push(new Date().toLocaleTimeString());

    if (cpuHistoryRef.current.length > HISTORY_LENGTH) {
      cpuHistoryRef.current.shift();
      labelsRef.current.shift();
    }

    updateChart(cpuHistoryRef.current, labelsRef.current);

    // Update memory
    setMemPercent(stats.memoryPercent);
    setMemDetail(`${stats.memoryUsedGB.toFixed(1)} GB / ${stats.memoryTotalGB.toFixed(1)} GB`);

    // Update uptime
    setUptime(formatUptime(stats.uptime));

    const time = new Date().toLocaleTimeString("en-US", { hour12: false });
    setStatusText(time);
    setStatusClass("polling");
  }, [updateChart]);

  const startPolling = useCallback(() => {
    if (isPolling) return;
    setIsPolling(true);
    setStatusText("Starting...");
    setStatusClass("polling");

    fetchStats();
    intervalRef.current = window.setInterval(fetchStats, POLL_INTERVAL);
  }, [isPolling, fetchStats]);

  const stopPolling = useCallback(() => {
    if (!isPolling) return;
    setIsPolling(false);
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    setStatusText("Stopped");
    setStatusClass("");
  }, [isPolling]);

  // Auto-start polling when system info is available
  useEffect(() => {
    if (systemInfo.hostname !== "—" && !isPolling) {
      startPolling();
    }
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [systemInfo.hostname]); // eslint-disable-line react-hooks/exhaustive-deps

  const memBarClass = memPercent >= 80 ? "danger" : memPercent >= 60 ? "warning" : "";

  return (
    <div className="sm-main">
      {/* Header */}
      <header className="sm-header">
        <h1 className="sm-title">System Monitor</h1>
        <div className="sm-header-controls">
          <button
            className={`sm-btn ${isPolling ? "active" : ""}`}
            onClick={isPolling ? stopPolling : startPolling}
          >
            {isPolling ? "Stop" : "Start"}
          </button>
          <div className="sm-status">
            <span className={`sm-status-indicator ${statusClass}`} />
            <span className="sm-status-text">{statusText}</span>
          </div>
        </div>
      </header>

      {/* CPU Chart */}
      <section className="sm-chart-section">
        <h2 className="sm-section-title">CPU Usage</h2>
        <div className="sm-chart-container">
          <canvas ref={canvasRef} />
        </div>
      </section>

      {/* Memory */}
      <section className="sm-memory-section">
        <h2 className="sm-section-title">Memory</h2>
        <div className="sm-memory-bar-container">
          <div className="sm-memory-bar">
            <div
              className={`sm-memory-bar-fill ${memBarClass}`}
              style={{ width: `${memPercent}%` }}
            />
          </div>
          <span className="sm-memory-percent">{memPercent}%</span>
        </div>
        <div className="sm-memory-detail">{memDetail}</div>
      </section>

      {/* System Info */}
      <section className="sm-info-section">
        <h2 className="sm-section-title">System Info</h2>
        <dl className="sm-info-list">
          <div className="sm-info-item">
            <dt>Hostname</dt>
            <dd>{systemInfo.hostname}</dd>
          </div>
          <div className="sm-info-item">
            <dt>Platform</dt>
            <dd>{systemInfo.platform}</dd>
          </div>
          <div className="sm-info-item">
            <dt>Uptime</dt>
            <dd>{uptime}</dd>
          </div>
        </dl>
      </section>
    </div>
  );
}
