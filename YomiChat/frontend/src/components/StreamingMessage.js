import React from 'react';
import ReactMarkdown from 'react-markdown';

export default function StreamingMessage({ from, avatar, content }) {
  const isUser = from === 'user';
  return (
    <div className={`message-row ${isUser ? 'user' : 'agent'}`}>
      <img className="avatar" src={avatar} alt={`${from} avatar`} />
      <div className="bubble">
        <div className="streaming-content">
          <ReactMarkdown>{content}</ReactMarkdown>
          <span className="streaming-cursor"></span>
        </div>
      </div>
    </div>
  );
}
