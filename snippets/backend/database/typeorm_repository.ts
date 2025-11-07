/**
 * TypeORM Repository Pattern
 */
import { Repository } from 'typeorm';

export class UserRepository {
  constructor(private repo: Repository<User>) {}

  async findByEmail(email: string) {
    return this.repo.findOne({ where: { email } });
  }

  async findActiveUsers() {
    return this.repo.find({ where: { isActive: true } });
  }
}
