import Header from "@/components/Header";
import Chat from "@/components/Chat";
import ReceiptUpload from "@/components/ReceiptUpload";
import Summary from "@/components/Summary";

export default function Home() {
  return (
    <main>
      <Header />

      <section className="max-w-5xl mx-auto px-4 mt-6">
        <h2 className="text-lg font-semibold mb-3">1) Chat</h2>
        <Chat />
      </section>

      <section className="max-w-5xl mx-auto px-4 mt-8">
        <h2 className="text-lg font-semibold mb-3">2) Upload a receipt</h2>
        <ReceiptUpload />
      </section>

      <section className="max-w-5xl mx-auto px-4 mt-8 pb-16">
        <h2 className="text-lg font-semibold mb-3">3) Summaries</h2>
        <Summary />
      </section>
    </main>
  );
}