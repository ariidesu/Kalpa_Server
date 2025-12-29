from api.database import manifest_database, labProducts, labMissions, noahChapters, noahParts, noahStages, achievements, battlePasses, battlePassRewardItems, battlePassMissions, rootCharacters, constellCharacters, characterAwakens, characterConnections, characterStories, characterRewardSystems, characterLevelSystems, characterCostSystems, characterFavoriteSongs, skills, albums, albumOpenConditions, albumPlayConstraints, albumLampConditions, subscriptionRotateSong, competitionTeams, competitionTeamPointRewards, competitionTeamRankingRewards, competitionTeamMissions, teamCompetitionEventMissions, performerHurdleMissions, performerLevels, stickers, emoticons, adPlayRotationSong, missions, gachas, gachaGradePercentages, gachaItems, randomProductPercentages, randomBoxPercentages, ingameActionByPlayTypes, allPlayerCoopPointGatheringEvents, localizationEntries, astralBoosts, AquaLevelReachCount, items, itemObtainConditions, packs, tracks, maps, products, productGroups, productBundles, artist

LAB_PRODUCTS = []
LAB_MISSIONS = []
NOAH_CHAPTERS = []
NOAH_PARTS = []
NOAH_STAGES = []
BATTLE_PASSES = []
BATTLE_PASS_REWARD_ITEMS = []
BATTLE_PASS_MISSIONS = []
ROOT_CHARACTERS = []
CONSTELLA_CHARACTERS = []
CHARACTER_AWAKENS = []
CHARACTER_CONNECTIONS = []
CHARACTER_STORIES = []
CHARACTER_REWARD_SYSTEMS = []
CHARACTER_LEVEL_SYSTEMS = []
CHARACTER_COST_SYSTEMS = []
CHARACTER_FAVORITE_SONGS = []
SKILLS = []
ALBUMS = []
ALBUM_OPEN_CONDITIONS = []
ALBUM_PLAY_CONSTRAINTS = []
ALBUM_LAMP_CONDITIONS = []
SUBSCRIPTION_ROTATE_SONG = []
COMPETITION_TEAMS = []
COMPETITION_TEAM_POINT_REWARDS = []
COMPETITION_TEAM_RANKING_REWARDS = []
COMPETITION_TEAM_MISSIONS = []
TEAM_COMPETITION_EVENT_MISSIONS = []
PERFORMER_HURDLE_MISSIONS = []
PERFORMER_LEVELS = []
STICKERS = []
EMOTICONS = []
AD_PLAY_ROTATION_SONG = []
MISSIONS = []
GACHAS = []
GACHA_GRADE_PERCENTAGES = []
GACHA_ITEMS = []
RANDOM_BOX_PERCENTAGES = []
RANDOM_PRODUCT_PERCENTAGES = []
INGAME_ACTION_BY_PLAY_TYPES = []
ALL_PLAYER_COOP_POINT_GATHERING_EVENTS = []
LOCALIZATION_ENTRIES = []
ASTRAL_BOOSTS = []
THUMB_AQUA_LEVEL_REACH_COUNT = {}
MULTI_AQUA_LEVEL_REACH_COUNT = {}
ITEM_OBTAIN_CONDITIONS = []
PACKS = []
TRACKS = []
MAPS = []
PRODUCT_GROUPS = []
PRODUCTS = []
PRODUCT_BUNDLES = []
ITEMS = []
ACHIEVEMENTS = []

async def init_templates_database():
    global LAB_PRODUCTS, LAB_MISSIONS, NOAH_CHAPTERS, NOAH_PARTS, NOAH_STAGES, BATTLE_PASSES, BATTLE_PASS_REWARD_ITEMS, BATTLE_PASS_MISSIONS, ROOT_CHARACTERS, CONSTELLA_CHARACTERS, CHARACTER_AWAKENS, CHARACTER_CONNECTIONS, CHARACTER_STORIES, CHARACTER_REWARD_SYSTEMS, CHARACTER_LEVEL_SYSTEMS, CHARACTER_COST_SYSTEMS, CHARACTER_FAVORITE_SONGS, SKILLS, ALBUMS, ALBUM_OPEN_CONDITIONS, ALBUM_PLAY_CONSTRAINTS, ALBUM_LAMP_CONDITIONS, SUBSCRIPTION_ROTATE_SONG, COMPETITION_TEAMS, COMPETITION_TEAM_POINT_REWARDS, COMPETITION_TEAM_RANKING_REWARDS, COMPETITION_TEAM_MISSIONS, TEAM_COMPETITION_EVENT_MISSIONS, PERFORMER_HURDLE_MISSIONS, PERFORMER_LEVELS, STICKERS, EMOTICONS, AD_PLAY_ROTATION_SONG, MISSIONS, GACHAS, GACHA_GRADE_PERCENTAGES, GACHA_ITEMS, RANDOM_BOX_PERCENTAGES, RANDOM_PRODUCT_PERCENTAGES, INGAME_ACTION_BY_PLAY_TYPES, ALL_PLAYER_COOP_POINT_GATHERING_EVENTS, LOCALIZATION_ENTRIES, ASTRAL_BOOSTS, THUMB_AQUA_LEVEL_REACH_COUNT, MULTI_AQUA_LEVEL_REACH_COUNT, ITEM_OBTAIN_CONDITIONS, PACKS, TRACKS, MAPS, PRODUCT_GROUPS, PRODUCTS, PRODUCT_BUNDLES, ACHIEVEMENTS

    global ITEMS

    query = labProducts.select()
    LAB_PRODUCTS = await manifest_database.fetch_all(query)
    LAB_PRODUCTS = [dict(row) for row in LAB_PRODUCTS]

    for row in LAB_PRODUCTS:
        if row['linkedMelodyList'] == []:
            row['linkedMelodyList'] = ""

    query = labMissions.select()
    LAB_MISSIONS = await manifest_database.fetch_all(query)
    LAB_MISSIONS = [dict(row) for row in LAB_MISSIONS]

    for row in LAB_MISSIONS:
        if row['curationList'] == []:
            row['curationList'] = ""

    query = noahChapters.select()
    NOAH_CHAPTERS = await manifest_database.fetch_all(query)
    NOAH_CHAPTERS = [dict(row) for row in NOAH_CHAPTERS]

    query = noahParts.select()
    NOAH_PARTS = await manifest_database.fetch_all(query)
    NOAH_PARTS = [dict(row) for row in NOAH_PARTS]

    query = noahStages.select()
    NOAH_STAGES = await manifest_database.fetch_all(query)
    NOAH_STAGES = [dict(row) for row in NOAH_STAGES]

    query = battlePasses.select()
    BATTLE_PASSES = await manifest_database.fetch_all(query)
    BATTLE_PASSES = [dict(row) for row in BATTLE_PASSES]

    query = battlePassRewardItems.select()
    BATTLE_PASS_REWARD_ITEMS = await manifest_database.fetch_all(query)
    BATTLE_PASS_REWARD_ITEMS = [dict(row) for row in BATTLE_PASS_REWARD_ITEMS]

    for row in BATTLE_PASS_REWARD_ITEMS:
        if row['royalItem2'] == []:
            row['royalItem2'] = ""
        if row['freeItem'] == []:
            row['freeItem'] = ""

    query = battlePassMissions.select()
    BATTLE_PASS_MISSIONS = await manifest_database.fetch_all(query)
    BATTLE_PASS_MISSIONS = [dict(row) for row in BATTLE_PASS_MISSIONS]

    query = rootCharacters.select()
    ROOT_CHARACTERS = await manifest_database.fetch_all(query)
    ROOT_CHARACTERS = [dict(row) for row in ROOT_CHARACTERS]

    query = constellCharacters.select()
    CONSTELLA_CHARACTERS = await manifest_database.fetch_all(query)
    CONSTELLA_CHARACTERS = [dict(row) for row in CONSTELLA_CHARACTERS]

    query = characterAwakens.select()
    CHARACTER_AWAKENS = await manifest_database.fetch_all(query)
    CHARACTER_AWAKENS = [dict(row) for row in CHARACTER_AWAKENS]

    query = characterConnections.select()
    CHARACTER_CONNECTIONS = await manifest_database.fetch_all(query)
    CHARACTER_CONNECTIONS = [dict(row) for row in CHARACTER_CONNECTIONS]

    query = characterStories.select()
    CHARACTER_STORIES = await manifest_database.fetch_all(query)
    CHARACTER_STORIES = [dict(row) for row in CHARACTER_STORIES]

    query = characterRewardSystems.select()
    CHARACTER_REWARD_SYSTEMS = await manifest_database.fetch_all(query)
    CHARACTER_REWARD_SYSTEMS = [dict(row) for row in CHARACTER_REWARD_SYSTEMS]

    query = characterLevelSystems.select()
    CHARACTER_LEVEL_SYSTEMS = await manifest_database.fetch_all(query)
    CHARACTER_LEVEL_SYSTEMS = [dict(row) for row in CHARACTER_LEVEL_SYSTEMS]

    query = characterCostSystems.select()
    CHARACTER_COST_SYSTEMS = await manifest_database.fetch_all(query)
    CHARACTER_COST_SYSTEMS = [dict(row) for row in CHARACTER_COST_SYSTEMS]

    query = characterFavoriteSongs.select()
    CHARACTER_FAVORITE_SONGS = await manifest_database.fetch_all(query)
    CHARACTER_FAVORITE_SONGS = [dict(row) for row in CHARACTER_FAVORITE_SONGS]

    query = skills.select()
    SKILLS = await manifest_database.fetch_all(query)
    SKILLS = [dict(row) for row in SKILLS]

    query = albums.select()
    ALBUMS = await manifest_database.fetch_all(query)
    ALBUMS = [dict(row) for row in ALBUMS]

    query = albumOpenConditions.select()
    ALBUM_OPEN_CONDITIONS = await manifest_database.fetch_all(query)
    ALBUM_OPEN_CONDITIONS = [dict(row) for row in ALBUM_OPEN_CONDITIONS]

    query = albumPlayConstraints.select()
    ALBUM_PLAY_CONSTRAINTS = await manifest_database.fetch_all(query)
    ALBUM_PLAY_CONSTRAINTS = [dict(row) for row in ALBUM_PLAY_CONSTRAINTS]

    query = albumLampConditions.select()
    ALBUM_LAMP_CONDITIONS = await manifest_database.fetch_all(query)
    ALBUM_LAMP_CONDITIONS = [dict(row) for row in ALBUM_LAMP_CONDITIONS]

    query = subscriptionRotateSong.select().order_by(subscriptionRotateSong.c.pk.desc())
    SUBSCRIPTION_ROTATE_SONG = await manifest_database.fetch_one(query)
    SUBSCRIPTION_ROTATE_SONG = dict(SUBSCRIPTION_ROTATE_SONG) if SUBSCRIPTION_ROTATE_SONG else {}

    query = competitionTeams.select()
    COMPETITION_TEAMS = await manifest_database.fetch_all(query)
    COMPETITION_TEAMS = [dict(row) for row in COMPETITION_TEAMS]

    query = competitionTeamPointRewards.select()
    COMPETITION_TEAM_POINT_REWARDS = await manifest_database.fetch_all(query)
    COMPETITION_TEAM_POINT_REWARDS = [dict(row) for row in COMPETITION_TEAM_POINT_REWARDS]

    query = competitionTeamRankingRewards.select()
    COMPETITION_TEAM_RANKING_REWARDS = await manifest_database.fetch_all(query)
    COMPETITION_TEAM_RANKING_REWARDS = [dict(row) for row in COMPETITION_TEAM_RANKING_REWARDS]

    query = competitionTeamMissions.select()
    COMPETITION_TEAM_MISSIONS = await manifest_database.fetch_all(query)
    COMPETITION_TEAM_MISSIONS = [dict(row) for row in COMPETITION_TEAM_MISSIONS]

    query = teamCompetitionEventMissions.select()
    TEAM_COMPETITION_EVENT_MISSIONS = await manifest_database.fetch_all(query)
    TEAM_COMPETITION_EVENT_MISSIONS = [dict(row) for row in TEAM_COMPETITION_EVENT_MISSIONS]

    query = performerHurdleMissions.select()
    PERFORMER_HURDLE_MISSIONS = await manifest_database.fetch_all(query)
    PERFORMER_HURDLE_MISSIONS = [dict(row) for row in PERFORMER_HURDLE_MISSIONS]

    query = performerLevels.select()
    PERFORMER_LEVELS = await manifest_database.fetch_all(query)
    PERFORMER_LEVELS = [dict(row) for row in PERFORMER_LEVELS]

    query = stickers.select()
    STICKERS = await manifest_database.fetch_all(query)
    STICKERS = [dict(row) for row in STICKERS]

    query = emoticons.select()
    EMOTICONS = await manifest_database.fetch_all(query)
    EMOTICONS = [dict(row) for row in EMOTICONS]

    query = adPlayRotationSong.select().order_by(adPlayRotationSong.c.pk.desc())
    AD_PLAY_ROTATION_SONG = await manifest_database.fetch_one(query)
    AD_PLAY_ROTATION_SONG = dict(AD_PLAY_ROTATION_SONG) if AD_PLAY_ROTATION_SONG else {}

    query = missions.select()
    MISSIONS = await manifest_database.fetch_all(query)
    MISSIONS = [dict(row) for row in MISSIONS]

    query = gachas.select()
    GACHAS = await manifest_database.fetch_all(query)
    GACHAS = [dict(row) for row in GACHAS]

    query = gachaGradePercentages.select()
    GACHA_GRADE_PERCENTAGES = await manifest_database.fetch_all(query)
    GACHA_GRADE_PERCENTAGES = [dict(row) for row in GACHA_GRADE_PERCENTAGES]

    query = gachaItems.select()
    GACHA_ITEMS = await manifest_database.fetch_all(query)
    GACHA_ITEMS = [dict(row) for row in GACHA_ITEMS]

    query = randomBoxPercentages.select()
    RANDOM_BOX_PERCENTAGES = await manifest_database.fetch_all(query)
    RANDOM_BOX_PERCENTAGES = [dict(row) for row in RANDOM_BOX_PERCENTAGES]

    query = randomProductPercentages.select()
    RANDOM_PRODUCT_PERCENTAGES = await manifest_database.fetch_all(query)
    RANDOM_PRODUCT_PERCENTAGES = [dict(row) for row in RANDOM_PRODUCT_PERCENTAGES]

    query = ingameActionByPlayTypes.select()
    INGAME_ACTION_BY_PLAY_TYPES = await manifest_database.fetch_all(query)
    INGAME_ACTION_BY_PLAY_TYPES = [dict(row) for row in INGAME_ACTION_BY_PLAY_TYPES]

    query = allPlayerCoopPointGatheringEvents.select()
    ALL_PLAYER_COOP_POINT_GATHERING_EVENTS = await manifest_database.fetch_all(query)
    ALL_PLAYER_COOP_POINT_GATHERING_EVENTS = [dict(row) for row in ALL_PLAYER_COOP_POINT_GATHERING_EVENTS]

    query = localizationEntries.select()
    LOCALIZATION_ENTRIES = await manifest_database.fetch_all(query)
    LOCALIZATION_ENTRIES = [dict(row) for row in LOCALIZATION_ENTRIES]

    query = astralBoosts.select()
    ASTRAL_BOOSTS = await manifest_database.fetch_all(query)
    ASTRAL_BOOSTS = [dict(row) for row in ASTRAL_BOOSTS]

    query = AquaLevelReachCount.select().where(AquaLevelReachCount.c.finger == "0").order_by(AquaLevelReachCount.c.pk.desc())
    THUMB_AQUA_LEVEL_REACH_COUNT = await manifest_database.fetch_one(query)
    THUMB_AQUA_LEVEL_REACH_COUNT = dict(THUMB_AQUA_LEVEL_REACH_COUNT)

    query = AquaLevelReachCount.select().where(AquaLevelReachCount.c.finger == "1").order_by(AquaLevelReachCount.c.pk.desc())
    MULTI_AQUA_LEVEL_REACH_COUNT = await manifest_database.fetch_one(query)
    MULTI_AQUA_LEVEL_REACH_COUNT = dict(MULTI_AQUA_LEVEL_REACH_COUNT) if MULTI_AQUA_LEVEL_REACH_COUNT else {}

    query = items.select()
    ITEMS = await manifest_database.fetch_all(query)
    ITEMS = [dict(row) for row in ITEMS]

    query = itemObtainConditions.select()
    ITEM_OBTAIN_CONDITIONS = await manifest_database.fetch_all(query)
    ITEM_OBTAIN_CONDITIONS = [dict(row) for row in ITEM_OBTAIN_CONDITIONS]

    query = packs.select()
    PACKS = await manifest_database.fetch_all(query)
    PACKS = [dict(row) for row in PACKS]

    query = tracks.select()
    TRACKS = await manifest_database.fetch_all(query)
    TRACKS = [dict(row) for row in TRACKS]

    for track in TRACKS:
        if track['pk'] == 0:
            del TRACKS[TRACKS.index(track)]
        else:
            artist_pk = track['ArtistPk']
            query = artist.select().where(artist.c.pk == artist_pk)
            artist_data = await manifest_database.fetch_one(query)
            track['Artist'] = dict(artist_data) if artist_data else {}

    query = maps.select()
    MAPS = await manifest_database.fetch_all(query)
    MAPS = [dict(row) for row in MAPS]

    query = productGroups.select()
    PRODUCT_GROUPS = await manifest_database.fetch_all(query)
    PRODUCT_GROUPS = [dict(row) for row in PRODUCT_GROUPS]

    query = products.select()
    PRODUCTS = await manifest_database.fetch_all(query)
    PRODUCTS = [dict(row) for row in PRODUCTS]

    query = productBundles.select()
    PRODUCT_BUNDLES = await manifest_database.fetch_all(query)
    PRODUCT_BUNDLES = [dict(row) for row in PRODUCT_BUNDLES]

    query = achievements.select()
    ACHIEVEMENTS = await manifest_database.fetch_all(query)
    ACHIEVEMENTS = [dict(row) for row in ACHIEVEMENTS]
