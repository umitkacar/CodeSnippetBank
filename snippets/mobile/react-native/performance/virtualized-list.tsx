import React from 'react';
import { VirtualizedList, View, Text, StyleSheet } from 'react-native';

interface Item {
  id: string;
  title: string;
}

interface VirtualizedListProps {
  data: Item[];
}

export const OptimizedVirtualizedList: React.FC<VirtualizedListProps> = ({ data }) => {
  const getItem = (data: Item[], index: number) => data[index];

  const getItemCount = (data: Item[]) => data.length;

  const renderItem = ({ item }: { item: Item }) => (
    <View style={styles.item}>
      <Text style={styles.title}>{item.title}</Text>
    </View>
  );

  return (
    <VirtualizedList
      data={data}
      initialNumToRender={10}
      renderItem={renderItem}
      keyExtractor={(item: Item) => item.id}
      getItemCount={getItemCount}
      getItem={getItem}
      maxToRenderPerBatch={10}
      updateCellsBatchingPeriod={50}
      windowSize={21}
    />
  );
};

// FlashList - more performant alternative
import { FlashList } from '@shopify/flash-list';

export const HighPerformanceList: React.FC<{ data: Item[] }> = ({ data }) => {
  return (
    <FlashList
      data={data}
      renderItem={({ item }) => (
        <View style={styles.flashItem}>
          <Text>{item.title}</Text>
        </View>
      )}
      estimatedItemSize={100}
      keyExtractor={(item) => item.id}
    />
  );
};

// Recycler list view for complex items
export const RecyclerListView: React.FC<{ data: any[] }> = ({ data }) => {
  const layoutProvider = new LayoutProvider(
    (index) => 0,
    (type, dim) => {
      dim.width = Dimensions.get('window').width;
      dim.height = 100;
    }
  );

  const rowRenderer = (type: string | number, data: any) => {
    return (
      <View style={styles.recyclerItem}>
        <Text>{data.title}</Text>
      </View>
    );
  };

  return (
    <RecyclerListView
      layoutProvider={layoutProvider}
      dataProvider={new DataProvider((r1, r2) => r1 !== r2).cloneWithRows(data)}
      rowRenderer={rowRenderer}
    />
  );
};

const styles = StyleSheet.create({
  item: {
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
    height: 100,
  },
  flashItem: {
    padding: 16,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  recyclerItem: {
    padding: 16,
    justifyContent: 'center',
  },
  title: {
    fontSize: 16,
    fontWeight: '500',
  },
});
