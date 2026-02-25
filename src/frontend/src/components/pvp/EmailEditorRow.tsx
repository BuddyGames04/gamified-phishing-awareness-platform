import React from 'react';

export type EmailDraft = {
  sender_name: string;
  sender_email: string;
  subject: string;
  body: string;
  is_phish: boolean;
  difficulty: number;
  category?: string;
  payloadType: 'link' | 'attachment';
  payloadValue: string; // one link or filename
  is_wave: boolean;
};

type Props = {
  index: number;
  value: EmailDraft;
  onChange: (next: EmailDraft) => void;
  onDelete: () => void;
  error?: string | null;
};

const EmailEditorRow: React.FC<Props> = ({
  index,
  value,
  onChange,
  onDelete,
  error,
}) => {
  const set = (patch: Partial<EmailDraft>) => onChange({ ...value, ...patch });

  return (
    <div
      style={{
        border: '1px solid rgba(255,255,255,0.12)',
        borderRadius: 10,
        padding: 12,
        display: 'grid',
        gap: 10,
      }}
    >
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          gap: 10,
        }}
      >
        <div style={{ fontWeight: 800 }}>Email #{index + 1}</div>
        <button className="btn" onClick={onDelete}>
          Delete
        </button>
      </div>

      {error && <div style={{ color: 'salmon', fontSize: 13 }}>{error}</div>}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
        <input
          className="fake-search"
          placeholder="Sender name"
          value={value.sender_name}
          onChange={(e) => set({ sender_name: e.target.value })}
        />
        <input
          className="fake-search"
          placeholder="Sender email"
          value={value.sender_email}
          onChange={(e) => set({ sender_email: e.target.value })}
        />
      </div>

      <input
        className="fake-search"
        placeholder="Subject"
        value={value.subject}
        onChange={(e) => set({ subject: e.target.value })}
      />

      <textarea
        style={{ width: '100%', minHeight: 90 }}
        placeholder="Body"
        value={value.body}
        onChange={(e) => set({ body: e.target.value })}
      />

      <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', alignItems: 'center' }}>
        <label style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
          <input
            type="checkbox"
            checked={value.is_phish}
            onChange={(e) => set({ is_phish: e.target.checked })}
          />
          Phish
        </label>

        <label style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
          <input
            type="checkbox"
            checked={value.is_wave}
            onChange={(e) => set({ is_wave: e.target.checked })}
          />
          Wave email
        </label>

        <label style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
          Difficulty:
          <select
            value={value.difficulty}
            onChange={(e) => set({ difficulty: Number(e.target.value) })}
          >
            {[1, 2, 3, 4, 5].map((d) => (
              <option key={d} value={d}>
                {d}
              </option>
            ))}
          </select>
        </label>

        <input
          className="fake-search"
          style={{ maxWidth: 220 }}
          placeholder="Category (optional)"
          value={value.category ?? ''}
          onChange={(e) => set({ category: e.target.value })}
        />
      </div>

      <div style={{ display: 'grid', gap: 8 }}>
        <div style={{ fontWeight: 700 }}>Payload (XOR)</div>

        <div
          style={{ display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap' }}
        >
          <label style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
            <input
              type="radio"
              checked={value.payloadType === 'link'}
              onChange={() => set({ payloadType: 'link', payloadValue: '' })}
            />
            Link
          </label>

          <label style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
            <input
              type="radio"
              checked={value.payloadType === 'attachment'}
              onChange={() => set({ payloadType: 'attachment', payloadValue: '' })}
            />
            Attachment
          </label>
        </div>

        <input
          className="fake-search"
          placeholder={
            value.payloadType === 'link' ? 'https://example.com/...' : 'Invoice_123.pdf'
          }
          value={value.payloadValue}
          onChange={(e) => set({ payloadValue: e.target.value })}
        />
      </div>
    </div>
  );
};

export default EmailEditorRow;
