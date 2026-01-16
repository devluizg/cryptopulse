/**
 * CryptoPulse - Disclaimer Component
 * Aviso legal sobre não ser aconselhamento financeiro
 */

import * as React from 'react';
import { cn } from '@/lib/utils';

interface DisclaimerProps {
  variant?: 'inline' | 'banner' | 'modal' | 'footer';
  showIcon?: boolean;
  className?: string;
}

export function Disclaimer({
  variant = 'inline',
  showIcon = true,
  className,
}: DisclaimerProps) {
  const content = (
    <>
      {showIcon && (
        <svg
          className="w-4 h-4 flex-shrink-0"
          fill="currentColor"
          viewBox="0 0 20 20"
        >
          <path
            fillRule="evenodd"
            d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
            clipRule="evenodd"
          />
        </svg>
      )}
      <span>
        <strong>Aviso:</strong> CryptoPulse não fornece aconselhamento financeiro.
        Os sinais apresentados são baseados em dados históricos e não garantem
        resultados futuros. Faça sua própria pesquisa antes de investir.
      </span>
    </>
  );

  const variants = {
    inline: 'flex items-start gap-2 text-xs text-crypto-muted p-3 bg-crypto-card/50 rounded-lg border border-crypto-border',
    banner: 'flex items-center gap-2 text-sm text-yellow-400 bg-yellow-500/10 border-y border-yellow-500/20 px-4 py-2',
    modal: 'text-sm text-crypto-muted bg-crypto-darker p-4 rounded-lg',
    footer: 'text-xs text-crypto-muted text-center',
  };

  return (
    <div className={cn(variants[variant], className)} role="alert">
      {content}
    </div>
  );
}

// Versão curta para rodapés
export function ShortDisclaimer({ className }: { className?: string }) {
  return (
    <p className={cn('text-xs text-crypto-muted', className)}>
      ⚠️ Não é aconselhamento financeiro. Faça sua própria pesquisa.
    </p>
  );
}

// Modal de disclaimer para primeiro acesso
interface DisclaimerModalProps {
  isOpen: boolean;
  onAccept: () => void;
}

export function DisclaimerModal({ isOpen, onAccept }: DisclaimerModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-crypto-card border border-crypto-border rounded-xl max-w-lg w-full p-6 space-y-4">
        <div className="flex items-center gap-3 text-yellow-400">
          <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
            <path
              fillRule="evenodd"
              d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
              clipRule="evenodd"
            />
          </svg>
          <h2 className="text-xl font-bold text-crypto-text">Aviso Importante</h2>
        </div>

        <div className="space-y-3 text-sm text-crypto-muted">
          <p>
            Bem-vindo ao <strong className="text-crypto-text">CryptoPulse</strong>!
            Antes de continuar, por favor leia e aceite os seguintes termos:
          </p>
          
          <ul className="list-disc list-inside space-y-2">
            <li>
              Este software <strong>NÃO</strong> fornece aconselhamento financeiro,
              de investimento, legal ou tributário.
            </li>
            <li>
              Os sinais e scores apresentados são baseados em análise de dados
              históricos e <strong>NÃO</strong> garantem resultados futuros.
            </li>
            <li>
              Investimentos em criptomoedas envolvem <strong>alto risco</strong> de
              perda. Nunca invista mais do que pode perder.
            </li>
            <li>
              Sempre faça sua própria pesquisa (DYOR) antes de tomar qualquer
              decisão de investimento.
            </li>
          </ul>

          <p className="pt-2 font-medium text-crypto-text">
            Ao continuar, você confirma que entende e aceita estes termos.
          </p>
        </div>

        <button
          onClick={onAccept}
          className="w-full py-3 bg-score-high text-white font-semibold rounded-lg hover:bg-score-high/90 transition-colors"
        >
          Eu entendo e aceito
        </button>
      </div>
    </div>
  );
}

export default Disclaimer;
