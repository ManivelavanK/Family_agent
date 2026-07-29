import React, { useState, useEffect } from 'react';
import { purchaseHistory as mockPurchaseHistory } from '../data/mockData';
import { IS_MOCK_MODE, apiClient } from '../services/api';
import { Search, Calendar, Filter, ShoppingBag, Receipt, Loader2 } from 'lucide-react';

interface PurchaseRecord {
  id: string;
  date: string;
  store: string;
  itemsCount: number;
  amount: number;
  category: string;
}

export const Purchases: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [history, setHistory] = useState<PurchaseRecord[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [storeFilter, setStoreFilter] = useState('All');
  const [amountSort, setAmountSort] = useState('default');

  useEffect(() => {
    async function loadHistory() {
      setLoading(true);
      try {
        if (IS_MOCK_MODE) {
          setHistory(mockPurchaseHistory);
        } else {
          const res = await apiClient.get<any[]>('/purchase/history');
          // Backend returns individual line-items: group by date into receipts
          const grouped: Record<string, PurchaseRecord> = {};
          res.data.forEach((item: any) => {
            const key = `${item.purchase_date}`;
            if (!grouped[key]) {
              grouped[key] = {
                id: String(item.id),
                date: item.purchase_date,
                store: item.category || 'General Store',
                itemsCount: 0,
                amount: 0,
                category: item.category || 'Mixed Groceries',
              };
            }
            grouped[key].itemsCount += 1;
            grouped[key].amount += item.price || 0;
          });
          const records = Object.values(grouped).sort(
            (a, b) => new Date(b.date).getTime() - new Date(a.date).getTime()
          );
          setHistory(records.length > 0 ? records : mockPurchaseHistory);
        }
      } catch (err) {
        console.error(err);
        setHistory(mockPurchaseHistory);
      } finally {
        setLoading(false);
      }
    }
    loadHistory();
  }, []);

  const uniqueStores = ['All', ...Array.from(new Set(history.map(p => p.store)))];

  const filteredHistory = history
    .filter(purchase => {
      const matchesSearch = purchase.store.toLowerCase().includes(searchTerm.toLowerCase()) ||
                            purchase.category.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesStore = storeFilter === 'All' || purchase.store === storeFilter;
      return matchesSearch && matchesStore;
    })
    .sort((a, b) => {
      if (amountSort === 'asc') return a.amount - b.amount;
      if (amountSort === 'desc') return b.amount - a.amount;
      return 0;
    });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-800">Purchase History</h1>
        <p className="text-slate-500 font-medium text-xs mt-1">Audit previous household grocery bills, receipt quantities, and category amounts.</p>
      </div>

      {/* Filter and search bar */}
      <div className="flex flex-wrap items-center gap-4 bg-white p-4 rounded-xl border border-slate-100 shadow-2xs">
        {/* Search */}
        <div className="relative flex-1 min-w-[200px]">
          <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-slate-400">
            <Search className="h-4 w-4" />
          </span>
          <input
            type="text"
            placeholder="Search stores or categories..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full rounded-lg border border-slate-200 py-2 pl-9 pr-4 text-xs font-medium focus:border-indigo-500 focus:outline-none bg-slate-50/50 focus:bg-white transition-colors"
          />
        </div>

        {/* Store filter */}
        <div className="flex items-center gap-2">
          <Filter className="h-4.5 w-4.5 text-slate-400" />
          <select
            value={storeFilter}
            onChange={(e) => setStoreFilter(e.target.value)}
            className="rounded-lg border border-slate-200 py-2 px-3 text-xs font-semibold bg-white focus:border-indigo-500 focus:outline-none"
          >
            {uniqueStores.map((store, idx) => (
              <option key={idx} value={store}>{store === 'All' ? 'All Stores' : store}</option>
            ))}
          </select>
        </div>

        {/* Price sort */}
        <div>
          <select
            value={amountSort}
            onChange={(e) => setAmountSort(e.target.value)}
            className="rounded-lg border border-slate-200 py-2 px-3 text-xs font-semibold bg-white focus:border-indigo-500 focus:outline-none"
          >
            <option value="default">Sort by Amount</option>
            <option value="asc">Low to High (₹)</option>
            <option value="desc">High to Low (₹)</option>
          </select>
        </div>
      </div>

      {/* Receipts lists */}
      {loading ? (
        <div className="flex h-40 items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
        </div>
      ) : (
        <div className="space-y-4">
          {filteredHistory.map((purchase) => (
            <div
              key={purchase.id}
              className="flex flex-col md:flex-row md:items-center justify-between rounded-2xl border border-slate-100 bg-white p-5 shadow-2xs hover:shadow-xs transition-shadow"
            >
              <div className="flex items-center gap-4">
                <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-indigo-50 text-indigo-650">
                  <ShoppingBag className="h-5 w-5" />
                </div>
                <div>
                  <h3 className="font-bold text-slate-800 text-sm">{purchase.store}</h3>
                  <div className="flex flex-wrap gap-x-3 gap-y-1 mt-1 text-xs text-slate-450 font-medium">
                    <span className="flex items-center gap-1">
                      <Calendar className="h-3.5 w-3.5" />
                      {purchase.date}
                    </span>
                    <span>•</span>
                    <span>{purchase.itemsCount} items</span>
                    <span>•</span>
                    <span className="font-semibold text-indigo-600 bg-indigo-50/50 px-1.5 py-0.5 rounded-md border border-indigo-100/30">
                      {purchase.category}
                    </span>
                  </div>
                </div>
              </div>

              <div className="mt-4 md:mt-0 flex items-center justify-between md:justify-end gap-6 border-t border-slate-50 pt-4 md:border-none md:pt-0">
                <div className="text-right">
                  <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider">Total amount paid</span>
                  <span className="text-lg font-bold text-slate-900">₹{purchase.amount.toFixed(0)}</span>
                </div>
                <button
                  className="flex items-center gap-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 px-3.5 py-2 text-xs font-bold text-slate-655 transition-colors cursor-pointer"
                  onClick={() => alert(`Opening digital receipt for ${purchase.store}...`)}
                >
                  <Receipt className="h-4.5 w-4.5 text-slate-400" />
                  View Receipt
                </button>
              </div>
            </div>
          ))}

          {filteredHistory.length === 0 && (
            <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-slate-200 bg-white py-12 px-4 text-center">
              <span className="text-4xl">🧾</span>
              <h3 className="mt-4 text-lg font-bold text-slate-800">No receipts found</h3>
              <p className="mt-1 text-sm text-slate-500">No transactions match your current search terms.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
export default Purchases;
