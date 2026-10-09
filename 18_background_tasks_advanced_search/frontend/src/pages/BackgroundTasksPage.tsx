import React, { useState, useEffect } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { FileText, Upload, Download, CheckCircle, Loader2 } from 'lucide-react';
import { apiClient } from '../services/apiClient';
import { useTaskTracker } from '../hooks/useTaskTracker';
import Button from '../components/ui/Button';

interface BackgroundTasksPageProps {
  isEmbedded?: boolean;
}

export const BackgroundTasksPage: React.FC<BackgroundTasksPageProps> = ({ isEmbedded = false }) => {
  const queryClient = useQueryClient();

  // Tracker for PDF Invoice Task
  const invoiceTracker = useTaskTracker();
  const [orderId, setOrderId] = useState<number>(1);

  // Tracker for CSV Import Task
  const csvTracker = useTaskTracker();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  useEffect(() => {
    if (csvTracker.state === 'SUCCESS') {
      queryClient.invalidateQueries({ queryKey: ['admin', 'products'] });
      queryClient.invalidateQueries({ queryKey: ['products'] });
    }
  }, [csvTracker.state, queryClient]);

  // 1. Trigger PDF Invoice
  const handleGenerateInvoice = async () => {
    try {
      const response = await apiClient.post<{ task_id: string }>(`/tasks/orders/${orderId}/invoice`);
      invoiceTracker.startTracking(response.task_id);
    } catch (err: any) {
      alert('Failed to start invoice task: ' + (err?.response?.data?.detail || err.message));
    }
  };

  // 2. Trigger CSV Bulk Import
  const handleImportCSV = async () => {
    if (!selectedFile) {
      alert('Please select a CSV file first');
      return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await apiClient.post<{ task_id: string }>('/tasks/products/import-csv', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      csvTracker.startTracking(response.task_id);
    } catch (err: any) {
      alert('Failed to start CSV import: ' + (err?.response?.data?.detail || err.message));
    }
  };

  // Sample CSV generator for testing
  const handleCreateSampleCSV = () => {
    const csvContent =
      'name,description,price,stock,category_id,image_url\n' +
      'Mechanical Gaming Keyboard,RGB Backlit Blue Switch,79.99,40,1,https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600&auto=format&fit=crop&q=80\n' +
      'Wireless Ergonomic Mouse,Rechargeable Silent Click,29.99,100,1,https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=600&auto=format&fit=crop&q=80\n' +
      'UltraWide 34-Inch Monitor,144Hz IPS Curved Display,499.99,15,1,https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=600&auto=format&fit=crop&q=80\n' +
      'Noise Cancelling Headphones,Bluetooth 5.3 Over-Ear,129.99,60,1,https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&auto=format&fit=crop&q=80\n';

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const file = new File([blob], 'sample_products.csv', { type: 'text/csv' });
    setSelectedFile(file);
  };

  return (
    <div className={isEmbedded ? 'space-y-8' : 'max-w-6xl mx-auto px-4 py-8 space-y-8'}>
      {/* Header */}
      {!isEmbedded ? (
        <div>
          <h1 className="text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">
            Background Tasks & Job Tracker
          </h1>
          <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">
            Trigger Celery worker jobs from the UI with real-time polling, progress bar animations, and downloadable results.
          </p>
        </div>
      ) : (
        <div className="bg-gradient-to-r from-purple-900/10 via-indigo-900/10 to-transparent p-5 rounded-xl border border-purple-200 dark:border-purple-800/50 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="p-1 rounded-md bg-purple-100 dark:bg-purple-900/50 text-purple-600 dark:text-purple-400">
                <Upload className="h-5 w-5" />
              </span>
              <h2 className="text-xl font-bold text-slate-900 dark:text-white">
                Admin Background Tasks & Bulk Operations
              </h2>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
              Bulk CSV product catalog import, ReportLab enterprise PDF invoice generation, and full-text search indexing.
            </p>
          </div>
          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-emerald-100 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-800">
            ● Celery Worker Active
          </span>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* CARD 1: PDF Invoice Generation */}
        <div className="bg-white dark:bg-slate-900 p-6 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-5">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-blue-100 dark:bg-blue-900/40 text-blue-600 dark:text-blue-400">
              <FileText className="h-6 w-6" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-slate-900 dark:text-white">PDF Invoice Generation</h2>
              <p className="text-xs text-slate-500">Asynchronous receipt creation with ReportLab</p>
            </div>
          </div>

          <div className="space-y-3">
            <label className="text-xs font-semibold text-slate-700 dark:text-slate-300">Target Order ID</label>
            <input
              type="number"
              value={orderId}
              onChange={(e) => setOrderId(Number(e.target.value))}
              disabled={invoiceTracker.isProcessing}
              className="w-full px-3 py-2 text-sm rounded-lg border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white"
            />
          </div>

          <Button
            onClick={handleGenerateInvoice}
            disabled={invoiceTracker.isProcessing}
            className="w-full justify-center"
          >
            {invoiceTracker.isProcessing ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Generating Invoice...
              </>
            ) : (
              'Generate Invoice (Celery Task)'
            )}
          </Button>

          {/* Progress Tracker Bar */}
          {invoiceTracker.state !== 'IDLE' && (
            <div className="p-4 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 space-y-2">
              <div className="flex justify-between items-center text-xs font-medium">
                <span className="text-slate-600 dark:text-slate-300">{invoiceTracker.message}</span>
                <span className="font-bold text-blue-600 dark:text-blue-400">{invoiceTracker.progress}%</span>
              </div>
              <div className="w-full bg-slate-200 dark:bg-slate-700 h-2.5 rounded-full overflow-hidden">
                <div
                  className="bg-blue-600 h-2.5 rounded-full transition-all duration-300 ease-out"
                  style={{ width: `${invoiceTracker.progress}%` }}
                />
              </div>

              {invoiceTracker.state === 'SUCCESS' && invoiceTracker.result && (
                <div className="pt-2 flex items-center justify-between">
                  <span className="flex items-center text-xs font-semibold text-emerald-600 dark:text-emerald-400">
                    <CheckCircle className="h-4 w-4 mr-1" /> Ready to download!
                  </span>
                  <a
                    href={invoiceTracker.result.file_url}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center px-3 py-1.5 text-xs font-bold rounded-md bg-emerald-600 text-white hover:bg-emerald-700 transition-colors"
                  >
                    <Download className="h-3.5 w-3.5 mr-1" /> Download PDF
                  </a>
                </div>
              )}
            </div>
          )}
        </div>

        {/* CARD 2: Bulk CSV Product Import */}
        <div className="bg-white dark:bg-slate-900 p-6 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-5">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-purple-100 dark:bg-purple-900/40 text-purple-600 dark:text-purple-400">
              <Upload className="h-6 w-6" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-slate-900 dark:text-white">Bulk CSV Product Import</h2>
              <p className="text-xs text-slate-500">Live progress tracking during bulk database inserts</p>
            </div>
          </div>

          <div className="space-y-3">
            <label className="text-xs font-semibold text-slate-700 dark:text-slate-300">Select CSV File</label>
            <div className="flex gap-2">
              <input
                type="file"
                accept=".csv"
                onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                disabled={csvTracker.isProcessing}
                className="w-full text-xs text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-purple-50 file:text-purple-700 hover:file:bg-purple-100"
              />
              <button
                type="button"
                onClick={handleCreateSampleCSV}
                className="px-3 py-1 text-xs whitespace-nowrap rounded-lg border border-slate-300 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300"
              >
                Use Sample CSV
              </button>
            </div>
            {selectedFile && (
              <p className="text-xs text-purple-600 dark:text-purple-400">Selected: {selectedFile.name}</p>
            )}
          </div>

          <Button
            onClick={handleImportCSV}
            disabled={csvTracker.isProcessing || !selectedFile}
            className="w-full justify-center bg-purple-600 hover:bg-purple-700"
          >
            {csvTracker.isProcessing ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Importing Products...
              </>
            ) : (
              'Start Bulk Import (Celery Task)'
            )}
          </Button>

          {/* Progress Tracker Bar */}
          {csvTracker.state !== 'IDLE' && (
            <div className="p-4 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 space-y-2">
              <div className="flex justify-between items-center text-xs font-medium">
                <span className="text-slate-600 dark:text-slate-300">{csvTracker.message}</span>
                <span className="font-bold text-purple-600 dark:text-purple-400">{csvTracker.progress}%</span>
              </div>
              <div className="w-full bg-slate-200 dark:bg-slate-700 h-2.5 rounded-full overflow-hidden">
                <div
                  className="bg-purple-600 h-2.5 rounded-full transition-all duration-300 ease-out"
                  style={{ width: `${csvTracker.progress}%` }}
                />
              </div>

              {csvTracker.state === 'SUCCESS' && csvTracker.result && (
                <div className="pt-2 flex items-center text-xs font-semibold text-emerald-600 dark:text-emerald-400">
                  <CheckCircle className="h-4 w-4 mr-1" /> {csvTracker.result.message}
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* SECTION 3: PostgreSQL Advanced Search Playground */}
      <SearchPlaygroundSection />
    </div>
  );
};

interface SearchResultItem {
  id: number;
  name: string;
  description: string;
  price: number;
  category: string;
}

const SearchPlaygroundSection: React.FC = () => {
  const [query, setQuery] = useState('iphoen');
  const [mode, setMode] = useState<'hybrid' | 'fuzzy' | 'fulltext'>('hybrid');
  const [results, setResults] = useState<SearchResultItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchedMeta, setSearchedMeta] = useState<any>(null);

  const executeSearch = async (searchTerm: string = query, searchMode: string = mode) => {
    if (!searchTerm.trim()) return;
    setLoading(true);
    try {
      const data = await apiClient.get<any>(
        `/products/search/advanced?q=${encodeURIComponent(searchTerm)}&mode=${searchMode}`
      );
      setResults(data.results || []);
      setSearchedMeta({ count: data.count, dialect: data.dialect, mode: data.mode });
    } catch (err: any) {
      alert('Search failed: ' + (err?.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleQuickTest = (testWord: string, testMode: 'hybrid' | 'fuzzy' | 'fulltext') => {
    setQuery(testWord);
    setMode(testMode);
    executeSearch(testWord, testMode);
  };

  return (
    <div className="bg-white dark:bg-slate-900 p-6 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-6">
      <div className="flex flex-col md:flex-row justify-between md:items-center gap-2">
        <div>
          <h2 className="text-xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <span>PostgreSQL Advanced Search Engine</span>
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-100 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border border-emerald-500/20 font-semibold">
              GIN & pg_trgm Powered
            </span>
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
            Full-Text Search (tsvector stemming) + Fuzzy Search (typo tolerance) + N+1 Eager Load Optimization
          </p>
        </div>

        {/* Quick Test Chips */}
        <div className="flex flex-wrap gap-1.5 items-center">
          <span className="text-xs text-slate-500 mr-1 font-medium">Try Typo / Keyword:</span>
          <button
            onClick={() => handleQuickTest('iphoen', 'fuzzy')}
            className="px-2.5 py-1 text-xs rounded-md bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-300 border border-amber-300 dark:border-amber-700 hover:bg-amber-100 transition-colors"
          >
            "iphoen" (Typo)
          </button>
          <button
            onClick={() => handleQuickTest('keybord', 'fuzzy')}
            className="px-2.5 py-1 text-xs rounded-md bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-300 border border-amber-300 dark:border-amber-700 hover:bg-amber-100 transition-colors"
          >
            "keybord" (Typo)
          </button>
          <button
            onClick={() => handleQuickTest('smartphone', 'fulltext')}
            className="px-2.5 py-1 text-xs rounded-md bg-blue-50 dark:bg-blue-950/40 text-blue-700 dark:text-blue-300 border border-blue-300 dark:border-blue-700 hover:bg-blue-100 transition-colors"
          >
            "smartphone" (FTS)
          </button>
          <button
            onClick={() => handleQuickTest('wireless', 'fulltext')}
            className="px-2.5 py-1 text-xs rounded-md bg-blue-50 dark:bg-blue-950/40 text-blue-700 dark:text-blue-300 border border-blue-300 dark:border-blue-700 hover:bg-blue-100 transition-colors"
          >
            "wireless" (FTS)
          </button>
        </div>
      </div>

      {/* Search Input Bar */}
      <div className="flex flex-col sm:flex-row gap-3">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && executeSearch()}
          placeholder="Search products or type misspelling (e.g., iphoen, samsng, laptop)..."
          className="flex-1 px-4 py-2.5 text-sm rounded-lg border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white"
        />

        <div className="flex gap-2">
          <select
            value={mode}
            onChange={(e: any) => setMode(e.target.value)}
            className="px-3 py-2 text-xs font-medium rounded-lg border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white"
          >
            <option value="hybrid">Mode: Hybrid (Best)</option>
            <option value="fuzzy">Mode: Fuzzy (pg_trgm)</option>
            <option value="fulltext">Mode: Full-Text (tsvector)</option>
          </select>

          <Button onClick={() => executeSearch()} disabled={loading} className="px-5">
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Search'}
          </Button>
        </div>
      </div>

      {/* Results Display */}
      {searchedMeta && (
        <div className="space-y-3">
          <div className="flex justify-between items-center text-xs text-slate-500">
            <span>
              Found <strong className="text-slate-900 dark:text-white">{searchedMeta.count}</strong> products matching query "
              <strong>{query}</strong>" in <strong>{searchedMeta.mode}</strong> mode.
            </span>
            <span className="font-mono text-emerald-600 dark:text-emerald-400">Database: {searchedMeta.dialect}</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
            {results.map((product) => (
              <div
                key={product.id}
                className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/60 dark:bg-slate-800/40 space-y-1.5"
              >
                <div className="flex justify-between items-start gap-2">
                  <h3 className="font-bold text-sm text-slate-900 dark:text-white line-clamp-1">{product.name}</h3>
                  <span className="text-xs px-2 py-0.5 rounded bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300 font-semibold whitespace-nowrap">
                    ${product.price}
                  </span>
                </div>
                <p className="text-xs text-slate-500 dark:text-slate-400 line-clamp-2">{product.description}</p>
                <div className="pt-2 flex items-center justify-between text-xs text-slate-400">
                  <span>Category: <strong className="text-slate-700 dark:text-slate-300">{product.category}</strong></span>
                  <span className="text-emerald-600 dark:text-emerald-400 font-semibold">Matched</span>
                </div>
              </div>
            ))}
          </div>

          {results.length === 0 && (
            <div className="p-8 text-center text-sm text-slate-500 bg-slate-50 dark:bg-slate-800/40 rounded-xl">
              No products found matching "{query}". Try another typo keyword!
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default BackgroundTasksPage;