import { Link, Outlet, useLocation } from 'react-router-dom';
import { useState } from 'react';
import { Bars3Icon, XMarkIcon } from '@heroicons/react/24/outline';
import HealthIndicator from './HealthIndicator';
import { useSystemStore } from '@/stores';
import { checkHealth } from '@/services';

export default function Layout() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();
  const { healthStatus, setHealthStatus } = useSystemStore();

  const handleHealthCheck = async () => {
    try {
      const status = await checkHealth();
      setHealthStatus(status);
    } catch (err) {
      // Health check failed - set error status
      setHealthStatus({
        status: 'error',
        service: 'unreachable',
        database: 'unknown',
      });
    }
  };

  const navigation = [
    { name: 'Query', href: '/app' },
    { name: 'Upload', href: '/app/upload' },
    { name: 'Metrics', href: '/app/metrics' },
  ];

  const isActive = (href: string) => {
    if (href === '/app') return location.pathname === '/app';
    return location.pathname.startsWith(href);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <nav className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8" aria-label="Top">
          <div className="flex h-16 items-center justify-between">
            {/* Logo and Desktop Navigation */}
            <div className="flex items-center gap-8">
              <div className="flex items-center">
                <Link to="/" className="text-xl font-bold text-primary-600 hover:text-primary-700 transition-colors">
                  AskMyDoc
                </Link>
              </div>
              
              {/* Desktop Navigation */}
              <div className="hidden md:flex md:gap-x-6">
                {navigation.map((item) => (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={`text-sm font-medium transition-colors ${
                      isActive(item.href)
                        ? 'text-primary-600'
                        : 'text-gray-700 hover:text-primary-600'
                    }`}
                  >
                    {item.name}
                  </Link>
                ))}
              </div>
            </div>

            {/* Health Indicator and Mobile Menu Button */}
            <div className="flex items-center gap-4">
              <HealthIndicator 
                status={healthStatus} 
                onCheck={handleHealthCheck}
                checkInterval={300000}
              />
              
              {/* Mobile menu button */}
              <button
                type="button"
                className="md:hidden inline-flex items-center justify-center rounded-md p-2 text-gray-700 hover:bg-gray-100"
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                aria-expanded={mobileMenuOpen}
                aria-label="Toggle navigation menu"
              >
                {mobileMenuOpen ? (
                  <XMarkIcon className="h-6 w-6" aria-hidden="true" />
                ) : (
                  <Bars3Icon className="h-6 w-6" aria-hidden="true" />
                )}
              </button>
            </div>
          </div>

          {/* Mobile Navigation */}
          {mobileMenuOpen && (
            <div className="md:hidden py-4 border-t border-gray-200">
              <div className="flex flex-col gap-2">
                {navigation.map((item) => (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={`px-3 py-2 text-base font-medium rounded-md transition-colors ${
                      isActive(item.href)
                        ? 'bg-primary-50 text-primary-600'
                        : 'text-gray-700 hover:bg-gray-100'
                    }`}
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    {item.name}
                  </Link>
                ))}
              </div>
            </div>
          )}
        </nav>
      </header>

      {/* Main Content */}
      <main className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>
    </div>
  );
}
