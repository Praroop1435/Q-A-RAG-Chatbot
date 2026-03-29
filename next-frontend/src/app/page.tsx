"use client";

import { useState, useRef, useEffect } from "react";
import { UploadCloud, File, Loader2, ArrowRight, Database, Server, ChevronDown, ChevronUp, TerminalSquare } from "lucide-react";
import { CommandPalette } from "@/components/CommandPalette";
import { motion, AnimatePresence } from "framer-motion";

type Message = {
  role: "user" | "assistant";
  content: string;
  context?: string[];
};

export default function Home() {
  const [cmdOpen, setCmdOpen] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [ingested, setIngested] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  
  // Document Stats
  const [docChunks, setDocChunks] = useState(0);

  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [isQuerying, setIsQuerying] = useState(false);
  
  const [openContextIdx, setOpenContextIdx] = useState<number | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isQuerying]);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (!selected) return;
    
    setFile(selected);
    setIsUploading(true);
    setIngested(false);

    const formData = new FormData();
    formData.append("file", selected);

    try {
      const res = await fetch("http://localhost:8000/ingest", {
        method: "POST",
        body: formData,
      });

      if (res.ok) {
        const data = await res.json();
        setIngested(true);
        setDocChunks(data.chunks);
      } else {
        alert("Failed to ingest PDF");
      }
    } catch (err) {
      alert("Error connecting to backend");
    } finally {
      setIsUploading(false);
    }
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim() || !ingested) return;

    const userQ = question;
    setMessages((prev) => [...prev, { role: "user", content: userQ }]);
    setQuestion("");
    setIsQuerying(true);

    try {
      const res = await fetch("http://localhost:8000/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: userQ }),
      });

      if (res.ok) {
        const data = await res.json();
        setMessages((prev) => [...prev, { 
          role: "assistant", 
          content: data.answer, 
          context: data.context 
        }]);
      } else {
        setMessages((prev) => [...prev, { role: "assistant", content: "Error: Could not retrieve answer." }]);
      }
    } catch (err) {
      setMessages((prev) => [...prev, { role: "assistant", content: "Error: Failed to connect to server." }]);
    } finally {
      setIsQuerying(false);
    }
  };

  return (
    <div className="flex h-screen w-full bg-black text-neutral-50 font-mono overflow-hidden">
      <CommandPalette open={cmdOpen} setOpen={setCmdOpen} onClear={() => setMessages([])} />

      {/* Left Panel: Knowledge Base & Upload Status */}
      <aside className="w-1/3 min-w-[320px] max-w-md border-r border-neutral-800 bg-[#0a0a0a] flex flex-col">
        {/* Header */}
        <header className="flex items-center justify-between p-6 border-b border-neutral-800/50">
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded border border-neutral-800 bg-black font-bold text-neutral-100">
              A
            </div>
            <span className="font-semibold tracking-wide text-sm">LLM Engine</span>
          </div>
          <button
            onClick={() => setCmdOpen(true)}
            className="flex items-center gap-2 rounded-md border border-neutral-800 bg-black px-2 py-1 text-[10px] text-neutral-400 font-sans transition-colors hover:border-neutral-600 hover:text-neutral-100"
          >
            ⌘K
          </button>
        </header>

        {/* Upload Container */}
        <div className="p-6 flex-1 flex flex-col gap-6">
          <section>
             <h2 className="mb-3 text-[10px] font-medium tracking-widest text-neutral-500 uppercase">
              Knowledge Source
            </h2>
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={isUploading}
              className={`group flex w-full flex-col items-center justify-center gap-3 rounded-lg border border-dashed border-neutral-800 px-6 py-10 transition-all ${
                ingested
                  ? "bg-black/50 border-green-900/40 hover:border-green-800/60"
                  : "bg-black hover:border-neutral-600 hover:bg-neutral-900"
              }`}
            >
              {isUploading ? (
                <Loader2 className="h-6 w-6 animate-spin text-neutral-400" />
              ) : ingested ? (
                <File className="h-6 w-6 text-green-500/80 group-hover:text-green-400/80" />
              ) : (
                <UploadCloud className="h-6 w-6 text-neutral-500 group-hover:text-neutral-300" />
              )}
              <div className="text-center">
                <p className="text-xs font-medium text-neutral-300">
                  {isUploading
                    ? "Indexing document..."
                    : ingested
                    ? file?.name || "Document Encoded"
                    : "Upload PDF Context"}
                </p>
              </div>
            </button>
            <input
              type="file"
              id="pdf-upload"
              ref={fileInputRef}
              className="hidden"
              accept="application/pdf"
              onChange={handleFileChange}
            />
          </section>

          {/* Real-time Status Visualization */}
          <section className="flex flex-col gap-3">
            <h2 className="text-[10px] font-medium tracking-widest text-neutral-500 uppercase">
              System Telemetry
            </h2>
            <div className="flex flex-col gap-2">
              <div className="flex items-center justify-between rounded-md border border-neutral-800 bg-black p-3">
                 <div className="flex items-center gap-3 text-neutral-400">
                    <Server className="h-4 w-4" />
                    <span className="text-xs">FastAPI Backend</span>
                 </div>
                 <div className="flex items-center gap-1.5">
                    <div className="h-1.5 w-1.5 rounded-full bg-green-500 animate-pulse" />
                    <span className="text-[10px] text-green-500">Online</span>
                 </div>
              </div>

              {ingested && (
                <motion.div 
                  initial={{ opacity: 0, y: 5 }} 
                  animate={{ opacity: 1, y: 0 }}
                  className="flex items-center justify-between rounded-md border border-neutral-800 bg-black p-3"
                >
                   <div className="flex items-center gap-3 text-neutral-400">
                      <Database className="h-4 w-4" />
                      <span className="text-xs">Vector DB Chunks</span>
                   </div>
                   <div className="text-xs font-medium text-neutral-100">
                      {docChunks}
                   </div>
                </motion.div>
              )}
            </div>
          </section>
        </div>
        
        {/* Decorative Divider */}
        <div className="hatched-pattern h-8 w-full border-t border-neutral-800/50" />
      </aside>

      {/* Right Panel: Interactive Terminal */}
      <main className="flex-1 flex flex-col relative bg-black">
        {/* Terminal Output Area */}
        <div className={`flex-1 overflow-y-auto p-8 lg:p-12 transition-opacity duration-1000 ${ingested ? "opacity-100" : "opacity-20"}`}>
           
           {!ingested && (
             <div className="h-full flex items-center justify-center text-neutral-600">
                <p className="text-sm">Awaiting knowledge source injection...</p>
             </div>
           )}

           <div className="mx-auto w-full max-w-4xl space-y-8">
              <AnimatePresence>
                {messages.map((msg, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={`flex flex-col ${msg.role === "user" ? "items-start" : "items-start"}`}
                  >
                    <div className="mb-2 flex items-center gap-2">
                       {msg.role === "assistant" ? (
                         <TerminalSquare className="h-3 w-3 text-neutral-500" />
                       ) : (
                         <div className="h-1.5 w-1.5 rounded-full bg-neutral-500" />
                       )}
                       <span className="text-[10px] uppercase tracking-widest text-neutral-500">
                         {msg.role === "user" ? "query" : "system.response"}
                       </span>
                    </div>

                    <div
                      className={`w-full rounded-md p-4 text-sm leading-relaxed ${
                        msg.role === "user"
                          ? "border border-neutral-800 bg-[#0a0a0a] text-neutral-300"
                          : "text-neutral-100"
                      }`}
                    >
                      {msg.content}
                    </div>

                    {/* RAG Context Visualization Explorer */}
                    {msg.context && msg.context.length > 0 && (
                      <div className="mt-4 w-full border border-neutral-800 rounded-md overflow-hidden bg-[#0A0A0A]">
                         <button
                           onClick={() => setOpenContextIdx(openContextIdx === i ? null : i)}
                           className="flex w-full items-center justify-between bg-black px-4 py-2 hover:bg-neutral-900 transition-colors"
                         >
                            <span className="text-xs text-neutral-400">
                              <Database className="inline h-3 w-3 mr-2" />
                              View {msg.context.length} Retrieved Snippets
                            </span>
                            {openContextIdx === i ? (
                              <ChevronUp className="h-3 w-3 text-neutral-500" />
                            ) : (
                              <ChevronDown className="h-3 w-3 text-neutral-500" />
                            )}
                         </button>
                         
                         <AnimatePresence>
                           {openContextIdx === i && (
                             <motion.div
                               initial={{ height: 0, opacity: 0 }}
                               animate={{ height: "auto", opacity: 1 }}
                               exit={{ height: 0, opacity: 0 }}
                               className="overflow-hidden border-t border-neutral-800"
                             >
                                <div className="max-h-60 overflow-y-auto p-4 space-y-4 bg-[#050505]">
                                  {msg.context.map((chunk, chunkIdx) => (
                                    <div key={chunkIdx} className="text-[11px] leading-relaxed text-neutral-500">
                                      <span className="font-bold text-neutral-400 mb-1 block">Chunk {chunkIdx + 1}</span>
                                      {chunk}
                                    </div>
                                  ))}
                                </div>
                             </motion.div>
                           )}
                         </AnimatePresence>
                      </div>
                    )}
                  </motion.div>
                ))}
                
                {isQuerying && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="flex flex-col items-start"
                  >
                    <div className="mb-2 flex items-center gap-2">
                       <TerminalSquare className="h-3 w-3 text-neutral-500" />
                       <span className="text-[10px] uppercase tracking-widest text-neutral-500">system.retrieval</span>
                    </div>
                    <div className="flex animate-pulse items-center gap-3 px-4 py-2 text-sm text-neutral-400">
                      <Loader2 className="h-4 w-4 animate-spin text-neutral-500" />
                      <span>Vectorizing intent and scanning database...</span>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
              <div ref={messagesEndRef} />
           </div>
        </div>

        {/* Input Form Area */}
        <div className="border-t border-neutral-800 bg-black p-6 lg:p-8">
           <form onSubmit={handleSearch} className="mx-auto flex w-full max-w-4xl relative items-center pointer-events-auto">
             <span className="absolute left-4 text-green-500/80 font-bold">&gt;</span>
             <input
               type="text"
               value={question}
               onChange={(e) => setQuestion(e.target.value)}
               placeholder="Execute a semantic search query..."
               className="w-full rounded-md border border-neutral-800 bg-[#0a0a0a] py-4 pl-10 pr-12 text-sm text-neutral-50 transition-colors focus:border-neutral-600 focus:outline-none focus:ring-0 placeholder:text-neutral-700 disabled:opacity-50"
               disabled={!ingested || isQuerying}
             />
             <button
               type="submit"
               disabled={!question.trim() || !ingested || isQuerying}
               className="absolute right-3 rounded bg-neutral-800 p-1.5 text-neutral-400 transition-colors hover:bg-neutral-600 hover:text-neutral-100 disabled:opacity-50"
             >
               <ArrowRight className="h-4 w-4" />
             </button>
           </form>
           
           {/* Diagonal hatched pattern for pure aesthetic underneath input */}
           <div className="mx-auto mt-6 w-full max-w-4xl hatched-pattern h-1" />
        </div>
      </main>
    </div>
  );
}
