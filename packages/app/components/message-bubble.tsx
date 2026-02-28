import React from 'react';
import { View, Text, Image, StyleSheet } from 'react-native';
import { colors } from '../theme/colors';
import type { ChatMessage } from '../types';

interface Props {
  message: ChatMessage;
  baseUrl: string;
}

const emotionColors: Record<string, string> = {
  happy: colors.happy,
  calm: colors.calm,
  nostalgic: colors.nostalgic,
  confused: colors.confused,
  anxious: colors.anxious,
  frustrated: colors.frustrated,
};

export function MessageBubble({ message, baseUrl }: Props) {
  const isUser = message.role === 'user';

  return (
    <View style={[styles.container, isUser ? styles.userContainer : styles.assistantContainer]}>
      {!isUser && message.monitor && (
        <View
          style={[
            styles.emotionDot,
            { backgroundColor: emotionColors[message.monitor.emotion] || colors.textLight },
          ]}
        />
      )}
      <View style={[styles.bubble, isUser ? styles.userBubble : styles.assistantBubble]}>
        <Text style={[styles.text, isUser ? styles.userText : styles.assistantText]}>
          {message.content}
        </Text>
        {message.imageUrl && (
          <Image
            source={{ uri: `${baseUrl}${message.imageUrl}` }}
            style={styles.sceneImage}
            resizeMode="cover"
          />
        )}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    marginVertical: 6,
    paddingHorizontal: 12,
    alignItems: 'flex-end',
  },
  userContainer: { justifyContent: 'flex-end' },
  assistantContainer: { justifyContent: 'flex-start' },
  emotionDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    marginRight: 6,
    marginBottom: 8,
  },
  bubble: {
    maxWidth: '78%',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 20,
  },
  userBubble: {
    backgroundColor: colors.primary,
    borderBottomRightRadius: 4,
  },
  assistantBubble: {
    backgroundColor: colors.surface,
    borderBottomLeftRadius: 4,
    borderWidth: 1,
    borderColor: colors.border,
  },
  text: { fontSize: 18, lineHeight: 26 },
  userText: { color: '#FFFFFF' },
  assistantText: { color: colors.text },
  sceneImage: {
    width: '100%',
    height: 180,
    borderRadius: 12,
    marginTop: 10,
  },
});
