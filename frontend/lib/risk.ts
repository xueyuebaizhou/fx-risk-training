import type { AnalysisData, RiskMetrics, ScenarioInputs, StrategyRow } from "@/lib/types";

const quantile = (values: number[], q: number) => {
  const ordered = [...values].sort((a, b) => a - b);
  const index = (ordered.length - 1) * q;
  const lower = Math.floor(index);
  const fraction = index - lower;
  return ordered[lower + 1] === undefined
    ? ordered[lower]
    : ordered[lower] + fraction * (ordered[lower + 1] - ordered[lower]);
};

const riskLevel = (ratio: number) => {
  if (ratio < 0.02) return "低风险";
  if (ratio < 0.05) return "中风险";
  return "高风险";
};

export function calculateMetrics(
  terminalRates: number[],
  inputs: ScenarioInputs,
  spotRate: number,
  ratio: number,
): RiskMetrics {
  const incomes = terminalRates.map(
    (terminal) => inputs.amount * (ratio * inputs.forwardRate + (1 - ratio) * terminal),
  );
  const budgetIncome = inputs.amount * inputs.budgetRate;
  const spotReferenceIncome = inputs.amount * spotRate;
  const meanIncome = incomes.reduce((sum, value) => sum + value, 0) / incomes.length;
  const q05Income = quantile(incomes, 0.05);
  const variance = incomes.reduce((sum, value) => sum + (value - meanIncome) ** 2, 0) / incomes.length;
  const losses = incomes.map((income) => spotReferenceIncome - income);
  const var95 = Math.max(quantile(losses, 0.95), 0);
  const cfar95 = Math.max(budgetIncome - q05Income, 0);
  const riskRatio = cfar95 / budgetIncome;
  return {
    meanIncome,
    q05Income,
    incomeStd: Math.sqrt(variance),
    var95,
    cfar95,
    riskRatio,
    riskLevel: riskLevel(riskRatio),
  };
}

function histogram(values: number[], bins = 44) {
  const min = Math.min(...values);
  const max = Math.max(...values);
  if (min === max) return [{ x: min, count: values.length }];
  const width = (max - min) / bins;
  const counts = Array.from({ length: bins }, () => 0);
  values.forEach((value) => {
    const index = Math.min(Math.floor((value - min) / width), bins - 1);
    counts[index] += 1;
  });
  return counts.map((count, index) => ({ x: min + width * (index + 0.5), count }));
}

export function deriveAnalysis(base: AnalysisData, inputs: ScenarioInputs): AnalysisData {
  const terminalRates = base.simulation.terminalRates;
  const spotRate = base.inputs.spotRate;
  const unhedged = calculateMetrics(terminalRates, inputs, spotRate, 0);
  const selected = calculateMetrics(terminalRates, inputs, spotRate, inputs.hedgeRatio);
  const strategies: StrategyRow[] = [0, 0.25, 0.5, 0.75, 1].map((ratio) => {
    const metrics = calculateMetrics(terminalRates, inputs, spotRate, ratio);
    return {
      ...metrics,
      ratio,
      riskReduction: unhedged.cfar95
        ? (unhedged.cfar95 - metrics.cfar95) / unhedged.cfar95
        : 0,
    };
  });
  const incomes = terminalRates.map(
    (terminal) =>
      inputs.amount *
      (inputs.hedgeRatio * inputs.forwardRate + (1 - inputs.hedgeRatio) * terminal),
  );
  return {
    ...base,
    inputs: { ...inputs, spotRate },
    exposure: {
      direction: "美元应收",
      budgetIncome: inputs.amount * inputs.budgetRate,
      spotReferenceIncome: inputs.amount * spotRate,
      unhedged,
    },
    strategy: {
      lockedAmount: inputs.amount * inputs.hedgeRatio,
      selected,
      cfarReduction: unhedged.cfar95
        ? (unhedged.cfar95 - selected.cfar95) / unhedged.cfar95
        : 0,
      meanHedgeEffect:
        inputs.amount *
        inputs.hedgeRatio *
        (inputs.forwardRate - base.simulation.terminalMean),
    },
    simulation: {
      ...base.simulation,
      incomeHistogram: histogram(incomes.map((value) => value / 10_000)),
    },
    strategies,
  };
}
