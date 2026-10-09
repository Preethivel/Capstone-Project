
import { useState } from 'react';
import { Bot, Send, Sparkles } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import api from '../services/api';

const prompts = ['Explain this lesson simply', 'Summarize this topic', 'Give me 5 practice questions', 'Help me understand this concept'];

const AiAssistant = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const [error, setError] = useState('');

  const send = async (value = input) => {
    const text = value.trim();
    if (!text || sending) return;
    setInput('');
    setError('');

    const updatedMessages = [...messages, { role: 'user', text }];
    setMessages(updatedMessages);
    setSending(true);

    // Build chat history for context/continuity
    const history = updatedMessages
      .map((m) => `${m.role === 'user' ? 'User' : 'Assistant'}: ${m.text}`)
      .join('\n');

    try {
      const response = await api.post(
        import.meta.env.VITE_AI_ENDPOINT || '/api/ai/chat',
        { message: text, context: history}
      );
      const reply =
        response.data?.data?.response ||
        response.data?.response ||
        response.data?.message;
      if (!reply) throw new Error('The assistant returned no message.');
      setMessages((current) => [...current, { role: 'assistant', text: reply }]);
    } catch (requestError) {
      setError(
        requestError.response?.data?.detail ||
        'AI service request failed'
      );
    } finally {
      setSending(false);
    }
  };

  return (
    <main className="page">
      <div className="container">
        <div className="dashboard-header">
          <div>
            <span className="eyebrow">Your learning companion</span>
            <h1>LearnVerse AI <span style={{ color: 'var(--blue)' }}>🤖</span></h1>
            <p>Ask for a simpler explanation, a new angle, or a little practice.</p>
          </div>
          <div className="badge"><Sparkles size={14} /> Personal assistant</div>
        </div>

        <div className="panel" style={{ maxWidth: 860, margin: '0 auto' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, paddingBottom: 20, borderBottom: '1px solid var(--line)' }}>
            <div className="stat-icon"><Bot size={19} /></div>
            <div>
              <h2 style={{ color: 'var(--navy)', fontSize: '1.15rem' }}>Your personal learning assistant</h2>
              <p className="muted" style={{ fontSize: '.84rem', marginTop: 3 }}>A thoughtful place to work through a tricky concept.</p>
            </div>
          </div>

          <div style={{ minHeight: 360, padding: '28px 0' }}>
            {messages.length === 0 ? (
              <div className="empty-state" style={{ border: 0, background: 'transparent' }}>
                <div className="empty-state-icon"><Bot size={25} /></div>
                <h3>Hi! I&apos;m your LearnVerse AI assistant.</h3>
                <p>What would you like to learn today?</p>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 9, justifyContent: 'center', marginTop: 22 }}>
                  {prompts.map((prompt) => (
                    <button className="btn btn-ghost" key={prompt} onClick={() => send(prompt)}>{prompt}</button>
                  ))}
                </div>
              </div>
            ) : (
              <div style={{ display: 'grid', gap: 14 }}>
                {messages.map((message, index) => (
                  <div key={`${message.role}-${index}`} style={{ display: 'flex', justifyContent: message.role === 'user' ? 'flex-end' : 'flex-start' }}>
                    <div style={{
                      maxWidth: '78%',
                      padding: '13px 16px',
                      color: message.role === 'user' ? 'white' : 'var(--ink)',
                      background: message.role === 'user' ? 'var(--blue)' : '#f2f5fb',
                      borderRadius: message.role === 'user' ? '15px 15px 4px 15px' : '15px 15px 15px 4px',
                      lineHeight: 1.6,
                    }}>
                      {message.role === 'assistant' ? (
                        <ReactMarkdown>{message.text}</ReactMarkdown>
                      ) : (
                        message.text
                      )}
                    </div>
                  </div>
                ))}
                {sending && (
                  <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
                    <div style={{ padding: '13px 16px', background: '#f2f5fb', borderRadius: '15px 15px 15px 4px', color: 'var(--ink)' }}>
                      Thinking...
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          {error && <div className="form-message" role="alert">{error}</div>}

          <form
            onSubmit={(event) => { event.preventDefault(); send(); }}
            style={{ display: 'flex', gap: 10, marginTop: 10 }}
          >
            <input
              className="input"
              value={input}
              onChange={(event) => setInput(event.target.value)}
              placeholder="Ask LearnVerse AI..."
              aria-label="Ask LearnVerse AI"
            />
            <button className="btn btn-primary" type="submit" disabled={sending || !input.trim()}>
              {sending ? 'Thinking...' : <><Send size={16} /> Send</>}
            </button>
          </form>
        </div>
      </div>
    </main>
  );
};

export default AiAssistant;