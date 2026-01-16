/**
 * CryptoPulse - Dashboard Loading
 * Estado de loading da página de dashboard
 */

import { Header } from '@/components/layout/Header';
import { Footer } from '@/components/layout/Footer';
import { SkeletonDashboard } from '@/components/ui/skeleton';

export default function DashboardLoading() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      
      <main className="flex-1 container mx-auto px-4 py-6">
        <div className="space-y-6">
          {/* Page header skeleton */}
          <div className="flex justify-between items-center">
            <div className="space-y-2">
              <div className="h-8 w-40 bg-crypto-border animate-pulse rounded" />
              <div className="h-4 w-64 bg-crypto-border animate-pulse rounded" />
            </div>
            <div className="h-10 w-28 bg-crypto-border animate-pulse rounded" />
          </div>
          
          {/* Dashboard skeleton */}
          <SkeletonDashboard />
        </div>
      </main>
      
      <Footer />
    </div>
  );
}
