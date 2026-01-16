/**
 * CryptoPulse - Home Page
 * Página inicial com redirect para dashboard
 */

import { redirect } from 'next/navigation';

export default function HomePage() {
  // Redireciona para o dashboard
  redirect('/dashboard');
}
