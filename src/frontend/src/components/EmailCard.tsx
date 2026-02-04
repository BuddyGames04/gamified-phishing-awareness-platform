import React from 'react';
import { Email } from '../api';

interface EmailCardProps {
  email: Email;
  onSelect: (email: Email) => void;
  selected: boolean;
}

const EmailCard: React.FC<EmailCardProps> = ({ email, onSelect, selected }) => {
  return (
    <div
      onClick={() => onSelect(email)}
      style={{
        padding: '8px',
        cursor: 'pointer',
        background: selected ? '#eef' : 'white',
        borderBottom: '1px solid #ddd',
      }}
    >
      <strong>{email.sender_name}</strong>
      <div>{email.subject}</div>
    </div>
  );
};

export default EmailCard;
