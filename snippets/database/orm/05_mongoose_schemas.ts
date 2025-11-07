// ============================================================================
// Mongoose Schemas, Models, and Queries
// ============================================================================

import mongoose, { Schema, Document, Model, Types } from 'mongoose';

// Connection
mongoose.connect('mongodb://localhost:27017/myapp');

// ============================================================================
// Interfaces
// ============================================================================

interface IUser extends Document {
  email: string;
  name: string;
  role: 'user' | 'admin' | 'moderator';
  isActive: boolean;
  profile?: Types.ObjectId;
  createdAt: Date;
  updatedAt: Date;
}

interface IProfile extends Document {
  bio?: string;
  avatar?: string;
  user: Types.ObjectId;
  createdAt: Date;
  updatedAt: Date;
}

interface IPost extends Document {
  title: string;
  content?: string;
  published: boolean;
  author: Types.ObjectId;
  categories: Types.ObjectId[];
  tags: string[];
  viewCount: number;
  createdAt: Date;
  updatedAt: Date;
}

interface IOrder extends Document {
  orderNumber: string;
  status: 'pending' | 'processing' | 'shipped' | 'delivered' | 'cancelled';
  totalAmount: number;
  user: Types.ObjectId;
  items: Array<{
    product: Types.ObjectId;
    quantity: number;
    price: number;
  }>;
  createdAt: Date;
  updatedAt: Date;
}

// ============================================================================
// Schemas
// ============================================================================

// Snippet 1: User schema with validation
const userSchema = new Schema<IUser>(
  {
    email: {
      type: String,
      required: true,
      unique: true,
      lowercase: true,
      trim: true,
      validate: {
        validator: (v: string) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v),
        message: 'Invalid email format'
      }
    },
    name: {
      type: String,
      required: true,
      trim: true
    },
    role: {
      type: String,
      enum: ['user', 'admin', 'moderator'],
      default: 'user'
    },
    isActive: {
      type: Boolean,
      default: true
    },
    profile: {
      type: Schema.Types.ObjectId,
      ref: 'Profile'
    }
  },
  {
    timestamps: true,
    toJSON: { virtuals: true },
    toObject: { virtuals: true }
  }
);

// Indexes
userSchema.index({ email: 1 });
userSchema.index({ role: 1, isActive: 1 });

// Virtual populate
userSchema.virtual('posts', {
  ref: 'Post',
  localField: '_id',
  foreignField: 'author'
});

userSchema.virtual('orders', {
  ref: 'Order',
  localField: '_id',
  foreignField: 'user'
});

// Instance methods
userSchema.methods.deactivate = function() {
  this.isActive = false;
  return this.save();
};

// Static methods
userSchema.statics.findByEmail = function(email: string) {
  return this.findOne({ email: email.toLowerCase() });
};

// Snippet 2: Profile schema with One-to-One reference
const profileSchema = new Schema<IProfile>(
  {
    bio: {
      type: String,
      maxlength: 500
    },
    avatar: String,
    user: {
      type: Schema.Types.ObjectId,
      ref: 'User',
      required: true,
      unique: true
    }
  },
  {
    timestamps: true
  }
);

// Snippet 3: Post schema with references and subdocuments
const postSchema = new Schema<IPost>(
  {
    title: {
      type: String,
      required: true,
      trim: true,
      maxlength: 200
    },
    content: {
      type: String,
      maxlength: 10000
    },
    published: {
      type: Boolean,
      default: false
    },
    author: {
      type: Schema.Types.ObjectId,
      ref: 'User',
      required: true
    },
    categories: [{
      type: Schema.Types.ObjectId,
      ref: 'Category'
    }],
    tags: [{
      type: String,
      lowercase: true,
      trim: true
    }],
    viewCount: {
      type: Number,
      default: 0
    }
  },
  {
    timestamps: true
  }
);

postSchema.index({ title: 'text', content: 'text' });
postSchema.index({ published: 1, createdAt: -1 });
postSchema.index({ author: 1, published: 1 });

// Pre-save hook
postSchema.pre('save', function(next) {
  // Remove duplicate tags
  this.tags = [...new Set(this.tags)];
  next();
});

// Snippet 4: Category schema
const categorySchema = new Schema({
  name: {
    type: String,
    required: true,
    unique: true,
    trim: true
  },
  description: String
});

// Snippet 5: Order schema with embedded documents
const orderSchema = new Schema<IOrder>(
  {
    orderNumber: {
      type: String,
      required: true,
      unique: true
    },
    status: {
      type: String,
      enum: ['pending', 'processing', 'shipped', 'delivered', 'cancelled'],
      default: 'pending'
    },
    totalAmount: {
      type: Number,
      required: true,
      min: 0
    },
    user: {
      type: Schema.Types.ObjectId,
      ref: 'User',
      required: true
    },
    items: [{
      product: {
        type: Schema.Types.ObjectId,
        ref: 'Product',
        required: true
      },
      quantity: {
        type: Number,
        required: true,
        min: 1
      },
      price: {
        type: Number,
        required: true,
        min: 0
      }
    }]
  },
  {
    timestamps: true
  }
);

orderSchema.index({ user: 1, status: 1 });
orderSchema.index({ orderNumber: 1 });

// Snippet 6: Product schema
const productSchema = new Schema(
  {
    name: {
      type: String,
      required: true,
      trim: true
    },
    description: String,
    price: {
      type: Number,
      required: true,
      min: 0
    },
    stock: {
      type: Number,
      default: 0,
      min: 0
    },
    isActive: {
      type: Boolean,
      default: true
    },
    category: {
      type: Schema.Types.ObjectId,
      ref: 'Category'
    },
    tags: [String],
    images: [String]
  },
  {
    timestamps: true
  }
);

productSchema.index({ name: 'text', description: 'text' });
productSchema.index({ isActive: 1, price: 1 });

// ============================================================================
// Models
// ============================================================================

const User = mongoose.model<IUser>('User', userSchema);
const Profile = mongoose.model<IProfile>('Profile', profileSchema);
const Post = mongoose.model<IPost>('Post', postSchema);
const Category = mongoose.model('Category', categorySchema);
const Order = mongoose.model<IOrder>('Order', orderSchema);
const Product = mongoose.model('Product', productSchema);

// ============================================================================
// Query Examples
// ============================================================================

// Snippet 7: Create with populate
async function createUserWithProfile(userData: any, profileData: any) {
  const user = new User(userData);
  await user.save();

  const profile = new Profile({
    ...profileData,
    user: user._id
  });
  await profile.save();

  user.profile = profile._id;
  await user.save();

  return await User.findById(user._id).populate('profile');
}

// Snippet 8: Find with multiple populations
async function getUserWithAllRelations(userId: string) {
  const user = await User.findById(userId)
    .populate('profile')
    .populate({
      path: 'posts',
      match: { published: true },
      options: { sort: { createdAt: -1 }, limit: 10 },
      populate: { path: 'categories' }
    })
    .populate({
      path: 'orders',
      options: { sort: { createdAt: -1 }, limit: 5 }
    });

  return user;
}

// Snippet 9: Complex query with aggregation
async function getPostStatsByAuthor(authorId: string) {
  const stats = await Post.aggregate([
    { $match: { author: new Types.ObjectId(authorId) } },
    {
      $group: {
        _id: '$published',
        count: { $sum: 1 },
        totalViews: { $sum: '$viewCount' },
        avgViews: { $avg: '$viewCount' }
      }
    }
  ]);

  return stats;
}

// Snippet 10: Transaction example
async function createOrderTransaction(userId: string, items: any[]) {
  const session = await mongoose.startSession();
  session.startTransaction();

  try {
    let totalAmount = 0;
    const orderItems = [];

    for (const item of items) {
      const product = await Product.findById(item.productId).session(session);

      if (!product || product.stock < item.quantity) {
        throw new Error(`Insufficient stock for product ${item.productId}`);
      }

      product.stock -= item.quantity;
      await product.save({ session });

      orderItems.push({
        product: product._id,
        quantity: item.quantity,
        price: product.price
      });

      totalAmount += product.price * item.quantity;
    }

    const order = new Order({
      orderNumber: `ORD-${Date.now()}`,
      user: userId,
      items: orderItems,
      totalAmount,
      status: 'pending'
    });

    await order.save({ session });

    await session.commitTransaction();
    return order;
  } catch (error) {
    await session.abortTransaction();
    throw error;
  } finally {
    session.endSession();
  }
}

// Snippet 11: Text search
async function searchPosts(searchTerm: string) {
  const posts = await Post.find(
    { $text: { $search: searchTerm } },
    { score: { $meta: 'textScore' } }
  )
    .sort({ score: { $meta: 'textScore' } })
    .populate('author', 'name email')
    .populate('categories')
    .limit(20);

  return posts;
}

// Snippet 12: Pagination
async function getPaginatedProducts(page: number = 1, limit: number = 20, filters: any = {}) {
  const skip = (page - 1) * limit;

  const query = {
    isActive: true,
    ...filters
  };

  const [products, total] = await Promise.all([
    Product.find(query)
      .skip(skip)
      .limit(limit)
      .sort({ createdAt: -1 })
      .populate('category'),
    Product.countDocuments(query)
  ]);

  return {
    products,
    pagination: {
      page,
      limit,
      total,
      totalPages: Math.ceil(total / limit)
    }
  };
}

// Snippet 13: Update with operators
async function incrementPostViews(postId: string) {
  const post = await Post.findByIdAndUpdate(
    postId,
    { $inc: { viewCount: 1 } },
    { new: true }
  );

  return post;
}

async function addTagToPost(postId: string, tag: string) {
  const post = await Post.findByIdAndUpdate(
    postId,
    { $addToSet: { tags: tag.toLowerCase() } },
    { new: true }
  );

  return post;
}

// Snippet 14: Bulk operations
async function bulkUpdateProductPrices(updates: Array<{ id: string; price: number }>) {
  const bulkOps = updates.map(update => ({
    updateOne: {
      filter: { _id: update.id },
      update: { $set: { price: update.price } }
    }
  }));

  const result = await Product.bulkWrite(bulkOps);
  return result;
}

// Snippet 15: Aggregation pipeline for analytics
async function getOrderAnalytics(startDate: Date, endDate: Date) {
  const analytics = await Order.aggregate([
    {
      $match: {
        createdAt: { $gte: startDate, $lte: endDate },
        status: { $ne: 'cancelled' }
      }
    },
    {
      $group: {
        _id: {
          $dateToString: { format: '%Y-%m-%d', date: '$createdAt' }
        },
        totalOrders: { $sum: 1 },
        totalRevenue: { $sum: '$totalAmount' },
        avgOrderValue: { $avg: '$totalAmount' }
      }
    },
    { $sort: { _id: 1 } }
  ]);

  return analytics;
}

export {
  User,
  Profile,
  Post,
  Category,
  Order,
  Product
};
