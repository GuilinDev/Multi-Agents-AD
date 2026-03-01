import type { AppProps } from 'next/app';
import { useRouter } from 'next/router';
import { TabBar } from '@memowell/app/components/tab-bar';

export default function App({ Component, pageProps }: AppProps) {
  const router = useRouter();
  const showTabBar = !router.pathname.startsWith('/chat');

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <div style={{ flex: 1 }}>
        <Component {...pageProps} />
      </div>
      {showTabBar && <TabBar currentPath={router.pathname} />}
    </div>
  );
}
