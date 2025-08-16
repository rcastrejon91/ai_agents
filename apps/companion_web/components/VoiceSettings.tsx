import React from 'react';

interface VoiceSettingsProps {
  settings: {
    pitch: number;
    rate: number;
    volume: number;
  };
  setSettings: (settings: { pitch: number; rate: number; volume: number }) => void;
}

export default function VoiceSettings({ settings, setSettings }: VoiceSettingsProps) {
  const handleChange = (key: keyof VoiceSettingsProps['settings'], value: string) => {
    setSettings({ ...settings, [key]: parseFloat(value) });
  };

  return (
    <div className="voice-settings">
      <label>
        Pitch: {settings.pitch}
        <input
          type="range"
          min="0.5"
          max="2"
          step="0.1"
          value={settings.pitch}
          onChange={(e) => handleChange('pitch', e.target.value)}
        />
      </label>
      <label>
        Rate: {settings.rate}
        <input
          type="range"
          min="0.5"
          max="2"
          step="0.1"
          value={settings.rate}
          onChange={(e) => handleChange('rate', e.target.value)}
        />
      </label>
      <label>
        Volume: {settings.volume}
        <input
          type="range"
          min="0"
          max="1"
          step="0.1"
          value={settings.volume}
          onChange={(e) => handleChange('volume', e.target.value)}
        />
      </label>
    </div>
  );
}

