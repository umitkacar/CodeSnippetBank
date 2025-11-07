import React, { memo, useMemo, useCallback, useState } from 'react';
import { View, Text, FlatList, TouchableOpacity, StyleSheet } from 'react-native';

// Memoized component
interface ListItemProps {
  item: { id: string; title: string; description: string };
  onPress: (id: string) => void;
}

export const ListItem = memo<ListItemProps>(({ item, onPress }) => {
  console.log('Rendering ListItem:', item.id);

  return (
    <TouchableOpacity
      style={styles.item}
      onPress={() => onPress(item.id)}
    >
      <Text style={styles.title}>{item.title}</Text>
      <Text style={styles.description}>{item.description}</Text>
    </TouchableOpacity>
  );
}, (prevProps, nextProps) => {
  // Custom comparison
  return (
    prevProps.item.id === nextProps.item.id &&
    prevProps.item.title === nextProps.item.title
  );
});

// Optimized list component
export const OptimizedList: React.FC<{ data: any[] }> = ({ data }) => {
  const [selectedId, setSelectedId] = useState<string | null>(null);

  // Memoize callback
  const handlePress = useCallback((id: string) => {
    setSelectedId(id);
  }, []);

  // Memoize filtered data
  const filteredData = useMemo(() => {
    return data.filter(item => item.active);
  }, [data]);

  // Memoize renderItem
  const renderItem = useCallback(({ item }: { item: any }) => {
    return <ListItem item={item} onPress={handlePress} />;
  }, [handlePress]);

  // Key extractor
  const keyExtractor = useCallback((item: any) => item.id, []);

  return (
    <FlatList
      data={filteredData}
      renderItem={renderItem}
      keyExtractor={keyExtractor}
      removeClippedSubviews={true}
      maxToRenderPerBatch={10}
      updateCellsBatchingPeriod={50}
      initialNumToRender={10}
      windowSize={21}
      getItemLayout={(data, index) => ({
        length: 100,
        offset: 100 * index,
        index,
      })}
    />
  );
};

// Expensive calculation with memoization
export const useExpensiveCalculation = (data: number[]) => {
  return useMemo(() => {
    console.log('Running expensive calculation...');
    return data.reduce((acc, val) => acc + val * 2, 0);
  }, [data]);
};

// Memoized selector
export const useMemoizedSelector = <T, R>(
  data: T,
  selector: (data: T) => R
): R => {
  return useMemo(() => selector(data), [data, selector]);
};

const styles = StyleSheet.create({
  item: {
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  title: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  description: {
    fontSize: 14,
    color: '#666',
    marginTop: 4,
  },
});
