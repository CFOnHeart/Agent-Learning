import React from 'react';
import ReactMarkdown from 'react-markdown';
// import './Message.css'; // 可选：给气泡加点样式

export default function Message({ from, avatar, content }) {
  const isUser = from === 'user';
  return (
    <div className={`message-row ${isUser ? 'user' : 'agent'}`}>
      <img className="avatar" src={avatar} alt={`${from} avatar`} />
      <div className="bubble">
        <ReactMarkdown>{content}</ReactMarkdown>
      </div>
    </div>
  );
}
