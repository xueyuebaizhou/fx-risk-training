export type StepId = "case" | "model" | "exposure" | "strategy" | "simulation" | "report";

export type ScenarioInputs = {
  amount: number;
  termDays: number;
  budgetRate: number;
  forwardRate: number;
  hedgeRatio: number;
};

export type MarketPoint = {
  date: string;
  rate: number;
  returnPct: number | null;
  volatilityPct: number | null;
};

export type MarketData = {
  pair: string;
  unit: string;
  spotRate: number;
  source: string;
  sourceUrl: string;
  retrievedAt: string;
  mode: string;
  startDate: string;
  endDate: string;
  observations: number;
  series: MarketPoint[];
};

export type RiskMetrics = {
  meanIncome: number;
  q05Income: number;
  incomeStd: number;
  var95: number;
  cfar95: number;
  riskRatio: number;
  riskLevel: string;
};

export type StrategyRow = RiskMetrics & {
  ratio: number;
  riskReduction: number;
};

export type AnalysisData = {
  inputs: ScenarioInputs & { spotRate: number };
  model: {
    predictionNextDay: number;
    previousRate: number;
    direction: string;
    mae: number;
    rmse: number;
    directionAccuracy: number;
    dailyVolatility: number;
    annualVolatility: number;
    dailyDrift: number;
    marketState: string;
    volatilityPercentile: number;
    sampleStartDate: string;
    sampleEndDate: string;
    sampleSize: number;
    trainSize: number;
    testSize: number;
    featureImportance: { feature: string; importance: number }[];
    testSeries: { date: string; actual: number; predicted: number }[];
    conditionalVolatility: { date: string; volatilityPct: number }[];
  };
  exposure: {
    direction: string;
    budgetIncome: number;
    spotReferenceIncome: number;
    unhedged: RiskMetrics;
  };
  strategy: {
    lockedAmount: number;
    selected: RiskMetrics;
    cfarReduction: number;
    meanHedgeEffect: number;
  };
  simulation: {
    pathsCount: number;
    displayPathsCount: number;
    tradingDays: number;
    seed: number;
    terminalMean: number;
    terminalQ05: number;
    paths: { id: number; values: number[] }[];
    terminalRates: number[];
    terminalHistogram: { x: number; count: number }[];
    incomeHistogram: { x: number; count: number }[];
  };
  strategies: StrategyRow[];
};
