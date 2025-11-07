// ============================================================================
// Sequelize Models, Associations, and Queries
// ============================================================================

import {
  Sequelize,
  DataTypes,
  Model,
  Optional,
  Association,
  HasOneGetAssociationMixin,
  HasManyGetAssociationsMixin,
  BelongsToManyAddAssociationMixin
} from 'sequelize';

const sequelize = new Sequelize('database', 'username', 'password', {
  host: 'localhost',
  dialect: 'postgres',
  logging: false,
  pool: {
    max: 10,
    min: 0,
    acquire: 30000,
    idle: 10000
  }
});

// Snippet 1: User model with attributes
interface UserAttributes {
  id: string;
  email: string;
  name: string;
  role: 'user' | 'admin' | 'moderator';
  isActive: boolean;
  createdAt?: Date;
  updatedAt?: Date;
}

interface UserCreationAttributes extends Optional<UserAttributes, 'id' | 'createdAt' | 'updatedAt'> {}

class User extends Model<UserAttributes, UserCreationAttributes> implements UserAttributes {
  public id!: string;
  public email!: string;
  public name!: string;
  public role!: 'user' | 'admin' | 'moderator';
  public isActive!: boolean;

  public readonly createdAt!: Date;
  public readonly updatedAt!: Date;

  // Associations
  public getProfile!: HasOneGetAssociationMixin<Profile>;
  public getPosts!: HasManyGetAssociationsMixin<Post>;
  public getOrders!: HasManyGetAssociationsMixin<Order>;

  public readonly profile?: Profile;
  public readonly posts?: Post[];
  public readonly orders?: Order[];

  public static associations: {
    profile: Association<User, Profile>;
    posts: Association<User, Post>;
    orders: Association<User, Order>;
  };
}

User.init(
  {
    id: {
      type: DataTypes.UUID,
      defaultValue: DataTypes.UUIDV4,
      primaryKey: true
    },
    email: {
      type: DataTypes.STRING,
      allowNull: false,
      unique: true,
      validate: {
        isEmail: true
      }
    },
    name: {
      type: DataTypes.STRING,
      allowNull: false
    },
    role: {
      type: DataTypes.ENUM('user', 'admin', 'moderator'),
      defaultValue: 'user'
    },
    isActive: {
      type: DataTypes.BOOLEAN,
      defaultValue: true
    }
  },
  {
    sequelize,
    tableName: 'users',
    indexes: [
      { fields: ['email'] }
    ]
  }
);

// Snippet 2: Profile model with One-to-One relation
interface ProfileAttributes {
  id: string;
  bio?: string;
  avatar?: string;
  userId: string;
  createdAt?: Date;
  updatedAt?: Date;
}

class Profile extends Model<ProfileAttributes> implements ProfileAttributes {
  public id!: string;
  public bio?: string;
  public avatar?: string;
  public userId!: string;

  public readonly createdAt!: Date;
  public readonly updatedAt!: Date;
}

Profile.init(
  {
    id: {
      type: DataTypes.UUID,
      defaultValue: DataTypes.UUIDV4,
      primaryKey: true
    },
    bio: {
      type: DataTypes.TEXT,
      allowNull: true
    },
    avatar: {
      type: DataTypes.STRING,
      allowNull: true
    },
    userId: {
      type: DataTypes.UUID,
      allowNull: false,
      unique: true
    }
  },
  {
    sequelize,
    tableName: 'profiles'
  }
);

// Snippet 3: Post model with Many-to-One relation
interface PostAttributes {
  id: string;
  title: string;
  content?: string;
  published: boolean;
  authorId: string;
  createdAt?: Date;
  updatedAt?: Date;
}

class Post extends Model<PostAttributes> implements PostAttributes {
  public id!: string;
  public title!: string;
  public content?: string;
  public published!: boolean;
  public authorId!: string;

  public readonly createdAt!: Date;
  public readonly updatedAt!: Date;

  public readonly author?: User;
  public readonly categories?: Category[];
}

Post.init(
  {
    id: {
      type: DataTypes.UUID,
      defaultValue: DataTypes.UUIDV4,
      primaryKey: true
    },
    title: {
      type: DataTypes.STRING,
      allowNull: false
    },
    content: {
      type: DataTypes.TEXT,
      allowNull: true
    },
    published: {
      type: DataTypes.BOOLEAN,
      defaultValue: false
    },
    authorId: {
      type: DataTypes.UUID,
      allowNull: false
    }
  },
  {
    sequelize,
    tableName: 'posts',
    indexes: [
      { fields: ['title'] },
      { fields: ['published'] }
    ]
  }
);

// Snippet 4: Category model for Many-to-Many relation
interface CategoryAttributes {
  id: string;
  name: string;
}

class Category extends Model<CategoryAttributes> implements CategoryAttributes {
  public id!: string;
  public name!: string;

  public readonly posts?: Post[];
}

Category.init(
  {
    id: {
      type: DataTypes.UUID,
      defaultValue: DataTypes.UUIDV4,
      primaryKey: true
    },
    name: {
      type: DataTypes.STRING,
      allowNull: false,
      unique: true
    }
  },
  {
    sequelize,
    tableName: 'categories',
    timestamps: false
  }
);

// Snippet 5: Order and OrderItem models
interface OrderAttributes {
  id: string;
  orderNumber: string;
  status: string;
  totalAmount: number;
  userId: string;
  createdAt?: Date;
  updatedAt?: Date;
}

class Order extends Model<OrderAttributes> implements OrderAttributes {
  public id!: string;
  public orderNumber!: string;
  public status!: string;
  public totalAmount!: number;
  public userId!: string;

  public readonly createdAt!: Date;
  public readonly updatedAt!: Date;

  public readonly items?: OrderItem[];
}

Order.init(
  {
    id: {
      type: DataTypes.UUID,
      defaultValue: DataTypes.UUIDV4,
      primaryKey: true
    },
    orderNumber: {
      type: DataTypes.STRING,
      allowNull: false,
      unique: true
    },
    status: {
      type: DataTypes.ENUM('pending', 'processing', 'shipped', 'delivered', 'cancelled'),
      defaultValue: 'pending'
    },
    totalAmount: {
      type: DataTypes.DECIMAL(10, 2),
      allowNull: false,
      defaultValue: 0
    },
    userId: {
      type: DataTypes.UUID,
      allowNull: false
    }
  },
  {
    sequelize,
    tableName: 'orders',
    indexes: [
      { fields: ['status'] }
    ]
  }
);

interface OrderItemAttributes {
  id: string;
  quantity: number;
  price: number;
  orderId: string;
  productId: string;
}

class OrderItem extends Model<OrderItemAttributes> implements OrderItemAttributes {
  public id!: string;
  public quantity!: number;
  public price!: number;
  public orderId!: string;
  public productId!: string;
}

OrderItem.init(
  {
    id: {
      type: DataTypes.UUID,
      defaultValue: DataTypes.UUIDV4,
      primaryKey: true
    },
    quantity: {
      type: DataTypes.INTEGER,
      allowNull: false
    },
    price: {
      type: DataTypes.DECIMAL(10, 2),
      allowNull: false
    },
    orderId: {
      type: DataTypes.UUID,
      allowNull: false
    },
    productId: {
      type: DataTypes.UUID,
      allowNull: false
    }
  },
  {
    sequelize,
    tableName: 'order_items',
    timestamps: false
  }
);

interface ProductAttributes {
  id: string;
  name: string;
  description?: string;
  price: number;
  stock: number;
  isActive: boolean;
  createdAt?: Date;
  updatedAt?: Date;
}

class Product extends Model<ProductAttributes> implements ProductAttributes {
  public id!: string;
  public name!: string;
  public description?: string;
  public price!: number;
  public stock!: number;
  public isActive!: boolean;

  public readonly createdAt!: Date;
  public readonly updatedAt!: Date;
}

Product.init(
  {
    id: {
      type: DataTypes.UUID,
      defaultValue: DataTypes.UUIDV4,
      primaryKey: true
    },
    name: {
      type: DataTypes.STRING,
      allowNull: false
    },
    description: {
      type: DataTypes.TEXT,
      allowNull: true
    },
    price: {
      type: DataTypes.DECIMAL(10, 2),
      allowNull: false
    },
    stock: {
      type: DataTypes.INTEGER,
      defaultValue: 0
    },
    isActive: {
      type: DataTypes.BOOLEAN,
      defaultValue: true
    }
  },
  {
    sequelize,
    tableName: 'products'
  }
);

// Snippet 6: Define associations
User.hasOne(Profile, { foreignKey: 'userId', as: 'profile' });
Profile.belongsTo(User, { foreignKey: 'userId' });

User.hasMany(Post, { foreignKey: 'authorId', as: 'posts' });
Post.belongsTo(User, { foreignKey: 'authorId', as: 'author' });

Post.belongsToMany(Category, { through: 'post_categories', as: 'categories' });
Category.belongsToMany(Post, { through: 'post_categories', as: 'posts' });

User.hasMany(Order, { foreignKey: 'userId', as: 'orders' });
Order.belongsTo(User, { foreignKey: 'userId', as: 'user' });

Order.hasMany(OrderItem, { foreignKey: 'orderId', as: 'items' });
OrderItem.belongsTo(Order, { foreignKey: 'orderId', as: 'order' });

Product.hasMany(OrderItem, { foreignKey: 'productId' });
OrderItem.belongsTo(Product, { foreignKey: 'productId', as: 'product' });

// ============================================================================
// Query Examples
// ============================================================================

// Snippet 7: Find with relations
async function getUserWithRelations(userId: string) {
  const user = await User.findByPk(userId, {
    include: [
      { model: Profile, as: 'profile' },
      { model: Post, as: 'posts' },
      { model: Order, as: 'orders' }
    ]
  });

  return user;
}

// Snippet 8: Find with complex conditions
async function findActiveUsers() {
  const users = await User.findAll({
    where: {
      isActive: true,
      role: 'user'
    },
    include: [{ model: Profile, as: 'profile' }],
    order: [['createdAt', 'DESC']],
    limit: 50
  });

  return users;
}

// Snippet 9: Transaction
async function createOrderWithItems(userId: string, items: any[]) {
  return await sequelize.transaction(async (t) => {
    const order = await Order.create(
      {
        userId,
        orderNumber: `ORD-${Date.now()}`,
        status: 'pending',
        totalAmount: 0
      },
      { transaction: t }
    );

    let totalAmount = 0;
    for (const item of items) {
      const product = await Product.findByPk(item.productId, { transaction: t });

      if (!product || product.stock < item.quantity) {
        throw new Error('Insufficient stock');
      }

      await OrderItem.create(
        {
          orderId: order.id,
          productId: item.productId,
          quantity: item.quantity,
          price: product.price
        },
        { transaction: t }
      );

      product.stock -= item.quantity;
      await product.save({ transaction: t });

      totalAmount += Number(product.price) * item.quantity;
    }

    order.totalAmount = totalAmount;
    await order.save({ transaction: t });

    return order;
  });
}

// Snippet 10: Aggregation
async function getOrderStatistics() {
  const stats = await Order.findAll({
    attributes: [
      'status',
      [sequelize.fn('COUNT', sequelize.col('id')), 'orderCount'],
      [sequelize.fn('SUM', sequelize.col('total_amount')), 'totalRevenue'],
      [sequelize.fn('AVG', sequelize.col('total_amount')), 'avgOrderValue']
    ],
    group: ['status']
  });

  return stats;
}

// Snippet 11: Raw query
async function getTopCustomers(limit: number = 10) {
  const [results] = await sequelize.query(`
    SELECT
      u.id,
      u.name,
      COUNT(o.id) as order_count,
      COALESCE(SUM(o.total_amount), 0) as lifetime_value
    FROM users u
    LEFT JOIN orders o ON u.id = o.user_id
    GROUP BY u.id, u.name
    ORDER BY lifetime_value DESC
    LIMIT :limit
  `, {
    replacements: { limit },
    type: Sequelize.QueryTypes.SELECT
  });

  return results;
}

// Snippet 12: Bulk operations
async function bulkUpdatePrices(updates: Array<{ id: string; price: number }>) {
  return await Promise.all(
    updates.map(({ id, price }) =>
      Product.update({ price }, { where: { id } })
    )
  );
}

// Snippet 13: Pagination
async function getPaginatedPosts(page: number = 1, limit: number = 20) {
  const offset = (page - 1) * limit;

  const { count, rows } = await Post.findAndCountAll({
    where: { published: true },
    include: [
      { model: User, as: 'author', attributes: ['id', 'name'] },
      { model: Category, as: 'categories' }
    ],
    order: [['createdAt', 'DESC']],
    limit,
    offset
  });

  return {
    posts: rows,
    total: count,
    page,
    totalPages: Math.ceil(count / limit)
  };
}

// Snippet 14: Upsert
async function upsertCategory(name: string) {
  const [category, created] = await Category.findOrCreate({
    where: { name },
    defaults: { name }
  });

  return { category, created };
}

// Snippet 15: Hooks (lifecycle events)
User.beforeCreate(async (user) => {
  // Hash password or perform other operations
  console.log('Creating user:', user.email);
});

User.afterUpdate(async (user) => {
  console.log('Updated user:', user.email);
});

export { sequelize, User, Profile, Post, Category, Order, OrderItem, Product };
