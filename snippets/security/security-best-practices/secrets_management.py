"""Secrets Management"""
class SecretsManagement:
    @staticmethod
    def store_secrets():
        """Never commit secrets to version control"""
        return {
            'use_env_vars': True,
            'use_secret_manager': True,
            'tools': ['AWS Secrets Manager', 'HashiCorp Vault']
        }
