import React from 'react';
import { StyleSheet, View } from 'react-native';
import { GestureDetector, Gesture } from 'react-native-gesture-handler';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withSpring,
  withTiming,
  runOnJS,
} from 'react-native-reanimated';

interface DoubleTapProps {
  children: React.ReactNode;
  onDoubleTap?: () => void;
}

export const DoubleTapToLike: React.FC<DoubleTapProps> = ({ children, onDoubleTap }) => {
  const scale = useSharedValue(1);
  const opacity = useSharedValue(0);

  const doubleTap = Gesture.Tap()
    .numberOfTaps(2)
    .onEnd(() => {
      scale.value = withSpring(1.5);
      opacity.value = withTiming(1, { duration: 200 }, () => {
        opacity.value = withTiming(0, { duration: 300 });
        scale.value = withSpring(1);
      });
      if (onDoubleTap) {
        runOnJS(onDoubleTap)();
      }
    });

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
    opacity: opacity.value,
  }));

  return (
    <GestureDetector gesture={doubleTap}>
      <View style={styles.container}>
        {children}
        <Animated.View style={[styles.heart, animatedStyle]}>
          <Text style={styles.heartIcon}>❤️</Text>
        </Animated.View>
      </View>
    </GestureDetector>
  );
};

export const DoubleTapZoom: React.FC<{
  children: React.ReactNode;
  maxScale?: number;
}> = ({ children, maxScale = 3 }) => {
  const scale = useSharedValue(1);
  const savedScale = useSharedValue(1);

  const doubleTap = Gesture.Tap()
    .numberOfTaps(2)
    .onEnd(() => {
      if (scale.value > 1) {
        scale.value = withSpring(1);
        savedScale.value = 1;
      } else {
        scale.value = withSpring(2);
        savedScale.value = 2;
      }
    });

  const pinch = Gesture.Pinch()
    .onUpdate((event) => {
      scale.value = Math.min(Math.max(savedScale.value * event.scale, 1), maxScale);
    })
    .onEnd(() => {
      savedScale.value = scale.value;
    });

  const composed = Gesture.Simultaneous(doubleTap, pinch);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
  }));

  return (
    <GestureDetector gesture={composed}>
      <Animated.View style={animatedStyle}>{children}</Animated.View>
    </GestureDetector>
  );
};

export const TripleTapAction: React.FC<{
  children: React.ReactNode;
  onTripleTap: () => void;
}> = ({ children, onTripleTap }) => {
  const scale = useSharedValue(1);

  const tripleTap = Gesture.Tap()
    .numberOfTaps(3)
    .onEnd(() => {
      scale.value = withSpring(0.9, {}, () => {
        scale.value = withSpring(1);
      });
      runOnJS(onTripleTap)();
    });

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
  }));

  return (
    <GestureDetector gesture={tripleTap}>
      <Animated.View style={animatedStyle}>{children}</Animated.View>
    </GestureDetector>
  );
};

const styles = StyleSheet.create({
  container: {
    position: 'relative',
  },
  heart: {
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: [{ translateX: -25 }, { translateY: -25 }],
    pointerEvents: 'none',
  },
  heartIcon: {
    fontSize: 50,
  },
});
