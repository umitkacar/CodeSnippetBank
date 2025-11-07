import React, { memo, useMemo, useCallback, useTransition, useDeferredValue } from 'react';
import { View, Text, FlatList, StyleSheet, TextInput } from 'react-native';

// React 18+ Concurrent features
export const SearchWithDeferred: React.FC = () => {
  const [query, setQuery] = React.useState('');
  const deferredQuery = useDeferredValue(query);

  const filteredResults = useMemo(() => {
    return items.filter(item =>
      item.title.toLowerCase().includes(deferredQuery.toLowerCase())
    );
  }, [deferredQuery]);

  return (
    <View style={styles.container}>
      <TextInput
        value={query}
        onChangeText={setQuery}
        placeholder="Search..."
        style={styles.input}
      />
      <FlatList
        data={filteredResults}
        renderItem={({ item }) => <ListItem item={item} />}
        keyExtractor={item => item.id}
      />
    </View>
  );
};

// useTransition for non-urgent updates
export const TransitionExample: React.FC = () => {
  const [isPending, startTransition] = useTransition();
  const [tab, setTab] = React.useState('home');

  const selectTab = (nextTab: string) => {
    startTransition(() => {
      setTab(nextTab);
    });
  };

  return (
    <View style={styles.container}>
      <View style={styles.tabs}>
        <Button title="Home" onPress={() => selectTab('home')} />
        <Button title="Profile" onPress={() => selectTab('profile')} />
        <Button title="Settings" onPress={() => selectTab('settings')} />
      </View>
      {isPending ? (
        <ActivityIndicator />
      ) : (
        <TabContent tab={tab} />
      )}
    </View>
  );
};

// Memoization best practices
interface ExpensiveComponentProps {
  data: any[];
  onItemPress: (id: string) => void;
}

export const ExpensiveComponent = memo<ExpensiveComponentProps>(
  ({ data, onItemPress }) => {
    const processedData = useMemo(() => {
      return data.map(item => ({
        ...item,
        formatted: `${item.title} - ${item.description}`,
      }));
    }, [data]);

    const handlePress = useCallback(
      (id: string) => {
        onItemPress(id);
      },
      [onItemPress]
    );

    return (
      <FlatList
        data={processedData}
        renderItem={({ item }) => (
          <ListItem item={item} onPress={() => handlePress(item.id)} />
        )}
        keyExtractor={item => item.id}
        removeClippedSubviews
        maxToRenderPerBatch={10}
        windowSize={5}
      />
    );
  }
);

// Avoiding unnecessary re-renders
export const OptimizedParent: React.FC = () => {
  const [count, setCount] = React.useState(0);
  const [text, setText] = React.useState('');

  // Memoized callback that doesn't change when text changes
  const increment = useCallback(() => {
    setCount(c => c + 1);
  }, []);

  return (
    <View>
      <TextInput value={text} onChangeText={setText} />
      <MemoizedChild count={count} onIncrement={increment} />
    </View>
  );
};

const MemoizedChild = memo<{ count: number; onIncrement: () => void }>(
  ({ count, onIncrement }) => {
    console.log('Child rendered');
    return (
      <View>
        <Text>Count: {count}</Text>
        <Button title="Increment" onPress={onIncrement} />
      </View>
    );
  }
);

// Selector pattern for complex state
const selectUserName = (state: AppState) => state.user.name;
const selectUserPosts = (state: AppState) => state.user.posts;

export const UserProfile: React.FC = () => {
  const userName = useSelector(selectUserName);
  const posts = useSelector(selectUserPosts);

  // Only re-renders when name or posts change
  return (
    <View>
      <Text>{userName}</Text>
      <PostList posts={posts} />
    </View>
  );
};

// Component splitting for performance
export const HeavyScreen: React.FC = () => {
  return (
    <View>
      <Header />
      <React.Suspense fallback={<LoadingSkeleton />}>
        <HeavyContent />
      </React.Suspense>
      <Footer />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    marginBottom: 16,
  },
  tabs: {
    flexDirection: 'row',
    gap: 8,
    marginBottom: 16,
  },
});
