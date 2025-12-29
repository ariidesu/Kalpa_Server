import sqlite3
import datetime

DB_PATH = "player.db"
MANIFEST_PATH = "manifest.db"

def unlock_all_tracks(user_pk):
    player_conn = sqlite3.connect(DB_PATH)
    player_cur = player_conn.cursor()

    manifest_conn = sqlite3.connect(MANIFEST_PATH)
    manifest_cur = manifest_conn.cursor()

    # Unlock all tracks
    manifest_cur.execute("SELECT pk FROM tracks")
    track_pks = [row[0] for row in manifest_cur.fetchall()]
    for track_pk in track_pks:
        player_cur.execute(
            "INSERT OR IGNORE INTO userTracks (stageState, UserPk, TrackPk) VALUES (?, ?, ?)",
            (0, user_pk, track_pk)
        )

    # Unlock all packs
    manifest_cur.execute("SELECT pk FROM packs")
    pack_pks = [row[0] for row in manifest_cur.fetchall()]
    for pack_pk in pack_pks:
        player_cur.execute(
            """INSERT OR IGNORE INTO userPacks (
                totalScore, stageState, stageTotalStarCount, stageTotalStarCountV2, stageTotalClearCount,
                courseBestSkin, courseBestTrackPk1, courseBestMode1, courseBestTrackPk2, courseBestMode2,
                courseBestTrackPk3, courseBestMode3, courseBestTrackPk4, courseBestMode4, courseBestEndAt,
                courseBestCombo, courseBestAvgRank, courseBestAvgRate, courseBestScore, courseBestHp,
                courseAllPerfectCount, courseAllComboCount, courseClearCount, courseDeathCount, courseGiveUpCount,
                courseIrregularCount, courseCosmosCount, normal, hard, hardplus, arcade, kalpa, UserPk, PackPk
            ) VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )""",
            (
                0, 0, 0, 0, 0, "", None, None, None, None,
                None, None, None, None, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, user_pk, pack_pk
            )
        )

    # Unlock all maps
    manifest_cur.execute("SELECT pk FROM maps")
    map_pks = [row[0] for row in manifest_cur.fetchall()]
    for map_pk in map_pks:
        player_cur.execute(
            """INSERT OR IGNORE INTO userMaps (
                stageStarCount, stageStarCountV2, stageBestRate, stageBestRank, stageBestHp,
                stageState, stageBestCombo, clearCount, archiveGauge, archiveReviveDarkmatterAmount,
                UserPk, MapPk
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, user_pk, map_pk
            )
        )

    # Unlock all products
    manifest_cur.execute("SELECT pk FROM products")
    product_pks = [row[0] for row in manifest_cur.fetchall()]
    for product_pk in product_pks:
        player_cur.execute(
            """INSERT OR IGNORE INTO userProducts (
                buyCount, periodicBuyCount, lastPeriodicRefreshDate, UserPk, ProductPk
            ) VALUES (?, ?, ?, ?, ?)""",
            (
                1, 0, None, user_pk, product_pk
            )
        )

    # Unlock all items with specific key prefixes
    manifest_cur.execute("SELECT pk, key FROM items")
    item_rows = manifest_cur.fetchall()
    prefixes = (
        "skin.", "icon.", "character.", "title.", "background.",
        "iconborder.", "story.", "track.", "map.", "play.", "sfx.", "taskeventgauge.", "pack.", "rootcharacter.",
        "emoticon.", "playnote.", "playgear.", "playbackground.", "playpulseeffect.", "playscouter.", "playcombojudge.", "playdeco.", "playhiteffect.", "taskeventgauge.", "pack."
    )
    for item_pk, item_key in item_rows:
        if any(item_key.startswith(prefix) for prefix in prefixes):
            player_cur.execute(
                """INSERT OR IGNORE INTO userItems (
                    amount, renewedDate, state, startDate, endDate, UserPk, ItemPk
                ) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (1, 0, 0, None, None, user_pk, item_pk)
            )
            # If item starts with rootcharacter., also insert into userRootCharacterItems
            if item_key.startswith("rootcharacter."):
                player_cur.execute(
                    """INSERT OR IGNORE INTO userRootCharacterItems (
                        amount, renewedDate, state, startDate, endDate, createdAt, updatedAt, UserPk, ItemPk
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (1, 0, 0, None, None, None, None, user_pk, item_pk)
                )  

    # Unlock all constellCharacters
    manifest_cur.execute("SELECT pk, defaultCharacterKey FROM constellCharacters")
    rows = manifest_cur.fetchall()

    now = datetime.datetime.now().isoformat()

    for pk, default_character_key in rows:
        player_cur.execute(
            """INSERT OR IGNORE INTO userConstellCharacters (
                characterKey, currentAwaken, currentReverse, startDate, endDate, UserPk, ConstellCharacterPk
            ) VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (default_character_key, 0, 4, now, None, user_pk, pk)
        )



    # Unlock all character awakens for each character
    for pk, default_character_key in rows:
        player_cur.execute(
            """INSERT OR IGNORE INTO userCharacterAwakens (
                awakenNum, currentExp0, currentExp1, currentExp2, currentExp3, currentExp4, currentExp5, currentExp6,
                endDate0, endDate1, endDate2, endDate3, endDate4, endDate5, endDate6,
                UserPk, CharacterAwakenPk
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                0, 0, 0, 0, 0, 0, 0, 0,
                None, None, None, None, None, None, None,
                user_pk, pk
            )
        )
    
    player_conn.commit()
    player_conn.close()

if __name__ == "__main__":
    user_pk = input("Enter the user pk to unlock all stuff for: ")
    user_pk = int(user_pk)
    unlock_all_tracks(user_pk)