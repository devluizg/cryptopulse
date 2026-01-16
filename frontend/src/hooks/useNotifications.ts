import { useState, useEffect, useCallback } from 'react';
import { getSoundManager } from '@/lib/sounds';
import { useSettingsStore } from '@/store';

export function useNotifications() {
  const [permission, setPermission] = useState<NotificationPermission>('default');
  const [isSupported, setIsSupported] = useState(false);
  const [volume, setVolumeState] = useState(0.5);
  
  const soundEnabled = useSettingsStore((state) => state.soundEnabled);
  const setSoundEnabled = useSettingsStore((state) => state.setSoundEnabled);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      setIsSupported('Notification' in window);
      if ('Notification' in window) setPermission(Notification.permission);
      setVolumeState(getSoundManager().getVolume());
    }
  }, []);

  const requestPermission = useCallback(async (): Promise<boolean> => {
    if (!isSupported) return false;
    try {
      const result = await Notification.requestPermission();
      setPermission(result);
      return result === 'granted';
    } catch { return false; }
  }, [isSupported]);

  const showNotification = useCallback((title: string, options?: NotificationOptions) => {
    if (!isSupported || permission !== 'granted') return;
    try { new Notification(title, options); } catch {}
  }, [isSupported, permission]);

  const toggleSound = useCallback(() => {
    setSoundEnabled(!soundEnabled);
    getSoundManager().setEnabled(!soundEnabled);
  }, [soundEnabled, setSoundEnabled]);

  const setVolume = useCallback((v: number) => {
    setVolumeState(v);
    getSoundManager().setVolume(v);
  }, []);

  const testSound = useCallback(async () => {
    await getSoundManager().testSound();
  }, []);

  return {
    permission, isSupported, requestPermission, showNotification,
    soundEnabled, toggleSound, setVolume, volume, testSound,
    isReady: isSupported && permission === 'granted',
  };
}

export default useNotifications;
