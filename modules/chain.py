from __future__ import annotations
from discord import Message, Member, User
import markovify

from typing import Optional, Dict, List, Union, TextIO
import json
import os

class MessageManager:
    def __init__(self, messages: Dict[List[str]]):
        self.messages = messages
        self.max_limit = 25_000 # TODO: make this a customizable variable in the config

    # methods for loading & dumping webhooks
    @staticmethod
    def from_file(file: TextIO) -> MessageManager:
        return MessageManager(json.load(file))

    @staticmethod
    def from_path(path: str) -> MessageManager:
        if not os.path.exists("/data/messages.json"):
            with open(path, "a") as file:
                json.dump({}, file)
                with open(path, "r") as file:
                    return MessageManager.from_file(file)
    
    def to_file(self, file: TextIO, indent: int = 4):
        json.dump(self.messages, file, indent=indent)
    
    def to_path(self, path: str, indent: int = 4):
        with open(path, "w") as file:
            self.to_file(file, indent=indent)

    # methods that will be used by other functions & should not be used by the "consumer"
    async def _default(self) -> List[str]:
        dataset = [message for pack in self.messages.values() for message in pack] # flattening

        if len(dataset) > self.max_limit:
            dataset = dataset[:self.max_limit] # get the specified number of latest messages

        return dataset
    
    # methods for interacting with a specific message dataset in a list
    async def add(self, message: Message):
        identificator = str(message.author.id)
        content = message.clean_content

        if identificator not in self.messages:
            self.messages[identificator] = []
        
        self.messages[identificator].append(content)

        if len(self.messages[identificator]) > self.max_limit:
            self.messages[identificator] = self.messages[identificator][1:] # strip out the oldest message in the list

    async def generate(self, author: Union[Member, User]) -> str:
        identificator = str(author.id)

        if identificator not in self.messages:
            dataset = await self._default()
        else:
            dataset = self.messages[identificator]

        chain = markovify.NewlineText(dataset, well_formed=False)

        return chain.make_short_sentence(200) # TODO: make the length (200) a customizable variable in the config too 
