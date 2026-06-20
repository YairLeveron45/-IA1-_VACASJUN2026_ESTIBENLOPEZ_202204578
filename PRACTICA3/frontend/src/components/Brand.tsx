import { ScanLine } from "lucide-react";

interface BrandProps {
  compact?: boolean;
}

export function Brand({ compact = false }: BrandProps) {
  return (
    <div className={`brand ${compact ? "brand--compact" : ""}`}>
      <div className="brand__mark">
        <ScanLine size={compact ? 19 : 24} strokeWidth={2.2} />
      </div>
      <div>
        <strong>SmartInvoice</strong>
        {!compact && <span>Document intelligence</span>}
      </div>
    </div>
  );
}
