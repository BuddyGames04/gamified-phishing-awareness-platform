import React, { useEffect } from "react";

type Props = {
  count: number;
  onClose: () => void;
};

export default function WaveToast({ count, onClose }: Props) {
  useEffect(() => {
    const t = setTimeout(onClose, 4500);
    return () => clearTimeout(t);
  }, [onClose]);

  return (
    <div
      style={{
        position: "fixed",
        top: 16,
        right: 16,
        zIndex: 9999,
        background: "rgba(20,20,20,0.95)",
        color: "white",
        padding: "12px 14px",
        borderRadius: 10,
        boxShadow: "0 8px 24px rgba(0,0,0,0.25)",
        maxWidth: 320,
        cursor: "pointer",
        userSelect: "none",
      }}
      onClick={onClose}
      role="status"
      aria-live="polite"
      title="Click to dismiss"
    >
      <div style={{ fontWeight: 700, marginBottom: 4 }}>New email</div>
      <div style={{ opacity: 0.9 }}>
        {count === 1 ? "1 new message arrived." : `${count} new messages arrived.`}
      </div>
      <div style={{ fontSize: 12, opacity: 0.75, marginTop: 6 }}>
        Click to dismiss
      </div>
    </div>
  );
}