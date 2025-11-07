// ============================================================================
// TypeORM Entities, Relations, and Queries
// ============================================================================

import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
  UpdateDateColumn,
  ManyToOne,
  OneToMany,
  OneToOne,
  ManyToMany,
  JoinColumn,
  JoinTable,
  Index,
  Repository,
  DataSource
} from 'typeorm';

// Snippet 1: Basic entity with decorators
@Entity('users')
@Index(['email'])
export class User {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column({ unique: true })
  email: string;

  @Column()
  name: string;

  @Column({ type: 'enum', enum: ['user', 'admin', 'moderator'], default: 'user' })
  role: string;

  @Column({ type: 'boolean', default: true })
  isActive: boolean;

  @OneToOne(() => Profile, profile => profile.user, { cascade: true })
  profile: Profile;

  @OneToMany(() => Post, post => post.author)
  posts: Post[];

  @OneToMany(() => Order, order => order.user)
  orders: Order[];

  @CreateDateColumn()
  createdAt: Date;

  @UpdateDateColumn()
  updatedAt: Date;
}

// Snippet 2: One-to-One relation
@Entity('profiles')
export class Profile {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column({ type: 'text', nullable: true })
  bio: string;

  @Column({ nullable: true })
  avatar: string;

  @Column({ nullable: true })
  phone: string;

  @OneToOne(() => User, user => user.profile)
  @JoinColumn()
  user: User;

  @CreateDateColumn()
  createdAt: Date;

  @UpdateDateColumn()
  updatedAt: Date;
}

// Snippet 3: Many-to-One relation
@Entity('posts')
@Index(['title'])
@Index(['published'])
export class Post {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column()
  title: string;

  @Column({ type: 'text', nullable: true })
  content: string;

  @Column({ default: false })
  published: boolean;

  @Column({ type: 'int', default: 0 })
  viewCount: number;

  @ManyToOne(() => User, user => user.posts, { onDelete: 'CASCADE' })
  author: User;

  @ManyToMany(() => Category, category => category.posts)
  @JoinTable({
    name: 'post_categories',
    joinColumn: { name: 'post_id' },
    inverseJoinColumn: { name: 'category_id' }
  })
  categories: Category[];

  @ManyToMany(() => Tag, tag => tag.posts)
  @JoinTable({
    name: 'post_tags',
    joinColumn: { name: 'post_id' },
    inverseJoinColumn: { name: 'tag_id' }
  })
  tags: Tag[];

  @CreateDateColumn()
  createdAt: Date;

  @UpdateDateColumn()
  updatedAt: Date;
}

// Snippet 4: Many-to-Many relation
@Entity('categories')
export class Category {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column({ unique: true })
  name: string;

  @Column({ nullable: true })
  description: string;

  @ManyToMany(() => Post, post => post.categories)
  posts: Post[];
}

@Entity('tags')
export class Tag {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column({ unique: true })
  name: string;

  @ManyToMany(() => Post, post => post.tags)
  posts: Post[];
}

// Snippet 5: Complex entity with multiple relations
@Entity('orders')
@Index(['orderNumber'], { unique: true })
@Index(['status'])
export class Order {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column({ unique: true })
  orderNumber: string;

  @Column({ type: 'enum', enum: ['pending', 'processing', 'shipped', 'delivered', 'cancelled'], default: 'pending' })
  status: string;

  @Column({ type: 'decimal', precision: 10, scale: 2 })
  totalAmount: number;

  @ManyToOne(() => User, user => user.orders)
  user: User;

  @OneToMany(() => OrderItem, item => item.order, { cascade: true })
  items: OrderItem[];

  @CreateDateColumn()
  createdAt: Date;

  @UpdateDateColumn()
  updatedAt: Date;
}

@Entity('order_items')
export class OrderItem {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column({ type: 'int' })
  quantity: number;

  @Column({ type: 'decimal', precision: 10, scale: 2 })
  price: number;

  @ManyToOne(() => Order, order => order.items, { onDelete: 'CASCADE' })
  order: Order;

  @ManyToOne(() => Product, product => product.orderItems)
  product: Product;
}

@Entity('products')
@Index(['name'])
export class Product {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column()
  name: string;

  @Column({ type: 'text', nullable: true })
  description: string;

  @Column({ type: 'decimal', precision: 10, scale: 2 })
  price: number;

  @Column({ type: 'int', default: 0 })
  stock: number;

  @Column({ default: true })
  isActive: boolean;

  @OneToMany(() => OrderItem, item => item.product)
  orderItems: OrderItem[];

  @CreateDateColumn()
  createdAt: Date;

  @UpdateDateColumn()
  updatedAt: Date;
}

// ============================================================================
// TypeORM Query Examples
// ============================================================================

// Initialize DataSource
const AppDataSource = new DataSource({
  type: 'postgres',
  host: 'localhost',
  port: 5432,
  username: 'user',
  password: 'password',
  database: 'myapp',
  entities: [User, Profile, Post, Category, Tag, Order, OrderItem, Product],
  synchronize: false
});

// Snippet 6: Find with relations
async function getUserWithRelations(userId: string) {
  const userRepository = AppDataSource.getRepository(User);

  const user = await userRepository.findOne({
    where: { id: userId },
    relations: ['profile', 'posts', 'orders']
  });

  return user;
}

// Snippet 7: Find with complex conditions
async function findActiveUsers() {
  const userRepository = AppDataSource.getRepository(User);

  const users = await userRepository.find({
    where: {
      isActive: true,
      role: 'user'
    },
    relations: ['profile'],
    order: { createdAt: 'DESC' },
    take: 50
  });

  return users;
}

// Snippet 8: Query builder for complex queries
async function getTopAuthors() {
  const userRepository = AppDataSource.getRepository(User);

  const topAuthors = await userRepository
    .createQueryBuilder('user')
    .leftJoinAndSelect('user.posts', 'post')
    .leftJoinAndSelect('user.profile', 'profile')
    .where('post.published = :published', { published: true })
    .groupBy('user.id')
    .addGroupBy('profile.id')
    .having('COUNT(post.id) >= :minPosts', { minPosts: 5 })
    .orderBy('COUNT(post.id)', 'DESC')
    .take(10)
    .getMany();

  return topAuthors;
}

// Snippet 9: Advanced query with joins
async function getOrdersWithDetails(userId: string) {
  const orderRepository = AppDataSource.getRepository(Order);

  const orders = await orderRepository
    .createQueryBuilder('order')
    .leftJoinAndSelect('order.items', 'item')
    .leftJoinAndSelect('item.product', 'product')
    .leftJoinAndSelect('order.user', 'user')
    .where('user.id = :userId', { userId })
    .andWhere('order.status != :status', { status: 'cancelled' })
    .orderBy('order.createdAt', 'DESC')
    .getMany();

  return orders;
}

// Snippet 10: Transaction example
async function createOrderTransaction(userId: string, items: any[]) {
  return await AppDataSource.transaction(async (manager) => {
    const order = manager.create(Order, {
      orderNumber: `ORD-${Date.now()}`,
      user: { id: userId },
      status: 'pending',
      totalAmount: 0
    });

    await manager.save(order);

    let totalAmount = 0;
    for (const item of items) {
      const product = await manager.findOneOrFail(Product, {
        where: { id: item.productId }
      });

      if (product.stock < item.quantity) {
        throw new Error(`Insufficient stock for ${product.name}`);
      }

      const orderItem = manager.create(OrderItem, {
        order,
        product,
        quantity: item.quantity,
        price: product.price
      });

      await manager.save(orderItem);

      product.stock -= item.quantity;
      await manager.save(product);

      totalAmount += Number(product.price) * item.quantity;
    }

    order.totalAmount = totalAmount;
    await manager.save(order);

    return order;
  });
}

// Snippet 11: Raw SQL query
async function getCustomerStatistics() {
  const results = await AppDataSource.query(`
    SELECT
      u.id,
      u.name,
      COUNT(DISTINCT o.id) as order_count,
      COALESCE(SUM(o.total_amount), 0) as lifetime_value
    FROM users u
    LEFT JOIN orders o ON u.id = o.user_id
    GROUP BY u.id, u.name
    HAVING COUNT(DISTINCT o.id) > 0
    ORDER BY lifetime_value DESC
    LIMIT 100
  `);

  return results;
}

// Snippet 12: Soft delete (requires @DeleteDateColumn)
async function softDeleteUser(userId: string) {
  const userRepository = AppDataSource.getRepository(User);
  await userRepository.softDelete(userId);
}

// Snippet 13: Update with query builder
async function updatePostViewCount(postId: string) {
  const postRepository = AppDataSource.getRepository(Post);

  await postRepository
    .createQueryBuilder()
    .update(Post)
    .set({ viewCount: () => 'view_count + 1' })
    .where('id = :id', { id: postId })
    .execute();
}

// Snippet 14: Pagination
async function getPaginatedPosts(page: number = 1, limit: number = 20) {
  const postRepository = AppDataSource.getRepository(Post);

  const [posts, total] = await postRepository.findAndCount({
    where: { published: true },
    relations: ['author', 'categories', 'tags'],
    order: { createdAt: 'DESC' },
    skip: (page - 1) * limit,
    take: limit
  });

  return {
    posts,
    total,
    page,
    totalPages: Math.ceil(total / limit)
  };
}

// Snippet 15: Subquery example
async function getUsersWithRecentOrders() {
  const userRepository = AppDataSource.getRepository(User);

  const users = await userRepository
    .createQueryBuilder('user')
    .where((qb) => {
      const subQuery = qb
        .subQuery()
        .select('order.user_id')
        .from(Order, 'order')
        .where('order.created_at >= :date', {
          date: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)
        })
        .getQuery();

      return `user.id IN ${subQuery}`;
    })
    .getMany();

  return users;
}
