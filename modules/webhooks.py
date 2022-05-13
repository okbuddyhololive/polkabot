from __future__ import annotations
from discord import Webhook, AsyncWebhookAdapter, TextChannel
from motor.motor_asyncio import AsyncIOMotorDatabase

class WebhookManager:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database.webhooks

    # methods for interacting with a specific webhook in a collection
    async def get(self, channel: TextChannel, adapter: AsyncWebhookAdapter) -> Webhook:
        webhook = await self.collection.find_one({"channel": {"id": str(channel.id)}})

        if webhook is None:
            return await self.create(channel)
        
        # stuff so that the webhook class will work 
        webhook.remove("_id")
        webhook.remove("channel")
        webhook["type"] = 1
        
        return Webhook(webhook, adapter=adapter)

    async def create(self, channel: TextChannel) -> Webhook:
        webhook = await channel.create_webhook(name=f"#{channel.name} Impersonation Webhook")
        
        await self.collection.insert_one({
            "id": webhook.id,
            "token": webhook.token,
            "channel": {"id": str(channel.id), "name": channel.name},
        })

        return webhook

    async def remove(self, channel: TextChannel):
        return await self.collection.delete_one({"channel": {"id": str(channel.id)}})