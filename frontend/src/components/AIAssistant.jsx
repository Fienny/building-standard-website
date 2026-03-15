import { useState } from 'react';
import './AIAssistant.css';

function AIAssistant() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch('/api/ai/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input }),
      });

      const data = await response.json();

      if (response.ok) {
        const aiMessage = {
          role: 'assistant',
          content: data.answer,
          sources: data.sources || [],
          table_html: data.table_html,
          image_urls: data.image_urls || [],
        };
        setMessages(prev => [...prev, aiMessage]);
      } else {
        const errorMessage = {
          role: 'error',
          content: data.error || 'Произошла ошибка при обращении к AI-помощнику',
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    } catch (error) {
      const errorMessage = {
        role: 'error',
        content: 'Ошибка соединения с сервером',
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* Floating button */}
      <button
        className="ai-assistant-toggle"
        onClick={() => setIsOpen(!isOpen)}
        title="AI-помощник по стандартам"
      >
        🤖
      </button>

      {/* Chat window */}
      {isOpen && (
        <div className="ai-assistant-window">
          <div className="ai-assistant-header">
            <h3>🤖 AI-помощник по стандартам</h3>
            <button onClick={() => setIsOpen(false)} className="ai-close-btn">×</button>
          </div>

          <div className="ai-assistant-messages">
            {messages.length === 0 && (
              <div className="ai-welcome">
                <p>Здравствуйте! Я AI-помощник по строительным стандартам РУз.</p>
                <p>Задайте вопрос, например:</p>
                <ul>
                  <li>"Что говорится в пункте 38 SHNQ 3.01.02-23?"</li>
                  <li>"Какие требования безопасности в норме 156?"</li>
                  <li>"Расскажи про таблицу 5 в SHNQ 2.07.01-23"</li>
                </ul>
              </div>
            )}

            {messages.map((msg, idx) => (
              <div key={idx} className={`ai-message ai-message-${msg.role}`}>
                <div className="ai-message-content">
                  {msg.content}

                  {msg.table_html && (
                    <div
                      className="ai-table"
                      dangerouslySetInnerHTML={{ __html: msg.table_html }}
                    />
                  )}

                  {msg.image_urls && msg.image_urls.length > 0 && (
                    <div className="ai-images">
                      {msg.image_urls.map((url, i) => (
                        <a key={i} href={url} target="_blank" rel="noopener noreferrer">
                          <img src={url} alt={`Image ${i + 1}`} />
                        </a>
                      ))}
                    </div>
                  )}

                  {msg.sources && msg.sources.length > 0 && (
                    <details className="ai-sources">
                      <summary>Источники ({msg.sources.length})</summary>
                      <ul>
                        {msg.sources.map((src, i) => (
                          <li key={i}>
                            <strong>{src.shnq_code || src.type}</strong>
                            {src.clause_number && ` - пункт ${src.clause_number}`}
                            {src.chapter && ` (${src.chapter})`}
                          </li>
                        ))}
                      </ul>
                    </details>
                  )}
                </div>
              </div>
            ))}

            {loading && (
              <div className="ai-message ai-message-loading">
                <div className="ai-typing">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            )}
          </div>

          <form className="ai-assistant-input" onSubmit={sendMessage}>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Задайте вопрос по стандартам..."
              disabled={loading}
            />
            <button type="submit" disabled={loading || !input.trim()}>
              Отправить
            </button>
          </form>
        </div>
      )}
    </>
  );
}

export default AIAssistant;
