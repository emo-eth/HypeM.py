assert any(fb_uid, fb_oauth_token, tw_oauth_token,
           tw_oauth_token_secret), 'Must provide at least one valid token'
if tw_oauth_token or tw_oauth_token_secret:
    assert tw_oauth_token and tw_oauth_token_secret, 'Must provide both twitter token and secret'