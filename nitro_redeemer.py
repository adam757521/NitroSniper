import re
import time
from enum import Enum
import json

import aiohttp


class Responses(Enum):
    """An enum representing all API responses.

    Attributes
    -----------
    RATE_LIMITED: :class:`int`
        The user is being rate-limited.
    INVALID_GIFT: :class:`int`
        The gift passed is invalid.
    ALREADY_CLAIMED: :class:`int`
        The gift passed is already claimed by another user.
    NO_PAYMENT_SOURCE: :class:`int`
        The gift passed needs a payment source id.
    ALREADY_PURCHASED: :class:`int`
        Cannot claim gift because the user already has a subscription of another tier.
    ACCESS_DENIED: :class:`int`
        Access to API is denied.
    NOT_VERIFIED: :class:`int
        User is not verified.
    CLAIMED: :class:`int`
        User claimed gift.
    SERVER_ERROR: :class:`int`
        Discord returned 500.
    ON_COOLDOWN: :class:`int`
        Cannot redeem code, currently on cooldown.
    IN_CACHE: :class:`int`
        Gift is already in NitroRedeemer's cache.
    """

    RATE_LIMITED = 0
    INVALID_GIFT = 1
    ALREADY_CLAIMED = 2
    NO_PAYMENT_SOURCE = 3
    ALREADY_PURCHASED = 4
    ACCESS_DENIED = 5
    NOT_VERIFIED = 6
    CLAIMED = 7
    SERVER_ERROR = 8
    ON_COOLDOWN = 9
    IN_CACHE = 10


class ErrorHandler:
    """An API error handler.

    Attributes
    -----------
    error_responses: :class:`dict[str, Responses]`
        Represents API errors and their API text.
    """

    def __init__(self):
        self.error_responses = {'{"message": "Unknown Gift Code", "code": 10038}': Responses.INVALID_GIFT,
                                '{"message": "This gift has been'
                                ' redeemed already.", "code": 50050}':
                                    Responses.ALREADY_CLAIMED,
                                '{"message": "Payment source required to'
                                ' redeem gift.", "code": 50070}':
                                    Responses.NO_PAYMENT_SOURCE,
                                '{"message": "Already purchased", "code": 100011}':
                                    Responses.ALREADY_PURCHASED,
                                '{"message": "You need to verify your account in order to perform this action.",'
                                ' "code": 40002}': Responses.NOT_VERIFIED,
                                'You are being rate limited': Responses.RATE_LIMITED,
                                'Access denied': Responses.ACCESS_DENIED,
                                '{"message": "500: Internal Server Error", "code": 0}': Responses.SERVER_ERROR
                                }

    def handle_errors(self, response_text):
        for error in self.error_responses:
            if error in response_text:
                return self.error_responses[error]

        return Responses.CLAIMED


class NitroResponse:
    def __init__(self, response, token, nitro_type):
        self.response = response
        self.token = token
        self.nitro_type = nitro_type

    @classmethod
    def parse_json(cls, response_json, error_handler: ErrorHandler, redeemer_token):
        response = error_handler.handle_errors(str(response_json))
        try:
            nitro_type = None if response != Responses.CLAIMED else json.loads(response_json)['subscription_plan'].get('name')
        except:
            nitro_type = None

        return cls(response, redeemer_token, nitro_type)


class NitroRedeemer:
    """A nitro redeemer class that redeems nitro gifts

    Attributes
    -----------
    tokens: :class:`list[str]`
        Represents the tokens used by the redeemer.
    error_handler: :class:`ErrorHandler`
        The error handler the redeemer will use.
    cache: :class:`dict[str, Responses]`
        Represents a dict of codes and responses.
    links: :class:`list[str]`
        Represents a list of links that are used to parse the gift.
    gift_re: :class:`re.Pattern`
        Represents the regex the redeemer will use to parse gifts.
    session: :class:`aiohttp.ClientSession`
        Represents a aiohttp session used by the redeemer.
    data: :class:`list[float]`
        Represents a list of type float that represents discord API latency.
    """

    def __init__(self, tokens, error_handler: ErrorHandler, max_gifts=2, cooldown=24):
        self.tokens = tokens
        self.error_handler = error_handler
        self.cache = {}
        self.links = ['discord.gift', 'discordapp.com/gifts', 'discord.com/gifts']
        self.gift_re = re.compile(fr'({"|".join(self.links)})/\w{{16,24}}')
        self.rate_limits = {'rate_timestamp': 0, 'rate_delay': 0}
        self.snipe_cooldown = {'cooldown': 0, 'sniped': 0}
        self.session = aiohttp.ClientSession()
        self.data = []
        self.max_gifts = max_gifts
        self.cooldown = cooldown

    async def redeem_code(self, code):
        if self.snipe_cooldown['cooldown'] > time.time():
            return NitroResponse(Responses.ON_COOLDOWN, None, None)

        if code in self.cache:
            return NitroResponse(Responses.IN_CACHE, None, None)

        payment_required = False
        nitro_response = NitroResponse(Responses.RATE_LIMITED, None, None)
        self.cache[code] = nitro_response.response

        for token in list(self.tokens):
            payment_id = self.tokens[token]
            if payment_required and not payment_id:
                continue

            if (time.time() - self.rate_limits['rate_timestamp']) <= self.rate_limits['rate_delay']:
                break

            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                              ' (KHTML, like Gecko) Chrome/89.0.4389.128 '
                              'Safari/537.36 OPR/75.0.3969.285',
                'Authorization': token
            }

            payload = {
                'channel_id': None,
                'payment_source_id': payment_id
            }

            start = time.time()
            request = await self.session.post(f'https://discordapp.com/api/v8/entitlements/'
                                              f'gift-codes/{code}/redeem',
                                              headers=headers, json=payload)
            self.data.append(round((time.time() - start) * 1000))

            nitro_response = NitroResponse.parse_json(await request.text(), self.error_handler, token)
            self.cache[code] = nitro_response.response
            if nitro_response.response == Responses.ALREADY_CLAIMED:
                break

            if nitro_response.response == Responses.CLAIMED:
                print(await request.text())  # debug remove if wanted.
                self.snipe_cooldown['sniped'] += 1
                if self.snipe_cooldown['sniped'] >= self.max_gifts:
                    self.snipe_cooldown['cooldown'] = int(time.time() + self.cooldown * 60 * 60)

                break

            if nitro_response.response == Responses.SERVER_ERROR:
                break

            if nitro_response.response == Responses.INVALID_GIFT:
                break

            if nitro_response.response == Responses.NO_PAYMENT_SOURCE:
                payment_required = True
                continue

            if nitro_response.response == Responses.ALREADY_PURCHASED:
                continue

            if nitro_response.response == Responses.NOT_VERIFIED:
                del self.tokens[token]

            if nitro_response.response == Responses.RATE_LIMITED:
                response_json = await request.json()

                self.rate_limits = {'rate_timestamp': time.time(),
                                    'rate_delay': response_json['retry_after']}
                break

        return nitro_response

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
