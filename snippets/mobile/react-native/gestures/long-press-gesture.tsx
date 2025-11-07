import React, { useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { GestureDetector, Gesture } from 'react-native-gesture-handler';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withSpring,
  runOnJS,
} from 'react-native-reanimated';

export const LongPressButton: React.FC<{ onLongPress: () => void }> = ({ onLongPress }) => {
  const scale = useSharedValue(1);

  const longPress = Gesture.LongPress()
    .minDuration(500)
    .onStart(() => {
      scale.value = withSpring(0.9);
    })
    .onEnd(() => {
      scale.value = withSpring(1);
      runOnJS(onLongPress)();
    });

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
  }));

  return (
    <GestureDetector gesture={longPress}>
      <Animated.View style={[styles.button, animatedStyle]}>
        <Text style={styles.buttonText}>Long Press Me</Text>
      </Animated.View>
    </GestureDetector>
  );
};

export const ContextMenuTrigger: React.FC<{
  children: React.ReactNode;
  onContextMenu: () => void;
}> = ({ children, onContextMenu }) => {
  const [menuVisible, setMenuVisible] = useState(false);
  const scale = useSharedValue(1);

  const longPress = Gesture.LongPress()
    .minDuration(400)
    .onStart(() => {
      scale.value = withSpring(0.95);
      runOnJS(setMenuVisible)(true);
      runOnJS(onContextMenu)();
    })
    .onEnd(() => {
      scale.value = withSpring(1);
    });

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
  }));

  return (
    <GestureDetector gesture={longPress}>
      <Animated.View style={animatedStyle}>
        {children}
        {menuVisible && (
          <View style={styles.contextMenu}>
            <Text>Context Menu</Text>
          </View>
        )}
      </Animated.View>
    </GestureDetector>
  );
};

const styles = StyleSheet.create({
  button: {
    backgroundColor: '#6200ee',
    paddingHorizontal: 32,
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  contextMenu: {
    position: 'absolute',
    top: 50,
    right: 0,
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
});
