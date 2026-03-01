import React, { useRef, useState, useCallback } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, PanResponder, GestureResponderEvent } from 'react-native';
import { colors } from '../theme/colors';

interface Point {
  x: number;
  y: number;
}

interface Props {
  onConfirm: (pathData: string) => void;
}

export function SignaturePad({ onConfirm }: Props) {
  const [paths, setPaths] = useState<Point[][]>([]);
  const currentPathRef = useRef<Point[]>([]);
  const [activePath, setActivePath] = useState<Point[]>([]);
  const hasSignature = paths.length > 0;

  const getPoint = (e: GestureResponderEvent): Point => ({
    x: e.nativeEvent.locationX,
    y: e.nativeEvent.locationY,
  });

  const panResponder = useRef(
    PanResponder.create({
      onStartShouldSetPanResponder: () => true,
      onMoveShouldSetPanResponder: () => true,
      onPanResponderGrant: (e) => {
        const pt = getPoint(e);
        currentPathRef.current = [pt];
        setActivePath([pt]);
      },
      onPanResponderMove: (e) => {
        const pt = getPoint(e);
        currentPathRef.current.push(pt);
        setActivePath([...currentPathRef.current]);
      },
      onPanResponderRelease: () => {
        if (currentPathRef.current.length > 1) {
          setPaths((prev) => [...prev, [...currentPathRef.current]]);
        }
        currentPathRef.current = [];
        setActivePath([]);
      },
    })
  ).current;

  const allPaths = [...paths, ...(activePath.length > 0 ? [activePath] : [])];

  const renderLine = (prev: Point, point: Point, key: string) => {
    const dx = point.x - prev.x;
    const dy = point.y - prev.y;
    const len = Math.sqrt(dx * dx + dy * dy);
    if (len < 0.5) return null;
    const angle = (Math.atan2(dy, dx) * 180) / Math.PI;
    return (
      <View
        key={key}
        pointerEvents="none"
        style={{
          position: 'absolute',
          left: prev.x,
          top: prev.y - 1,
          width: len,
          height: 2.5,
          backgroundColor: '#000',
          transform: [{ rotate: `${angle}deg` }],
          transformOrigin: 'left center',
        }}
      />
    );
  };

  const handleClear = () => {
    setPaths([]);
    currentPathRef.current = [];
    setActivePath([]);
  };

  const handleConfirm = () => {
    if (!hasSignature) return;
    const data = JSON.stringify(
      paths.map((p) => p.map(({ x, y }) => [Math.round(x), Math.round(y)]))
    );
    onConfirm(data);
  };

  return (
    <View style={styles.container}>
      <View style={styles.canvas} {...panResponder.panHandlers}>
        {allPaths.map((path, pi) =>
          path.map((point, i) => {
            if (i === 0) return null;
            return renderLine(path[i - 1]!, point, `${pi}-${i}`);
          })
        )}
        {allPaths.length === 0 && (
          <Text style={styles.placeholder}>Sign here</Text>
        )}
      </View>
      <View style={styles.actions}>
        <TouchableOpacity style={styles.clearButton} onPress={handleClear}>
          <Text style={styles.clearText}>Clear</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.confirmButton, !hasSignature && styles.buttonDisabled]}
          onPress={handleConfirm}
          disabled={!hasSignature}
        >
          <Text style={styles.confirmText}>Confirm Signature</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { width: '100%' },
  canvas: {
    height: 200,
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: colors.border,
    overflow: 'hidden',
    justifyContent: 'center',
    alignItems: 'center',
  },
  placeholder: { color: colors.textLight, fontSize: 16 },
  actions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 12,
    gap: 12,
  },
  clearButton: {
    flex: 1,
    paddingVertical: 12,
    borderRadius: 8,
    backgroundColor: colors.card,
    alignItems: 'center',
  },
  clearText: { color: colors.textSecondary, fontSize: 16, fontWeight: '600' },
  confirmButton: {
    flex: 1,
    paddingVertical: 12,
    borderRadius: 8,
    backgroundColor: colors.primary,
    alignItems: 'center',
  },
  confirmText: { color: '#FFF', fontSize: 16, fontWeight: '600' },
  buttonDisabled: { opacity: 0.4 },
});
