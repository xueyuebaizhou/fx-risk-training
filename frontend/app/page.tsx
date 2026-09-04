import { AppShell } from "@/components/app-shell";
import { TrainingProvider } from "@/lib/training-context";

export default function Home() {
  return (
    <TrainingProvider>
      <AppShell />
    </TrainingProvider>
  );
}
