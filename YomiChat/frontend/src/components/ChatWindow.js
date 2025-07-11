import React, { useState, useRef, useEffect } from 'react';
import Message from './Message';
import LoadingMessage from './LoadingMessage';
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
  }, [messages, loading]);

  async function handleSend() {
    if (!input.trim() || loading) return;
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
      // 添加错误处理消息
      const errorMsg = { from: 'agent', avatar: agentAvatar, content: 'Sorry, something went wrong. Please try again.' };
      setMessages(m => [...m, errorMsg]);
    } finally {
      setLoading(false);
    }
  }

  function handleKeyPress(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <div className="chat-container">
      <div className="header">智能体聊天</div>
      <div className="messages">
        {messages.map((m, i) => <Message key={i} {...m} />)}
        {loading && <LoadingMessage avatar={agentAvatar} />}
        <div ref={bottomRef} />
      </div>
      <div className="input-area">
        <textarea
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="输入你的问题，支持多行…（Enter发送，Shift+Enter换行）"
        />
        <button onClick={handleSend} disabled={loading}>
          {loading ? '思考中…' : '发送'}
        </button>
      </div>
    </div>
  );
}
