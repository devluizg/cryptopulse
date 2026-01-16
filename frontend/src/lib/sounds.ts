/**
 * CryptoPulse - Sound Manager
 */

import { AlertSeverity } from '@/types';

type SoundType = 'alert' | 'critical' | 'warning' | 'info' | 'success' | 'notification';

const SOUND_FREQUENCIES: Record<SoundType, number[]> = {
  critical: [880, 1100, 880, 1100],
  warning: [660, 880],
  info: [523, 659],
  alert: [784, 988],
  success: [523, 659, 784],
  notification: [587],
};

class SoundManager {
  private audioContext: AudioContext | null = null;
  private config = { enabled: true, volume: 0.5 };

  constructor() {
    if (typeof window !== 'undefined') this.loadConfig();
  }

  private initAudioContext(): AudioContext {
    if (!this.audioContext) {
      this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
    }
    return this.audioContext;
  }

  private loadConfig(): void {
    try {
      const saved = localStorage.getItem('cryptopulse-sound-config');
      if (saved) this.config = { ...this.config, ...JSON.parse(saved) };
    } catch (e) {}
  }

  private saveConfig(): void {
    try {
      localStorage.setItem('cryptopulse-sound-config', JSON.stringify(this.config));
    } catch (e) {}
  }

  private playTone(frequency: number, duration: number): void {
    try {
      const ctx = this.initAudioContext();
      const oscillator = ctx.createOscillator();
      const gainNode = ctx.createGain();
      
      oscillator.connect(gainNode);
      gainNode.connect(ctx.destination);
      oscillator.type = 'sine';
      oscillator.frequency.value = frequency;
      
      gainNode.gain.setValueAtTime(0, ctx.currentTime);
      gainNode.gain.linearRampToValueAtTime(this.config.volume, ctx.currentTime + 0.01);
      gainNode.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + duration / 1000);
      
      oscillator.start(ctx.currentTime);
      oscillator.stop(ctx.currentTime + duration / 1000);
    } catch (e) {}
  }

  async play(type: SoundType): Promise<void> {
    if (!this.config.enabled || typeof window === 'undefined') return;
    const frequencies = SOUND_FREQUENCIES[type];
    for (const freq of frequencies) {
      this.playTone(freq, 150);
      await new Promise(r => setTimeout(r, 200));
    }
  }

  async playAlertSound(severity: AlertSeverity): Promise<void> {
    await this.play(severity);
  }

  setEnabled(enabled: boolean): void { this.config.enabled = enabled; this.saveConfig(); }
  setVolume(volume: number): void { this.config.volume = Math.max(0, Math.min(1, volume)); this.saveConfig(); }
  isEnabled(): boolean { return this.config.enabled; }
  getVolume(): number { return this.config.volume; }
  async testSound(): Promise<void> { await this.play('notification'); }
}

let soundManager: SoundManager | null = null;
export function getSoundManager(): SoundManager {
  if (!soundManager) soundManager = new SoundManager();
  return soundManager;
}

export async function playAlertSound(severity: AlertSeverity): Promise<void> {
  await getSoundManager().playAlertSound(severity);
}

export function setSoundEnabled(enabled: boolean): void {
  getSoundManager().setEnabled(enabled);
}

export function isSoundEnabled(): boolean {
  return getSoundManager().isEnabled();
}

export { SoundManager };
export default getSoundManager;
