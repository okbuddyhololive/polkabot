import re
from typing import Dict, List, Union

import markovify
from discord import Attachment, Member, Message, User
from motor.motor_asyncio import AsyncIOMotorDatabase

class MessageManager:
    def __init__(self, database: AsyncIOMotorDatabase, min_limit: int = 1_000, max_limit: int = 25_000, length: int = 200, tries: int = 100) -> None:
        self.collection = database.messages

        self.min_limit = min_limit
        self.max_limit = max_limit
        self.length = length

        self.tries = tries

    async def get(self, user: Union[Member, User]) -> List[Dict]:
        return await self.collection.find({"author": {"id": str(user.id)}}).to_list(length=None)

    async def default(self) -> List[Dict]:
        return await self.collection.find({}).to_list(length=self.max_limit)

    async def links(self, extensions: List[str]) -> List[Dict]:
        cursor = self.collection.aggregate([
            {
                "$project": {
                    "url": {
                        "$regexFind": {
                            "input": "$content",
                            "regex": rf"\bhttps?:\/\/\S+\.(?:{"|".join(extensions)})\S*\b",
                            "options": "i"
                        }
                    }
                }
            },
            {
                "$match": {
                    "url": {
                        "$ne": None
                    }
                }
            }
        ])

        return await cursor.to_list(length=None)

    async def containing(self, keyword: str) -> List[Dict]:
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        cursor = self.collection.find({"content": pattern})

        return await cursor.to_list(length=None)

    async def add(self, message: Message) -> None:
        content = message.clean_content

        if message.attachments:
            content += " " + " ".join(attachment.url for attachment in message.attachments)

        await self.collection.insert_one({
            "author": {"id": str(message.author.id)},
            "content": content
        })

    async def remove(self, author: Union[Member, User]) -> None:
        await self.collection.delete_many({"author": {"id": str(author.id)}})

    async def generate(self, dataset: List[Dict]) -> str:
        dataset = [message.get("content") for message in dataset]
        chain = markovify.NewlineText(dataset, well_formed=False)

        return chain.make_short_sentence(self.length, tries=self.tries)