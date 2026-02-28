import { emotionColor } from '../theme';

interface Props {
  text: string;
  isUser: boolean;
  timestamp: string;
  emotion?: string;
  imageUrl?: string;
}

export default function MessageBubble({ text, isUser, timestamp, emotion, imageUrl }: Props) {
  return (
    <div className={`msg-row ${isUser ? 'msg-right' : 'msg-left'}`}>
      <div className={`msg-bubble ${isUser ? 'msg-user' : 'msg-bot'}`}>
        {emotion && !isUser && (
          <span
            className="emotion-dot"
            style={{ background: emotionColor[emotion] || emotionColor.neutral }}
            title={emotion}
          />
        )}
        <p className="msg-text">{text}</p>
        {imageUrl && <img src={imageUrl} alt="" className="msg-image" />}
        <span className="msg-time">{timestamp}</span>
      </div>
    </div>
  );
}
