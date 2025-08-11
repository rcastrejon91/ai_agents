import React from 'react';
import { banner } from '../../../server/legal/guardrails';

export default function LegalNotice() {
  return <div style={{ background: '#fff3cd', color: '#664d03', padding: '8px', border: '1px solid #ffeeba' }}>{banner}</div>;
}
