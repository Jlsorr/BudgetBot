
# Budget Management Discord Bot

This project is a Discord bot developed in Python, designed to help users manage their personal finances directly on a Discord server. The bot allows users to track their income, expenses, and manage recurring subscriptions. It can also be deployed on Railway for continuous and autonomous use.

## Features

- **Income Tracking**: Easily add and track your income.
- **Expense Tracking**: Record your expenses and view the totals.
- **Recurring Subscriptions Management**: Add monthly, weekly, or yearly subscriptions that will be automatically deducted from the budget.
- **Financial Summary Display**: View your balance, total income, and total expenses at any time.

## Prerequisites

Before starting, make sure you have installed:

- [Python 3.8+](https://www.python.org/downloads/)
- [A Discord account](https://discord.com) and a server to host the bot
- [A Discord bot](https://discord.com/developers/applications) (create an application and a bot via the Discord developers portal)

## Local Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/BudgetBot.git
cd BudgetBot
```

### 2. Create a virtual environment (optional but recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create a `.env` file

At the root of the project, create a `.env` file containing the following information:

```bash
DISCORD_TOKEN=your_discord_token_here
CHANNEL_ID=your_channel_id_here
```

- **DISCORD_TOKEN**: Your Discord bot token (available on the Discord developer portal).
- **CHANNEL_ID**: The ID of the Discord channel where the bot interacts. You can get this ID by enabling Developer Mode in Discord and right-clicking on the channel to copy its ID.

### 5. Run the bot locally

```bash
python budget_bot.py
```

The bot should now be online on your Discord server, and you can start using the available commands.

## Deploying on Railway

### 1. Create a Railway account

If you haven't already, [create an account on Railway](https://railway.app) and create a new project.

### 2. Connect the GitHub repository

After creating a project on Railway, connect your GitHub repository so Railway can automatically deploy the bot.

### 3. Add environment variables on Railway

In the Railway project settings, add the following environment variables:

- `DISCORD_TOKEN`: Your Discord bot token.
- `CHANNEL_ID`: The ID of the Discord channel where the bot interacts.

### 4. Deploy

Railway will automatically deploy the bot every time you push updates to the GitHub repository.

## Bot Commands

### `!ajouter_revenu <amount> <description>`
Adds an income with a specified amount and description.

Example:
```
!ajouter_revenu 1500 Salary
```

### `!ajouter_depense <amount> <description>`
Adds an expense with a specified amount and description.

Example:
```
!ajouter_depense 50 Groceries
```

### `!bilan`
Displays the financial summary (total income, total expenses, and balance).

Example:
```
!bilan
```

### `!ajouter_abonnement <amount> <frequency> <description>`
Adds a recurring subscription with a frequency (monthly, weekly, yearly).

Example:
```
!ajouter_abonnement 9.99 monthly Netflix
```

### `!voir_abonnements`
Displays all active recurring subscriptions.

Example:
```
!voir_abonnements
```

## Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request if you'd like to add features or fix bugs.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
