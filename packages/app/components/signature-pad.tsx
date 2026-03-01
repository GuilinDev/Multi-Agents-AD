import React, { useRef, useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Platform } from 'react-native';
import { colors } from '../theme/colors';

interface Props {
  onConfirm: (pathData: string) => void;
}

export function SignaturePad({ onConfirm }: Props) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [hasDrawn, setHasDrawn] = useState(false);
  const isDrawing = useRef(false);

  useEffect(() => {
    if (Platform.OS !== 'web') return;
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas size to match display size
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = rect.height;
    ctx.strokeStyle = '#000';
    ctx.lineWidth = 2.5;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';

    const getPos = (e: MouseEvent | TouchEvent) => {
      const r = canvas.getBoundingClientRect();
      if ('touches' in e) {
        return { x: e.touches[0].clientX - r.left, y: e.touches[0].clientY - r.top };
      }
      return { x: (e as MouseEvent).clientX - r.left, y: (e as MouseEvent).clientY - r.top };
    };

    const onStart = (e: MouseEvent | TouchEvent) => {
      e.preventDefault();
      isDrawing.current = true;
      const pos = getPos(e);
      ctx.beginPath();
      ctx.moveTo(pos.x, pos.y);
    };

    const onMove = (e: MouseEvent | TouchEvent) => {
      if (!isDrawing.current) return;
      e.preventDefault();
      const pos = getPos(e);
      ctx.lineTo(pos.x, pos.y);
      ctx.stroke();
      setHasDrawn(true);
    };

    const onEnd = () => {
      isDrawing.current = false;
    };

    canvas.addEventListener('mousedown', onStart);
    canvas.addEventListener('mousemove', onMove);
    canvas.addEventListener('mouseup', onEnd);
    canvas.addEventListener('mouseleave', onEnd);
    canvas.addEventListener('touchstart', onStart, { passive: false });
    canvas.addEventListener('touchmove', onMove, { passive: false });
    canvas.addEventListener('touchend', onEnd);

    return () => {
      canvas.removeEventListener('mousedown', onStart);
      canvas.removeEventListener('mousemove', onMove);
      canvas.removeEventListener('mouseup', onEnd);
      canvas.removeEventListener('mouseleave', onEnd);
      canvas.removeEventListener('touchstart', onStart);
      canvas.removeEventListener('touchmove', onMove);
      canvas.removeEventListener('touchend', onEnd);
    };
  }, []);

  const handleClear = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    setHasDrawn(false);
  };

  const handleConfirm = () => {
    const canvas = canvasRef.current;
    if (!canvas || !hasDrawn) return;
    const dataUrl = canvas.toDataURL('image/png');
    onConfirm(dataUrl);
  };

  if (Platform.OS !== 'web') {
    // Native fallback - simple placeholder
    return (
      <View style={styles.container}>
        <View style={[styles.canvas, { justifyContent: 'center', alignItems: 'center' }]}>
          <Text style={styles.placeholder}>Signature (native coming soon)</Text>
        </View>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.canvasWrapper}>
        <canvas
          ref={canvasRef as any}
          style={{
            width: '100%',
            height: 200,
            backgroundColor: '#FFFFFF',
            borderRadius: 12,
            border: `1px solid ${colors.border}`,
            touchAction: 'none',
            cursor: 'crosshair',
          }}
        />
        {!hasDrawn && (
          <Text style={styles.overlayPlaceholder}>Sign here</Text>
        )}
      </View>
      <View style={styles.actions}>
        <TouchableOpacity style={styles.clearButton} onPress={handleClear}>
          <Text style={styles.clearText}>Clear</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.confirmButton, !hasDrawn && styles.buttonDisabled]}
          onPress={handleConfirm}
          disabled={!hasDrawn}
        >
          <Text style={styles.confirmText}>Confirm Signature</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { width: '100%' },
  canvasWrapper: { position: 'relative' },
  canvas: {
    height: 200,
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: colors.border,
    overflow: 'hidden',
  },
  overlayPlaceholder: {
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: [{ translateX: -30 }, { translateY: -10 }],
    color: colors.textLight,
    fontSize: 16,
    pointerEvents: 'none' as any,
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
