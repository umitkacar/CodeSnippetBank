import React, { useState } from 'react';
import { View, Text, Pressable, StyleSheet, LayoutAnimation, Platform, UIManager } from 'react-native';
import Animated, { Layout, FadeIn, FadeOut, SlideInLeft, SlideOutRight } from 'react-native-reanimated';

if (Platform.OS === 'android' && UIManager.setLayoutAnimationEnabledExperimental) {
  UIManager.setLayoutAnimationEnabledExperimental(true);
}

export const ExpandableCard: React.FC<{ title: string; content: string }> = ({ title, content }) => {
  const [expanded, setExpanded] = useState(false);

  const toggleExpanded = () => {
    LayoutAnimation.configureNext(LayoutAnimation.Presets.easeInEaseOut);
    setExpanded(!expanded);
  };

  return (
    <Pressable onPress={toggleExpanded} style={styles.card}>
      <Text style={styles.title}>{title}</Text>
      {expanded && <Text style={styles.content}>{content}</Text>}
    </Pressable>
  );
};

export const AnimatedList: React.FC<{ items: any[] }> = ({ items }) => {
  const [list, setList] = useState(items);

  const removeItem = (id: string) => {
    LayoutAnimation.configureNext(LayoutAnimation.Presets.spring);
    setList(list.filter(item => item.id !== id));
  };

  return (
    <View>
      {list.map(item => (
        <Animated.View
          key={item.id}
          entering={SlideInLeft}
          exiting={SlideOutRight}
          layout={Layout.springify()}
        >
          <Pressable onPress={() => removeItem(item.id)} style={styles.listItem}>
            <Text>{item.title}</Text>
          </Pressable>
        </Animated.View>
      ))}
    </View>
  );
};

export const ReorderableList: React.FC = () => {
  const [items, setItems] = useState(['Item 1', 'Item 2', 'Item 3', 'Item 4']);

  const moveItem = (fromIndex: number, toIndex: number) => {
    LayoutAnimation.configureNext(LayoutAnimation.Presets.easeInEaseOut);
    const newItems = [...items];
    const [removed] = newItems.splice(fromIndex, 1);
    newItems.splice(toIndex, 0, removed);
    setItems(newItems);
  };

  return (
    <View>
      {items.map((item, index) => (
        <Animated.View key={item} layout={Layout.springify()}>
          <Pressable
            style={styles.reorderItem}
            onPress={() => moveItem(index, (index + 1) % items.length)}
          >
            <Text>{item}</Text>
          </Pressable>
        </Animated.View>
      ))}
    </View>
  );
};

const customSpring = {
  damping: 15,
  mass: 1,
  stiffness: 150,
  overshootClamping: false,
  restDisplacementThreshold: 0.01,
  restSpeedThreshold: 0.01,
};

export const CustomLayoutAnimation = LayoutAnimation.create(
  300,
  LayoutAnimation.Types.spring,
  LayoutAnimation.Properties.scaleXY
);

const styles = StyleSheet.create({
  card: {
    padding: 16,
    margin: 8,
    backgroundColor: '#fff',
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  content: {
    marginTop: 8,
    fontSize: 14,
    color: '#666',
  },
  listItem: {
    padding: 16,
    margin: 8,
    backgroundColor: '#f5f5f5',
    borderRadius: 8,
  },
  reorderItem: {
    padding: 16,
    margin: 8,
    backgroundColor: '#e0e0e0',
    borderRadius: 8,
  },
});
