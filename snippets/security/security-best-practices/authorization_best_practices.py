"""Authorization Best Practices"""
class AuthorizationBestPractices:
    @staticmethod
    def implement_rbac():
        """Role-Based Access Control"""
        return {
            'admin': ['read', 'write', 'delete', 'manage_users'],
            'user': ['read', 'write'],
            'guest': ['read']
        }
