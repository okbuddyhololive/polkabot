from typing import Optional

from aiohttp import ClientSession
from discord import TextChannel, Webhook
from motor.motor_asyncio import AsyncIOMotorDatabase

class WebhookManager:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database.webhooks

    # methods for interacting with a specific webhook in a collection
    async def get(self, channel: TextChannel, session: ClientSession) -> Optional[Webhook]:
        webhook = await self.collection.find_one({"channel": {"id": str(channel.id)}})

        if webhook is None:
            return

        return Webhook.partial(id=int(webhook.get("id")), token=webhook.get("token"), session=session)

    async def create(self, channel: TextChannel) -> Webhook:
        webhook = await channel.create_webhook(name=f"#{channel.name} Impersonation Webhook")

        await self.collection.insert_one({
            "id": str(webhook.id),
            "token": webhook.token,
            "channel": {"id": str(channel.id)},
        })

        return webhook

    async def remove(self, channel: TextChannel):
        await self.collection.delete_one({"channel": {"id": str(channel.id)}})