"use client";

import {
  createContext,
  type ReactNode,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

import { fetchMarket, requestAnalysis } from "@/lib/api";
import { deriveAnalysis } from "@/lib/risk";
import type { AnalysisData, MarketData, ScenarioInputs, StepId } from "@/lib/types";

const DEFAULT_INPUTS: ScenarioInputs = {
  amount: 1_000_000,
  termDays: 90,
  budgetRate: 7.1,
  forwardRate: 7.08,
  hedgeRatio: 0.5,
};

type TrainingContextValue = {
  activeStep: StepId;
  setActiveStep: (step: StepId) => void;
  inputs: ScenarioInputs;
  updateInput: <K extends keyof ScenarioInputs>(key: K, value: ScenarioInputs[K]) => void;
  market: MarketData | null;
  analysis: AnalysisData | null;
  loadingMarket: boolean;
  runningAnalysis: boolean;
  error: string | null;
  analysisNeedsRefresh: boolean;
  runAnalysis: () => Promise<void>;
};

const TrainingContext = createContext<TrainingContextValue | null>(null);

export function TrainingProvider({ children }: { children: ReactNode }) {
  const [activeStep, setActiveStepState] = useState<StepId>("case");
  const [inputs, setInputs] = useState(DEFAULT_INPUTS);
  const [market, setMarket] = useState<MarketData | null>(null);
  const [baseAnalysis, setBaseAnalysis] = useState<AnalysisData | null>(null);
  const [loadingMarket, setLoadingMarket] = useState(true);
  const [runningAnalysis, setRunningAnalysis] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchMarket()
      .then((value) => {
        setMarket(value);
        setError(null);
      })
      .catch((reason: unknown) => {
        setError(reason instanceof Error ? reason.message : "真实汇率数据读取失败。 ");
      })
      .finally(() => setLoadingMarket(false));
  }, []);

  useEffect(() => {
    window.localStorage.setItem("fx-training-inputs-v2", JSON.stringify(inputs));
  }, [inputs]);

  const setActiveStep = useCallback((step: StepId) => {
    setActiveStepState(step);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }, []);

  const updateInput = useCallback(
    <K extends keyof ScenarioInputs>(key: K, value: ScenarioInputs[K]) => {
      setInputs((current) => ({ ...current, [key]: value }));
      setError(null);
    },
    [],
  );

  const analysisNeedsRefresh = Boolean(
    baseAnalysis && baseAnalysis.inputs.termDays !== inputs.termDays,
  );

  const analysis = useMemo(() => {
    if (!baseAnalysis || analysisNeedsRefresh) return null;
    return deriveAnalysis(baseAnalysis, inputs);
  }, [baseAnalysis, inputs, analysisNeedsRefresh]);

  const runAnalysis = useCallback(async () => {
    setRunningAnalysis(true);
    setError(null);
    try {
      const result = await requestAnalysis(inputs);
      setBaseAnalysis(result);
    } catch (reason: unknown) {
      setError(reason instanceof Error ? reason.message : "模型计算失败，请稍后重试。 ");
    } finally {
      setRunningAnalysis(false);
    }
  }, [inputs]);

  const value = useMemo<TrainingContextValue>(
    () => ({
      activeStep,
      setActiveStep,
      inputs,
      updateInput,
      market,
      analysis,
      loadingMarket,
      runningAnalysis,
      error,
      analysisNeedsRefresh,
      runAnalysis,
    }),
    [
      activeStep,
      setActiveStep,
      inputs,
      updateInput,
      market,
      analysis,
      loadingMarket,
      runningAnalysis,
      error,
      analysisNeedsRefresh,
      runAnalysis,
    ],
  );

  return <TrainingContext.Provider value={value}>{children}</TrainingContext.Provider>;
}

export function useTraining() {
  const context = useContext(TrainingContext);
  if (!context) throw new Error("useTraining must be used inside TrainingProvider");
  return context;
}
