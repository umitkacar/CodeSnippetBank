import * as SQLite from 'expo-sqlite';

interface User {
  id?: number;
  name: string;
  email: string;
  createdAt?: number;
}

export class DatabaseService {
  private db: SQLite.WebSQLDatabase;

  constructor(databaseName: string = 'app.db') {
    this.db = SQLite.openDatabase(databaseName);
    this.initialize();
  }

  private initialize(): void {
    this.db.transaction((tx) => {
      tx.executeSql(
        `CREATE TABLE IF NOT EXISTS users (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT NOT NULL,
          email TEXT UNIQUE NOT NULL,
          createdAt INTEGER DEFAULT (strftime('%s', 'now'))
        );`
      );

      tx.executeSql(
        `CREATE TABLE IF NOT EXISTS posts (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          title TEXT NOT NULL,
          content TEXT,
          userId INTEGER,
          createdAt INTEGER DEFAULT (strftime('%s', 'now')),
          FOREIGN KEY (userId) REFERENCES users (id)
        );`
      );
    });
  }

  // Create
  async createUser(user: User): Promise<number> {
    return new Promise((resolve, reject) => {
      this.db.transaction((tx) => {
        tx.executeSql(
          'INSERT INTO users (name, email) VALUES (?, ?);',
          [user.name, user.email],
          (_, result) => resolve(result.insertId!),
          (_, error) => {
            reject(error);
            return false;
          }
        );
      });
    });
  }

  // Read
  async getUsers(): Promise<User[]> {
    return new Promise((resolve, reject) => {
      this.db.transaction((tx) => {
        tx.executeSql(
          'SELECT * FROM users ORDER BY createdAt DESC;',
          [],
          (_, { rows }) => resolve(rows._array),
          (_, error) => {
            reject(error);
            return false;
          }
        );
      });
    });
  }

  async getUserById(id: number): Promise<User | null> {
    return new Promise((resolve, reject) => {
      this.db.transaction((tx) => {
        tx.executeSql(
          'SELECT * FROM users WHERE id = ?;',
          [id],
          (_, { rows }) => resolve(rows._array[0] || null),
          (_, error) => {
            reject(error);
            return false;
          }
        );
      });
    });
  }

  // Update
  async updateUser(id: number, user: Partial<User>): Promise<void> {
    return new Promise((resolve, reject) => {
      const fields = Object.keys(user)
        .map((key) => `${key} = ?`)
        .join(', ');
      const values = [...Object.values(user), id];

      this.db.transaction((tx) => {
        tx.executeSql(
          `UPDATE users SET ${fields} WHERE id = ?;`,
          values,
          () => resolve(),
          (_, error) => {
            reject(error);
            return false;
          }
        );
      });
    });
  }

  // Delete
  async deleteUser(id: number): Promise<void> {
    return new Promise((resolve, reject) => {
      this.db.transaction((tx) => {
        tx.executeSql(
          'DELETE FROM users WHERE id = ?;',
          [id],
          () => resolve(),
          (_, error) => {
            reject(error);
            return false;
          }
        );
      });
    });
  }

  // Search
  async searchUsers(query: string): Promise<User[]> {
    return new Promise((resolve, reject) => {
      this.db.transaction((tx) => {
        tx.executeSql(
          'SELECT * FROM users WHERE name LIKE ? OR email LIKE ?;',
          [`%${query}%`, `%${query}%`],
          (_, { rows }) => resolve(rows._array),
          (_, error) => {
            reject(error);
            return false;
          }
        );
      });
    });
  }

  // Drop table
  async dropTable(tableName: string): Promise<void> {
    return new Promise((resolve, reject) => {
      this.db.transaction((tx) => {
        tx.executeSql(
          `DROP TABLE IF EXISTS ${tableName};`,
          [],
          () => resolve(),
          (_, error) => {
            reject(error);
            return false;
          }
        );
      });
    });
  }
}

export const database = new DatabaseService();
