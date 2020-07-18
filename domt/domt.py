import discord
from redbot.core import commands, checks, Config
# needed to improve autocomplete
from redbot.core.bot import Red
from discord.ext.commands import Context

import random


class Domt(commands.Cog):
    def __init__(self, bot: Red):
        # images taken from https://imgur.com/a/8wneGfK
        self.cards = [
            {
                'name': 'Rogue',
                'img': 'https://i.imgur.com/voPBc64.png',
                'desc': "A nonplayer character of the DM's choice becomes Hostile toward you. The identity of your new enemy isn't known until the NPC or someone else reveals it. Nothing less than a wish spell or Divine Intervention can end the NPC's hostility toward you."
            },
            {
                'name': 'Balance',
                'img': 'https://i.imgur.com/dlHlMSJ.png',
                'desc': "Your mind suffers a wrenching alteration, causing your Alignment to change. Lawful becomes chaotic, good becomes evil, and vice versa. If you are true neutral or unaligned, this card has no effect on you."
            },
            {
                'name': 'Comet',
                'img': 'https://i.imgur.com/tLWgYA5.png',
                'desc': "If you single-handedly defeat the next Hostile monster or group of Monsters you encounter, you gain Experience Points enough to gain one level. Otherwise, this card has no effect."
            },
            {
                'name': 'Donjon',
                'img': 'https://i.imgur.com/Y7zITG4.png',
                'desc': "You disappear and become entombed in a state of suspended animation in an extradimensional Sphere. Everything you were wearing and carrying stays behind in the space you occupied when you disappeared. You remain imprisoned until you are found and removed from the Sphere. You can't be located by any Divination magic, but a wish spell can reveal the location of your prison. You draw no more cards."
            },
            {
                'name': 'Euryale',
                'img': 'https://i.imgur.com/DxgQ9o1.png',
                'desc': "The card's medusa-like visage curses you. You take a -2 penalty on Saving Throws while Cursed in this way. Only a god or the magic of The Fates card can end this curse."
            },
            {
                'name': 'The Fates',
                'img': 'https://i.imgur.com/L4ag0fK.png',
                'desc': "Reality's fabric unravels and spins anew, allowing you to avoid or erase one event as if it never happened. You can use the card's magic as soon as you draw the card or at any other time before you die."
            },
            {
                'name': 'Flames',
                'img': 'https://i.imgur.com/j7kEK96.png',
                'desc': "A powerful devil becomes your enemy. The devil seeks your ruin and plagues your life, savoring your suffering before attempting to slay you. This enmity lasts until either you or the devil dies."
            },
            {
                'name': 'Fool',
                'img': 'https://i.imgur.com/m7ych8E.png',
                'desc': "You lose 10,000 XP, discard this card, and draw from the deck again, counting both draws as one of your declared draws. If losing that much XP would cause you to lose a level, you instead lose an amount that leaves you with just enough XP to keep your level."
            },
            {
                'name': 'Gem',
                'img': 'https://i.imgur.com/8TBp17r.png',
                'desc': "Twenty-five pieces of jewelry worth 2,000 gp each or fifty gems worth 1,000 gp each appear at your feet."
            },
            {
                'name': 'Idiot',
                'img': 'https://i.imgur.com/4NtUg2g.png',
                'desc': "Permanently reduce your Intelligence by 1d4 + 1 (to a minimum score of 1). You can draw one additional card beyond your declared draws."
            },
            {
                'name': 'Jester',
                'img': 'https://i.imgur.com/9h9mMaR.png',
                'desc': "You gain 10,000 XP, or you can draw two additional cards beyond your declared draws."
            },
            {
                'name': 'Key',
                'img': 'https://i.imgur.com/bAfjOyA.png',
                'desc': "A rare or rarer Magic Weapon with which you are proficient appears in your hands. The DM chooses the weapon."
            },
            {
                'name': 'Knight',
                'img': 'https://i.imgur.com/ZALdmca.png',
                'desc': "You gain the service of a 4th-level Fighter who appears in a space you choose within 30 feet of you. The Fighter is of the same race as you and serves you loyally until death, believing the fates have drawn him or her to you. You control this character."
            },
            {
                'name': 'Moon',
                'img': 'https://i.imgur.com/Bcti8iW.png',
                'desc': "You are granted the ability to cast the wish spell 1d3 times."
            },
            {
                'name': 'Ruin',
                'img': 'https://i.imgur.com/pvMSQTZ.png',
                'desc': "All forms of Wealth that you carry or own, other than Magic Items, are lost to you. Portable property vanishes. Businesses, buildings, and land you own are lost in a way that alters reality the least. Any documentation that proves you should own something lost to this card also disappears."
            },
            {
                'name': 'Skull',
                'img': 'https://i.imgur.com/bIJZZAR.png',
                'desc': "You summon an avatar of death-a ghostly Humanoid Skeleton clad in a tattered black robe and carrying a spectral scythe. It appears in a space of the DM's choice within 10 feet of you and attacks you, warning all others that you must win the battle alone. The avatar fights until you die or it drops to 0 Hit Points, whereupon it disappears. If anyone tries to help you, the helper summons its own Avatar of Death. A creature slain by an Avatar of Death can't be restored to life."
            },
            {
                'name': 'Star',
                'img': 'https://i.imgur.com/zgGikPc.png',
                'desc': " Increase one of your Ability Scores by 2. The score can exceed 20 but can't exceed 24."
            },
            {
                'name': 'Sun',
                'img': 'https://i.imgur.com/zYyIMoe.png',
                'desc': "You gain 50,000 XP, and a wondrous item (which the DM determines randomly) appears in your hands."
            },
            {
                'name': 'Talons',
                'img': 'https://i.imgur.com/gGStBpn.png',
                'desc': "Every magic item you wear or carry disintegrates. Artifacts in your possession aren't destroyed but do Vanish."
            },
            {
                'name': 'Throne',
                'img': 'https://i.imgur.com/ihUkfzo.png',
                'desc': "You gain proficiency in the Persuasion skill, and you double your Proficiency Bonus on checks made with that skill. In addition, you gain rightful ownership of a small keep somewhere in the world. However, the keep is currently in the hands of Monsters, which you must clear out before you can claim the keep as. yours."
            },
            {
                'name': 'Vizier',
                'img': 'https://i.imgur.com/8CB1NbW.png',
                'desc': "At any time you choose within one year of drawing this card, you can ask a question in meditation and mentally receive a truthful answer to that question. Besides information, the answer helps you solve a puzzling problem or other dilemma. In other words, the knowledge comes with Wisdom on how to apply it."
            },
            {
                'name': 'The Void',
                'img': 'https://i.imgur.com/45aIClQ.png',
                'desc': "This black card Spells Disaster. Your soul is drawn from your body and contained in an object in a place of the DM's choice. One or more powerful beings guard the place. While your soul is trapped in this way, your body is Incapacitated. A wish spell can't restore your soul, but the spell reveals the location of the object that holds it. You draw no more cards."
            }
        ]

    @commands.command(pass_context=True)
    async def domt(self, ctx, *, card: str = None):
        """Draws a card from the Deck of Many Things or a specific one by name."""
        async with ctx.typing():
            if card is None:
                p = random.randrange(len(self.cards))
                await self.show_card(ctx, self.cards[p])
            elif card.lower() in ['list', 'info', 'about', 'deck']:
                await self.list_cards(ctx)
            else:
                for c in self.cards:
                    if c['name'].lower() == card.lower():
                        await self.show_card(ctx, c)
                        return
                await ctx.send(f"Invalid card!")

    async def show_card(self, ctx, card: dict):
        """Shows a card in the deck"""
        emb = discord.Embed(
            title=card['name'],
            colour=discord.Colour.dark_purple(),
            url='https://roll20.net/compendium/dnd5e/Deck%20of%20Many%20Things#content',
            description=card['desc']
        )
        emb.set_footer(text='Use [p]domt info for list of all cards.')
        emb.set_image(url=card['img'])
        await ctx.send(embed=emb)

    async def list_cards(self, ctx):
        """Lists all cards in the deck"""
        description = """
Usually found in a box or pouch, this deck contains a number of cards made of ivory or vellum. Most (75 percent) of these decks have only thirteen cards, but the rest have twenty-two.

Before you draw a card, you must declare how many cards you intend to draw and then draw them randomly (you can use an altered deck of playing cards to simulate the deck). Any cards drawn in excess of this number have no effect. Otherwise, as soon as you draw a card from the deck, its magic takes effect. You must draw each card no more than 1 hour after the previous draw. If you fail to draw the chosen number, the remaining number of cards fly from the deck on their own and take effect all at once.

Once a card is drawn, it fades from existence. Unless the card is the Fool or the Jester, the card reappears in the deck, making it possible to draw the same card twice.

"""
        
        description += "Cards: "
        for card in self.cards:
            description += f"**{card['name']}**, "

        emb = discord.Embed(
            title='Deck of Many Things',
            colour=discord.Colour.dark_purple(),
            url='https://roll20.net/compendium/dnd5e/Deck%20of%20Many%20Things#content',
            description=description
        )
        emb.set_thumbnail(url='https://i.imgur.com/741T6Lk.png')
        await ctx.send(embed=emb)