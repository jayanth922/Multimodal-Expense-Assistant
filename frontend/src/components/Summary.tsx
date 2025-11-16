"use client";
import { useEffect, useState } from "react";
import api from "@/lib/api";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import { Calendar, RefreshCcw } from "lucide-react";

type CatRow = { category: string; total: number };
type Total = { total: number; currency: string };

export default function Summary() {
  const [total, setTotal] = useState<Total | null>(null);
  const [cats, setCats] = useState<CatRow[]>([]);
  const [loading, setLoading] = useState(false);
  const [start, setStart] = useState<string>("");
  const [end, setEnd] = useState<string>("");

  async function refresh() {
    setLoading(true);
    try {
      const qs = new URLSearchParams();
      if (start) qs.append("start", start);
      if (end) qs.append("end", end);
      const [t, c] = await Promise.all([
        api.get(`/api/summary/total${qs.toString() ? "?" + qs.toString() : ""}`),
        api.get(`/api/summary/by-category${qs.toString() ? "?" + qs.toString() : ""}`),
      ]);
      setTotal(t.data);
      setCats(c.data);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { refresh(); }, []);

  return (
    <div className="w-full max-w-5xl mx-auto px-4 space-y-4">
      <div className="flex flex-wrap items-center gap-2">
        <div className="flex items-center gap-2 text-sm text-zinc-600">
          <Calendar size={16} />
          <input
            type="date"
            className="border rounded-lg px-2 py-1"
            value={start}
            onChange={(e) => setStart(e.target.value)}
          />
          <span>to</span>
          <input
            type="date"
            className="border rounded-lg px-2 py-1"
            value={end}
            onChange={(e) => setEnd(e.target.value)}
          />
        </div>
        <button
          onClick={refresh}
          className="ml-2 inline-flex items-center gap-2 px-3 py-2 rounded-xl bg-black text-white"
        >
          <RefreshCcw size={16} />
          {loading ? "Refreshing…" : "Refresh"}
        </button>
        {total && (
          <div className="text-sm text-zinc-700 ml-auto">
            Total spend: <b>{total.currency} {total.total.toFixed(2)}</b>
          </div>
        )}
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        <div className="rounded-2xl border bg-white/70 backdrop-blur p-4 shadow-sm">
          <h3 className="font-semibold mb-2">By category</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={cats}>
                <XAxis dataKey="category" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="total" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="rounded-2xl border bg-white/70 backdrop-blur p-4 shadow-sm">
          <h3 className="font-semibold mb-2">Table</h3>
          <div className="rounded-lg border bg-white overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left border-b">
                  <th className="py-2 px-3">Category</th>
                  <th className="py-2 px-3">Total</th>
                </tr>
              </thead>
              <tbody>
                {cats.map((r, i) => (
                  <tr key={i} className="border-b last:border-0">
                    <td className="py-2 px-3">{r.category}</td>
                    <td className="py-2 px-3">{r.total.toFixed(2)}</td>
                  </tr>
                ))}
                {!cats.length && (
                  <tr><td className="py-2 px-3 text-zinc-500" colSpan={2}>No data yet.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}