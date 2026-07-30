import { useState, useEffect } from 'react';
import { useAuthStore } from '../store/useAuthStore';

export default function MotherAgent() {
  const token = useAuthStore(state => state.token);
  const [data, setData] = useState<any>(null);
  const [errorMsg, setErrorMsg] = useState('');
  const [newItem, setNewItem] = useState('');

  const fetchContext = async () => {
    if (!token) return;
    try {
      const res = await fetch('http://localhost:8000/orchestrator/context/shopping', {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) setData(await res.json());
      else setErrorMsg(`Error: ${res.status}`);
    } catch (err: any) {
      setErrorMsg(err.message);
    }
  };

  useEffect(() => {
    fetchContext();
  }, [token]);

  const handleUpdate = async () => {
    if (!token || !newItem) return;
    try {
      const currentItems = data?.items || [];
      const res = await fetch('http://localhost:8000/orchestrator/context/shopping', {
        method: 'PATCH',
        headers: { 
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}` 
        },
        body: JSON.stringify({ items: [...currentItems, newItem] })
      });
      if (res.ok) {
        setNewItem('');
        fetchContext();
      } else {
        setErrorMsg(`Update Error: ${res.status}`);
      }
    } catch (err: any) {
      setErrorMsg(err.message);
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">MotherAgent (Shopping)</h1>
      {errorMsg && <p className="text-red-500 mb-4">{errorMsg}</p>}
      
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 mb-6">
        <h2 className="font-semibold text-lg mb-2">Shopping Context</h2>
        <pre className="text-sm bg-slate-50 p-4 rounded overflow-auto mb-4">
          {JSON.stringify(data, null, 2)}
        </pre>
        
        <div className="flex space-x-2">
          <input 
            type="text" 
            value={newItem} 
            onChange={(e) => setNewItem(e.target.value)} 
            placeholder="Add new item..." 
            className="flex-1 px-3 py-2 border rounded" 
          />
          <button 
            onClick={handleUpdate} 
            className="px-4 py-2 bg-pink-500 text-white rounded hover:bg-pink-600"
          >
            Update
          </button>
        </div>
      </div>
    </div>
  );
}