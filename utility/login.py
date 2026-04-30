import os
import coc


async def coc_login():
    coc_client: coc.Client = coc.Client(
        base_url='https://proxy.clashk.ing/v1',
        key_count=10,
        key_names='test',
        throttle_limit=500,
        cache_max_size=10_000,
        load_game_data=coc.LoadGameData(default=True),
        raw_attribute=True,
        stats_max_size=10_000,
    )

    coc_tokens = os.getenv('COC_TOKENS')
    if coc_tokens:
        tokens = [token.strip() for token in coc_tokens.split(',') if token.strip()]
        if tokens:
            await coc_client.login_with_tokens(*tokens)
    else:
        print('WARNING: No COC tokens provided; starting without COC login.')

    return coc_client
