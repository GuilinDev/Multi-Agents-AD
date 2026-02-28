import { Html, Head, Main, NextScript } from 'next/document';

export default function Document() {
  return (
    <Html lang="en">
      <Head>
        <meta name="application-name" content="Memowell" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="default" />
        <meta name="apple-mobile-web-app-title" content="Memowell" />
        <meta name="description" content="Reminiscence Therapy Companion" />
        <meta name="theme-color" content="#FFF8F0" />
        <link rel="manifest" href="/manifest.json" />
      </Head>
      <body style={{ backgroundColor: '#FFF8F0', margin: 0 }}>
        <Main />
        <NextScript />
      </body>
    </Html>
  );
}
