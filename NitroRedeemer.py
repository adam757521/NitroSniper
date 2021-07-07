import re
import time
from enum import Enum
import aiohttp


class Responses(Enum):
    RATE_LIMITED = 0
    INVALID_GIFT = 1
    ALREADY_CLAIMED = 2
    NO_PAYMENT_SOURCE = 3
    ALREADY_PURCHASED = 4
    ACCESS_DENIED = 5
    NOT_VERIFIED = 6
    CLAIMED = 7
    IN_CACHE = 8


class ErrorHandler:
    def __init__(self):
        self.error_responses = {'{"message": "Unknown Gift Code", "code": 10038}': Responses.INVALID_GIFT,
                                '{"message": "This gift has been redeemed already.", "code": 50050}': Responses.ALREADY_CLAIMED,
                                '{"message": "Payment source required to redeem gift.", "code": 50070}': Responses.NO_PAYMENT_SOURCE,
                                '{"message": "Already purchased", "code": 100011}': Responses.ALREADY_PURCHASED,
                                '{"message": "You need to verify your account in order to perform this action", "code": 40002}': Responses.NOT_VERIFIED,
                                'You are being rate limited': Responses.RATE_LIMITED,
                                'Access denied': Responses.ACCESS_DENIED,
                                }

    def handle_errors(self, response_text):
        for error in self.error_responses:
            if error in response_text:
                return self.error_responses[error]

        return Responses.CLAIMED


class NitroRedeemer:
    def __init__(self, tokens, error_handler: ErrorHandler):
        self.tokens = tokens
        self.error_handler = error_handler
        self.cache = {}
        self.links = ['discord.gift', 'discordapp.com/gifts', 'discord.com/gifts']
        self.gift_re = re.compile(fr'({"|".join(self.links)})/\w{{16,24}}')
        self.rate_limits = {'rate_timestamp': 0, 'rate_delay': 0}
        self.session = aiohttp.ClientSession()
        self.data = []

    async def redeem_code(self, code):
        if code in self.cache:
            return None, Responses.IN_CACHE

        payment_required = False
        response = Responses.RATE_LIMITED
        self.cache[code] = response
        token = None

        for token in self.tokens:
            payment_id = self.tokens[token]
            if payment_required and not payment_id:
                continue

            if (time.time() - self.rate_limits['rate_timestamp']) <= self.rate_limits['rate_delay']:
                break

            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36 OPR/75.0.3969.285',
                'Authorization': token
            }

            payload = {
                'channel_id': None,
                'payment_source_id': payment_id
            }

            start = time.time()
            r = await self.session.post(f'https://discordapp.com/api/v8/entitlements/gift-codes/{code}/redeem',
                                        headers=headers, json=payload)
            self.data.append(round((time.time() - start) * 1000))

            response = self.error_handler.handle_errors(await r.text())
            self.cache[code] = response
            if response == Responses.ALREADY_CLAIMED:
                break

            if response == Responses.CLAIMED:
                print(await r.text())
                break

            if response == Responses.INVALID_GIFT:
                break

            if response == Responses.NO_PAYMENT_SOURCE:
                payment_required = True
                continue

            if response == Responses.ALREADY_PURCHASED:
                continue

            if response == Responses.NOT_VERIFIED:
                self.tokens.remove(token)

            if response == Responses.RATE_LIMITED:
                response_json = await r.json()

                self.rate_limits = {'rate_timestamp': time.time(), 'rate_delay': response_json['retry_after']}
                break

        return token, response

    def remove_links(self, text):
        for link in self.links:
            text = text.replace(link + '/', '')

        return text

    def find_codes(self, text):
        codes = []

        for match in self.gift_re.finditer(text):
            current_code = match.group(0)

            codes.append(self.remove_links(current_code))

        return codes
