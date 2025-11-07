import React from 'react';
import { StyleSheet, View, Text } from 'react-native';
import Animated, {
  useAnimatedStyle,
  useSharedValue,
  withSpring,
  withDelay,
  Layout,
  FadeIn,
  FadeOut,
} from 'react-native-reanimated';

interface AnimatedListItemProps {
  item: any;
  index: number;
}

export const AnimatedListItem: React.FC<AnimatedListItemProps> = ({ item, index }) => {
  return (
    <Animated.View
      entering={FadeIn.delay(index * 100).springify()}
      exiting={FadeOut}
      layout={Layout.springify()}
      style={styles.listItem}
    >
      <Text style={styles.itemText}>{item.title}</Text>
    </Animated.View>
  );
};

interface StaggeredListProps {
  items: any[];
}

export const StaggeredList: React.FC<StaggeredListProps> = ({ items }) => {
  return (
    <View style={styles.container}>
      {items.map((item, index) => (
        <AnimatedListItem key={item.id} item={item} index={index} />
      ))}
    </View>
  );
};

export const AnimatedCard: React.FC<{ children: React.ReactNode; delay?: number }> = ({
  children,
  delay = 0,
}) => {
  const translateY = useSharedValue(50);
  const opacity = useSharedValue(0);

  React.useEffect(() => {
    translateY.value = withDelay(delay, withSpring(0));
    opacity.value = withDelay(delay, withSpring(1));
  }, []);

  const animatedStyle = useAnimatedStyle(() => {
    return {
      transform: [{ translateY: translateY.value }],
      opacity: opacity.value,
    };
  });

  return <Animated.View style={[styles.card, animatedStyle]}>{children}</Animated.View>;
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
  },
  listItem: {
    padding: 16,
    marginVertical: 8,
    backgroundColor: '#fff',
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  itemText: {
    fontSize: 16,
    fontWeight: '500',
  },
  card: {
    padding: 16,
    backgroundColor: '#fff',
    borderRadius: 12,
    marginBottom: 16,
  },
});
