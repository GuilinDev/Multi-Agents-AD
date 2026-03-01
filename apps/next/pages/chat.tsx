import { useRouter } from 'next/router';
import { ChatScreen } from '@memowell/app';

export default function ChatPage() {
  const router = useRouter();
  const { patientId, patientName } = router.query;

  if (!patientId || !patientName) {
    return null;
  }

  return (
    <ChatScreen
      patientId={patientId as string}
      patientName={patientName as string}
    />
  );
}
