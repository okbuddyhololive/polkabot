from discord import Webhook, AsyncWebhookAdapter, TextChannel

from typing import List, Optional, TextIO
from __future__ import annotations
import json

def webhook_to_dict(webhook: Webhook) -> dict:
    return {
        "type": 1,
        "id": webhook.id,
        "token": webhook.token,
        "channel_id": webhook.channel_id
    }
    
class WebhookManager:
    def __init__(self, webhooks: List[dict]):
        self.webhooks = webhooks

    # methods for loading & dumping webhooks
    @staticmethod
    def from_file(file: TextIO) -> WebhookManager:
        return WebhookManager(json.load(file))

    @staticmethod
    def from_path(path: str) -> WebhookManager:
        with open(path, "r") as file:
            return WebhookManager.from_file(file)
    
    def to_file(self, file: TextIO, indent: int = 4):
        json.dump(self.webhooks, file, indent=indent)
    
    def to_path(self, path: str, indent: int = 4):
        with open(path, "w") as file:
            self.to_file(file, indent=indent)
    
    # methods that will be used by other functions & should not be used by the "consumer"
    def _find(self, channel: TextChannel) -> dict:
        for webhook in self.webhooks:
            if webhook["channel_id"] == channel.id:
                return webhook
    
    # methods for interacting with a specific webhook in a list
    async def get(self, channel: TextChannel, adapter: AsyncWebhookAdapter) -> Optional[Webhook]:
        webhook = self._find(channel)

        if webhook is None:
            return
        
        return Webhook(webhook, adapter)

    async def create(self, channel: TextChannel) -> Webhook:
        webhook = await channel.create_webhook(name=f"#{channel.name} Impersonation Webhook")
        self.webhooks.append(webhook_to_dict(webhook))
        return webhook

    async def remove(self, channel: TextChannel):
        webhook = self._find(channel)

        if webhook is None:
            return # TODO: raise a KeyError & then handle it in the command

        self.webhooks.remove(webhook)