import React, { useEffect } from 'react';
import { StyleSheet, Pressable } from 'react-native';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withSpring,
  withTiming,
  withSequence,
} from 'react-native-reanimated';

export const BouncyButton: React.FC<{ children: React.ReactNode; onPress: () => void }> = ({
  children,
  onPress,
}) => {
  const scale = useSharedValue(1);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
  }));

  const handlePressIn = () => {
    scale.value = withSpring(0.9, {
      damping: 10,
      stiffness: 100,
    });
  };

  const handlePressOut = () => {
    scale.value = withSpring(1, {
      damping: 10,
      stiffness: 100,
    });
  };

  return (
    <Pressable onPressIn={handlePressIn} onPressOut={handlePressOut} onPress={onPress}>
      <Animated.View style={[styles.button, animatedStyle]}>{children}</Animated.View>
    </Pressable>
  );
};

export const WobbleAnimation: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const rotation = useSharedValue(0);

  useEffect(() => {
    rotation.value = withSequence(
      withSpring(10, { damping: 2 }),
      withSpring(-10, { damping: 2 }),
      withSpring(10, { damping: 2 }),
      withSpring(0, { damping: 5 })
    );
  }, []);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ rotateZ: `${rotation.value}deg` }],
  }));

  return <Animated.View style={animatedStyle}>{children}</Animated.View>;
};

export const ElasticButton: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const scale = useSharedValue(1);

  const handlePress = () => {
    scale.value = withSequence(
      withSpring(1.2, { damping: 3, stiffness: 200 }),
      withSpring(1, { damping: 5, stiffness: 100 })
    );
  };

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
  }));

  return (
    <Pressable onPress={handlePress}>
      <Animated.View style={animatedStyle}>{children}</Animated.View>
    </Pressable>
  );
};

export const PulseAnimation: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const scale = useSharedValue(1);

  useEffect(() => {
    const animate = () => {
      scale.value = withSequence(
        withSpring(1.1, { damping: 2, stiffness: 100 }),
        withSpring(1, { damping: 2, stiffness: 100 })
      );
    };

    const interval = setInterval(animate, 2000);
    return () => clearInterval(interval);
  }, []);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
  }));

  return <Animated.View style={animatedStyle}>{children}</Animated.View>;
};

const styles = StyleSheet.create({
  button: {
    padding: 16,
    backgroundColor: '#6200ee',
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
});
