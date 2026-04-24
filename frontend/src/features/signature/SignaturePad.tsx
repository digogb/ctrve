import { useEffect, useRef } from "react";
import ReactSignatureCanvas from "react-signature-canvas";
import { Button } from "@/components/ui/button";

interface SignaturePadProps {
  value: string | null;
  onChange: (value: string | null) => void;
  label: string;
  readOnly?: boolean;
}

export default function SignaturePad({ value, onChange, label, readOnly }: SignaturePadProps) {
  const sigRef = useRef<ReactSignatureCanvas>(null);

  useEffect(() => {
    if (!readOnly && sigRef.current) {
      if (!value) {
        sigRef.current.clear();
      } else {
        sigRef.current.fromDataURL(value);
      }
    }
  }, [value, readOnly]);

  if (readOnly) {
    if (!value) return null;
    return (
      <div data-testid="signature-readonly">
        <p className="mb-1 text-sm font-medium">{label}</p>
        <img src={value} alt={label} className="rounded-lg border border-border" />
      </div>
    );
  }

  const handleEnd = () => {
    if (sigRef.current && !sigRef.current.isEmpty()) {
      onChange(sigRef.current.toDataURL("image/png"));
    }
  };

  const handleClear = () => {
    sigRef.current?.clear();
    onChange(null);
  };

  return (
    <div data-testid="signature-pad">
      <p className="mb-1 text-sm font-medium">{label}</p>
      <div className="rounded-lg border border-border">
        <ReactSignatureCanvas
          ref={sigRef}
          penColor="#000"
          canvasProps={{ className: "w-full h-40" }}
          onEnd={handleEnd}
        />
      </div>
      <Button type="button" variant="outline" size="sm" onClick={handleClear} className="mt-1">
        Limpar
      </Button>
    </div>
  );
}
