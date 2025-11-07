/**
 * Sequelize Model Definition
 */
import { Model, DataTypes } from 'sequelize';

export class User extends Model {
  declare id: string;
  declare email: string;
  declare name: string;
}

export function initUserModel(sequelize: any) {
  User.init({
    id: { type: DataTypes.UUID, primaryKey: true },
    email: { type: DataTypes.STRING, unique: true },
    name: DataTypes.STRING,
  }, { sequelize });
}
