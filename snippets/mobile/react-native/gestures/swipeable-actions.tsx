import React from 'react';
import { View, Text, StyleSheet, Animated } from 'react-native';
import { Swipeable, GestureHandlerRootView } from 'react-native-gesture-handler';

interface SwipeableItemProps {
  item: { id: string; title: string };
  onDelete: () => void;
  onArchive: () => void;
}

export const SwipeableItem: React.FC<SwipeableItemProps> = ({ item, onDelete, onArchive }) => {
  const renderRightActions = (
    progress: Animated.AnimatedInterpolation<number>,
    dragX: Animated.AnimatedInterpolation<number>
  ) => {
    const trans = dragX.interpolate({
      inputRange: [-160, 0],
      outputRange: [0, 160],
      extrapolate: 'clamp',
    });

    return (
      <View style={styles.rightActions}>
        <Animated.View style={[styles.actionButton, styles.archiveButton, { transform: [{ translateX: trans }] }]}>
          <Text style={styles.actionText}>Archive</Text>
        </Animated.View>
        <Animated.View style={[styles.actionButton, styles.deleteButton, { transform: [{ translateX: trans }] }]}>
          <Text style={styles.actionText}>Delete</Text>
        </Animated.View>
      </View>
    );
  };

  const renderLeftActions = (
    progress: Animated.AnimatedInterpolation<number>,
    dragX: Animated.AnimatedInterpolation<number>
  ) => {
    const trans = dragX.interpolate({
      inputRange: [0, 80],
      outputRange: [-80, 0],
      extrapolate: 'clamp',
    });

    return (
      <Animated.View style={[styles.leftAction, { transform: [{ translateX: trans }] }]}>
        <Text style={styles.actionText}>Mark as Read</Text>
      </Animated.View>
    );
  };

  return (
    <Swipeable
      renderRightActions={renderRightActions}
      renderLeftActions={renderLeftActions}
      onSwipeableOpen={(direction) => {
        if (direction === 'right') {
          onDelete();
        } else if (direction === 'left') {
          onArchive();
        }
      }}
    >
      <View style={styles.itemContainer}>
        <Text style={styles.itemTitle}>{item.title}</Text>
      </View>
    </Swipeable>
  );
};

export const SwipeableList: React.FC<{ items: any[] }> = ({ items }) => {
  const [data, setData] = React.useState(items);

  const handleDelete = (id: string) => {
    setData(data.filter(item => item.id !== id));
  };

  const handleArchive = (id: string) => {
    console.log('Archive item:', id);
  };

  return (
    <GestureHandlerRootView style={styles.container}>
      {data.map(item => (
        <SwipeableItem
          key={item.id}
          item={item}
          onDelete={() => handleDelete(item.id)}
          onArchive={() => handleArchive(item.id)}
        />
      ))}
    </GestureHandlerRootView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  itemContainer: {
    padding: 20,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  itemTitle: {
    fontSize: 16,
    fontWeight: '500',
  },
  rightActions: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  actionButton: {
    width: 80,
    height: '100%',
    justifyContent: 'center',
    alignItems: 'center',
  },
  deleteButton: {
    backgroundColor: '#ff3b30',
  },
  archiveButton: {
    backgroundColor: '#ff9500',
  },
  leftAction: {
    backgroundColor: '#34c759',
    justifyContent: 'center',
    alignItems: 'flex-end',
    paddingRight: 20,
    width: 80,
  },
  actionText: {
    color: '#fff',
    fontWeight: '600',
    fontSize: 14,
  },
});
