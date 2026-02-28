import React, { useState, useRef, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  FlatList,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  Alert,
} from 'react-native';
import { Audio } from 'expo-av';
import { colors } from '../theme/colors';
import { ChatMessage, SessionInfo } from '../types';
import { sendMessage, sendAudio, endSession, getBaseUrl } from '../api/client';
import MessageBubble from '../components/MessageBubble';
import VoiceButton from '../components/VoiceButton';

interface Props {
  route: { params: { session: SessionInfo } };
  navigation: any;
}

export default function ChatScreen({ route, navigation }: Props) {
  const { session } = route.params;
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const [baseUrl, setBaseUrlState] = useState('');
  const flatListRef = useRef<FlatList>(null);
  const soundRef = useRef<Audio.Sound | null>(null);

  useEffect(() => {
    getBaseUrl().then(setBaseUrlState);
    navigation.setOptions({ title: session.patient_name });
    return () => {
      soundRef.current?.unloadAsync();
    };
  }, []);

  const playAudio = async (url: string) => {
    try {
      if (soundRef.current) {
        await soundRef.current.unloadAsync();
      }
      const { sound } = await Audio.Sound.createAsync({ uri: url });
      soundRef.current = sound;
      await sound.playAsync();
    } catch (err) {
      console.error('Audio playback error', err);
    }
  };

  const handleSend = async (text?: string, audioUri?: string) => {
    const msg = text ?? input.trim();
    if (!msg && !audioUri) return;
    setSending(true);

    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: audioUri ? '🎤 Voice message...' : msg,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');

    try {
      const res = audioUri
        ? await sendAudio(session.session_id, audioUri)
        : await sendMessage(session.session_id, msg);

      // Update user message if it was audio (show transcription)
      if (audioUri) {
        setMessages((prev) =>
          prev.map((m) => (m.id === userMsg.id ? { ...m, content: '🎤 (voice)' } : m))
        );
      }

      const assistantMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: res.response,
        audioUrl: res.audio_url ? `${baseUrl}${res.audio_url}` : undefined,
        imageUrl: res.image_url || undefined,
        monitor: res.monitor,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMsg]);

      // Auto-play TTS
      if (res.audio_url && baseUrl) {
        playAudio(`${baseUrl}${res.audio_url}`);
      }
    } catch (err: any) {
      Alert.alert('Error', err.message || 'Failed to send message');
    } finally {
      setSending(false);
    }
  };

  const handleEndSession = () => {
    Alert.alert('End Session', 'End this therapy session?', [
      { text: 'Cancel', style: 'cancel' },
      {
        text: 'End',
        style: 'destructive',
        onPress: async () => {
          try {
            const result = await endSession(session.session_id);
            Alert.alert('Session Summary', result.summary.slice(0, 500), [
              { text: 'OK', onPress: () => navigation.goBack() },
            ]);
          } catch {
            navigation.goBack();
          }
        },
      },
    ]);
  };

  useEffect(() => {
    navigation.setOptions({
      headerRight: () => (
        <TouchableOpacity onPress={handleEndSession} style={{ marginRight: 16 }}>
          <Text style={{ color: colors.error, fontSize: 16, fontWeight: '600' }}>End</Text>
        </TouchableOpacity>
      ),
    });
  }, []);

  const latestEmotion = messages
    .filter((m) => m.role === 'assistant' && m.monitor)
    .slice(-1)[0]?.monitor?.emotion;

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      keyboardVerticalOffset={90}
    >
      {latestEmotion && (
        <View style={styles.emotionBar}>
          <View
            style={[
              styles.emotionIndicator,
              { backgroundColor: (colors as any)[latestEmotion] || colors.textLight },
            ]}
          />
          <Text style={styles.emotionText}>{latestEmotion}</Text>
        </View>
      )}

      <FlatList
        ref={flatListRef}
        data={messages}
        keyExtractor={(m) => m.id}
        renderItem={({ item }) => <MessageBubble message={item} baseUrl={baseUrl} />}
        contentContainerStyle={styles.messageList}
        onContentSizeChange={() => flatListRef.current?.scrollToEnd({ animated: true })}
      />

      <View style={styles.inputBar}>
        <TextInput
          style={styles.textInput}
          value={input}
          onChangeText={setInput}
          placeholder="Type a message..."
          placeholderTextColor={colors.textLight}
          multiline
          editable={!sending}
          onSubmitEditing={() => handleSend()}
        />
        <VoiceButton
          onRecordingComplete={(uri) => handleSend(undefined, uri)}
          disabled={sending}
        />
        <TouchableOpacity
          style={[styles.sendButton, (!input.trim() || sending) && styles.sendButtonDisabled]}
          onPress={() => handleSend()}
          disabled={!input.trim() || sending}
          activeOpacity={0.7}
        >
          <Text style={styles.sendIcon}>➤</Text>
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  emotionBar: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 8,
    backgroundColor: colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  emotionIndicator: {
    width: 12,
    height: 12,
    borderRadius: 6,
    marginRight: 8,
  },
  emotionText: {
    fontSize: 14,
    color: colors.textSecondary,
    textTransform: 'capitalize',
  },
  messageList: {
    paddingVertical: 12,
  },
  inputBar: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    paddingHorizontal: 12,
    paddingVertical: 10,
    backgroundColor: colors.surface,
    borderTopWidth: 1,
    borderTopColor: colors.border,
    gap: 8,
  },
  textInput: {
    flex: 1,
    minHeight: 48,
    maxHeight: 120,
    backgroundColor: colors.card,
    borderRadius: 24,
    paddingHorizontal: 18,
    paddingVertical: 12,
    fontSize: 17,
    color: colors.text,
  },
  sendButton: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
  },
  sendButtonDisabled: {
    opacity: 0.4,
  },
  sendIcon: {
    color: '#FFF',
    fontSize: 20,
  },
});
