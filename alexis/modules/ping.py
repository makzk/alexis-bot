import random

from alexis import Command


class Ping(Command):
    def __init__(self, bot):
        super().__init__(bot)
        self.name = 'ping'
        self.help = 'Responde al comando *ping*'
        self.user_delay = 5

    async def handle(self, cmd):
        await cmd.answer(['wena xoro', 'pong!'][int(random.random() >= .5)])
