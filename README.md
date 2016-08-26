# HypeM.py

This is a python wrapper for the public HypeMachine API, as documented here: <https://api.hypem.com/api-docs/>

This wrapper implements all endpoints listed. Documentation is provided in the form of docstrings, as documented by HypeM. Functions are named after their `nicknames` in the documentation (which aren't always good). Assertion statements give helpful errors for parameters that only take certain values.  
These methods are largely generated programmatically from the raw json provided on the site, with a couple manual assertion statements.  

# Getting Started


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

# Issues
The HypeM backend is a little temperamental, so don't try to load too many anything with `count` >6000, otherwise you should probably expect an error. Just use a smaller `count` with more `pages`.  
It also can be inconsistent, e.g. the `total_tracks` listed for a blog in `get_site_info` isn't necessarily correct (in the case of Indie Shuffle, it can be wrong by thousands).  

I'm pretty sure `get_tag_info` isn't a real function, since in the documentation, it's exacly the same as `get_site_info` (name + description included). That, and it doesn't work.  

Otherwise, enjoy!
