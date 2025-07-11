import React, { useState, useRef, useEffect } from 'react';
import Message from './Message';
import LoadingMessage from './LoadingMessage';
import StreamingMessage from './StreamingMessage';
import userAvatar from '../images/avatar.png';
import agentAvatar from '../images/avatar.png';

export default function ChatWindow() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [streamingContent, setStreamingContent] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const bottomRef = useRef();

  // 自动滚到底
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading, streamingContent]);

  async function handleSend() {
    if (!input.trim() || loading || isStreaming) return;
    const userMsg = { from: 'user', avatar: userAvatar, content: input };
    const currentInput = input;
    setMessages(m => [...m, userMsg]);
    setInput('');
    setLoading(true);
    setStreamingContent('');
    setIsStreaming(false);

    try {
      // 使用streaming endpoint
      const response = await fetch('http://localhost:8000/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: currentInput })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      
      setLoading(false);
      setIsStreaming(true);
      let accumulatedContent = '';

      try {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));
                if (data.type === 'chunk' && data.content) {
                  accumulatedContent += data.content;
                  setStreamingContent(accumulatedContent);
                } else if (data.type === 'end') {
                  // Streaming结束，将内容添加到messages
                  const agentMsg = { 
                    from: 'agent', 
                    avatar: agentAvatar, 
                    content: accumulatedContent 
                  };
                  setMessages(m => [...m, agentMsg]);
                  setStreamingContent('');
                  setIsStreaming(false);
                  return;
                }
              } catch (parseError) {
                console.error('Error parsing SSE data:', parseError);
              }
            }
          }
        }
      } finally {
        reader.releaseLock();
      }

    } catch (e) {
      console.error('Streaming error:', e);
      setLoading(false);
      setIsStreaming(false);
      setStreamingContent('');
      
      // 回退到普通API
      try {
        const res = await fetch('http://localhost:8000/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: currentInput })
        });
        const data = await res.json();
        const agentMsg = { from: 'agent', avatar: agentAvatar, content: data.reply };
        setMessages(m => [...m, agentMsg]);
      } catch (fallbackError) {
        console.error('Fallback error:', fallbackError);
        const errorMsg = { 
          from: 'agent', 
          avatar: agentAvatar, 
          content: 'Sorry, something went wrong. Please try again.' 
        };
        setMessages(m => [...m, errorMsg]);
      }
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
        {isStreaming && streamingContent && (
          <StreamingMessage 
            from="agent" 
            avatar={agentAvatar} 
            content={streamingContent} 
          />
        )}
        <div ref={bottomRef} />
      </div>
      <div className="input-area">
        <textarea
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="输入你的问题，支持多行…（Enter发送，Shift+Enter换行）"
        />
        <button onClick={handleSend} disabled={loading || isStreaming}>
          {loading ? '思考中…' : isStreaming ? '回复中…' : '发送'}
        </button>
      </div>
    </div>
  );
}
