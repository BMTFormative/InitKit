import base64
from cryptography.fernet import Fernet
from sqlmodel import Session, select
from datetime import datetime
import uuid
from typing import Tuple, List

from app.models import TenantApiKey, AdminApiKey

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
        # Store API keys in plaintext (no encryption)
        return api_key
        
    def decrypt_key(self, encrypted_key: str) -> str:
        # Return stored API key as-is
        return encrypted_key
        
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
    
    def get_tenant_active_providers(
        self,
        session: Session,
        tenant_id: uuid.UUID
    ) -> List[str]:
        """
        Get list of providers that tenant already has active keys for
        
        Returns:
            List of provider names (e.g., ['openai', 'anthropic'])
        """
        statement = select(TenantApiKey.provider).where(
            TenantApiKey.tenant_id == tenant_id,
            TenantApiKey.is_active == True
        )
        providers = session.exec(statement).all()
        return list(providers)
    
    def consume_next_available_admin_key(
        self,
        session: Session
    ) -> Tuple[str, str] | None:
        """
        Get the next available admin API key from any provider and mark it as consumed
        
        Returns:
            Tuple of (provider, api_key) or None if no keys available
        """
        # Fetch the next unassigned (inactive) admin key from any provider
        stmt = select(AdminApiKey).where(
            AdminApiKey.is_active == False
        ).order_by(AdminApiKey.created_at)
        
        admin_key = session.exec(stmt).first()
        if not admin_key:
            return None
        
        # Get the raw key value and mark as consumed
        raw_key = self.decrypt_key(admin_key.encrypted_key)
        provider = admin_key.provider
        
        # Mark as active (consumed)
        admin_key.is_active = True
        session.add(admin_key)
        session.commit()
        
        return (provider, raw_key)
    
    def create_admin_api_key(
        self,
        session: Session,
        provider: str,
        api_key: str
    ) -> AdminApiKey:
        # Deactivate any existing active admin keys for this provider
        stmt = select(AdminApiKey).where(
            AdminApiKey.provider == provider,
            AdminApiKey.is_active == True
        )
        existing = session.exec(stmt).all()
        for key in existing:
            key.is_active = False
            session.add(key)
        # Create new admin key
        encrypted = self.encrypt_key(api_key)
        new_key = AdminApiKey(
            provider=provider,
            encrypted_key=encrypted
        )
        session.add(new_key)
        session.commit()
        session.refresh(new_key)
        return new_key
    
    def get_active_admin_key(
        self,
        session: Session,
        provider: str
    ) -> str | None:
        stmt = select(AdminApiKey).where(
            AdminApiKey.provider == provider,
            AdminApiKey.is_active == True
        )
        api_key = session.exec(stmt).first()
        if not api_key:
            return None
        # Update last used timestamp
        api_key.last_used = datetime.utcnow()
        session.add(api_key)
        session.commit()
        return self.decrypt_key(api_key.encrypted_key)
    
    def consume_admin_api_key(
        self,
        session: Session,
        provider: str
    ) -> str | None:
        """
        Fetch the next available Admin API key for provider, mark it consumed (inactive), and return its raw value.
        Each call returns a unique key (one tenant per key).
        """
        # Fetch the next unassigned (inactive) admin key
        stmt = select(AdminApiKey).where(
            AdminApiKey.provider == provider,
            AdminApiKey.is_active == False
        ).order_by(AdminApiKey.created_at)
        api_key = session.exec(stmt).first()
        if not api_key:
            return None
        # Activate the admin key to mark assignment
        raw = self.decrypt_key(api_key.encrypted_key)
        api_key.is_active = True
        session.add(api_key)
        session.commit()
        return raw