import base64
from cryptography.fernet import Fernet
from sqlmodel import Session, select
from datetime import datetime
import uuid

from app.models import TenantApiKey

class ApiKeyService:
    def __init__(self, encryption_key: str = None):
        """
        Initialize the API Key Service with an encryption key.
        If no key is provided, generate a new one.
        """
        if encryption_key:
            # Generate a valid Fernet key from the provided string
            key_bytes = encryption_key.encode()
            # Ensure the key is 32 bytes by hashing it or padding/truncating
            key_bytes = base64.urlsafe_b64encode(key_bytes[:32].ljust(32, b'\0'))
            self.fernet = Fernet(key_bytes)
        else:
            # Generate a new key
            self.fernet = Fernet(Fernet.generate_key())
        
    def encrypt_key(self, api_key: str) -> str:
        return self.fernet.encrypt(api_key.encode()).decode()
        
    def decrypt_key(self, encrypted_key: str) -> str:
        return self.fernet.decrypt(encrypted_key.encode()).decode()
        
    def create_tenant_api_key(
        self, 
        session: Session, 
        tenant_id: uuid.UUID, 
        provider: str, 
        api_key: str
    ) -> TenantApiKey:
        # Deactivate any existing active keys for this provider
        statement = select(TenantApiKey).where(
            TenantApiKey.tenant_id == tenant_id,
            TenantApiKey.provider == provider,
            TenantApiKey.is_active == True
        )
        existing_keys = session.exec(statement).all()
        for key in existing_keys:
            key.is_active = False
            session.add(key)
            
        # Create new key
        encrypted_key = self.encrypt_key(api_key)
        new_key = TenantApiKey(
            tenant_id=tenant_id,
            provider=provider,
            encrypted_key=encrypted_key
        )
        session.add(new_key)
        session.commit()
        session.refresh(new_key)
        return new_key
        
    def get_active_key_for_tenant(
        self, 
        session: Session, 
        tenant_id: uuid.UUID, 
        provider: str
    ) -> str | None:
        statement = select(TenantApiKey).where(
            TenantApiKey.tenant_id == tenant_id,
            TenantApiKey.provider == provider,
            TenantApiKey.is_active == True
        )
        api_key = session.exec(statement).first()
        if not api_key:
            return None
        
        # Update last used timestamp
        api_key.last_used = datetime.utcnow()
        session.add(api_key)
        session.commit()
        
        return self.decrypt_key(api_key.encrypted_key)