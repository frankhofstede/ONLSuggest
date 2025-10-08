// Story 2.2: Gemeente CRUD
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { adminFetch, getAuthHeader, API_URL } from '../utils/adminApi';
import './AdminCRUD.css';

interface Gemeente {
  id: number;
  name: string;
  metadata: Record<string, any>;
  created_at: string;
}

export function AdminGemeentes() {
  const [gemeentes, setGemeentes] = useState<Gemeente[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);

  // Form state
  const [formName, setFormName] = useState('');
  const [formProvince, setFormProvince] = useState('');

  useEffect(() => {
    fetchGemeentes();
  }, []);

  const fetchGemeentes = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await adminFetch('/api/admin/gemeentes');
      setGemeentes(data.gemeentes || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formName.trim()) return;

    try {
      const response = await fetch(`${API_URL}/api/admin/gemeentes`, {
        method: 'POST',
        headers: {
          'Authorization': getAuthHeader(),
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          name: formName,
          metadata: { province: formProvince }
        })
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      setFormName('');
      setFormProvince('');
      setIsCreating(false);
      fetchGemeentes();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to create');
    }
  };

  const handleUpdate = async (id: number) => {
    if (!formName.trim()) return;

    try {
      const response = await fetch(`${API_URL}/api/admin/gemeentes/${id}`, {
        method: 'PUT',
        headers: {
          'Authorization': getAuthHeader(),
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          name: formName,
          metadata: { province: formProvince }
        })
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      setFormName('');
      setFormProvince('');
      setEditingId(null);
      fetchGemeentes();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to update');
    }
  };

  const handleDelete = async (id: number, name: string) => {
    if (!confirm(`Weet je zeker dat je "${name}" wilt verwijderen?`)) return;

    try {
      const response = await fetch(`${API_URL}/api/admin/gemeentes/${id}`, {
        method: 'DELETE',
        headers: { 'Authorization': getAuthHeader() }
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      fetchGemeentes();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to delete');
    }
  };

  const startEdit = (gemeente: Gemeente) => {
    setEditingId(gemeente.id);
    setFormName(gemeente.name);
    setFormProvince(gemeente.metadata?.province || '');
    setIsCreating(false);
  };

  const cancelEdit = () => {
    setEditingId(null);
    setIsCreating(false);
    setFormName('');
    setFormProvince('');
  };

  return (
    <div className="admin-crud">
      <header className="admin-crud__header">
        <div>
          <Link to="/admin" className="admin-crud__back">← Dashboard</Link>
          <h1>Gemeentes Beheer</h1>
        </div>
        {!isCreating && !editingId && (
          <button onClick={() => setIsCreating(true)} className="btn-primary">
            + Nieuwe Gemeente
          </button>
        )}
      </header>

      <main className="admin-crud__main">
        {isLoading && <p>Loading...</p>}
        {error && <div className="error-box">Error: {error}</div>}

        {(isCreating || editingId) && (
          <form onSubmit={(e) => editingId ? (e.preventDefault(), handleUpdate(editingId)) : handleCreate(e)} className="crud-form">
            <h3>{editingId ? 'Bewerk Gemeente' : 'Nieuwe Gemeente'}</h3>
            <div className="form-group">
              <label>Naam *</label>
              <input
                type="text"
                value={formName}
                onChange={(e) => setFormName(e.target.value)}
                required
                placeholder="Amsterdam"
              />
            </div>
            <div className="form-group">
              <label>Provincie</label>
              <input
                type="text"
                value={formProvince}
                onChange={(e) => setFormProvince(e.target.value)}
                placeholder="Noord-Holland"
              />
            </div>
            <div className="form-actions">
              <button type="submit" className="btn-primary">
                {editingId ? 'Opslaan' : 'Aanmaken'}
              </button>
              <button type="button" onClick={cancelEdit} className="btn-secondary">
                Annuleren
              </button>
            </div>
          </form>
        )}

        <div className="crud-list">
          <h3>Alle Gemeentes ({gemeentes.length})</h3>
          <table className="crud-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Naam</th>
                <th>Provincie</th>
                <th>Aangemaakt</th>
                <th>Acties</th>
              </tr>
            </thead>
            <tbody>
              {gemeentes.map((g) => (
                <tr key={g.id}>
                  <td>{g.id}</td>
                  <td><strong>{g.name}</strong></td>
                  <td>{g.metadata?.province || '-'}</td>
                  <td>{new Date(g.created_at).toLocaleDateString('nl-NL')}</td>
                  <td>
                    <button onClick={() => startEdit(g)} className="btn-small btn-edit">
                      Bewerk
                    </button>
                    <button onClick={() => handleDelete(g.id, g.name)} className="btn-small btn-delete">
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
