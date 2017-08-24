from commands.base.command import Command


class Fullwidth(Command):
    supported = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&()*+,-./:;<=>?@[\\]^_`{|}~'

    def __init__(self, bot):
        super().__init__(bot)
        self.name = ['fullwidth', 'full']
        self.help = 'Convierte los carácteres soportados a fullwidth y responde con el texto resultante'

    async def handle(self, message, cmd):
        converted = [chr(0xFEE0 + ord(i)) if i in Fullwidth.supported else i for i in list(cmd.text)]
        await cmd.answer(''.join(converted))