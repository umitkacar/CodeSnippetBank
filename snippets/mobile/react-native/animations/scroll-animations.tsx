import React from 'react';
import { StyleSheet, Dimensions } from 'react-native';
import Animated, {
  useAnimatedScrollHandler,
  useSharedValue,
  useAnimatedStyle,
  interpolate,
  Extrapolate,
} from 'react-native-reanimated';

const { width, height } = Dimensions.get('window');

interface ParallaxScrollProps {
  children: React.ReactNode;
  headerHeight?: number;
}

export const ParallaxScroll: React.FC<ParallaxScrollProps> = ({
  children,
  headerHeight = 300,
}) => {
  const scrollY = useSharedValue(0);

  const scrollHandler = useAnimatedScrollHandler({
    onScroll: (event) => {
      scrollY.value = event.contentOffset.y;
    },
  });

  const headerStyle = useAnimatedStyle(() => {
    const translateY = interpolate(
      scrollY.value,
      [0, headerHeight],
      [0, -headerHeight / 2],
      Extrapolate.CLAMP
    );

    const scale = interpolate(
      scrollY.value,
      [-headerHeight, 0, headerHeight],
      [2, 1, 1],
      Extrapolate.CLAMP
    );

    return {
      transform: [{ translateY }, { scale }],
    };
  });

  return (
    <Animated.ScrollView
      onScroll={scrollHandler}
      scrollEventThrottle={16}
      style={styles.container}
    >
      <Animated.View style={[styles.header, headerStyle, { height: headerHeight }]}>
        {/* Header content */}
      </Animated.View>
      {children}
    </Animated.ScrollView>
  );
};

export const FadeInScrollView: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const scrollY = useSharedValue(0);

  const scrollHandler = useAnimatedScrollHandler({
    onScroll: (event) => {
      scrollY.value = event.contentOffset.y;
    },
  });

  return (
    <Animated.ScrollView
      onScroll={scrollHandler}
      scrollEventThrottle={16}
      style={styles.container}
    >
      {children}
    </Animated.ScrollView>
  );
};

interface ScrollItemProps {
  index: number;
  scrollY: Animated.SharedValue<number>;
  children: React.ReactNode;
}

export const ScrollAnimatedItem: React.FC<ScrollItemProps> = ({
  index,
  scrollY,
  children,
}) => {
  const animatedStyle = useAnimatedStyle(() => {
    const inputRange = [(index - 1) * 100, index * 100, (index + 1) * 100];

    const opacity = interpolate(
      scrollY.value,
      inputRange,
      [0.3, 1, 0.3],
      Extrapolate.CLAMP
    );

    const scale = interpolate(
      scrollY.value,
      inputRange,
      [0.8, 1, 0.8],
      Extrapolate.CLAMP
    );

    return {
      opacity,
      transform: [{ scale }],
    };
  });

  return <Animated.View style={[styles.item, animatedStyle]}>{children}</Animated.View>;
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    width: '100%',
    backgroundColor: '#6200ee',
    justifyContent: 'center',
    alignItems: 'center',
  },
  item: {
    padding: 16,
    marginVertical: 8,
  },
});
