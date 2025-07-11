import discord
import json
from discord.ext import commands
from discord import app_commands
from discord.ext import tasks
import time
import math
import discord.ui
import random
import datetime
import asyncio

intents = discord.Intents.default()
intents.message_content=True
#ще можна додати щоб для кожної ролі були свої особливості
#Реворк роботи:роботи будуть мінііграми а не команда і чекати
DATA={
    "prefix":"!",
    "token file":"magnat_token.txt",
    "user data file":"user_data.json",
    "initial user data":{
        "мідні": 0,
        "срібні": 0,
        "золоті": 0,
        "пойнти роботи":100,
        "рівень":0,
        "пойнти досягнень":0,
        "працює":0,
        "час початку роботи":time.time(),
        "credit_мідні":0,
        "credit_срібні":0,
        "credit_золоті":0,
    },
    "allowed money types":["мідні", "срібні", "золоті"],
    "owner id":1309961406191239178,
    "initial bank data":{
        "мідні": 0,
        "срібні": 0,
        "золоті": 0,
        "timeoflastdepositloop:":time.time(),
    },
    "bank data file":"bank_data.json",
    "credit percentage": 1.05,
    "exchange rates percentage return": 0.98,
    "exchange rate": 100,
    "exchange value": {"мідні":0,
                      "срібні":1,
                      "золоті":2},
    "initial quest data":{
        "quests": [],
        "time of generation": 0,
        "completed quests": [],
        "gift10copper":False,
        "commands used":[],
        "channelsmsg":[],
        "gifsent":False,
    },
    "quest data file":"quest_data.json",
    "shop data file":"shop_data.json",
    "initial shop data":{
        "bank upgrade bought":0,
    },
    "channels autosend on":[1387483882386886656],
    "deposit percentage":1.05,
    "dailypay":1,
    "gusid":1311041588557905940,
    "channel data file":"channels.json",
    "initial channel data":[],
}
wordle=""
guesses=0
def load_wordle(): 
    all_data = ["Бобер"]
    try:
        with open("wordle.json","r") as f:
            all_data = json.load(f)
            all_data=all_data["текст"].split()
    except FileNotFoundError:
        pass
    except json.JSONDecodeError:
        print("ПОМИЛКА: Не вдалося декодувати JSON файл. Файл пошкоджений або порожній.")
    return all_data
def begin():
	global wordle
	global guesses
	wordle=load_wordle()[random.randint(0,len(load_wordle())-1)]
	guesses=0
	
def guessw(guess):
	global wordle	
	global guesses
	printr=""
   
	if wordle=="":
		print("Вордл ще не розпочато!")
		return
	if len(guess)!=len(wordle):
	    print("Довжина вордлу не дорівнює довжині спроби!")
	    return
	if guesses+1>6:
		print("Надто багато спроб")
		return
	if guess not in load_wordle():
		print("Неможливе слово")
	else:
	   for x in range(0, len(wordle)):
	   	if wordle[x].lower()==guess[x].lower():
	   	   printr+="З"
	   	elif wordle[x].lower()!=guess[x].lower() and guess[x] in wordle:
	   	   printr+="Ж"
	   	else:
	   	   printr+="Б"
	guesses+=1
	return printr
	
QUESTS=["Подарувати комусь 10 мідних", "Написати повідомлення у 5 чатах", "Надішли 1 гіфочку", "Використай 5 різних команд Магната"]

BOT = commands.Bot(command_prefix=DATA["prefix"], intents=intents, help_command=None)

def _next():
	quests=[]
	completed=[]
	while len(quests)!=3:
	       quest=random.choice(QUESTS)
	       if quest not in completed:
	           quests.append(quest)
	           completed.append(quest)
	return quests

@BOT.tree.command(name="wordle", description="Пограти у вордл за гроші")
async def wordlep(interaction: discord.Interaction):
	begin()
	await interaction.response.send_message("Ви граєте у вордл!", view=WGM())

class WordleGuessModal(discord.ui.Modal, title="Вгадай слово..."): 
    guess=discord.ui.TextInput(label="Слово", placeholder="Введіть ваше слово...",custom_id="word",style=discord.TextStyle.short, required=True)
    act="оййй"
    async def on_submit(self, interaction: discord.Interaction):
        act=guessw(self.guess.value)
        if act=="ЗЗЗЗЗ":
        	loaded_data=load_user_data(interaction.user.id)
        	loaded_data["мідні"]+=100
        	save_user_data(loaded_data)
        	guesses=6
        await interaction.response.send_message(f"Ось результат: {act}")

class WGM(discord.ui.View):
    def __init__(self):
        super().__init__()
    @discord.ui.button(label="Вгадати слово", style=discord.ButtonStyle.green,custom_id="play_button_id")
    async def guess_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(WordleGuessModal())

@BOT.tree.command(name="quests", description="Подивитися квести на сьогодні")   
async def viewquests(interaction:discord.Interaction):
    qd=load_quest_data(interaction.user.id)
    if "Використай 5 різних команд Магната" in qd["quests"] and "Використай 5 різних команд Магната" not in qd["completed quests"] and "viewquests" not in qd["commands used"]:
        qd["commands used"].append("viewquests")
        save_quest_data(interaction.user.id, qd)
    quest_data=load_quest_data(interaction.user.id)
    if quest_data["quests"]==[] or math.floor(quest_data["time of generation"]/(3600*24))<math.floor(time.time()/(3600*24)):
        quest_data["quests"]=_next()
        quest_data["time of generation"]=time.time()
        quest_data["completed quests"]=[]
    embed = discord.Embed(title="Квести",description="Магнат пропонує вам квести:", color=discord.Color.blue())
    embed.add_field(name="Квест Перший: ", value=quest_data["quests"][0],  inline=False)
    embed.add_field(name="Квест Другий: ", value=quest_data["quests"][1], inline=False)
    embed.add_field(name="Квест Третій: ", value=quest_data["quests"][2], inline=False)
    await interaction.response.send_message(embed=embed)
    save_quest_data(interaction.user.id, quest_data)
@BOT.tree.command(name="help", description="Допомога")
async def help(interaction:discord.Interaction):
    qd=load_quest_data(interaction.user.id)
    if "Використай 5 різних команд Магната" in qd["quests"] and "Використай 5 різних команд Магната" not in qd["completed quests"] and "help" not in qd["commands used"]:
        qd["commands used"].append("help")
        save_quest_data(interaction.user.id, qd)
    embed = discord.Embed(
        title="Команди",
        description="МАГНАТ вміє:",
        color=discord.Color.blue()
    )
    embed.add_field(name="!help, !h", value="Викликає це повідомлення", inline=False)
    embed.add_field(name="!bank, !bnk", value="Викликає банк. Доступні команди у банку: Кредит, Депозит, Взяти гроші, Обміняти гроші і Сплатити борг", inline=False)
    embed.add_field(name="!steal, !stl", value="Вкрасти гроші у іншого користувача. Приймає один аргумент: користувач. Є можливість потрапити у тюрму на 1 день. Наприклад: !stl @Українська Перемога!", inline=False)
    embed.add_field(name="!slots, !sl", value="Крутити слоти. Приймає два аргументи: кількість монет, тип монет. Введіть all як кількість монет щоб поставити всі ваші гроші. Наприклад: !sl 100 срібні", inline=False)
    embed.add_field(name="!gift, !gft", value="Подарувати гроші іншому користувачу. Приймає три аргументи: кількість монет, тип монет і користувач. Наприклад: !gift 100 золоті @vadimosolo", inline=False)
    embed.add_field(name="!work, !wk", value="Працювати. Споживає пойнти роботи і ви отримуєте гроші і пойнти досягнень. Якщо занадто втомилися, ви автоматично будете відпочивати", inline=False)
    embed.add_field(name="!stopwork, !swk", value="Припинити роботу. Під час відпочинку ви регенеруєте пойнти роботи", inline=False)
    embed.add_field(name="!balance, !bal", value="Показує ваш баланс.", inline=False)
    embed.add_field(name="!free, !fr", value="Вивести на свободу користувача з тюрми. Приймає один аргумент: користувач. Наприклад: !fr @Бобер Писар. Доступно лише овнеру",inline=False)
    embed.add_field(name="!give, !gv", value="Дати користувачу гроші. Приймає три аргументи: кількість монет, тип монет, користувач. Наприклад: !give 100 мідні @vadimosolo. Доступно лише овнеру",inline=False)
    embed.add_field(name="/take", value="Забрати гроші у користувача. Приймає три аргументи: кількість монет, тип монет, користувач. Наприклад: /take 100 мідні @Українська Перемога!. Доступно лише овнеру",inline=False)
    embed.add_field(name="/quests", value="Видає щоденні квести, коли ти виконав квести тобі напише магнат у ПП і видасть винагороду")
    embed.set_footer(text="ОГО, як багато команд тут є!")
    await interaction.response.send_message(embed=embed)

@BOT.event
async def on_ready():
    print("Магнат вже тут і готовий! \n")
    print(f"Він під'єднався як {BOT.user}")
    repeat.start()
    _taskcredit.start()
    _taskdeposit.start()
    _taskquest.start()
    await BOT.tree.sync()
    print("ЗАРЕЄСТРОВАНІ ВСІ КОМАНДИ!")
    for channel in DATA["channels autosend on"]:
        await BOT.get_channel(channel).send("МАГНАТ готовий до роботи!")
def _activate():
    with open(DATA["token file"],"r") as file:
        token=file.read()
    if not token:
        print("ПОМИЛКА ТОКЕНА: Токен не існує")
    try:
        BOT.run(token)
    except discord.errors.LoginFailure as e:
        print("ПОМИЛКА ТОКЕНА: Токен неправильний")

@tasks.loop(hours=1)
async def _taskcredit():
    print("CREDIT LOOP STARTED...")
    loaded_data = {}
    try:
        with open(DATA["user data file"],"r") as f:
            loaded_data = json.load(f)
            
    except FileNotFoundError:
        pass
    except json.JSONDecodeError:
        print("ПОМИЛКА: Не вдалося декодувати JSON файл. Файл пошкоджений або порожній.")
        exit()

    data_changed = False
    for user_id_str in list(loaded_data.keys()):
        user_data=loaded_data[user_id_str]
        credit_copper=user_data["credit_мідні"]
        credit_silver=user_data["credit_срібні"]
        credit_gold=user_data["credit_золоті"]
        credit_copper=round(DATA["credit percentage"]*credit_copper,0)
        credit_silver=round(DATA["credit percentage"]*credit_silver,0)
        credit_gold=round(DATA["credit percentage"]*credit_gold,0)
        user_data["credit_золоті"]=credit_gold
        user_data["credit_срібні"]=credit_silver
        user_data["credit_мідні"]=credit_copper
        save_user_data(user_id_str,user_data)

@tasks.loop(seconds=1)
async def _taskquest():
    loaded_data = {}
    try:
        with open(DATA["user data file"],"r") as f:
            loaded_data = json.load(f)
            
    except FileNotFoundError:
        pass
    except json.JSONDecodeError:
        print("ПОМИЛКА: Не вдалося декодувати JSON файл. Файл пошкоджений або порожній.")
        exit()

    data_changed = False
    for user_id_str in list(loaded_data.keys()):
        quest_data=load_quest_data(user_id_str)
        user_data=loaded_data[user_id_str]
        if len(quest_data["commands used"])>=5 and "Використай 5 різних команд Магната" in quest_data["quests"] and "Використай 5 різних команд Магната" not in quest_data["completed quests"]:
            quest_data["completed quests"].append("Використай 5 різних команд Магната")
            quest_data["commands used"]=[]
            user_obj = await BOT.fetch_user(int(user_id_str))
            user_data["мідні"]+=100
            try:
                await user_obj.send(f"Ви пройшли квест 'Використай 5 різних команд Магната' і отримали 100 мідних!")
            except:
                pass
            save_user_data(user_id_str,user_data)
            save_quest_data(user_id_str, quest_data)
        if quest_data["gift10copper"]==True and "Подарувати комусь 10 мідних" in quest_data["quests"] and "Подарувати комусь 10 мідних" not in quest_data["completed quests"]:
            quest_data["completed quests"].append("Подарувати комусь 10 мідних")
            user_obj = await BOT.fetch_user(int(user_id_str))
            user_data["мідні"]+=100
            quest_data["gift10copper"]=False
            try:
                await user_obj.send(f"Ви пройшли квест 'Подарувати комусь 10 мідних' і отримали 100 мідних!")
            except:
                pass
            save_user_data(user_id_str,user_data)
            save_quest_data(user_id_str, quest_data)
        user_obj = await BOT.fetch_user(int(user_id_str))
        for channel in BOT.get_guild(DATA["gusid"]).text_channels:
            if quest_data["time of generation"]==0:
            	break
            hist=channel.history(after=datetime.datetime.fromtimestamp(quest_data["time of generation"]), limit=None)
            fnd=False
            gif=False
            async for msg in hist:
                auth=msg.author
                for attachment in msg.attachments:
                	if attachment.content_type == 'image/gif':
                		gif=True
                if auth.id==user_obj.id:
                    fnd=True
                    break
            if fnd==True and channel.id not in quest_data["channelsmsg"] and "Написати повідомлення у 5 чатах" in quest_data["quests"] and "Написати повідомлення у 5 чатах" not in quest_data["completed quests"]:
                quest_data["channelsmsg"].append(channel.id)
            if gif==True and quest_data["gifsent"]==False and "Надішли 1 гіфочку" in quest_data["quests"] and "Надішли 1 гіфочку" not in quest_data["completed quests"]:
                quest_data["gifsent"]=True
        save_quest_data(user_id_str, quest_data)
        if len(quest_data["channelsmsg"])>=5 and "Написати повідомлення у 5 чатах" in quest_data["quests"] and "Написати повідомлення у 5 чатах" not in quest_data["completed quests"]:
        	quest_data["completed quests"].append("Написати повідомлення у 5 чатах")
        	user_obj = await BOT.fetch_user(int(user_id_str))
        	user_data["мідні"]+=100
        	quest_data["channelsmsg"]=[]
        	try:
        	   await user_obj.send(f"Ви пройшли квест 'Написати повідомлення у 5 чатах' і отримали 100 мідних!")
        	except:
        	   pass
        	save_user_data(user_id_str,user_data)
        	save_quest_data(user_id_str, quest_data)
        if quest_data["gifsent"]==True and "Надішли 1 гіфочку" in quest_data["quests"] and "Надішли 1 гіфочку" not in quest_data["completed quests"]:
        	quest_data["completed quests"].append("Надішли 1 гіфочку")
        	user_obj = await BOT.fetch_user(int(user_id_str))
        	user_data["мідні"]+=100
        	quest_data["gifsent"]=False
        	try:
        	   await user_obj.send(f"Ви пройшли квест 'Надішли 1 гіфочку' і отримали 100 мідних!")
        	except:
        	   pass
        	save_user_data(user_id_str,user_data)
        	save_quest_data(user_id_str, quest_data)
@tasks.loop(seconds=1)
async def _taskdeposit():
    loaded_data = {}
    try:
        with open(DATA["bank data file"],"r") as f:
            loaded_data = json.load(f)
            
    except FileNotFoundError:
        pass
    except json.JSONDecodeError:
        print("ПОМИЛКА: Не вдалося декодувати JSON файл. Файл пошкоджений або порожній.")
        exit()
    loaded_sdata = {}
    try:
        with open(DATA["shop data file"],"r") as f:
            loaded_sdata = json.load(f)
            
    except FileNotFoundError:
        pass
    except json.JSONDecodeError:
        print("ПОМИЛКА: Не вдалося декодувати JSON файл. Файл пошкоджений або порожній.")
        exit()
    data_changed = False
    for user_id_str in list(loaded_data.keys()):
        if loaded_sdata[user_id_str]["bank upgrade bought"]==0:
            print("ZERO")
            return
        bank_data=loaded_data[user_id_str]
        dayspassed=math.floor((time.time()-bank_data["timeoflastdepositloop:"])/(3600*24))
        user_data=load_user_data(user_id_str)
        for x in range(0,dayspassed):
            if user_data["срібні"]<1 and user_data["мідні"]<98:
                print("MONEY")
                break
            if user_data["срібні"]>=1:
                user_data["срібні"]-=1
            else:
                user_data["мідні"]-=98
            bank_data["timeoflastdepositloop:"]=time.time()
            credit_copper=bank_data["мідні"]
            credit_silver=bank_data["срібні"]
            credit_gold=bank_data["золоті"]
            credit_copper=round(DATA["deposit percentage"]*credit_copper,0)
            credit_silver=round(DATA["deposit percentage"]*credit_silver,0)
            credit_gold=round(DATA["deposit percentage"]*credit_gold,0)
            bank_data["золоті"]=credit_gold
            bank_data["срібні"]=credit_silver
            bank_data["мідні"]=credit_copper
        save_bank_data(user_id_str,bank_data)

@tasks.loop(seconds=1)
async def repeat():
    loaded_data = {}
    try:
        with open(DATA["user data file"],"r") as f:
            loaded_data = json.load(f)
            
    except FileNotFoundError:
        pass
    except json.JSONDecodeError:
        print("ПОМИЛКА: Не вдалося декодувати JSON файл. Файл пошкоджений або порожній.")
        exit()

    data_changed = False
    for user_id_str in list(loaded_data.keys()): 
        user_data = loaded_data[user_id_str]
        level = user_data["рівень"]
        timer2 = time.time()
        timediff = timer2 - user_data["час початку роботи"]
        seconds = timediff
        wpusage = timediff * ((0.95**level) * 1.5) / 60
        
        if user_data["працює"] == 1 and user_data["пойнти роботи"] - wpusage <= 0:
            minutes = math.floor(timediff / 60)
            hours = math.floor(minutes / 60)
            days = math.floor(hours / 24)
            weeks = math.floor(days / 7)
            print("ОЙ")
            
            user_obj = await BOT.fetch_user(int(user_id_str))
            
            coppergain = timediff * (2**(level) * 70) / 3600
            user_data["час початку роботи"] = timer2
            rpgain = timediff * (1.9**level) / 3600
            user_data["мідні"] += round(coppergain,0)
            user_data["пойнти досягнень"] += round(rpgain,0)
            user_data["пойнти роботи"] = 0
            user_data["працює"] = 0
            try:
                await user_obj.send(f"Ти пішов відпочивати! Ти дуже втомився бо працював аж {round(weeks,0)} тижнів, {round(days-7*weeks,0)} днів, {round(hours-24*days,0)} годин, {round(minutes-60*hours,0)} хвилин і {round(seconds-60*minutes,0)} секунд. А також ти використав ВСІ пойнти роботи. Проте ти отримав {round(coppergain,0)} мідних монет і {round(rpgain,0)} пойнтів досягнень!")
            except:
                pass
            while True:
                nextl = 2**(user_data["рівень"]+1)
                if nextl <= user_data["пойнти досягнень"]:
                    try:
                        await user_obj.send(f"{user_obj.display_name} підвищився до рівня {level}")
                    except:
                        pass
                    user_data["рівень"] += 1
                    print(nextl)
                else:
                    break
            data_changed = True

    if data_changed:
        try:
            with open(DATA["user data file"], "w") as f:
                json.dump(loaded_data, f, indent=4)
            print("Всі дані користувачів збережено після циклу repeat.")
        except Exception as e:
            print(f"ПОМИЛКА при збереженні всіх даних у файл: {e}")

@BOT.tree.command(name="deposit", description="Депозитити гроші до банку")
@app_commands.describe(money_num="Кількість грошей", money_type="Вид грошей")
@app_commands.choices(
    money_type=[app_commands.Choice(name="Мідні", value="мідні"),
        app_commands.Choice(name="Срібні", value="срібні"),
        app_commands.Choice(name="Золоті", value="золоті"),
            ]
)
async def deposit(interaction:discord.Interaction,money_num:int,money_type:app_commands.Choice[str]):
    qd=load_quest_data(interaction.user.id)
    if "Використай 5 різних команд Магната" in qd["quests"] and "Використай 5 різних команд Магната" not in qd["completed quests"] and "deposit" not in qd["commands used"]:
        qd["commands used"].append("deposit")
        save_quest_data(interaction.user.id, qd)
    money_amount = money_num
    money_type=money_type.value
    mony=0
    user = interaction.user
    try:
        mony=int(money_amount)
    except ValueError:
        return
    
    bank_data = load_bank_data(user.id)
    user_data = load_user_data(user.id)

    if money_type in DATA["allowed money types"]:
        if user_data.get(money_type, 0) >= mony:
            bank_data[money_type] += mony
            user_data[money_type] -= mony
            save_bank_data(user.id, bank_data)
            save_user_data(user.id, user_data)
            await interaction.response.send_message(f"Ви успішно внесли {mony} {money_type} монет до банку.")
        else:
            await interaction.response.send_message(f"У вас недостатньо {money_type} монет.")
    else:
        await interaction.response.send_message("На жаль, такого типу монет немає.")
        
@BOT.tree.command(name="exchange", description="Обміняти гроші. Комісія: 2%")
@app_commands.describe(money_num="Кількість грошей", money_type_from="Вид грошей")
@app_commands.choices(
    money_type_from=[app_commands.Choice(name="Мідні", value="мідні"),
        app_commands.Choice(name="Срібні", value="срібні"),
        app_commands.Choice(name="Золоті", value="золоті"),
            ],
    money_type_to=[app_commands.Choice(name="Мідні", value="мідні"),
        app_commands.Choice(name="Срібні", value="срібні"),
        app_commands.Choice(name="Золоті", value="золоті"),
            ]
)
async def exchange(interaction:discord.Interaction,money_num:int,money_type_from:app_commands.Choice[str],money_type_to:app_commands.Choice[str]):
    qd=load_quest_data(interaction.user.id)
    if "Використай 5 різних команд Магната" in qd["quests"] and "Використай 5 різних команд Магната" not in qd["completed quests"] and "exchange" not in qd["commands used"]:
        qd["commands used"].append("exchange")
        save_quest_data(interaction.user.id, qd)
    money_amount = money_num
    money_type_to=money_type_to.value
    money_type_from=money_type_from.value
    mony=0
    user = interaction.user
    try:
        mony=int(money_amount)
    except ValueError:
        return
    user_data = load_user_data(user.id)
    if money_type_from in DATA["allowed money types"] and money_type_to in DATA["allowed money types"]:
        money_diff=DATA["exchange value"][money_type_to]-DATA["exchange value"][money_type_from]
        money_div=DATA["exchange rate"]**money_diff
        if mony>user_data[money_type_from]:
            await interaction.response.send_message("У вас немає стільки монет")
            return
        user_data[money_type_from]-=mony
        if money_diff<0:
            user_data[money_type_to]+=mony/money_div*DATA["exchange rates percentage return"]
        else:
            user_data[money_type_to]+=mony/money_div
        save_user_data(user.id,user_data)
        await interaction.response.send_message("Ви успішно здійснили обмін!")
    else:
        await interaction.response.send_message("На жаль, такого типу монет немає.")
        
@BOT.tree.command(name="bank", description="Функції банку")
async def bank(interaction:discord.Interaction):
    qd=load_quest_data(interaction.user.id)
    if "Використай 5 різних команд Магната" in qd["quests"] and "Використай 5 різних команд Магната" not in qd["completed quests"] and "bank" not in qd["commands used"]:
        qd["commands used"].append("bank")
        save_quest_data(interaction.user.id, qd)
    bank_data=load_bank_data(interaction.user.id)
    мідні=bank_data["мідні"]
    срібні=bank_data["срібні"]
    золоті=bank_data["золоті"]
    embed = discord.Embed(
        color=0xFFFF00,
        title=f"**БАНК МАГНАТА**",
        description=f'''
# Вітаємо вас у Банку Магната
**Тут Ви можете інвестувати та зберігати гроші!**
У вас в банку:
{мідні} мідних монет :rosette:
{срібні} срібних монет :cd:
і {золоті} золотих монет :dvd:
'''
        )
    embed.set_footer(text="Це потужний банк!")
    await interaction.response.send_message(embed=embed,view=Bank())

class DepositModal(discord.ui.Modal, title="Внести монети"): 
    money_type=discord.ui.TextInput(label="Вид грошей", placeholder="Введіть ваш вид грошей...",custom_id="money_type",style=discord.TextStyle.short, required=True)
    money_num=discord.ui.TextInput(label="Кількість грошей", placeholder="Введіть вашу кількість грошей...",custom_id="money_num",style=discord.TextStyle.short, required=True)
    async def on_submit(self, interaction: discord.Interaction):
        money_amount = self.money_num.value
        money_type=self.money_type.value
        mony=0
        user = interaction.user
        try:
            mony=int(money_amount)
        except ValueError:
            return
        
        bank_data = load_bank_data(user.id)
        user_data = load_user_data(user.id)

        if money_type in DATA["allowed money types"]:
            if user_data.get(money_type, 0) >= mony:
                bank_data[money_type] += mony
                user_data[money_type] -= mony
                save_bank_data(user.id, bank_data)
                save_user_data(user.id, user_data)
                await interaction.response.send_message(f"Ви успішно внесли {mony} {money_type} монет до банку.")
            else:
                await interaction.response.send_message(f"У вас недостатньо {money_type} монет.")
        else:
            await interaction.response.send_message("На жаль, такого типу монет немає.")

class RetrieveModal(discord.ui.Modal, title="Взяти монети"): 
    money_type=discord.ui.TextInput(label="Вид грошей", placeholder="Введіть ваш вид грошей...",custom_id="money_type",style=discord.TextStyle.short, required=True)
    money_num=discord.ui.TextInput(label="Кількість грошей", placeholder="Введіть вашу кількість грошей...",custom_id="money_num",style=discord.TextStyle.short, required=True)
    async def on_submit(self, interaction: discord.Interaction):
        money_amount = self.money_num.value
        money_type=self.money_type.value
        mony=0
        user = interaction.user
        try:
            mony=int(money_amount)
        except ValueError:
            return
        
        bank_data = load_bank_data(user.id)
        user_data = load_user_data(user.id)

        if money_type in DATA["allowed money types"]:
            if bank_data.get(money_type, 0) >= mony:
                bank_data[money_type] -= mony
                user_data[money_type] += mony
                save_bank_data(user.id, bank_data)
                save_user_data(user.id, user_data)
                await interaction.response.send_message(f"Ви успішно взяли {mony} {money_type} монет з банку.")
            else:
                await interaction.response.send_message(f"У банку недостатньо {money_type} монет.")
        else:
            await interaction.response.send_message("На жаль, такого типу монет немає.")

class ExchangeModal(discord.ui.Modal, title="Обміняти монети"): 
    money_type_from=discord.ui.TextInput(label="Вид грошей з", placeholder="Введіть ваш вид грошей...",custom_id="money_type_to",style=discord.TextStyle.short, required=True)
    money_type_to=discord.ui.TextInput(label="Вид грошей у", placeholder="Введіть ваш вид грошей...",custom_id="money_type_from",style=discord.TextStyle.short, required=True)
    money_num=discord.ui.TextInput(label="Кількість грошей", placeholder="Введіть вашу кількість грошей...",custom_id="money_num",style=discord.TextStyle.short, required=True)
    async def on_submit(self, interaction: discord.Interaction):
        money_amount = self.money_num.value
        money_type_to=self.money_type_to.value
        money_type_from=self.money_type_from.value
        mony=0
        user = interaction.user
        try:
            mony=int(money_amount)
        except ValueError:
            return

        user_data = load_user_data(user.id)

        if money_type_from in DATA["allowed money types"] and money_type_to in DATA["allowed money types"]:
            money_diff=DATA["exchange value"][money_type_to]-DATA["exchange value"][money_type_from]
            money_div=DATA["exchange rate"]**money_diff
            if mony>user_data[money_type_from]:
                await interaction.response.send_message("У вас немає стільки монет")
                return
            user_data[money_type_from]-=mony
            if money_diff<0:
                user_data[money_type_to]+=mony/money_div*DATA["exchange rates percentage return"]
            else:
                user_data[money_type_to]+=mony/money_div
            save_user_data(user.id,user_data)
            await interaction.response.send_message("Ви успішно здійснили обмін!")
        else:
            await interaction.response.send_message("На жаль, такого типу монет немає.")



class TakeCreditModal(discord.ui.Modal, title="Взяти у кредит..."): 
    money_type=discord.ui.TextInput(label="Вид грошей", placeholder="Введіть ваш вид грошей...",custom_id="money_type",style=discord.TextStyle.short, required=True)
    money_num=discord.ui.TextInput(label="Кількість грошей", placeholder="Введіть вашу кількість грошей...",custom_id="money_num",style=discord.TextStyle.short, required=True)
    async def on_submit(self, interaction: discord.Interaction):
        money_amount = self.money_num.value
        money_type=self.money_type.value
        mony=0
        user = interaction.user
        try:
            mony=int(money_amount)
        except ValueError:
            return
        
        user_data = load_user_data(user.id)
        mony2=0
        if money_type=="срібні":
            mony2=mony*98
        if money_type=="золоті":
            mony2=mony*98*98
        if mony2>2000*98 and user_data["мідні"]+user_data["срібні"]*98+user_data["золоті"]*98*98<500000:
            mony=2000
            money_type="срібні"
        if mony2>2000*98*98 and user_data["мідні"]+user_data["срібні"]*98+user_data["золоті"]*98*98>500000:
            mony=2000
            money_type="золоті"  
        if money_type in DATA["allowed money types"]:
            if (user_data["credit_мідні"]==0 and user_data["credit_срібні"]==0 and user_data["credit_золоті"]==0):
                user_data["credit_"+money_type] += mony
                user_data[money_type]+=mony
                save_user_data(user.id, user_data)
                await interaction.response.send_message(f"Ви успішно взяли {mony} {money_type} монет з банку на кредит.")
            else:
                await interaction.response.send_message(f"Ви ще маєте неоплачений кредит!!")
        else:
            await interaction.response.send_message("На жаль, такого типу монет немає.")

class PayCreditModal(discord.ui.Modal, title="Оплатити кредит..."): 
    money_num=discord.ui.TextInput(label="Кількість грошей", placeholder="Введіть вашу кількість грошей...",custom_id="money_num",style=discord.TextStyle.short, required=True)
    async def on_submit(self, interaction: discord.Interaction):
        money_amount = self.money_num.value
        mony=0
        user = interaction.user
        try:
            mony=int(money_amount)
        except ValueError:
            return
        flag=False
        user_data = load_user_data(user.id)
        money_type=None
        if user_data["credit_золоті"]!=0:
            money_type="золоті"
        elif user_data["credit_срібні"]!=0:
            money_type="срібні"
        elif user_data["credit_мідні"]!=0:
            money_type="мідні"
        else:
            await interaction.response.send_message("У вас немає заборгованостей!")
            flag=True

        if money_type in DATA["allowed money types"] and flag==False:
            if mony>user_data["credit_"+money_type]:
                mony=user_data["credit_"+money_type]
            if mony>user_data[money_type]:
                await interaction.response.send_message("У вас немає стільки монет")
                return
            user_data["credit_"+money_type] -= mony
            user_data[money_type]-=mony
            save_user_data(user.id, user_data)
            await interaction.response.send_message(f"Ви успішно оплатили {mony} {money_type} монет з кредиту.")
        else:
            await interaction.response.send_message("На жаль, такого типу монет немає.")

class Bank(discord.ui.View):
    def __init__(self):
        super().__init__()
    @discord.ui.button(label="Взяти гроші", style=discord.ButtonStyle.red,custom_id="retr_button_id")
    async def retrieve_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(RetrieveModal())
    
    @discord.ui.button(label="Депозит", style=discord.ButtonStyle.green, custom_id="save_button_id")
    async def deposit_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(DepositModal())

    @discord.ui.button(label="Кредит", custom_id="credit_take_button_id")
    async def credit_take_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(TakeCreditModal())
    @discord.ui.button(label="Сплатити борг", custom_id="credit_pay_button_id")
    async def credit_pay_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(PayCreditModal())
    @discord.ui.button(label="Обмін валют", custom_id="exchange_button_id")
    async def exchange_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ExchangeModal())

@BOT.tree.command(name="give", description="Дати гроші користувачу. Лише овнеру")
@app_commands.describe(cointype="Вид грошей", user="Користувач", coinamount="Кількість грошей")
@app_commands.choices(
    cointype=[app_commands.Choice(name="Мідні", value="мідні"),
        app_commands.Choice(name="Срібні", value="срібні"),
        app_commands.Choice(name="Золоті", value="золоті"),
            ],
)
async def give(interaction:discord.Interaction, coinamount:int, cointype:app_commands.Choice[str], user:discord.Member):

    if interaction.user.id != DATA["owner id"]:
        await interaction.response.send_message(f"Вибач, {ctx.author}, але, хоча Ви і маєте дуже багато грошей, цю команду може використовувати лише овнер!")
        return
    else:
        if cointype.value not in DATA["initial user data"]:
            await interaction.response.send_message("На жаль, такого типу монет немає") 
            return
        
        userdata = load_user_data(str(user.id)) 
        
        userdata[cointype.value] += coinamount
        
        save_user_data(str(user.id), data=userdata) 
        
        await interaction.response.send_message(f"Овнер бота надіслав {user.display_name} {coinamount} {cointype.value}! Вітаймо {user.display_name}!")

@BOT.tree.command(name="take", description="Забрати гроші у користувача. Лише овнеру")
@app_commands.describe(cointype="Вид грошей", user="Користувач", coinamount="Кількість грошей")
@app_commands.choices(
    cointype=[app_commands.Choice(name="Мідні", value="мідні"),
        app_commands.Choice(name="Срібні", value="срібні"),
        app_commands.Choice(name="Золоті", value="золоті"),
            ],
)
async def take(interaction:discord.Interaction, coinamount:str, cointype:app_commands.Choice[str], user:discord.Member):
    if interaction.user.id != DATA["owner id"]:
        await interaction.response.send_message(f"Вибач, {ctx.author}, але, хоча Ви і маєте дуже багато грошей, цю команду може використовувати лише овнер!")
        return
    else:
        if cointype.value not in DATA["initial user data"]:
            await interaction.response.send_message("На жаль, такого типу монет немає") 
            return
        userdata = load_user_data(str(user.id)) 
        if coinamount=="all":
            coinamount=userdata[cointype.value]
        elif userdata[cointype.value]<int(coinamount):
            coinamount=userdata[cointype.value]
        userdata[cointype.value] -= int(coinamount)
        
        save_user_data(str(user.id), data=userdata) 
        
        await interaction.response.send_message(f"Овнер бота забрав у {user.display_name} {coinamount} {cointype.value}! ")


class Shop(discord.ui.View):
    def __init__(self, bank_upgrade_bought: int):
        super().__init__()
        self.bank_upgrade_bought = bank_upgrade_bought

        if self.bank_upgrade_bought == 0:
            buy_bank_upgrade_button = discord.ui.Button(
                label="Купити Банкове Покращення",
                custom_id="buy_bank_upgrade_button_id",
            )
            buy_bank_upgrade_button.callback = self.bankupgradebought_callback
            self.add_item(buy_bank_upgrade_button)

    async def bankupgradebought_callback(self, interaction: discord.Interaction):
        save_data=load_user_data(interaction.user.id)
        shop_data=load_shop_data(interaction.user.id)
        if self.bank_upgrade_bought == 1:
            await interaction.response.send_message(f"{interaction.user.display_name} вже купив банкове покращення")
            return
        if save_data["срібні"]>=20:
            save_data["срібні"]-=20
            shop_data["bank upgrade bought"]=1
            await interaction.response.send_message(f"{interaction.user.display_name} купив банкове покращення!")
            save_shop_data(interaction.user.id,shop_data)
            save_user_data(interaction.user.id,save_data)
        else:
            await interaction.response.send_message(f"У {interaction.user.display_name} було недостатньо грошей щоб купити банкове покращення!")
@BOT.tree.command(name="shop", description="Функції магазину")
async def shop(interaction:discord.Interaction):
    qd=load_quest_data(interaction.user.id)
    if "Використай 5 різних команд Магната" in qd["quests"] and "Використай 5 різних команд Магната" not in qd["completed quests"] and "shop" not in qd["commands used"]:
        qd["commands used"].append("shop")
        save_quest_data(interaction.user.id, qd)
    shop_data=load_shop_data(interaction.user.id)
    datal=[]
    for data in shop_data:
        datal.append(data)
    embed = discord.Embed(
        color=0x0000FF,
        title=f"**МАГАЗИН МАГНАТА**",
        description=f'''
# Добрий день! Вас вітає Магазин Магната
**Тут Ви можете купувати речі за гроші!**
'''
        )
    if shop_data["bank upgrade bought"]==0:
        embed.add_field(name="Банкове покращення", value="Покращення банку. Робить так що депозит коштує 1 срібні за день але ви отримуєте +15% кожен день",inline=False)
    embed.set_footer(text="Крутий магазин! Як тут багато речей!")
    await interaction.response.send_message(embed=embed, view=Shop(shop_data["bank upgrade bought"]))

@BOT.tree.command(name="gift", description="Подарувати гроші користувачу.")
@app_commands.describe(cointype="Вид грошей", user="Користувач", coinamount="Кількість грошей")
@app_commands.choices(
    cointype=[app_commands.Choice(name="Мідні", value="мідні"),
        app_commands.Choice(name="Срібні", value="срібні"),
        app_commands.Choice(name="Золоті", value="золоті"),
            ],
)
async def gift(interaction:discord.Interaction,coinamount:int,cointype:app_commands.Choice[str],user:discord.Member):
    qd=load_quest_data(interaction.user.id)
    if "Використай 5 різних команд Магната" in qd["quests"] and "Використай 5 різних команд Магната" not in qd["completed quests"] and "gift" not in qd["commands used"]:
        qd["commands used"].append("gift")
        save_quest_data(interaction.user.id, qd)
    qd=load_quest_data(interaction.user.id)
    if "Подарувати комусь 10 мідних" in qd["quests"] and "Подарувати комусь 10 мідних" not in qd["completed quests"] and qd["gift10copper"]==False and cointype.value=="мідні" and str(coinamount)=="10":
        qd["gift10copper"]=True
        print("WELP")
        save_quest_data(interaction.user.id, qd)
    typem=cointype.value
    data=load_user_data(interaction.user.id)
    data2=load_user_data(user.id)
    if typem not in DATA["allowed money types"]:
        await interaction.response.send_message(f"Такого виду грошей, як {typem.value} не існує!")
        return
    if coinamount>data[typem]:
        await interaction.response.send_message(f"У вас немає {coinamount} {typem.value} у гаманці!")
        return
    data[typem]-=coinamount
    data2[typem]+=coinamount
    save_user_data(interaction.user.id,data)
    save_user_data(user.id,data2)
    await interaction.response.send_message(f"Користувач {interaction.user.display_name} успішно надіслав {user.display_name} {coinamount} {typem}.")
    
@BOT.tree.command(name="steal", description="Вкрасти всі гроші у користувача.")
@app_commands.describe(user="Користувач")
async def steal(interaction:discord.Interaction,user:discord.Member):
    qd=load_quest_data(interaction.user.id)
    if "Використай 5 різних команд Магната" in qd["quests"] and "Використай 5 різних команд Магната" not in qd["completed quests"] and "steal" not in qd["commands used"]:
        qd["commands used"].append("steal")
        save_quest_data(interaction.user.id, qd)
    data=load_user_data(interaction.user.id)
    data2=load_user_data(user.id)
    chance=0
    if data2["мідні"]>100 or data2["срібні"]!=0 or data2["золоті"]!=0:
        chance=20
    else:
        chance=5
    randomi=random.randint(1,chance)
    print(randomi)
    if randomi==2:
        golden=data2["золоті"]
        silver=data2["срібні"]
        copper=data2["мідні"]
        data2["золоті"]=0
        data2["срібні"]=0
        data2["мідні"]=0
        data["золоті"]+=golden
        data["срібні"]+=golden
        data["мідні"]+=copper
        await interaction.response.send_message(f"Користувач {interaction.user.display_name} вкрав всі гроші у {user.display_name}!")
        save_user_data(interaction.user.id,data)
        save_user_data(user.id,data2)
    else:
        midni=0
        if data["срібні"]>=20:
        	data["срібні"]-=20
        	midni=20
        	type="срібні"
        elif data["мідні"]>=1960:
        	data["мідні"]-=1960
        	midni=1960
        	type="мідні"
        else:
        	data["мідні"]=0
        	data["срібні"]=0
        	type=""
        	midni="всі свої гроші"
        data["працює"]=0
        data["час початку роботи"]=time.time()
        
        await interaction.response.send_message(f"Користувач {interaction.user.display_name} намагався вкрасти всі гроші у {user.display_name}, але його затримала поліція і йому довелося оплатити штраф: {midni} {type}!")
        save_user_data(interaction.user.id,data)
         
@BOT.tree.command(name="slots", description="Крутити колесо фортуни")
@app_commands.describe(cointype="Вид грошей", coinamount="Кількість грошей")
@app_commands.choices(
    cointype=[app_commands.Choice(name="Мідні", value="мідні"),
        app_commands.Choice(name="Срібні", value="срібні"),
        app_commands.Choice(name="Золоті", value="золоті"),
            ],
)
async def slots(interaction:discord.Interaction,coinamount:str,cointype:app_commands.Choice[str]):
    qd=load_quest_data(interaction.user.id)
    if "Використай 5 різних команд Магната" in qd["quests"] and "Використай 5 різних команд Магната" not in qd["completed quests"] and "slots" not in qd["commands used"]:
        qd["commands used"].append("slots")
        save_quest_data(interaction.user.id, qd)
    amount=coinamount
    typem=cointype.value
    l=[]
    wl=[]
    data=load_user_data(interaction.user.id)
    resu=random.randint(1,201)
    res=resu/100
    if res<1:
        color=0xFF0000
        footer="Яка невдача..."
    else:
        color=0x00FF00
        footer="КРУТЕ КАЗИНО!"
    if amount=="all":
        amount=data[typem]
    else:
        if int(amount)>=data[typem]:
            amount=data[typem]
    prev=data[typem]
    data[typem]-=int(amount)
    data[typem]+=int(amount)*res
    embed = discord.Embed(
        color=color,
        title=f"**КАЗИНО**",
        description=f'''
** Ваш баланс був:
{round(prev,2)} {typem}
**
** І ви виграли множник...
{res}x!
**
** Ваш баланс тепер...
{round(data[typem],2)} {typem}
**
''')
    embed.set_footer(text=footer)
    await interaction.response.send_message(embed=embed)
    save_user_data(interaction.user.id, data)
    

@BOT.tree.command(name="balance", description="Переглянути свій баланс")
async def balance(interaction:discord.Interaction):
    qd=load_quest_data(interaction.user.id)
    if "Використай 5 різних команд Магната" in qd["quests"] and "Використай 5 різних команд Магната" not in qd["completed quests"] and "balance" not in qd["commands used"]:
        qd["commands used"].append("balance")
        save_quest_data(interaction.user.id, qd)
    data = load_user_data(str(interaction.user.id))
    
    мідні = round(data["мідні"],0)
    срібні = round(data["срібні"],0)
    золоті = round(data["золоті"],0)
    credit_copper = round(data["credit_мідні"],0)
    credit_silver = round(data["credit_срібні"],0)
    credit_gold = round(data["credit_золоті"],0)
    if credit_copper!=0 or credit_silver!=0 or credit_gold!=0:
        cpr='''
** :money_with_wings: Кредит :money_with_wings:
Ви також маєте кредит
'''
    else:
        cpr=''''''
    if credit_copper!=0:
        cpr+=("Мідні монети: "+str(credit_copper)+'''
''')
    if credit_silver!=0:
        cpr+=("Срібні монети: "+str(credit_silver)+'''
''')
    if credit_gold!=0:
        cpr+=("Золоті монети: "+str(credit_gold)+'''
''')
    cpr+='''**'''
    рп = round(data["пойнти роботи"],0)
    дп = round(data["пойнти досягнень"],0)
    рівень = data["рівень"]
    working = data["працює"]
    timet = data["час початку роботи"]
    timer2 = time.time()
    timediff = timer2 - data["час початку роботи"]
    seconds = timediff
    minutes = math.floor(timediff / 60)
    hours = math.floor(minutes / 60)
    days = math.floor(hours / 24)
    weeks = math.floor(days / 7)
    
    if working == 0:
        рп_реген = (2**рівень) * ((time.time() - timet) / 60)
        рп += рп_реген
        реген = f"регенеруєте {2**рівень} пойнтів роботи за хвилину"
        статус = "відпочиваєте. :zzz:"
        праця = ""
    else:
        рп_використання = ((0.95**рівень) * 1.5) / 60 * (time.time() - timet)
        рп -= рп_використання
        реген = f"використовуєте {round((0.95**рівень)*1.5,2)} пойнтів роботи за хвилину"
        статус = "працюєте! :office_worker:"
        праця = f"Ви вже працюєте: {round(weeks,2)} тижнів, {round(days-7*weeks,2)} днів, {round(hours-24*days,2)} годин, {round(minutes-60*hours,2)} хвилин і {round(seconds-60*minutes,2)} секунд."
    if рп>100:
        рп=100
    
    embed = discord.Embed(
        color=0xFFFF00,
        title=f"**БАЛАНС КОРИСТУВАЧА {interaction.user.display_name}**",
        description=f'''
# Ваш баланс:
** :moneybag:  Гаманець :moneybag:
У вашому гаманці
{round(мідні,2)} мідних монет  :rosette: ,
{round(срібні,2)} срібних монет :cd: ,
і {round(золоті,2)} золотих монет. :dvd: **

** ⚡ Робота ⚡
У вас є
{round(рп,2)} пойнтів роботи :fish_cake: ,
{round(дп,2)} пойнтів досягнень :full_moon: ,
ваш рівень {round(рівень,2)}.
Ви {реген}.
{праця}**{cpr}
** :trophy: Статус :trophy:
Ви {статус}
**

Непогано!
'''
    )
    embed.set_footer(text="Диви, як багато грошей ти маєш!")
    
    if interaction.user.avatar:
        embed.set_thumbnail(url=interaction.user.avatar.url)
    else:
        pass 
        
    await interaction.response.send_message(embed=embed)

@BOT.tree.command(name="work", description="Почати працювати")
async def work(interaction:discord.Interaction):
    qd=load_quest_data(interaction.user.id)
    if "Використай 5 різних команд Магната" in qd["quests"] and "Використай 5 різних команд Магната" not in qd["completed quests"] and "work" not in qd["commands used"]:
        qd["commands used"].append("work")
        save_quest_data(interaction.user.id, qd)
    data=load_user_data(str(interaction.user.id))
    level=data["рівень"]
    working=data["працює"]
    if working==1:
        await interaction.response.send_message(f"Ви вже працюєте!")
    if working==0:
        wpgain = (2**data["рівень"]) * ((time.time() - data["час початку роботи"]) / 60)
        data["пойнти роботи"]+=round(wpgain,0)
        if data["пойнти роботи"]>100:
            data["пойнти роботи"]=100
        data["час початку роботи"]=time.time()
        data["працює"]=1
        save_user_data(str(interaction.user.id), data)
        await interaction.response.send_message(f"{interaction.user.display_name} пішов працювати! Він використовує {round((0.95**level)*1.5,2)} пойнтів роботи за хвилину і отримує {(2**level)*70} мідних монет і {round(1.9**level,2)} пойнтів досягнень за годину!")

@BOT.tree.command(name="stopwork", description="Припинити працювати")
async def stopwork(interaction:discord.Interaction):
    qd=load_quest_data(interaction.user.id)
    if "Використай 5 різних команд Магната" in qd["quests"] and "Використай 5 різних команд Магната" not in qd["completed quests"] and "stopwork" not in qd["commands used"]:
        qd["commands used"].append("stopwork")
        save_quest_data(interaction.user.id, qd)
    data=load_user_data(str(interaction.user.id))
    level=data["рівень"]
    working=data["працює"]
    if working==0:
        await interaction.response.send_message(f"Ви вже відпочиваєте!")
    if working==1:
        timer2=time.time()
        timediff=timer2-data["час початку роботи"]
        data["час початку роботи"]=timer2
        data["працює"]=0
        seconds=timediff
        minutes=math.floor(timediff/60)
        hours=math.floor(minutes/60)
        days=math.floor(hours/24)
        weeks=math.floor(days/7)
        coppergain=timediff*(2**(level)*70)/3600
        rpgain=timediff*(1.9**level)/3600
        wpusage=timediff*((0.95**level)*1.5)/60
        data["мідні"]+=round(coppergain,0)
        data["пойнти досягнень"]+=round(rpgain,0)
        data["пойнти роботи"]-=round(wpusage,0)
        await interaction.response.send_message(f"{interaction.user.display_name} пішов відпочивати! Він дуже втомився бо працював аж {round(weeks,0)} тижнів, {round(days-7*weeks,0)} днів, {round(hours-24*days,0)} годин, {round(minutes-60*hours,0)} хвилин і {round(seconds-60*minutes,0)} секунд. А також він використав {round(wpusage,0)} пойнтів роботи. Проте він отримав {round(coppergain,0)} мідних монет і {round(rpgain,0)} пойнтів досягнень!")
        while True:
            nextl = 2**(data["рівень"]+1)
            if nextl <= data["пойнти досягнень"]:
                await interaction.user.send(f"{interaction.user.display_name} підвищився до рівня {level}")
                data["рівень"] += 1
            else:
                break
        
        save_user_data(str(interaction.user.id),data)


def load_user_data(user_id): 
    user_id_str = str(user_id)
    all_data = {}
    
    try:
        with open(DATA["user data file"],"r") as f:
            all_data = json.load(f)
    except FileNotFoundError:
        pass
    except json.JSONDecodeError:
        print("ПОМИЛКА: Не вдалося декодувати JSON файл. Файл пошкоджений або порожній. Починаємо з пустих даних.")
        
    if user_id_str not in all_data:
        all_data[user_id_str] = DATA["initial user data"].copy()
        print(f"Була ініціалізована дата для нового користувача {user_id_str} в пам'яті.")
        
    return all_data[user_id_str]

def save_user_data(user_id, data): 
    user_id_str = str(user_id)
    total_data = {}
    
    try:
        with open(DATA["user data file"],"r") as f:
            total_data = json.load(f)
    except FileNotFoundError:
        pass
    except json.JSONDecodeError:
        print("ПОМИЛКА: Не вдалося декодувати JSON файл під час збереження. Файл пошкоджений. Створюємо новий файл.")
        
    total_data[user_id_str] = data
    
    try:
        with open(DATA["user data file"],"w") as f:
            json.dump(total_data, f, indent=4)
            
    except Exception as e:
        print(f"ПОМИЛКА при збереженні файлу '{DATA['user data file']}': {e}")

def load_bank_data(user_id): 
    user_id_str = str(user_id)
    all_data = {}
    
    try:
        with open(DATA["bank data file"],"r") as f:
            all_data = json.load(f)
    except FileNotFoundError:
        pass
    except json.JSONDecodeError:
        print("ПОМИЛКА: Не вдалося декодувати JSON файл. Файл пошкоджений або порожній. Починаємо з пустих даних.")
        
    if user_id_str not in all_data:
        all_data[user_id_str] = DATA["initial bank data"].copy()
            
    return all_data[user_id_str]

def save_bank_data(user_id, data): 
    user_id_str = str(user_id)
    total_data = {}
    
    try:
        with open(DATA["bank data file"],"r") as f:
            total_data = json.load(f)
    except FileNotFoundError:
        pass
    except json.JSONDecodeError:
        print("ПОМИЛКА: Не вдалося декодувати JSON файл під час збереження. Файл пошкоджений. Створюємо новий файл.")
        
    total_data[user_id_str] = data
    
    try:
        with open(DATA["bank data file"],"w") as f:
            json.dump(total_data, f, indent=4)
            
    except Exception as e:
        print(f"ПОМИЛКА при збереженні файлу '{DATA['bank data file']}': {e}")
def load_shop_data(user_id): 
    user_id_str = str(user_id)
    all_data = {}
    
    try:
        with open(DATA["shop data file"],"r") as f:
            all_data = json.load(f)
    except FileNotFoundError:
        pass
    except json.JSONDecodeError:
        print("ПОМИЛКА: Не вдалося декодувати JSON файл. Файл пошкоджений або порожній. Починаємо з пустих даних.")
        
    if user_id_str not in all_data:
        all_data[user_id_str] = DATA["initial quest data"].copy()
            
    return all_data[user_id_str]

def save_shop_data(user_id, data): 
    user_id_str = str(user_id)
    total_data = {}
    
    try:
        with open(DATA["shop data file"],"r") as f:
            total_data = json.load(f)
    except FileNotFoundError:
        pass
    except json.JSONDecodeError:
        print("ПОМИЛКА: Не вдалося декодувати JSON файл під час збереження. Файл пошкоджений. Створюємо новий файл.")
        
    total_data[user_id_str] = data
    
    try:
        with open(DATA["shop data file"],"w") as f:
            json.dump(total_data, f, indent=4)
        print(f"Дані користувача {user_id_str} збережено.")
            
    except Exception as e:
        print(f"ПОМИЛКА при збереженні файлу '{DATA['shop data file']}': {e}")

def load_quest_data(user_id): 
    user_id_str = str(user_id)
    all_data = {}
    
    try:
        with open(DATA["quest data file"],"r") as f:
            all_data = json.load(f)
    except FileNotFoundError:
        pass
    except json.JSONDecodeError:
        print("ПОМИЛКА: Не вдалося декодувати JSON файл. Файл пошкоджений або порожній. Починаємо з пустих даних.")
        
    if user_id_str not in all_data:
        all_data[user_id_str] = DATA["initial quest data"].copy()
            
    return all_data[user_id_str]

def save_quest_data(user_id, data): 
    user_id_str = str(user_id)
    total_data = {}
    
    try:
        with open(DATA["quest data file"],"r") as f:
            total_data = json.load(f)
    except FileNotFoundError:
        pass
    except json.JSONDecodeError:
        print("ПОМИЛКА: Не вдалося декодувати JSON файл під час збереження. Файл пошкоджений. Створюємо новий файл.")
        
    total_data[user_id_str] = data
    
    try:
        with open(DATA["quest data file"],"w") as f:
            json.dump(total_data, f, indent=4)
        print(f"Дані користувача {user_id_str} збережено.")
            
    except Exception as e:
        print(f"ПОМИЛКА при збереженні файлу '{DATA['quest data file']}': {e}")

@BOT.tree.command(name="backup", description="бекапить канали на сервері") 
async def backup(interaction: discord.Interaction):
    data = []
    server_id = interaction.guild.id
    for channel in interaction.guild.channels:
        try:
            data.append([channel.name, channel.type, channel.category.name])
            print(f"Канал: {channel.name}, Тип: {channel.type}, Категорія: {channel.category.name}")
        except:
            data.append([channel.name, channel.type, None])
            print(f"Канал: {channel.name}, Тип: {channel.type}, Категорія: None")
    
    print(f"Зібрано {len(data)} каналів для backup")
    
    server_id_str = str(server_id)
    total_data = {}
    
    try:
        with open(DATA["channel data file"], "r") as f:
            total_data = json.load(f)
    except FileNotFoundError:
        pass
    except json.JSONDecodeError:
        print("ПОМИЛКА: Не вдалося декодувати JSON файл під час збереження. Файл пошкоджений. Створюємо новий файл.")
        
    total_data[server_id_str] = data
    
    try:
        with open(DATA["channel data file"], "w") as f:
            json.dump(total_data, f, indent=4)
        print(f"Дані користувача {server_id_str} збережено. Всього каналів: {len(data)}")
        await interaction.response.send_message(f"Backup успішний! Збережено {len(data)} каналів")
            
    except Exception as e:
        print(f"ПОМИЛКА при збереженні файлу '{DATA['channel data file']}': {e}")
        await interaction.response.send_message(f"Помилка при збереженні: {e}")
        return
    
    # Removed the success message since we already responded above

@BOT.tree.command(name="refresh", description="рефрешить канали на сервері") 
async def refresh(interaction: discord.Interaction):
    if interaction.user.id != DATA["owner id"] and interaction.user.id != interaction.guild.owner.id:
        await interaction.response.send_message("Ви не овнер бота чи овнер сервера")
        return

    guild = interaction.guild
    await interaction.response.defer()

    delete_channels = [asyncio.create_task(ch.delete()) for ch in guild.channels]
    await asyncio.gather(*delete_channels, return_exceptions=True)
    
    # Create a temporary channel to send response
    temp_channel = await guild.create_text_channel("general")
    
    server_id = interaction.guild.id
    server_id_str = str(server_id)
    all_data = {}
    
    try:
        with open(DATA["channel data file"], "r") as f:
            all_data = json.load(f)
    except FileNotFoundError:
        pass
    except json.JSONDecodeError:
        print("ПОМИЛКА: Не вдалося декодувати JSON файл. Файл пошкоджений або порожній. Починаємо з пустих даних.")
        
    if server_id_str not in all_data:
        all_data[server_id_str] = DATA["initial channel data"].copy()
            
    data = all_data[server_id_str]
    
    # First create all categories
    categories_created = 0
    for channel in data:
        if len(channel) >= 2:
            await temp_channel.send(f"Перевірка...")
            if channel[1][0] == "category":
                await interaction.guild.create_category(name=channel[0])
                categories_created += 1
    
    await temp_channel.send(f"Створено {categories_created} категорій")
    
    # Then create other channels and assign them to categories
    channels_created = 0
    for channel in data:
        if len(channel) >= 2:
            channel_type = channel[1][0]
            category = None
            if len(channel) >= 3 and channel[2]:
                category = discord.utils.get(interaction.guild.categories, name=channel[2])
            
            if channel_type == "text":
                await guild.create_text_channel(name=channel[0], category=category)
                channels_created += 1
            elif channel_type == "voice":
                await guild.create_voice_channel(name=channel[0], category=category)
                channels_created += 1
            elif channel_type == "news":
                await guild.create_text_channel(name=channel[0], category=category, news=True)
                channels_created += 1
            elif channel_type == "forum":
                await guild.create_forum(name=channel[0], category=category)
                channels_created += 1
            elif channel_type == "stage_voice":
                await guild.create_stage_channel(name=channel[0], category=category)
                channels_created += 1
    
    await temp_channel.send(f"Створено {channels_created} каналів")
    
    await temp_channel.send("Канали відновлено!")
_activate()
