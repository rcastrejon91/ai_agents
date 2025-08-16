import { banner } from "../server/legal/guardrails";

export default function LegalNotice() {
  return (
    <div className="legal-notice">
      {banner}
      <style jsx>{`
        .legal-notice {
          border: 1px solid #facc15;
          background: #fef3c7;
          padding: 8px;
          color: #92400e;
          margin-bottom: 1rem;
        }
      `}</style>
    </div>
  );
}
