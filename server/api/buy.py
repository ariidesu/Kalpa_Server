from starlette.responses import JSONResponse
from starlette.requests import Request
from starlette.routing import Route
import random
from datetime import datetime, timezone

from api.database import manifest_database, player_database, products, productBundles, randomProductPercentages, items, userProducts, get_user_and_validate_session,  get_user_product, add_tracks, add_packs, add_root_characters, check_item_entitlement,  combine_queues
from api.misc import get_standard_response, convert_datetime

PACK_PREFIXES = ["pack."]
CHARACTER_PREFIXES = ["rootcharacter."]
TRACK_PREFIXES = ["track."]
ITEM_PREFIXES = [
    "background.", "icon.", "iconborder.", "skin.", "playComboJudge.", "playBackground.", "playDeco.", "playGear.", 
    "playHitEffect.", "playNote.", "playPulseEffect.", "emoticon.", "playScouter.", "sfx.", "title.", "character.",
    "missionclearticket.", "fragment", "darkmatter", "astralorgel", "astralmelody"
]

def starts_with_any(key, prefixes):
    return any(key.startswith(prefix) for prefix in prefixes)

async def process_star_item(product_pk):
    result = 0
    random_product_query = randomProductPercentages.select().where(randomProductPercentages.c.ProductPk == product_pk)
    random_products = await manifest_database.fetch_all(random_product_query)
    percentages = [dict(row) for row in random_products]
    total_weight = sum(item['appearProportion'] for item in percentages)
    random_float = random.uniform(0, total_weight)
    cumulative_percentage = 0.0
    for percentage in percentages:
        cumulative_percentage += percentage['appearProportion']
        if random_float <= cumulative_percentage:
            item_query = items.select().where(items.c.key == percentage['itemKey'])
            item = await manifest_database.fetch_one(item_query)
            if not item:
                return None
            result = percentage['value']
            break
    return result

async def buy_product(request: Request):
    product_pk = request.path_params["product"]
    user, user_profile, error = await get_user_and_validate_session(request)
    if error:
        return error
    
    form = await request.form()
    is_subscription = int(form.get("isSubscription", 0))
    amount = int(form.get("amount", 1))

    product_query = products.select().where(products.c.pk == product_pk)
    target_product = await manifest_database.fetch_one(product_query)
    target_product = dict(target_product) if target_product else None
    if not target_product:
        return JSONResponse({"message": "Product not found"}, status_code=404)

    target_category = target_product['category']
    product_item = []
    item_queue = {}

    for a in range(amount):
        product_item.extend(target_product['items'])
        product_item.extend(target_product['bonus'])
        item_queue[target_product['moneyType']] = item_queue.get(target_product['moneyType'], 0) - target_product['price']

    can_buy = await check_item_entitlement(user['pk'], item_queue)
    if not can_buy:
        message = "Insufficient funds."
        data = {}

    else:
        existing_product = await get_user_product(user['pk'], product_pk)
        if existing_product and target_category not in [0, 5, 6, 200, 900]:
            return JSONResponse({"message": "Product already owned"}, status_code=400)

        for tgt_item in product_item:
            product_key = tgt_item['key']
            product_value = tgt_item['value']
            if starts_with_any(product_key, PACK_PREFIXES):
                pack_item_queue = await add_packs(user['pk'], product_key)
                item_queue = combine_queues(item_queue, pack_item_queue)

            elif starts_with_any(product_key, CHARACTER_PREFIXES):
                character_key, default_character_key = await add_root_characters(user['pk'], product_key)
                if character_key:
                    item_queue[character_key] = 1
                    #item_queue[default_character_key] = 1

            elif starts_with_any(product_key, TRACK_PREFIXES):
                track_item_queue = await add_tracks(user['pk'], product_key)
                item_queue = combine_queues(item_queue, track_item_queue)

            elif target_product['key'] == "star.fragment_ad":
                result = await process_star_item(product_pk)
                item_queue['fragment'] = item_queue.get('fragment', 0) + result

            elif starts_with_any(product_key, ITEM_PREFIXES):
                item_queue[product_key] = item_queue.get(product_key, 0) + product_value

            else:
                print(f"Unknown product key prefix, skipping: {product_key}")

        if existing_product:
            if target_product['refreshPeriod'] in ['weekly', 'daily']:
                user_product_update = userProducts.update().where(userProducts.c.pk == existing_product['pk']).values(
                    buyCount = existing_product['buyCount'] + amount,
                    periodicBuyCount = existing_product['periodicBuyCount'] + amount,
                    updatedAt = datetime.now(timezone.utc)
                )
            else:
                user_product_update = userProducts.update().where(userProducts.c.pk == existing_product['pk']).values(
                    buyCount = existing_product['buyCount'] + amount,
                    updatedAt = datetime.now(timezone.utc)
                )
            await player_database.execute(user_product_update)
        else:
            if target_product['refreshPeriod'] in ['weekly', 'daily']:
                user_product_insert = userProducts.insert().values(
                    periodicBuyCount = 1,
                    lastPeriodicRefreshDate = datetime.now(timezone.utc),
                    UserPk = user['pk'],
                    ProductPk = product_pk,
                    buyCount = 1,
                    createdAt = datetime.now(timezone.utc),
                    updatedAt = datetime.now(timezone.utc)
                )
            else:
                user_product_insert = userProducts.insert().values(
                    periodicBuyCount = 0,
                    lastPeriodicRefreshDate = None,
                    UserPk = user['pk'],
                    ProductPk = product_pk,
                    buyCount = 1,
                    createdAt = datetime.now(timezone.utc),
                    updatedAt = datetime.now(timezone.utc)
                )
            await player_database.execute(user_product_insert)

        latest_user_product = await get_user_product(user['pk'], product_pk)
        
        message = "Success."
        data = {
            "userproduct": latest_user_product,
            "randomItems": []
        }

    json_data, completed_ach = await get_standard_response(user, user_profile, item_list=item_queue)
    json_data['message'] = message
    json_data['data'] = data

    json_data = convert_datetime(json_data)
    return JSONResponse(json_data)

async def buy_product_bundle(request: Request):
    product_bundle_pk = request.path_params["product_bundle"]
    user, user_profile, error = await get_user_and_validate_session(request)
    if error:
        return error
    
    form = await request.form()
    is_subscription = int(form.get("isSubscription", 0))
    amount = int(form.get("amount", 1))

    product_bundle_query = productBundles.select().where(productBundles.c.pk == product_bundle_pk)
    target_product_bundle = await manifest_database.fetch_one(product_bundle_query)
    target_product_bundle = dict(target_product_bundle) if target_product_bundle else None
    if not target_product_bundle:
        return JSONResponse({"message": "Product bundle not found"}, status_code=400)
    
    products = target_product_bundle['productKeys']

    # STUB


route = [
    Route("/api/buy/product/{product}", buy_product, methods=["POST"]),
    Route("/api/productbundle/buy/{product_bundle}", buy_product_bundle, methods=["POST"]),
]