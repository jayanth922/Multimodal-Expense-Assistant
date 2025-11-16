import "./globals.css";

export const metadata = { title: "Multimodal Expense Assistant" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-zinc-100 to-zinc-50 text-zinc-900 antialiased">
        <div className="pointer-events-none fixed inset-0 -z-10">
          {/* subtle blurred glow */}
          <div className="absolute right-[-20%] top-[-20%] h-[40rem] w-[40rem] rounded-full bg-amber-200 blur-[80px] opacity-30" />
          <div className="absolute left-[-10%] bottom-[-20%] h-[32rem] w-[32rem] rounded-full bg-emerald-200 blur-[90px] opacity-30" />
        </div>
        {children}
      </body>
    </html>
  );
}