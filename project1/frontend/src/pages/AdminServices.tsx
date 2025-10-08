// Story 2.3: Service CRUD
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getAuthHeader, API_URL } from '../utils/adminApi';
import './AdminCRUD.css';

interface Service {
  id: number;
  name: string;
  description: string;
  category: string;
  keywords: string[];
  created_at: string;
}

export function AdminServices() {
  const [services, setServices] = useState<Service[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);

  // Form state
  const [formName, setFormName] = useState('');
  const [formDescription, setFormDescription] = useState('');
  const [formCategory, setFormCategory] = useState('');
  const [formKeywords, setFormKeywords] = useState('');

  useEffect(() => {
    fetchServices();
  }, []);

  const fetchServices = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_URL}/api/admin/services`, {
        headers: { 'Authorization': getAuthHeader() }
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      const data = await response.json();
      setServices(data.services || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formName.trim() || !formDescription.trim() || !formCategory.trim()) return;

    try {
      const keywords = formKeywords.split(',').map(k => k.trim()).filter(k => k);
      const response = await fetch(`${API_URL}/api/admin/services`, {
        method: 'POST',
        headers: {
          'Authorization': getAuthHeader(),
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          name: formName,
          description: formDescription,
          category: formCategory,
          keywords
        })
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      resetForm();
      fetchServices();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to create');
    }
  };

  const handleUpdate = async (id: number) => {
    if (!formName.trim() || !formDescription.trim() || !formCategory.trim()) return;

    try {
      const keywords = formKeywords.split(',').map(k => k.trim()).filter(k => k);
      const response = await fetch(`${API_URL}/api/admin/services/${id}`, {
        method: 'PUT',
        headers: {
          'Authorization': getAuthHeader(),
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          name: formName,
          description: formDescription,
          category: formCategory,
          keywords
        })
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      resetForm();
      fetchServices();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to update');
    }
  };

  const handleDelete = async (id: number, name: string) => {
    if (!confirm(`Weet je zeker dat je "${name}" wilt verwijderen?`)) return;

    try {
      const response = await fetch(`${API_URL}/api/admin/services/${id}`, {
        method: 'DELETE',
        headers: { 'Authorization': getAuthHeader() }
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      fetchServices();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to delete');
    }
  };

  const startEdit = (service: Service) => {
    setEditingId(service.id);
    setFormName(service.name);
    setFormDescription(service.description);
    setFormCategory(service.category);
    setFormKeywords(service.keywords.join(', '));
    setIsCreating(false);
  };

  const resetForm = () => {
    setEditingId(null);
    setIsCreating(false);
    setFormName('');
    setFormDescription('');
    setFormCategory('');
    setFormKeywords('');
  };

  return (
    <div className="admin-crud">
      <header className="admin-crud__header">
        <div>
          <Link to="/admin" className="admin-crud__back">← Dashboard</Link>
          <h1>Services Beheer</h1>
        </div>
        {!isCreating && !editingId && (
          <button onClick={() => setIsCreating(true)} className="btn-primary">
            + Nieuwe Service
          </button>
        )}
      </header>

      <main className="admin-crud__main">
        {isLoading && <p>Loading...</p>}
        {error && <div className="error-box">Error: {error}</div>}

        {(isCreating || editingId) && (
          <form onSubmit={(e) => editingId ? (e.preventDefault(), handleUpdate(editingId)) : handleCreate(e)} className="crud-form">
            <h3>{editingId ? 'Bewerk Service' : 'Nieuwe Service'}</h3>
            <div className="form-group">
              <label>Naam *</label>
              <input
                type="text"
                value={formName}
                onChange={(e) => setFormName(e.target.value)}
                required
                placeholder="Parkeervergunning aanvragen"
              />
            </div>
            <div className="form-group">
              <label>Beschrijving *</label>
              <textarea
                value={formDescription}
                onChange={(e) => setFormDescription(e.target.value)}
                required
                rows={3}
                placeholder="Vraag een parkeervergunning aan voor uw auto"
              />
            </div>
            <div className="form-group">
              <label>Categorie *</label>
              <input
                type="text"
                value={formCategory}
                onChange={(e) => setFormCategory(e.target.value)}
                required
                placeholder="Verkeer"
              />
            </div>
            <div className="form-group">
              <label>Keywords (komma gescheiden)</label>
              <input
                type="text"
                value={formKeywords}
                onChange={(e) => setFormKeywords(e.target.value)}
                placeholder="parkeer, parkeren, auto, vergunning"
              />
            </div>
            <div className="form-actions">
              <button type="submit" className="btn-primary">
                {editingId ? 'Opslaan' : 'Aanmaken'}
              </button>
              <button type="button" onClick={resetForm} className="btn-secondary">
                Annuleren
              </button>
            </div>
          </form>
        )}

        <div className="crud-list">
          <h3>Alle Services ({services.length})</h3>
          <table className="crud-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Naam</th>
                <th>Categorie</th>
                <th>Keywords</th>
                <th>Acties</th>
              </tr>
            </thead>
            <tbody>
              {services.map((s) => (
                <tr key={s.id}>
                  <td>{s.id}</td>
                  <td>
                    <strong>{s.name}</strong>
                    <br />
                    <small className="text-muted">{s.description}</small>
                  </td>
                  <td>{s.category}</td>
                  <td>
                    <div className="keywords">
                      {s.keywords.map((k, i) => (
                        <span key={i} className="keyword-tag">{k}</span>
                      ))}
                    </div>
                  </td>
                  <td>
                    <button onClick={() => startEdit(s)} className="btn-small btn-edit">
                      Bewerk
                    </button>
                    <button onClick={() => handleDelete(s.id, s.name)} className="btn-small btn-delete">
                      Verwijder
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </main>
    </div>
  );
}
