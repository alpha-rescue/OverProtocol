
import random
import ssl

import time
import traceback
import cloudscraper
import requests
import warnings

from OverWallet.config import *
from logger import logger

warnings.filterwarnings("ignore", category=DeprecationWarning)
timezones = ["Africa/Abidjan",
            "Africa/Algiers",
            "Africa/Bissau",
            "Africa/Cairo",
            "Africa/Casablanca",
            "Africa/Ceuta",
            "Africa/El_Aaiun",
            "Asia/Pyongyang",
            "Asia/Qatar",
            "Asia/Qostanay",
            "Asia/Qyzylorda",
            "Asia/Riyadh",
            "Asia/Sakhalin",
            "Europe/Berlin",
            "Europe/Brussels",
            "Europe/Bucharest",
            "Europe/Budapest",
            "Europe/Chisinau",
            "Europe/Dublin",
            "Europe/Gibraltar",
            "Europe/Moscow",
            "Europe/Paris",
            "Europe/Prague",
            "Europe/Riga",
            "Europe/Rome",
            "Europe/Samara"]


class OverWallet:

    def __init__(self, email, proxy, access_token=None, refresh_token=None):

        self.points = 0

        self.access_token, self.refresh_token = access_token, refresh_token

        self.sitekey = '6LdAUmQfAAAAAK7cFboDQx2teLP3Tu2QxKk9jwB4'
        self.email= email
        self.session = self._make_scraper
        self.session.proxies = {"http": f"http://{proxy.split(':')[2]}:{proxy.split(':')[3]}@{proxy.split(':')[0]}:{proxy.split(':')[1]}",
                                "https": f"http://{proxy.split(':')[2]}:{proxy.split(':')[3]}@{proxy.split(':')[0]}:{proxy.split(':')[1]}"}
        adapter = requests.adapters.HTTPAdapter(max_retries=3)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

        self.session.headers.update({"user-agent": self.generate_user_agent,
                                     'content-type': 'application/json'})

    def RefreshAccessToken(self, access_token, refresh_token):


        payload = {
            "access_token": access_token,
            "refresh_token": refresh_token
        }

        with self.session.post(f"https://mover-api-prod.over.network/auth/refresh", json=payload) as response:
            new_access_token = response.json()['data']['access_token']

            self.session.headers.update({"authorization": f"Bearer {response.json()['data']['access_token']}"})

        with open('result.txt', 'r') as file:
            file_contents = file.read()

        # print(access_token, new_access_token)

        file_contents = file_contents.replace(access_token, new_access_token)

        with open('result.txt', 'w') as file:
            file.write(file_contents)

    def Quiz(self):

        with self.session.get("https://mover-api-prod.over.network/mission/3/info") as response:

            quiz = response.json()["data"]["quiz_id"]

            with self.session.get(f"https://mover-api-prod.over.network/mission/3/quiz/{quiz}/start") as response:

                answers = response.json()["data"]["choices"]
                payload = {
                    "answer_list": [
                        f"{random.randint(1, len(answers))}"
                    ]
                }
                with self.session.post(f"https://mover-api-prod.over.network/mission/3/quiz/{quiz}/submit", json=payload) as response:
                    # pprint(response.json())
                    return response.json()["data"]["point"]



    def AcceptReferral(self, code):

        payload = {
            "code": code
        }
        with self.session.post(f"https://mover-api-prod.over.network/mission/1/claim", json=payload) as response:
            ...

    def GetClaimableReferrals(self) -> list:
        with self.session.get(f"https://mover-api-prod.over.network/mission/1/claimable_friends") as response:
            return response.json()["data"]["friends"]

    @property
    def ClaimPointsForDailyEvent(self) -> int:
        with self.session.post(f"https://mover-api-prod.over.network/daily/claim") as response:
            # pprint(response.json())
            return response.json()["data"]["point"]

    @property
    def ClaimPointsForEvent1(self) -> int:
        with self.session.post(f"https://mover-api-prod.over.network/event/1/click") as response:
            return response.json()["data"]["reward"]

    @property
    def GetPoints(self) -> int:
        with self.session.get(f"https://mover-api-prod.over.network/user") as response:
            try:
                return response.json()["data"]["point"]
            except:
                print(response.text)

    @property
    def ClaimPointsForInvite(self) -> bool:

        with self.session.post(f"https://mover-api-prod.over.network/user/claim/invite") as response:
            if response.json()["data"] == None:
                return True
            else:
                return False

    @property
    def GetInviteCode(self)->str:

        with self.session.get("https://mover-api-prod.over.network/user/signin") as response:
            return response.json()["data"]["my_invite_code"]

    def AcceptInvite(self, refCode):

        with self.session.post(f"https://mover-api-prod.over.network/user/invite_code/{refCode}") as response:
            if response.json()["data"] != None:
                return True
            else:
                return False

    def NicknameChange(self, nickname):

        with self.session.post(f"https://mover-api-prod.over.network/user/name/{nickname}") as response:
            if response.json()["data"] == None:
                return True
            else:
                return False

    def NicknameValidStatus(self, nickname):

        with self.session.get(f"https://mover-api-prod.over.network/user/name/{nickname}") as response:
            # print(response.text)
            if response.json()["data"] == None:
                return True
            else:
                return False

    @property
    def StakeAll(self) -> dict:

        with self.session.get("https://mover-api-prod.over.network/user/staking") as response:
            points = response.json()['data']['available_balance']

            with self.session.post(f"https://mover-api-prod.over.network/user/staking/amount/{points}") as response:
                return response.json()

    @property
    def GetMe(self) -> dict:

        with self.session.get("https://mover-api-prod.over.network/user/signin") as response:
            self.inviteCode = response.json()["data"]["my_invite_code"]
            return response.json()


    @property
    def generate_user_agent(self) -> str:
        return f"OverMobile/171 CFNetwork/{random.randint(1380,1450)} Darwin/{random.randint(1380,1450)}.1.0"

    @property
    def _make_scraper(self):
        ssl_context = ssl.create_default_context()
        ssl_context.set_ciphers(
            "ECDH-RSA-NULL-SHA:ECDH-RSA-RC4-SHA:ECDH-RSA-DES-CBC3-SHA:ECDH-RSA-AES128-SHA:ECDH-RSA-AES256-SHA:"
            "ECDH-ECDSA-NULL-SHA:ECDH-ECDSA-RC4-SHA:ECDH-ECDSA-DES-CBC3-SHA:ECDH-ECDSA-AES128-SHA:"
            "ECDH-ECDSA-AES256-SHA:ECDHE-RSA-NULL-SHA:ECDHE-RSA-RC4-SHA:ECDHE-RSA-DES-CBC3-SHA:ECDHE-RSA-AES128-SHA:"
            "ECDHE-RSA-AES256-SHA:ECDHE-ECDSA-NULL-SHA:ECDHE-ECDSA-RC4-SHA:ECDHE-ECDSA-DES-CBC3-SHA:"
            "ECDHE-ECDSA-AES128-SHA:ECDHE-ECDSA-AES256-SHA:AECDH-NULL-SHA:AECDH-RC4-SHA:AECDH-DES-CBC3-SHA:"
            "AECDH-AES128-SHA:AECDH-AES256-SHA"
        )
        ssl_context.set_ecdh_curve("prime256v1")
        ssl_context.options |= (ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3 | ssl.OP_NO_TLSv1_3 | ssl.OP_NO_TLSv1)
        ssl_context.check_hostname = False

        return cloudscraper.create_scraper(
            debug=False,
            ssl_context=ssl_context
        )



if __name__ == '__main__':

    print(' ___________________________________________________________________\n'
          '|                       Rescue Alpha Soft                           |\n'
          '|                   Telegram - @rescue_alpha                        |\n'
          '|                   Discord - discord.gg/438gwCx5hw                 |\n'
          '|___________________________________________________________________|\n\n\n')


    data = []
    with open('result.txt', 'r') as file:
        for i in file:
            data.append(i.rstrip().split("|"))

    while True:

        random.shuffle(data)

        for i in data:

            if i[-1] == None:
                continue

            try:

                if mobile_proxy_mode:
                    model = OverWallet('', proxy=mobile_proxy,
                                       access_token=i[-2],
                                       refresh_token=i[-1])
                else:
                    model = OverWallet('', proxy=i[2],
                                       access_token=i[-2],
                                       refresh_token=i[-1])

                model.RefreshAccessToken(model.access_token , model.refresh_token)
                startPoints = model.GetPoints

                endPoints = model.ClaimPointsForDailyEvent

                q_status = False
                if random.choice([True, True, False]) == False:
                    endPoints = model.Quiz()
                    q_status = True

                while True:
                    result = model.StakeAll
                    if result['data']['available_balance'] == 0:
                        endPoints = result['data']['staking_balance']
                        break

                logger.success(f"{i[0]} | {startPoints} -> {endPoints} | Daily: True + Quiz: {q_status}")

            except Exception as e:

                traceback.print_exc()

                logger.success(f"{i[0]} | Error ({str(e)})")

            if mobile_proxy_mode:
                requests.get(mobile_proxy_change_ip_link)

            time.sleep(random.randint(delay[0], delay[1]))

