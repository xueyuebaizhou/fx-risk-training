import Image from "next/image";

export function Brand({ compact = false }: { compact?: boolean }) {
  return (
    <div className={`brand ${compact ? "brand-compact" : ""}`}>
      <Image
        src="/shanghe-logo.png"
        alt="熵合科技"
        width={112}
        height={74}
        priority
        className="brand-image"
      />
      {!compact && (
        <div className="brand-copy">
          <strong>跨境汇率实训</strong>
          <span>大连理工大学熵合科技团队</span>
        </div>
      )}
    </div>
  );
}
