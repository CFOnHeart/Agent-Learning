import React, { useState, useRef, useEffect } from 'react';
import Message from './Message';
import userAvatar from '../images/avatar.png';
import agentAvatar from '../images/avatar.png';

export default function ChatWindow() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef();

  // 自动滚到底
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  async function handleSend() {
    if (!input.trim()) return;
    const userMsg = { from: 'user', avatar: userAvatar, content: input };
    setMessages(m => [...m, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input })
      });
      const data = await res.json();
      const agentMsg = { from: 'agent', avatar: agentAvatar, content: data.reply };
      setMessages(m => [...m, agentMsg]);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="chat-container">
      <div className="header">智能体聊天</div>
      <div className="messages">
        {messages.map((m, i) => <Message key={i} {...m} />)}
        <div ref={bottomRef} />
      </div>
      <div className="input-area">
        <textarea
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder="输入你的问题，支持多行…"
        />
        <button onClick={handleSend} disabled={loading}>
          {loading ? '思考中…' : '发送'}
        </button>
      </div>
    </div>
  );
}
