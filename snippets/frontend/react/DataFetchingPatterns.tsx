import React, { useState, useEffect } from 'react';

/**
 * Various data fetching patterns in React
 */

// 1. Basic fetch with loading and error states
export const BasicFetch: React.FC<{ userId: string }> = ({ userId }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(`/api/users/${userId}`);
        if (!response.ok) throw new Error('Failed to fetch');
        const result = await response.json();
        setData(result);
      } catch (err) {
        setError(err as Error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [userId]);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;
  return <div>{JSON.stringify(data)}</div>;
};

// 2. Fetch with abort controller (cleanup)
export const FetchWithCleanup: React.FC<{ query: string }> = ({ query }) => {
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const controller = new AbortController();
    const signal = controller.signal;

    const searchData = async () => {
      if (!query) {
        setResults([]);
        return;
      }

      setLoading(true);
      try {
        const response = await fetch(`/api/search?q=${query}`, { signal });
        const data = await response.json();
        setResults(data);
      } catch (err: any) {
        if (err.name !== 'AbortError') {
          console.error('Search error:', err);
        }
      } finally {
        setLoading(false);
      }
    };

    searchData();

    return () => {
      controller.abort();
    };
  }, [query]);

  return (
    <div>
      {loading && <p>Searching...</p>}
      <ul>
        {results.map((result) => (
          <li key={result.id}>{result.name}</li>
        ))}
      </ul>
    </div>
  );
};

// 3. Parallel data fetching
export const ParallelFetch: React.FC = () => {
  const [user, setUser] = useState(null);
  const [posts, setPosts] = useState([]);
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAllData = async () => {
      try {
        const [userRes, postsRes, commentsRes] = await Promise.all([
          fetch('/api/user'),
          fetch('/api/posts'),
          fetch('/api/comments'),
        ]);

        const [userData, postsData, commentsData] = await Promise.all([
          userRes.json(),
          postsRes.json(),
          commentsRes.json(),
        ]);

        setUser(userData);
        setPosts(postsData);
        setComments(commentsData);
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchAllData();
  }, []);

  if (loading) return <div>Loading all data...</div>;

  return (
    <div>
      <div>User: {JSON.stringify(user)}</div>
      <div>Posts: {posts.length}</div>
      <div>Comments: {comments.length}</div>
    </div>
  );
};

// 4. Sequential data fetching (dependent requests)
export const SequentialFetch: React.FC<{ userId: string }> = ({ userId }) => {
  const [userData, setUserData] = useState(null);
  const [userPosts, setUserPosts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSequential = async () => {
      try {
        // First request
        const userResponse = await fetch(`/api/users/${userId}`);
        const user = await userResponse.json();
        setUserData(user);

        // Second request depends on first
        const postsResponse = await fetch(`/api/users/${user.id}/posts`);
        const posts = await postsResponse.json();
        setUserPosts(posts);
      } catch (error) {
        console.error('Error:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchSequential();
  }, [userId]);

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <h2>{userData ? (userData as any).name : 'Unknown'}</h2>
      <ul>
        {userPosts.map((post: any) => (
          <li key={post.id}>{post.title}</li>
        ))}
      </ul>
    </div>
  );
};

// 5. Polling pattern
export const PollingFetch: React.FC = () => {
  const [data, setData] = useState(null);
  const [isPolling, setIsPolling] = useState(true);

  useEffect(() => {
    if (!isPolling) return;

    const fetchData = async () => {
      try {
        const response = await fetch('/api/status');
        const result = await response.json();
        setData(result);
      } catch (error) {
        console.error('Polling error:', error);
      }
    };

    fetchData(); // Initial fetch
    const intervalId = setInterval(fetchData, 5000); // Poll every 5 seconds

    return () => clearInterval(intervalId);
  }, [isPolling]);

  return (
    <div>
      <button onClick={() => setIsPolling(!isPolling)}>
        {isPolling ? 'Stop Polling' : 'Start Polling'}
      </button>
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
};
