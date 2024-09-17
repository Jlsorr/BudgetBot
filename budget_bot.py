import discord
from discord.ext import commands, tasks
import sqlite3
import datetime
import os
from dotenv import load_dotenv

# Charger les variables d'environnement à partir du fichier .env
load_dotenv()

# Récupérer le token du bot et l'ID du channel depuis le .env
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))

# Initialisation du bot avec les intents nécessaires
intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Connexion à la base de données SQLite
conn = sqlite3.connect('budget.db')
cursor = conn.cursor()

# Création des tables si elles n'existent pas encore
cursor.execute('''CREATE TABLE IF NOT EXISTS budget
                 (id INTEGER PRIMARY KEY, user_id TEXT, type TEXT, amount REAL, description TEXT, date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS abonnements
                 (id INTEGER PRIMARY KEY, user_id TEXT, amount REAL, description TEXT, frequency TEXT, start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
conn.commit()

### FONCTIONS DE BASE ###
@bot.event
async def on_ready():
    print(f"Bot connecté en tant que {bot.user}")
    check_abonnements.start()  # Lancement de la tâche automatique pour les abonnements

    # Envoie un message au channel spécifié lors du démarrage du bot
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send("Le bot est en ligne et prêt à gérer vos budgets !")


### COMMANDES ###

# Commande pour ajouter un revenu
@bot.command(name='ajouter_revenu')
async def ajouter_revenu(ctx, montant: float, *, description: str):
    user_id = str(ctx.author.id)
    cursor.execute("INSERT INTO budget (user_id, type, amount, description) VALUES (?, ?, ?, ?)",
                   (user_id, 'revenu', montant, description))
    conn.commit()

    # Création de l'embed
    embed = discord.Embed(title="Revenu ajouté", color=discord.Color.green())
    embed.add_field(name="Montant", value=f"{montant} €", inline=False)
    embed.add_field(name="Description", value=description, inline=False)
    await ctx.send(embed=embed)


# Commande pour ajouter une dépense
@bot.command(name='ajouter_depense')
async def ajouter_depense(ctx, montant: float, *, description: str):
    user_id = str(ctx.author.id)
    cursor.execute("INSERT INTO budget (user_id, type, amount, description) VALUES (?, ?, ?, ?)",
                   (user_id, 'depense', montant, description))
    conn.commit()

    # Création de l'embed
    embed = discord.Embed(title="Dépense ajoutée", color=discord.Color.red())
    embed.add_field(name="Montant", value=f"{montant} €", inline=False)
    embed.add_field(name="Description", value=description, inline=False)
    await ctx.send(embed=embed)


# Commande pour voir le bilan financier
@bot.command(name='bilan')
async def bilan(ctx):
    user_id = str(ctx.author.id)
    cursor.execute("SELECT type, SUM(amount) FROM budget WHERE user_id = ? GROUP BY type", (user_id,))
    results = cursor.fetchall()

    total_revenus = sum([r[1] for r in results if r[0] == 'revenu'])
    total_depenses = sum([r[1] for r in results if r[0] == 'depense'])
    bilan = total_revenus - total_depenses

    # Création de l'embed
    embed = discord.Embed(title="Bilan Financier", color=discord.Color.blue())
    embed.add_field(name="Revenus totaux", value=f"{total_revenus} €", inline=False)
    embed.add_field(name="Dépenses totales", value=f"{total_depenses} €", inline=False)
    embed.add_field(name="Solde", value=f"{bilan} €", inline=False)
    await ctx.send(embed=embed)


# Commande pour ajouter un abonnement récurrent
@bot.command(name='ajouter_abonnement')
async def ajouter_abonnement(ctx, montant: float, frequency: str, *, description: str):
    user_id = str(ctx.author.id)
    
    # Vérification si la fréquence est valide
    if frequency not in ['mensuel', 'hebdomadaire', 'annuel']:
        await ctx.send("Fréquence invalide. Choisissez parmi 'mensuel', 'hebdomadaire', ou 'annuel'.")
        return
    
    cursor.execute("INSERT INTO abonnements (user_id, amount, description, frequency) VALUES (?, ?, ?, ?)",
                   (user_id, montant, description, frequency))
    conn.commit()

    # Création de l'embed
    embed = discord.Embed(title="Abonnement ajouté", color=discord.Color.purple())
    embed.add_field(name="Montant", value=f"{montant} €", inline=False)
    embed.add_field(name="Description", value=description, inline=False)
    embed.add_field(name="Fréquence", value=frequency.capitalize(), inline=False)
    await ctx.send(embed=embed)


# Commande pour voir les abonnements actifs
@bot.command(name='voir_abonnements')
async def voir_abonnements(ctx):
    user_id = str(ctx.author.id)
    cursor.execute("SELECT amount, description, frequency FROM abonnements WHERE user_id = ?", (user_id,))
    abonnements = cursor.fetchall()

    if not abonnements:
        await ctx.send("Vous n'avez pas d'abonnements récurrents.")
    else:
        embed = discord.Embed(title="Abonnements récurrents", color=discord.Color.orange())
        for abonnement in abonnements:
            amount, description, frequency = abonnement
            embed.add_field(name=f"{description}", value=f"{amount} € - {frequency.capitalize()}", inline=False)
        await ctx.send(embed=embed)


### GESTION DES ABONNEMENTS RÉCURRENTS ###

# Fonction pour appliquer les abonnements récurrents
def appliquer_abonnements():
    aujourdhui = datetime.datetime.now().date()
    cursor.execute("SELECT id, user_id, amount, description, frequency, start_date FROM abonnements")
    abonnements = cursor.fetchall()

    for abonnement in abonnements:
        abonnement_id, user_id, amount, description, frequency, start_date = abonnement
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S").date()

        if frequency == 'mensuel' and (aujourdhui - start_date).days >= 30:
            cursor.execute("INSERT INTO budget (user_id, type, amount, description) VALUES (?, ?, ?, ?)",
                           (user_id, 'depense', amount, description))
            new_start_date = aujourdhui + datetime.timedelta(days=30)
            cursor.execute("UPDATE abonnements SET start_date = ? WHERE id = ?", (new_start_date, abonnement_id))

        elif frequency == 'hebdomadaire' and (aujourdhui - start_date).days >= 7:
            cursor.execute("INSERT INTO budget (user_id, type, amount, description) VALUES (?, ?, ?, ?)",
                           (user_id, 'depense', amount, description))
            new_start_date = aujourdhui + datetime.timedelta(days=7)
            cursor.execute("UPDATE abonnements SET start_date = ? WHERE id = ?", (new_start_date, abonnement_id))

        elif frequency == 'annuel' and (aujourdhui - start_date).days >= 365:
            cursor.execute("INSERT INTO budget (user_id, type, amount, description) VALUES (?, ?, ?, ?)",
                           (user_id, 'depense', amount, description))
            new_start_date = aujourdhui + datetime.timedelta(days=365)
            cursor.execute("UPDATE abonnements SET start_date = ? WHERE id = ?", (new_start_date, abonnement_id))

    conn.commit()


# Tâche répétée pour vérifier les abonnements récurrents chaque jour
@tasks.loop(hours=24)
async def check_abonnements():
    appliquer_abonnements()

### Lancer le bot ###
bot.run(TOKEN)
