export function detectRedFlags(text: string) {
  const flags = [
    /chest pain|pressure/i,
    /shortness of breath|difficulty breathing/i,
    /stroke|facial droop|slurred speech/i,
    /suicidal|self\-harm/i,
    /anaphylaxis|throat swelling/i,
    /sepsis|fever.*(confusion|rapid heart)/i,
  ].filter((r) => r.test(text));
  return flags.length > 0;
}
