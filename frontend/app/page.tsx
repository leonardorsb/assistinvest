"use client";

import { useState, useRef, useEffect } from "react";
import { Send, User, Bot, LineChart } from "lucide-react";

export default function PainelAgente() {
  const [input, setInput] = useState("");
  const [historico, setHistorico] = useState([
    { role: "agent", text: "Olá! Sou o seu agente de investimentos. Como posso te ajudar hoje?" }
  ]);
  const [carregando, setCarregando] = useState(false);
  const fimDoChatRef = useRef<HTMLDivElement>(null);

  // Rola o chat para baixo automaticamente
  useEffect(() => {
    fimDoChatRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [historico, carregando]);

  const enviarMensagem = async () => {
    if (!input.trim()) return;

    const mensagemUsuario = input;
    setInput("");
    
    // Adiciona a mensagem do utilizador à tela
    setHistorico((prev) => [...prev, { role: "user", text: mensagemUsuario }]);
    setCarregando(true); // Ativa o aviso "Analisando..."

    try {
      // Faz o pedido simples e aguarda a resposta final (Sem streaming quebrado)
      const res = await fetch("http://localhost:8000/api/agente", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mensagem: mensagemUsuario, session_id: "carteira_principal" }),
      });

      if (!res.ok) throw new Error("Sem resposta do servidor");

      const data = await res.json();

      // Imprime o texto final imaculado de uma só vez
      setHistorico((prev) => [...prev, { role: "agent", text: data.resposta }]);
      
    } catch (erro) {
      console.error(erro);
      setHistorico((prev) => [
        ...prev, 
        { role: "agent", text: "Erro de conexão. Verifique se o backend Python está rodando na porta 8000." }
      ]);
    } finally {
      setCarregando(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50 font-sans">
      <header className="bg-slate-900 text-white p-4 flex items-center shadow-md">
        <LineChart className="mr-3" />
        <h1 className="text-xl font-bold">Agente de Investimentos AI</h1>
      </header>

      <main className="flex-1 overflow-y-auto p-4 md:p-8">
        <div className="max-w-4xl mx-auto space-y-6">
          {historico.map((msg, idx) => (
            <div key={idx} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
              <div className={`flex items-start max-w-[85%] ${msg.role === "user" ? "flex-row-reverse" : "flex-row"}`}>
                <div className={`p-2 rounded-full ${msg.role === "user" ? "bg-blue-600 ml-3" : "bg-slate-700 mr-3"}`}>
                  {msg.role === "user" ? <User size={20} className="text-white" /> : <Bot size={20} className="text-white" />}
                </div>
                {/* O whitespace-pre-wrap garante que as tabelas Markdown mantêm o formato correto */}
                <div className={`p-4 rounded-2xl shadow-sm whitespace-pre-wrap ${msg.role === "user" ? "bg-blue-600 text-white rounded-tr-none" : "bg-white border border-gray-200 text-gray-800 rounded-tl-none"}`}>
                  {msg.text}
                </div>
              </div>
            </div>
          ))}
          {carregando && (
            <div className="flex items-center text-gray-500 text-sm ml-12 animate-pulse">
              ⏳ Analisando os dados...
            </div>
          )}
          <div ref={fimDoChatRef} />
        </div>
      </main>

      <footer className="p-4 bg-white border-t border-gray-200">
        <div className="max-w-4xl mx-auto flex items-center gap-2">
          <input
            type="text"
            className="flex-1 p-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-800"
            placeholder="Ex: Deseja informações sobre algum ativo ou fazer um aporte hoje?"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && enviarMensagem()}
            disabled={carregando}
          />
          <button
            onClick={enviarMensagem}
            disabled={carregando || !input.trim()}
            className="p-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl transition-colors disabled:opacity-50"
          >
            <Send size={24} />
          </button>
        </div>
      </footer>
    </div>
  );
}