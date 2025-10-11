// Story 2.6: Admin Dashboard
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { adminFetch } from '../utils/adminApi';
import './AdminDashboard.css';

interface Stats {
  total_gemeentes: number;
  total_services: number;
  total_associations: number;
}

export function AdminDashboard() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await adminFetch('/api/admin/stats');
      setStats(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch stats');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="admin-dashboard">
      <header className="admin-dashboard__header">
        <h1>ONLSuggest Admin</h1>
        <Link to="/" className="admin-dashboard__back-link">← Terug naar frontend</Link>
      </header>

      <main className="admin-dashboard__main">
        {isLoading && <p>Loading...</p>}

        {error && (
          <div className="admin-dashboard__error">
            <p>Error: {error}</p>
            <button onClick={fetchStats}>Retry</button>
          </div>
        )}

        {stats && (
          <>
            <section className="admin-dashboard__stats">
              <h2>Overzicht</h2>
              <div className="stats-grid">
                <div className="stat-card">
                  <div className="stat-card__value">{stats.total_gemeentes}</div>
                  <div className="stat-card__label">Gemeentes</div>
                </div>
                <div className="stat-card">
                  <div className="stat-card__value">{stats.total_services}</div>
                  <div className="stat-card__label">Services</div>
                </div>
                <div className="stat-card">
                  <div className="stat-card__value">{stats.total_associations}</div>
                  <div className="stat-card__label">Koppelingen</div>
                </div>
              </div>
            </section>

            <section className="admin-dashboard__navigation">
              <h2>Beheer</h2>
              <div className="nav-grid">
                <Link to="/admin/gemeentes" className="nav-card">
                  <h3>Gemeentes</h3>
                  <p>Beheer gemeentes en metadata</p>
                </Link>
                <Link to="/admin/services" className="nav-card">
                  <h3>Services</h3>
                  <p>Beheer diensten en keywords</p>
                </Link>
                <Link to="/admin/associations" className="nav-card">
                  <h3>Koppelingen</h3>
                  <p>Beheer gemeente-service koppelingen</p>
                </Link>
                <Link to="/admin/settings" className="nav-card">
                  <h3>Instellingen</h3>
                  <p>Configureer suggestie engine en andere opties</p>
                </Link>
              </div>
            </section>
          </>
        )}
      </main>
    </div>
  );
}
