from discord import Message, Member, User
import markovify

from typing import Optional, Dict, List, Union

class MessageManager:
    def __init__(self, messages: Dict[List[str]]):
        self.messages = messages
        self.max_limit = 25_000 # TODO: make this a customizable variable in the config

    async def _default(self) -> List[str]:
        dataset = [message for pack in self.messages.values() for message in pack] # flattening

        if len(dataset) > self.max_limit:
            dataset = dataset[:self.max_limit] # get the specified number of latest messages

        return dataset
    
    async def add(self, message: Message, author: Union[Member, User]):
        identificator = str(author.id)
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
