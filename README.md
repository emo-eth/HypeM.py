# HypeM.py

This is a python wrapper for the public HypeMachine API, as documented here: <https://api.hypem.com/api-docs/>

This wrapper implements all endpoints listed. Documentation is provided in the form of docstrings, as documented by HypeM. Functions are named after their `nicknames` in the documentation. The nicknames aren't always good, so more useful names have been added as aliases. Assertion statements give helpful errors for parameters that only take certain values.  
These methods are largely generated programmatically from the raw json provided on the site, with a couple manual assertion statements.  

# Getting Started

## Installation

Install using `pip install HypeM.py`  

## Usage

For account-authenticated methods, you can pass in a `username`+`password` and/or `hm_token`
```
>>> hm = HypeM(user, pass)
or
>>> hm = HypeM(hm_token=hm_token)
or
>>> hm = HypeM()
>>> hm.get_token(user, pass)
```
Or even sign up, if you haven't:
```
>>> hm = HypeM()
>>> hm.signup(user, email, pass, newsletter=False)
```
Any of the above are good enough for authenticated methods.
```
>>> hm.friends_me()
# this should print out a list of your friends
```
Methods that don't modify an account directly are unauthenticated.
```
>>> hm.list_blogs_count()
# this should print out current # of blogs indexed by HypeM
>>> hm.list_blogs()
# list of blogs with metadata currently indexed by Hypem
>>> hm.get_blog_tracks(hm.test_blog)
# list of tracks for When The Horn Blows
```  

Default `count` is `20`.  

# Aliases

HypeM Nicknames for operations can be terrible. Here are the aliases I've added manually:  
(Note: These are not all methods available, just the ones whose names weren't very informative)


```
get_popular_artists = popular_artists
get_artist = get_artist_info
get_blogs = list_blogs
get_blogs_count = list_blogs_count
get_blog = get_site_info
get_featured = featured
get_my_favorites = favorites_me
favorite_track = toggle_favorite
get_my_playlist = playlist_me
add_to_playlist = add_playlist
remove_from_playlist = remove_playlist
get_my_history = history_me
get_my_friends = friends_me
get_my_feed = feed
get_my_unread = feed_count
reset_my_unread = reset_feed_count
get_tags = list_tags
get_tracks = latest
get_track = item
get_track_blogs = item_blogs
get_track_favorites = item_users
get_popular = popular
get_user_playlist = playlis  # I think they forgot to finish writing this one
```

# Unofficial Methods

HypeM.py impelements a couple methods that scrape directly from the HypeM website. As such, be considerate when using them.  

`get_track_tags` gets the tags listed for a given `track_id`.  
`get_track_stream` gets a direct link to the .mp3 file for a given `track_id` (usually hosted on SoundCloud).

# Issues
The HypeM backend is a little temperamental, so don't try to load too many things with `count` >~6000, otherwise you should probably expect an error. Just use a smaller `count` with more `pages`.  
It also can be inconsistent, e.g. the `total_tracks` listed for a blog in `get_site_info` isn't necessarily correct (in the case of Indie Shuffle, it can be wrong by thousands).  

I'm pretty sure `get_tag_info` isn't a real function, since in the documentation, it's exacly the same as `get_site_info` (name + description included). That, and it doesn't work.  

Otherwise, enjoy!
