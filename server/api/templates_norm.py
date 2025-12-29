import json
import os
from Crypto.PublicKey import RSA

DARKMOON_THUMB = []
DARKMOON_MULTI = []

NOTICE = []
METADATA = {}
SUBSCRIPTION_REMAIN_ITEMS = []
EVENT_BANNERS = []
DARKMOON_ASTRAL_BOOSTS = []

INIT_ITEMS = [[1, 99999], [2, 999999], [18, 1], [19, 1], [28, 1], [29, 1], [30, 1], [31, 1], [94, 99999], [239, 1000], [307, 1], [321, 1], [324, 1], [366, 1], [442, 1], [443, 1], [444, 1], [445, 1], [446, 1], [447, 1], [448, 1], [449, 1], [450, 1], [533, 1], [575, 1], [579, 1], [585, 1], [599, 1], [600, 1], [624, 1], [626, 1], [628, 1], [798, 1], [814, 1], [815, 1], [816, 1], [817, 1], [818, 1], [836, 1], [837, 1], [838, 1], [839, 1], [840, 1], [872, 1], [873, 1], [874, 1], [875, 1], [876, 1], [953, 1], [954, 1], [955, 1], [956, 1], [957, 1], [959, 1], [960, 1], [961, 1], [962, 1], [963, 1], [1304, 1], [1305, 1], [1306, 1], [1307, 1], [1308, 1], [1324, 1], [1325, 1], [1326, 1], [1327, 1], [1328, 1], [1344, 1], [1345, 1], [1346, 1], [1347, 1], [1348, 1], [3044, 1], [3045, 1], [3046, 1], [3047, 1], [3048, 1], [4301, 1], [6854, 1], [8203, 1], [8204, 1], [8205, 1], [8206, 1], [8207, 1], [8208, 1], [8212, 1], [10101, 1], [10104, 1], [10845, 1], [10846, 1], [10847, 1], [10848, 1], [10849, 1], [10850, 1], [10854, 1], [12520, 1], [12521, 1], [12522, 1], [12523, 1], [12524, 1], [12525, 1], [12601, 1], [12602, 1], [12603, 1], [12604, 1], [12605, 1], [12606, 1], [12610, 1], [13683, 1], [13684, 1], [13685, 1], [13686, 1], [13687, 1], [13688, 1], [13711, 1], [13712, 1], [13713, 1], [13714, 1], [13715, 1], [13716, 1], [13738, 1], [13739, 1], [13740, 1], [13741, 1], [13742, 1], [13743, 1], [13765, 1], [13766, 1], [13767, 1], [13768, 1], [13769, 1], [13770, 1], [13792, 1], [13793, 1], [13794, 1], [13795, 1], [13796, 1], [13797, 1], [13819, 1], [13820, 1], [13821, 1], [13822, 1], [13823, 1], [13824, 1], [13846, 1], [13847, 1], [13848, 1], [13849, 1], [13850, 1], [13851, 1], [13873, 1], [13874, 1], [13875, 1], [13876, 1], [13877, 1], [13878, 1], [13900, 1], [13901, 1], [13902, 1], [13903, 1], [13904, 1], [13905, 1], [13927, 1], [13928, 1], [13929, 1], [13930, 1], [13931, 1], [13932, 1], [13954, 1], [13955, 1], [13956, 1], [13957, 1], [13958, 1], [13959, 1], [13981, 1], [13982, 1], [13983, 1], [13984, 1], [13985, 1], [13986, 1], [14008, 1], [14009, 1], [14010, 1], [14011, 1], [14012, 1], [14013, 1], [14035, 1], [14036, 1], [14037, 1], [14038, 1], [14039, 1], [14040, 1], [14062, 1], [14063, 1], [14064, 1], [14065, 1], [14066, 1], [14067, 1], [14089, 1], [14090, 1], [14091, 1], [14092, 1], [14093, 1], [14094, 1], [14116, 1], [14117, 1], [14118, 1], [14119, 1], [14120, 1], [14121, 1], [14143, 1], [14144, 1], [14145, 1], [14146, 1], [14147, 1], [14148, 1], [14170, 1], [14171, 1], [14172, 1], [14173, 1], [14174, 1], [14175, 1], [14197, 1], [14198, 1], [14199, 1], [14200, 1], [14201, 1], [14202, 1], [14957, 1], [14958, 1], [14959, 1], [14960, 1], [14961, 1], [14962, 1]]

INIT_NOAH_PARTS = 5

INIT_NOAH_STAGES = [[0, 5], [0, 4], [0, 3], [0, 2], [0, 1], [1, 10], [1, 9], [1, 8], [1, 7], [2, 13], [2, 12], [2, 11], [3, 15], [3, 14]]

PLAY_PUBLIC_KEY = ""
PLAY_CRYPTOR = None

ALBUM_SEASON = 0

DARKMOON_BOOST_CONFIG = [[1, 1], [5, 3], [10, 5]]

DIFF_TABLE = [
    "Normal",
    "Hard",
    "HardPlus",
    "SHard",
    "SHardPlus",
    "Chaos",
    "Cosmos",
    "Abyss",
]

USER_PROFILE_LOOKUP_TABLE = {
    "2": "totalSRankCount",
    "3": "totalAllComboCount",
    "4": "totalAllPerfectCount",
    "6": "totalClearCount",
    "7": "totalFailCount",
    "9": "totalCosmosClearCount",
    "11": "cosmosMapClearCount",
    "13": "totalOwnedFragmentCount",
    "50": "abyssMapClearCount",
    "51": "totalAbyssClearCount"
}

def init_templates():
    base_path = 'api/config'
    print("[TEMPLATES] Initializing templates...")

    global NOTICE, METADATA, SUBSCRIPTION_REMAIN_ITEMS, EVENT_BANNERS, DARKMOON_ASTRAL_BOOSTS, DARKMOON_THUMB, DARKMOON_MULTI
    global PLAY_PUBLIC_KEY, PLAY_CRYPTOR

    try:
        with open(os.path.join(base_path, 'notice.json'), 'r', encoding='utf-8') as f:
            NOTICE = json.load(f)

        with open(os.path.join(base_path, 'metadata.json'), 'r', encoding='utf-8') as f:
            METADATA = json.load(f)

        with open(os.path.join(base_path, 'subscriptionRemainItems.json'), 'r', encoding='utf-8') as f:
            SUBSCRIPTION_REMAIN_ITEMS = json.load(f)

        with open(os.path.join(base_path, 'eventBanners.json'), 'r', encoding='utf-8') as f:
            EVENT_BANNERS = json.load(f)

        with open(os.path.join(base_path, 'darkmoonAstralBoosts.json'), 'r', encoding='utf-8') as f:
            DARKMOON_ASTRAL_BOOSTS = json.load(f)

        with open(os.path.join(base_path, 'darkmoonThumb.json'), 'r', encoding='utf-8') as f:
            DARKMOON_THUMB = json.load(f)

        with open(os.path.join(base_path, 'darkmoonMulti.json'), 'r', encoding='utf-8') as f:
            DARKMOON_MULTI = json.load(f)

        with open(os.path.join(base_path, 'play_public.xml'), 'r', encoding='utf-8') as f:
            PLAY_PUBLIC_KEY = f.read()

        with open(os.path.join(base_path, 'play_private.pem'), 'r', encoding='utf-8') as f:
            private_key = f.read()
            PLAY_CRYPTOR = RSA.import_key(private_key)

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")