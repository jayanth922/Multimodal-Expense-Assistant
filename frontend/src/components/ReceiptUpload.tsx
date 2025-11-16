"use client";
import { useState, useRef } from "react";
import api from "@/lib/api";
import { UploadCloud, CheckCircle2, Loader2 } from "lucide-react";
import { motion } from "framer-motion";

type UploadResp = {
  ok: boolean;
  note: string;
  vendor?: string;
  transaction_date?: string;
  total?: number;
  currency?: string;
  category?: string;
  items?: { description: string; quantity?: number; unit_price?: number; amount?: number }[];
  inserted_id?: number;
  confidence?: number;
};

export default function ReceiptUpload() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [resp, setResp] = useState<UploadResp | null>(null);
  const [loading, setLoading] = useState(false);
  const dropRef = useRef<HTMLDivElement>(null);

  function onPick(f: File | null) {
    setResp(null);
    setFile(f);
    setPreview(f ? URL.createObjectURL(f) : null);
  }

  function onDrop(e: React.DragEvent<HTMLDivElement>) {
    e.preventDefault();
    const f = e.dataTransfer.files?.[0];
    if (f) onPick(f);
  }

  async function upload() {
    if (!file) return;
    setLoading(true);
    setResp(null);
    try {
      const fd = new FormData();
      fd.append("file", file);
      const { data } = await api.post("/api/upload-receipt", fd, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setResp(data);
    } catch {
      setResp({ ok: false, note: "Upload failed." });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="w-full max-w-5xl mx-auto px-4 grid lg:grid-cols-[1.2fr_1fr] gap-6">
      <div
        ref={dropRef}
        onDragOver={(e) => e.preventDefault()}
        onDrop={onDrop}
        className="rounded-2xl border-2 border-dashed bg-white/70 backdrop-blur p-6 text-center hover:border-zinc-400 transition-shadow shadow-sm"
      >
        <div className="flex flex-col items-center gap-3">
          <UploadCloud className="text-zinc-600" />
          <p className="text-sm text-zinc-600">Drag & drop a receipt image here, or choose a file</p>
          <input
            type="file"
            accept="image/*"
            onChange={(e) => onPick(e.target.files?.[0] ?? null)}
            className="mx-auto block"
          />
          <button
            onClick={upload}
            disabled={!file || loading}
            className="mt-1 inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-black text-white disabled:opacity-50"
          >
            {loading ? <Loader2 size={16} className="animate-spin" /> : null}
            {loading ? "Uploading..." : "Upload"}
          </button>
        </div>

        {preview && (
          <motion.div
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-4 grid place-items-center"
          >
            <img
              src={preview}
              alt="preview"
              className="max-h-64 rounded-xl border object-contain"
            />
          </motion.div>
        )}
      </div>

      <div className="rounded-2xl border bg-white/70 backdrop-blur p-4 shadow-sm">
        <h3 className="font-semibold mb-2">Parse result</h3>
        {!resp && <p className="text-sm text-zinc-600">No result yet.</p>}

        {resp && (
          <div className="space-y-2 text-sm">
            <div className="flex items-center gap-2">
              {resp.ok ? (
                <CheckCircle2 className="text-emerald-600" />
              ) : (
                <span className="text-red-500">!</span>
              )}
              <span>{resp.note}</span>
            </div>
            {resp.ok && (
              <>
                <div className="grid grid-cols-2 gap-2">
                  <div><span className="text-zinc-500">Vendor:</span> <b>{resp.vendor}</b></div>
                  <div><span className="text-zinc-500">Date:</span> <b>{resp.transaction_date}</b></div>
                  <div><span className="text-zinc-500">Total:</span> <b>{resp.currency} {resp.total?.toFixed(2)}</b></div>
                  <div><span className="text-zinc-500">Category:</span> <b>{resp.category}</b></div>
                </div>
                {"confidence" in resp && typeof resp.confidence === "number" && (
                  <div>
                    <div className="flex justify-between text-xs text-zinc-500">
                      <span>Confidence</span>
                      <span>{Math.round((resp.confidence || 0) * 100)}%</span>
                    </div>
                    <div className="h-2 w-full bg-zinc-200 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-emerald-500"
                        style={{ width: `${Math.min(100, Math.max(0, Math.round((resp.confidence || 0) * 100)))}%` }}
                      />
                    </div>
                  </div>
                )}
              </>
            )}
            {!!resp?.items?.length && (
              <details className="mt-2">
                <summary className="cursor-pointer">Line items</summary>
                <div className="mt-2 rounded-lg border bg-white">
                  <table className="w-full text-xs">
                    <thead className="border-b">
                      <tr>
                        <th className="text-left p-2">Description</th>
                        <th className="text-right p-2">Qty</th>
                        <th className="text-right p-2">Unit</th>
                        <th className="text-right p-2">Amount</th>
                      </tr>
                    </thead>
                    <tbody>
                      {resp.items!.map((it, idx) => (
                        <tr key={idx} className="border-b last:border-0">
                          <td className="p-2">{it.description}</td>
                          <td className="p-2 text-right">{it.quantity ?? "-"}</td>
                          <td className="p-2 text-right">{it.unit_price ?? "-"}</td>
                          <td className="p-2 text-right">{it.amount ?? "-"}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </details>
            )}
          </div>
        )}
      </div>
    </div>
  );
}