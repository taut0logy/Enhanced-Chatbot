from typing import Optional
from pydantic import BaseModel
from redis_om import HashModel, Field, JsonModel, Migrator
from app.core.config import settings

class RedisOTP(HashModel):
    email: str = Field(index=True)
    otp: str
    purpose: str = Field(index=True)
    attempts: int = Field(default=0)
    expiry: float

    class Meta:
        database = settings.REDIS_URL
        model_key_prefix = "otp"
        ttl = 3600

    def get_key(self) -> str:
        """Get the Redis key for this OTP."""
        return f"{self.email}:{self.purpose}"

    @classmethod
    async def get(cls, key: str) -> Optional['RedisOTP']:
        """Get an OTP by its key."""
        try:
            primaryKey = await cls.db().get(f"{cls.Meta.model_key_prefix}:{key}")
            if primaryKey:
                return await cls.get(primaryKey)
            return None
        except Exception:
            return None

    async def save(self) -> None:
        """Save the OTP with expiry."""
        await super().save()
        key = self.get_key()
        await self.db().set(
            f"{self.Meta.model_key_prefix}:{key}",
            self.pk,
            ex=self.Meta.ttl
        )

    async def delete(self) -> None:
        """Delete the OTP and its key."""
        key = self.get_key()
        await self.db().delete(f"{self.Meta.model_key_prefix}:{key}")
        await super().delete()
