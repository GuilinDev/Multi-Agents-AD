import { useRouter } from 'next/router';
import { ChatScreen } from '@memowell/app';

export default function ChatPage() {
  const router = useRouter();
  const { sessionId, patientName } = router.query;

  if (!sessionId || !patientName) {
    return null;
  }

  return (
    <ChatScreen
      sessionId={sessionId as string}
      patientName={patientName as string}
    />
  );
}
