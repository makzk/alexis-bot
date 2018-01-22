from datetime import datetime
import peewee

from alexis import Command
from alexis.database import BaseModel
import random

from alexis.utils import is_int


class BanCmd(Command):
    def __init__(self, bot):
        super().__init__(bot)
        self.name = 'ban'
        self.help = 'Banea (simbólicamente) a un usuario'
        self.allow_pm = False
        self.pm_error = 'banéame esta xd'
        self.db_models = [Ban]

        self.user_delay = 10

    async def handle(self, cmd):
        if cmd.argc < 1:
            await cmd.answer('formato: $PX$NM <nombre, id, @mención>')
            return

        member = await cmd.get_user(cmd.text, member_only=True)
        if member is None:
            await cmd.answer(cmd.l('user-not-found'))
            return

        mention_name = member.display_name

        if not cmd.owner and cmd.is_owner(member):
            await cmd.answer('nopo wn no hagai esa wea xd')
            return

        if member.id == self.bot.user.id:
            await cmd.answer('oye que te has creído')
            return

        if member.bot:
            await cmd.answer('con mi colega no, tamo? :angry:')
            return

        # Evitar que alguien se banee a si mismo
        if self.bot.last_author == member.id:
            await cmd.answer('no te odies por favor :(')
            return

        # No banear personas que no están en el canal
        if not member.permissions_in(cmd.message.channel).read_messages:
            await cmd.answer('oye pero **{}** no está ná aquí'.format(mention_name))
            return

        if not random.randint(0, 1):
            await cmd.answer('¡**$AU** intentó banear a **{}**, quien se salvó de milagro!'
                             .format(mention_name), withname=False)
            return

        user, created = Ban.get_or_create(userid=member.id, server=cmd.message.server.id,
                                          defaults={'user': str(member)})
        update = Ban.update(bans=Ban.bans + 1, lastban=datetime.now(), user=str(member))
        update = update.where(Ban.userid == member.id, Ban.server == cmd.message.server.id)
        update.execute()

        if created:
            text = 'Uff, ¡**$AU** le ha dado a **{}** su primer ban!'.format(mention_name)
        else:
            text = '¡**$AU** ha baneado a **{}** sumando **{} baneos**!'
            text = text.format(mention_name, user.bans + 1)
        await cmd.answer(text, withname=False)


class Bans(Command):
    def __init__(self, bot):
        super().__init__(bot)
        self.name = 'bans'
        self.help = 'Muestra la cantidad de bans de una persona'
        self.allow_pm = False
        self.pm_error = 'no po wn que te crei'

    async def handle(self, cmd):
        if len(cmd.args) != 1:
            user = cmd.author
        else:
            user = await cmd.get_user(cmd.text)
            if user is None:
                await cmd.answer('usuario no encontrado')
                return

        if cmd.is_owner(user) and not cmd.owner:
            mesg = 'te voy a decir la cifra exacta: Cuatro mil trescientos cuarenta y '
            mesg += 'cuatro mil quinientos millones coma cinco bans, ese es el valor.'
            await cmd.answer(mesg)
            return

        userbans, created = Ban.get_or_create(userid=user.id, server=cmd.message.server.id,
                                              defaults={'user': str(user)})

        if userbans.bans == 0:
            mesg = "```\nException in thread \"main\" cl.discord.alexis.ZeroBansException\n"
            mesg += "    at AlexisBot.main(AlexisBot.java:34)\n```"
        else:
            word = 'ban' if userbans.bans == 1 else 'bans'
            if userbans.bans == 2:
                word = '~~papás~~ bans'

            if user.id == cmd.author.id:
                prefix = 'tienes'
            else:
                prefix = '**{}** tiene'.format(user.display_name)

            mesg = '{} {} {}'.format(prefix, userbans.bans, word)

        await cmd.answer(mesg)


class SetBans(Command):
    def __init__(self, bot):
        super().__init__(bot)
        self.name = 'setbans'
        self.help = 'Determina la cantidad de baneos de un usuario'
        self.allow_pm = False
        self.pm_error = 'como va a funcionar esta weá por pm wn que chucha'
        self.owner_only = True

    async def handle(self, cmd):
        if cmd.argc < 2 or not is_int(cmd.args[-1]):
            await cmd.answer('formato: $PX$NM <nombre, id, cantidad> <cantidad>')
            return

        mention = await cmd.get_user(' '.join(cmd.args[0:-1]))
        if mention is None:
            await cmd.answer('usuario no encontrado')
            return

        num_bans = int(cmd.args[-1])
        user, _ = Ban.get_or_create(userid=mention.id, server=cmd.message.server.id,
                                    defaults={'user': str(mention)})
        update = Ban.update(bans=num_bans, lastban=datetime.now(), user=str(mention))
        update = update.where(Ban.userid == mention.id, Ban.server == cmd.message.server.id)
        update.execute()

        name = mention.display_name
        if num_bans == 0:
            mesg = 'bans de **{}** reiniciados xd'.format(name)
            await cmd.answer(mesg)
        else:
            word = 'ban' if num_bans == 1 else 'bans'
            mesg = '**{}** ahora tiene {} {}'.format(name, num_bans, word)
            await cmd.answer(mesg)


class BanRank(Command):
    def __init__(self, bot):
        super().__init__(bot)
        self.name = 'banrank'
        self.aliases = [self.bot.config['command_prefix'] + 'banrank']
        self.help = 'Muestra el ranking de usuarios baneados. Con dos símbolos muestra una lista más extensa.'
        self.allow_pm = False
        self.pm_error = 'como va a funcionar esta weá por pm wn que chucha'

    async def handle(self, cmd):
        bans = Ban.select().where(Ban.server == cmd.message.channel.server.id).order_by(Ban.bans.desc())
        px = self.bot.config['command_prefix']
        banlist = []
        limit = 10 if cmd.cmdname == '{}{}'.format(px, self.name) else 5

        i = 1
        for item in bans.iterator():
            banlist.append('{}. {}: {}'.format(i, item.user, item.bans))

            i += 1
            if i > limit:
                break

        if len(banlist) == 0:
            await cmd.answer('no hay bans registrados')
        else:
            await cmd.answer('\nranking de bans:\n```\n{}\n```'.format('\n'.join(banlist)))


class Ban(BaseModel):
    user = peewee.TextField()
    userid = peewee.TextField(default="")
    bans = peewee.IntegerField(default=0)
    server = peewee.TextField()
    lastban = peewee.DateTimeField(null=True)
