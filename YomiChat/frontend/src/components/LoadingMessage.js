import React from 'react';

export default function LoadingMessage({ avatar }) {
  return (
    <div className="message-row agent">
      <img className="avatar" src={avatar} alt="agent avatar" />
      <div className="bubble loading-bubble">
        <span className="loading-text">Agent is thinking</span>
        <div className="loading-spinner"></div>
      </div>
    </div>
  );
}
