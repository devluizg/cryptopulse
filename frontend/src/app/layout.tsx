import '@/styles/globals.css';
import { Inter } from 'next/font/google';
import type { Metadata, Viewport } from 'next';
import { ToastProvider } from '@/components/alerts/Toast';
import { AlertProvider } from '@/components/alerts/AlertProvider';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: { default: 'CryptoPulse', template: '%s | CryptoPulse' },
  description: 'Plataforma de monitoramento de sinais antecipados do mercado de criptomoedas.',
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  themeColor: '#0d1117',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR" className="dark">
      <body className={`${inter.className} bg-crypto-dark text-crypto-text antialiased`}>
        <ToastProvider maxToasts={5}>
          <AlertProvider>
            {children}
          </AlertProvider>
        </ToastProvider>
      </body>
    </html>
  );
}
