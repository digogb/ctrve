interface StepperProps {
  currentStep: number;
  steps: { label: string }[];
}

export default function ChecklistStepper({ currentStep, steps }: StepperProps) {
  return (
    <div className="w-full">
      <div className="relative h-1 bg-gray-100 rounded-full mb-4 overflow-hidden">
        <div
          className="h-1 bg-[#003366] transition-all"
          style={{ width: `${Math.max(0, Math.min(((currentStep - 1) / steps.length) * 100, 100))}%` }}
        />
      </div>
      <div className="flex gap-2 overflow-x-auto pb-1">
        {steps.map((step, i) => {
          const num = i + 1;
          const isDone = num < currentStep;
          const isActive = num === currentStep;
          const className = isDone
            ? "bg-green-600 text-white font-semibold"
            : isActive
            ? "bg-[#003366] text-white font-semibold"
            : "bg-gray-100 text-gray-400";
          return (
            <span
              key={step.label}
              className={`shrink-0 rounded-full px-3 py-1.5 text-xs flex items-center gap-1.5 ${className}`}
            >
              <span>{num}</span>
              <span>{step.label}</span>
            </span>
          );
        })}
      </div>
    </div>
  );
}
