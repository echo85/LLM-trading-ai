import ollama
from pydantic import BaseModel, Field
from typing import Literal

from hyperliquid.info import Info
from hyperliquid.utils import constants
from coingecko_trending import coingecko_trending
from coingecko_coin import *
from newsapi import *

from dotenv import load_dotenv
import os
# Load the environment variables from .env file
load_dotenv()

info = Info(constants.TESTNET_API_URL, skip_ws=True)

# This is an example address, when you start trading this should be replaced with your address
user_state = info.user_state("0x7617C64A8C4DAf8D80fe4d6825E5a3048Fb4b20b") 

# if you're getting an error or no user_state here make sure your environment variables are set correctly and that all requirements are installed
identity_map = {
    "risk_level": "Moderate risk, willing to risk some money for the right investments but not chasing every new opportunity.",
    "token_preferences": "Likes ETH more than BTC, doesnt like SOL",
    "mission_statement": "Accumulate as much top coins as possible given the available funds.",
}

# the amount available to withdraw is approximately equal to the balance available to trade
# there is room for a better way to track this
available_balance = user_state.get('withdrawable') # denominated in USD

coin_list = fetch_coin_list()
# We're also going to take a look at the current positions that are open, and format them for use with our models
positions = user_state.get('assetPositions')
positions_for_llm = ''
recent_sentiments = ''
coingecko_trends = coingecko_trending()
if positions:
    
    for position in positions:
        position = position.get('position')
        position_for_llm = f"Current {position.get('coin')} position: size {position.get('szi')} {position.get('coin')}, value of {position.get('positionValue')} usd, leverage {position.get('leverage').get('value')}, and unrealizedPnl {position.get('unrealizedPnl')} usd. The max leverage for this position is {position.get('maxLeverage')}.\n"
        positions_for_llm += position_for_llm
        recent_sentiments += coingecko_sentiment(position.get('coin'), coin_list)

chat_summary = "Bob is happy with the Ethereum roadmap and has been hearing more people talk about it.\n"

chat_and_data_summary = chat_summary

top_headlines = news_topheadlines()

system_prompt = (
    "# Instructions:\n"
    "Act as a helpful cryptocurrency assistant helping users manage their trading portfolio.\n"
    "They understand it is inherently risky to trade cryptocurrency, and they want to make sure they are making informed decisions.\n"
    "You will be given a `available_balance` representing the user's total available value to make new trades with, a list of available assets, a risk level, and a list of their current positions.\n"
    "Think carefully through all scenarios and please provide your best guidance and reasoning for this decision.\n"
    "The USD value of each individual trade should not exceed the `available_balance`, and trades should be sized to allow for sufficient 'available_balance' to handle market volatility or unforeseen events.\n"
    "Do not suggest or provide reasoning for order where your suggested order size (for both new and addition to existing positions) is less than 10 USD.\n"
    "Ensure that there is enough margin available to support the trade size and leverage. Adjust leverage or order size accordingly, if required, while remaining within the 10 USD per order limit. If not possible, then do not suggest a new position and instead recommend to the user to deposit additional funds.\n"
    "# Available Options:\n"
    "- create a new position which should be tracked in the list ```positions_to_open```\n"
    "- modify or close an existing position which should be tracked in the list ```positions_to_modify```\n"
    "- maintain an existing position without changes which should be tracked in the list ```positions_to_maintain```\n"
    "# Fields for each option:\n"
    "- asset: the asset to trade\n"
    "\t- example: ETH\n"
    "- direction: the direction to trade\n"
    "\t- example: long, short\n"
    "- size: the size of the trade denominated in USD. It has to be bigger than 10 and should not use up the entire 'available_balance', leaving enough funds available for risk management and flexibility.\n"
    "\t- the trade size should be greater than 10 USD even when modifying an existing position.\n"
    "\t- example: 90 # If the 'available_balance' is 90, use at most 80 for the sum of all trades, keeping 10 as a buffer. Ensure trades are sized to allow for sufficient 'available_balance' to handle market volatility or unforeseen events.\n"
    "- leverage: the leverage to use for the trade\n"
    "\t- example: 10\n"
    "- reasoning: the reasoning for the decision\n"
    "\t- example: ['People value Alice's opinion and she really likes ETH here.', 'ETH price is low right now, volume is high compared to yesterday.', 'ETH is a solid long term investment.']\n"
)

user_message = (
    "# Instructions:\n"
    "Here are some details about me, can you help me make decisions about my trading portfolio?\n"
    "# Personality\n"
    f"{identity_map.get('chat_personality')}\n"
    "# Risk Level\n"
    f"{identity_map.get('risk_level')}\n"
    "This represents the total $USD value of the account, including positions, margin, and available funds.\n"
    "# Available Balance\n"
    f"{available_balance}\n"
    "Portions of this 'available_balance' can be used for placing new orders or modifying existing positions.\n"
    "Always leave a fraction of total 'available_balance' as a safety buffer for unforeseen volatility.\n"
    "The 'available_balance' is shared by all positions, so it is important to keep track of the available value and adjust your position sizes accordingly.\n"
    "# Open Positions\n"
    f"{positions_for_llm}\n"
#    "# Here is the most recent information I want to base my decisions on:\n"
#    f"{chat_and_data_summary}\n"
    "# Here is the most recent information about Crypto World that I want to base my decisions on:\n"
    f"{top_headlines}\n"
     "# Here is the sentimens of users about my opened positions:\n"
    f"{recent_sentiments}\n"
    "# Here is the most recent trendings coins on Coingecko ordered by score based on the user search:\n"
    f"{coingecko_trends}\n"
)

# append our messages to the chat
model = "llama3.2"
messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_message},
]

print(system_prompt)
print(user_message)

# This class will be used to submit the trades
class Position(BaseModel):
    market: str = Field(..., description="The asset to trade")
    direction: Literal["long", "short"] = Field(
        ...,
        description="The direction to trade",
    )
    size: float = Field(
        ...,
        description="The size of the trade denominated in USD. It should be greater than 10.",
    )
    reasoning: list[str] = Field(
        default_factory=list,
        description="The reasoning for the decision",
    )
    leverage: int | None = Field(None, description="Optional leverage multiplier")


class PositionReasoning(BaseModel):
    positions_to_maintain: list[Position] = Field(
        default_factory=list,
        description="Positions to maintain without changes",
    )
    positions_to_modify: list[Position] = Field(
        default_factory=list,
        description="Positions to modify or close",
    )
    positions_to_open: list[Position] = Field(
        default_factory=list,
        description="Positions to open",
    )

response = ollama.chat(
    model=model,
    messages=messages,
    format=PositionReasoning.model_json_schema(),
)

result = response.message.content
print(result)
