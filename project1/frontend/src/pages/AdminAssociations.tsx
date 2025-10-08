// Story 2.4: Gemeente-Service Associations
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getAuthHeader, API_URL } from '../utils/adminApi';
import './AdminCRUD.css';

interface Gemeente {
  id: number;
  name: string;
}

interface Service {
  id: number;
  name: string;
  category: string;
}

interface Association {
  id: number;
  gemeente_id: number;
  service_id: number;
  gemeente?: Gemeente;
  service?: Service;
}

export function AdminAssociations() {
  const [gemeentes, setGemeentes] = useState<Gemeente[]>([]);
  const [services, setServices] = useState<Service[]>([]);
  const [associations, setAssociations] = useState<Association[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isCreating, setIsCreating] = useState(false);

  // Form state
  const [selectedGemeente, setSelectedGemeente] = useState('');
  const [selectedService, setSelectedService] = useState('');

  useEffect(() => {
    fetchAll();
  }, []);

  const fetchAll = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const [gRes, sRes, aRes] = await Promise.all([
        fetch(`${API_URL}/api/admin/gemeentes`, { headers: { 'Authorization': getAuthHeader() } }),
        fetch(`${API_URL}/api/admin/services`, { headers: { 'Authorization': getAuthHeader() } }),
        fetch(`${API_URL}/api/admin/associations`, { headers: { 'Authorization': getAuthHeader() } })
      ]);

      if (!gRes.ok || !sRes.ok || !aRes.ok) throw new Error('Failed to fetch');

      const [gData, sData, aData] = await Promise.all([gRes.json(), sRes.json(), aRes.json()]);

      setGemeentes(gData.gemeentes || []);
      setServices(sData.services || []);
      setAssociations(aData.associations || []);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedGemeente || !selectedService) return;

    try {
      const response = await fetch(`${API_URL}/api/admin/associations`, {
        method: 'POST',
        headers: {
          'Authorization': getAuthHeader(),
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          gemeente_id: parseInt(selectedGemeente),
          service_id: parseInt(selectedService)
        })
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      setSelectedGemeente('');
      setSelectedService('');
      setIsCreating(false);
      fetchAll();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to create');
    }
  };

  const handleDelete = async (gemeenteId: number, serviceId: number) => {
    const association = associations.find(a => a.gemeente_id === gemeenteId && a.service_id === serviceId);
    const gemeente = gemeentes.find(g => g.id === gemeenteId);
    const service = services.find(s => s.id === serviceId);

    if (!association) {
      alert('Association not found');
      return;
    }

    if (!confirm(`Koppeling verwijderen: ${gemeente?.name} - ${service?.name}?`)) return;

    try {
      const response = await fetch(`${API_URL}/api/admin/associations/${association.id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': getAuthHeader()
        }
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      fetchAll();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to delete');
    }
  };

  // Group associations by gemeente
  const associationsByGemeente = gemeentes.map(g => ({
    gemeente: g,
    services: associations.filter(a => a.gemeente_id === g.id).map(a => a.service!)
  }));

  return (
    <div className="admin-crud">
      <header className="admin-crud__header">
        <div>
          <Link to="/admin" className="admin-crud__back">← Dashboard</Link>
          <h1>Koppelingen Beheer</h1>
        </div>
        {!isCreating && (
          <button onClick={() => setIsCreating(true)} className="btn-primary">
            + Nieuwe Koppeling
          </button>
        )}
      </header>

      <main className="admin-crud__main">
        {isLoading && <p>Loading...</p>}
        {error && <div className="error-box">Error: {error}</div>}

        {isCreating && (
          <form onSubmit={handleCreate} className="crud-form">
            <h3>Nieuwe Koppeling</h3>
            <div className="form-group">
              <label>Gemeente *</label>
              <select
                value={selectedGemeente}
                onChange={(e) => setSelectedGemeente(e.target.value)}
                required
              >
                <option value="">-- Kies gemeente --</option>
                {gemeentes.map(g => (
                  <option key={g.id} value={g.id}>{g.name}</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>Service *</label>
              <select
                value={selectedService}
                onChange={(e) => setSelectedService(e.target.value)}
                required
              >
                <option value="">-- Kies service --</option>
                {services.map(s => (
                  <option key={s.id} value={s.id}>{s.name} ({s.category})</option>
                ))}
              </select>
            </div>
            <div className="form-actions">
              <button type="submit" className="btn-primary">Aanmaken</button>
              <button type="button" onClick={() => setIsCreating(false)} className="btn-secondary">
                Annuleren
              </button>
            </div>
          </form>
        )}

        <div className="crud-list">
          <h3>Koppelingen per Gemeente</h3>
          {associationsByGemeente.map(({ gemeente, services: gServices }) => (
            <div key={gemeente.id} style={{ marginBottom: '2rem' }}>
              <h4 style={{ color: '#0066cc', marginBottom: '0.5rem' }}>{gemeente.name}</h4>
              {gServices.length === 0 ? (
                <p style={{ color: '#999' }}>Geen services gekoppeld</p>
              ) : (
                <ul style={{ listStyle: 'none', padding: 0 }}>
                  {gServices.map(s => (
                    <li key={s.id} style={{
                      padding: '0.5rem 0',
                      borderBottom: '1px solid #f0f0f0',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center'
                    }}>
                      <span>{s.name} <span className="text-muted">({s.category})</span></span>
                      <button
                        onClick={() => handleDelete(gemeente.id, s.id)}
                        className="btn-small btn-delete"
                      >
                        Verwijder
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
