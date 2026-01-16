/**
 * CryptoPulse - Jest Setup
 */

import '@testing-library/jest-dom';

// Tipos para evitar erros do TypeScript
declare const jest: {
  fn: () => jest.Mock;
  mock: (moduleName: string, factory?: () => unknown) => void;
};

declare namespace jest {
  interface Mock {
    mockImplementation: (fn: (...args: unknown[]) => unknown) => Mock;
  }
}
