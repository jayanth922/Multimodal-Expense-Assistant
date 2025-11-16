"use client";
import { Sparkles, ReceiptText } from "lucide-react";
import { motion } from "framer-motion";

export default function Header() {
  return (
    <header className="max-w-5xl mx-auto px-4 pt-8 pb-2">
      <motion.div
        initial={{ opacity: 0, y: -8 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center gap-3"
      >
        <div className="h-10 w-10 rounded-2xl bg-black text-white grid place-items-center shadow-md">
          <ReceiptText size={22} />
        </div>
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Multimodal Expense Assistant</h1>
          <p className="text-sm text-zinc-600 flex items-center gap-1">
            <Sparkles size={16} className="text-amber-500" />
            Chat with your agent, upload receipts, and view insights.
          </p>
        </div>
      </motion.div>
    </header>
  );
}