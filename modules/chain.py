from __future__ import annotations
from discord import Message, Member, User
from motor.motor_asyncio import AsyncIOMotorDatabase
import markovify

from typing import Dict, List, Union

class MessageManager:
    def __init__(self, database: AsyncIOMotorDatabase, max_limit: int = 25_000, length: int = 200, tries: int = 100):
        self.collection = database.messages

        self.max_limit = max_limit
        self.length = length
        self.tries = tries
    
    async def default(self) -> List[Dict]:
        cursor = self.collection.find({})
        return await cursor.to_list(length=self.max_limit)
    
    async def add(self, message: Message):
        return await self.collection.insert_one({
            "author": {"id": message.author.id},
            "content": message.clean_content
        })

    async def remove(self, author: Union[Member, User]) -> List[str]:
        return await self.collection.delete_many({"author": {"id": author.id}})

    async def generate(self, author: Union[Member, User]) -> str:
        cursor = self.collection.find({"author": {"id": author.id}})
        dataset = await cursor.to_list(length=self.max_limit)

        if not dataset:
            dataset = await self.default()
        
        dataset = [message.get("content") for message in dataset]
        chain = markovify.NewlineText(dataset, well_formed=False)

        return chain.make_short_sentence(self.length, tries=self.tries)
