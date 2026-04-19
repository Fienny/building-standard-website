import { useEffect, useMemo, useRef, useState } from 'react';
import './AIAssistant.css';

const CHAT_STORAGE_KEY = 'ai_assistant_messages_v1';
const REQUEST_TIMEOUT_MS = 45000;
const SUGGESTIONS = [
  'Какие требования по пожарной безопасности в жилых домах?',
  'Что сказано про вентиляцию в SHNQ 2.08.01-22?',
  'Какой документ нужен для проектирования детского сада?',
];

function safeParseMessages(raw) {
  if (!raw) {
    return [];
  }

  try {
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) {
      return [];
    }

    return parsed.filter((item) => item && typeof item.content === 'string').slice(-20);
  } catch {
    return [];
  }
}

function formatAssistantText(text) {
  if (!text) {
    return '';
  }
  return text.split('\n').map((line) => line.trim()).join('\n');
}

function AIAssistant() {
  const [messages, setMessages] = useState(() => safeParseMessages(localStorage.getItem(CHAT_STORAGE_KEY)));
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [networkHint, setNetworkHint] = useState('');
  const messageBoxRef = useRef(null);

  useEffect(() => {
    localStorage.setItem(CHAT_STORAGE_KEY, JSON.stringify(messages.slice(-20)));
  }, [messages]);

  useEffect(() => {
    if (!messageBoxRef.current) {
      return;
    }
    messageBoxRef.current.scrollTop = messageBoxRef.current.scrollHeight;
  }, [messages, loading, isOpen]);

  const canSend = useMemo(() => input.trim().length > 0 && !loading, [input, loading]);

  const sendMessage = async (messageText) => {
    const normalizedText = messageText.trim();
    if (!normalizedText) {
      return;
    }

    const userMessage = { role: 'user', content: normalizedText };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);
    setNetworkHint('');

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

    try {
      const response = await fetch('/api/ai/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: normalizedText }),
        signal: controller.signal,
      });

      const data = await response.json().catch(() => ({}));

      if (response.ok) {
        const aiMessage = {
          role: 'assistant',
          content: formatAssistantText(data.answer || 'Не удалось получить ответ от AI.'),
          sources: Array.isArray(data.sources) ? data.sources : [],
          table_html: data.table_html,
          image_urls: Array.isArray(data.image_urls) ? data.image_urls : [],
        };
        setMessages((prev) => [...prev, aiMessage]);
      } else {
        setMessages((prev) => [
          ...prev,
          {
            role: 'error',
            content: data.error || 'Произошла ошибка при обращении к AI-помощнику.',
          },
        ]);
      }
    } catch (error) {
      if (error.name === 'AbortError') {
        setNetworkHint('Ответ задерживается. Попробуйте более короткий вопрос или повторите запрос.');
      }
      setMessages((prev) => [
        ...prev,
        {
          role: 'error',
          content: 'Ошибка соединения с AI-сервисом.',
        },
      ]);
    } finally {
      clearTimeout(timeoutId);
      setLoading(false);
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!canSend) {
      return;
    }
    await sendMessage(input);
  };

  const clearChat = () => {
    setMessages([]);
    localStorage.removeItem(CHAT_STORAGE_KEY);
  };

  return (
    <>
      <button
        className="ai-assistant-toggle"
        onClick={() => setIsOpen((prev) => !prev)}
        title="AI-помощник по стандартам"
      >
        🤖
      </button>

      {isOpen && (
        <div className="ai-assistant-window" role="dialog" aria-label="AI помощник">
          <div className="ai-assistant-header">
            <h3>🤖 AI-помощник Benka</h3>
            <div className="ai-assistant-header-actions">
              <button onClick={clearChat} className="ai-clear-btn" type="button">
                Очистить
              </button>
              <button onClick={() => setIsOpen(false)} className="ai-close-btn" type="button">
                ×
              </button>
            </div>
          </div>

          <div className="ai-assistant-messages" ref={messageBoxRef}>
            {messages.length === 0 && (
              <div className="ai-welcome">
                <p>Здравствуйте! Я помогу подобрать стандарт и найти нужные требования.</p>
                <p>Быстрые подсказки:</p>
                <div className="ai-suggestion-list">
                  {SUGGESTIONS.map((suggestion) => (
                    <button
                      key={suggestion}
                      type="button"
                      className="ai-suggestion-btn"
                      onClick={() => sendMessage(suggestion)}
                      disabled={loading}
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {messages.map((msg, idx) => (
              <div key={`${msg.role}-${idx}`} className={`ai-message ai-message-${msg.role}`}>
                <div className="ai-message-content">
                  {msg.content.split('\n').map((line, index) => (
                    <p key={index}>{line}</p>
                  ))}

                  {msg.table_html && (
                    <div className="ai-table" dangerouslySetInnerHTML={{ __html: msg.table_html }} />
                  )}

                  {msg.image_urls && msg.image_urls.length > 0 && (
                    <div className="ai-images">
                      {msg.image_urls.map((url, imageIndex) => (
                        <a key={imageIndex} href={url} target="_blank" rel="noopener noreferrer">
                          <img src={url} alt={`Image ${imageIndex + 1}`} loading="lazy" />
                        </a>
                      ))}
                    </div>
                  )}

                  {msg.sources && msg.sources.length > 0 && (
                    <details className="ai-sources">
                      <summary>Источники ({msg.sources.length})</summary>
                      <ul>
                        {msg.sources.map((src, sourceIndex) => (
                          <li key={sourceIndex}>
                            <strong>{src.shnq_code || src.type}</strong>
                            {src.clause_number && ` — пункт ${src.clause_number}`}
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

          {networkHint && <div className="ai-network-hint">{networkHint}</div>}

          <form className="ai-assistant-input" onSubmit={handleSubmit}>
            <input
              type="text"
              value={input}
              onChange={(event) => setInput(event.target.value)}
              placeholder="Например: какой стандарт нужен для офисного здания?"
              disabled={loading}
            />
            <button type="submit" disabled={!canSend}>
              {loading ? '...' : 'Отправить'}
            </button>
          </form>
        </div>
      )}
    </>
  );
}

export default AIAssistant;
