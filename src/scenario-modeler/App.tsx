/**
 * SaaS Scenario Modeler Widget
 *
 * Interactive financial projection tool with sliders and Chart.js visualization.
 * Ported from modelcontextprotocol/ext-apps scenario-modeler-server.
 */

import { useState, useMemo, useCallback, useEffect } from "react";
import { useWidgetProps } from "../use-widget-props";
import { useWidgetState } from "../use-widget-state";
import { SliderRow } from "./components/SliderRow";
import { MetricCard } from "./components/MetricCard";
import { ProjectionChart } from "./components/ProjectionChart";
import { calculateProjections, calculateSummary } from "./lib/calculations";
import {
  formatCurrency,
  formatPercent,
  formatCurrencySlider,
} from "./lib/formatters";
import type {
  ScenarioInputs,
  ScenarioTemplate,
  ScenarioSummary,
} from "./types";
import "./scenario-modeler.css";

interface ToolOutput {
  templates: ScenarioTemplate[];
  defaultInputs: ScenarioInputs;
}

interface ScenarioWidgetState {
  selectedTemplateId: string | null;
  selectedTemplateName: string | null;
}

// Local defaults for immediate render (should match server's DEFAULT_INPUTS)
const FALLBACK_INPUTS: ScenarioInputs = {
  startingMRR: 50000,
  monthlyGrowthRate: 5,
  monthlyChurnRate: 3,
  grossMargin: 80,
  fixedCosts: 30000,
};

const defaultToolOutput: ToolOutput = {
  templates: [],
  defaultInputs: FALLBACK_INPUTS,
};

export default function App() {
  const props = useWidgetProps<ToolOutput>(defaultToolOutput);

  return (
    <ScenarioModelerInner
      templates={props.templates}
      defaultInputs={props.defaultInputs}
    />
  );
}

interface ScenarioModelerInnerProps {
  templates: ScenarioTemplate[];
  defaultInputs: ScenarioInputs;
}

function ScenarioModelerInner({
  templates,
  defaultInputs,
}: ScenarioModelerInnerProps) {
  const [inputs, setInputs] = useState<ScenarioInputs>(FALLBACK_INPUTS);
  const [selectedTemplateId, setSelectedTemplateId] = useState<string | null>(
    null,
  );
  const [widgetState, setWidgetState] = useWidgetState<ScenarioWidgetState>({
    selectedTemplateId: null,
    selectedTemplateName: null,
  });

  // Derived state - recalculates when inputs change
  const projections = useMemo(() => calculateProjections(inputs), [inputs]);
  const summary = useMemo(
    () => calculateSummary(projections, inputs),
    [projections, inputs],
  );

  // Selected template (if any)
  const selectedTemplate = useMemo(
    () => templates.find((t) => t.id === selectedTemplateId) ?? null,
    [templates, selectedTemplateId],
  );

  // Handlers
  const handleInputChange = useCallback(
    (key: keyof ScenarioInputs, value: number) => {
      setInputs((prev) => ({ ...prev, [key]: value }));
    },
    [],
  );

  const handleReset = useCallback(() => {
    setInputs(defaultInputs);
    setSelectedTemplateId(null);
    setWidgetState({ selectedTemplateId: null, selectedTemplateName: null });
  }, [defaultInputs, setWidgetState]);

  const handleTemplateSelect = useCallback(
    (e: React.ChangeEvent<HTMLSelectElement>) => {
      const value = e.target.value;
      setSelectedTemplateId(value || null);
      const template = templates.find((t) => t.id === value);
      setWidgetState({
        selectedTemplateId: value || null,
        selectedTemplateName: template?.name || null,
      });
    },
    [templates, setWidgetState],
  );

  const handleLoadTemplate = useCallback(() => {
    if (selectedTemplate) {
      setInputs(selectedTemplate.parameters);
      setSelectedTemplateId(null);
    }
  }, [selectedTemplate]);

  return (
    <main className="main">
      {/* Header */}
      <header className="header">
        <h1 className="header-title">SaaS Scenario Modeler</h1>
        <div className="header-controls">
          <select
            className="template-select"
            value={selectedTemplateId ?? ""}
            onChange={handleTemplateSelect}
          >
            <option value="">Compare to...</option>
            {templates.map((t) => (
              <option key={t.id} value={t.id}>
                {t.icon} {t.name}
              </option>
            ))}
          </select>
          {selectedTemplate && (
            <button className="reset-button" onClick={handleLoadTemplate}>
              Load
            </button>
          )}
          <button className="reset-button" onClick={handleReset}>
            Reset
          </button>
        </div>
      </header>

      {/* Parameters */}
      <section className="parameters-section">
        <h2 className="section-title">Parameters</h2>
        <SliderRow
          label="Starting MRR"
          value={inputs.startingMRR}
          min={10000}
          max={500000}
          step={5000}
          format={formatCurrencySlider}
          onChange={(v) => handleInputChange("startingMRR", v)}
        />
        <SliderRow
          label="Growth Rate"
          value={inputs.monthlyGrowthRate}
          min={0}
          max={20}
          step={0.5}
          format={(v) => formatPercent(v)}
          onChange={(v) => handleInputChange("monthlyGrowthRate", v)}
        />
        <SliderRow
          label="Churn Rate"
          value={inputs.monthlyChurnRate}
          min={0}
          max={15}
          step={0.5}
          format={(v) => formatPercent(v)}
          onChange={(v) => handleInputChange("monthlyChurnRate", v)}
        />
        <SliderRow
          label="Gross Margin"
          value={inputs.grossMargin}
          min={50}
          max={95}
          step={5}
          format={(v) => formatPercent(v)}
          onChange={(v) => handleInputChange("grossMargin", v)}
        />
        <SliderRow
          label="Fixed Costs"
          value={inputs.fixedCosts}
          min={5000}
          max={200000}
          step={5000}
          format={formatCurrencySlider}
          onChange={(v) => handleInputChange("fixedCosts", v)}
        />
      </section>

      {/* Chart */}
      <ProjectionChart
        userProjections={projections}
        templateProjections={selectedTemplate?.projections ?? null}
        templateName={selectedTemplate?.name}
      />

      {/* Metrics */}
      <MetricsSection
        userSummary={summary}
        templateSummary={selectedTemplate?.summary ?? null}
        templateName={selectedTemplate?.name}
      />
    </main>
  );
}

interface MetricsSectionProps {
  userSummary: ScenarioSummary;
  templateSummary: ScenarioSummary | null;
  templateName?: string;
}

function MetricsSection({
  userSummary,
  templateSummary,
  templateName,
}: MetricsSectionProps) {
  const profitVariant = userSummary.totalProfit >= 0 ? "positive" : "negative";

  // Calculate comparison delta
  const profitDelta = templateSummary
    ? ((userSummary.totalProfit - templateSummary.totalProfit) /
        Math.abs(templateSummary.totalProfit)) *
      100
    : null;

  return (
    <section className="metrics-section">
      <div className="metrics-comparison">
        {/* User's scenario */}
        <div className="metrics-column">
          <h3>Your Scenario</h3>
          <div className="metrics-grid">
            <MetricCard
              label="End MRR"
              value={formatCurrency(userSummary.endingMRR)}
            />
            <MetricCard
              label="Total Revenue"
              value={formatCurrency(userSummary.totalRevenue)}
            />
            <MetricCard
              label="Total Profit"
              value={formatCurrency(userSummary.totalProfit)}
              variant={profitVariant}
            />
          </div>
        </div>

        {/* Template comparison (only when selected) */}
        {templateSummary && templateName && (
          <div className="metrics-column template">
            <h3>vs. {templateName}</h3>
            <div className="metrics-grid">
              <MetricCard
                label="End MRR"
                value={formatCurrency(templateSummary.endingMRR)}
              />
              <MetricCard
                label="Total Profit"
                value={formatCurrency(templateSummary.totalProfit)}
                variant={
                  templateSummary.totalProfit >= 0 ? "positive" : "negative"
                }
              />
            </div>
          </div>
        )}
      </div>

      {/* Summary row */}
      <div className="metrics-summary">
        <span className="summary-item">
          Break-even:{" "}
          <span className="summary-value">
            {userSummary.breakEvenMonth
              ? `Month ${userSummary.breakEvenMonth}`
              : "Not achieved"}
          </span>
        </span>
        <span className="summary-item">
          MRR Growth:{" "}
          <span
            className={`summary-value ${userSummary.mrrGrowthPct >= 0 ? "positive" : "negative"}`}
          >
            {formatPercent(userSummary.mrrGrowthPct, true)}
          </span>
        </span>
        {profitDelta !== null && (
          <span className="summary-item">
            vs. template:{" "}
            <span
              className={`summary-value ${profitDelta >= 0 ? "positive" : "negative"}`}
            >
              {formatPercent(profitDelta, true)}
            </span>
          </span>
        )}
      </div>
    </section>
  );
}
