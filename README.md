# HypeM.py

This is a python wrapper for the public HypeMachine API, as documented here: <https://api.hypem.com/api-docs/>

This wrapper implements all endpoints listed. Documentation is provided in the form of docstrings, as documented by HypeM. Functions are named after their `nickname`s in the documentation (which aren't always good). Assertion statements give helpful errors for parameters that only take certain values.  
These methods are largely generated programmatically from the raw json provided on the site, with a couple manual assertion statements.

# Getting Started

```
For account-authenticated methods, you can pass in
a username+password and/or hm_token
>>> hm = HypeM(user, pass)
or
>>> hm = HypeM(hm_token=hm_token)
or
>>> hm = HypeM()
>>> hm.get_token(user, pass)
Any of the above are good enough for authenticated methods
>>> hm.friends_me()
# this should print out a list of your friends
The remainder are unauthenticated.
>>> hm.list_blogs_count()
# this should print out current # of blogs indexed by HypeM
>>> hm.list_blogs()
# list of blogs with metadata currently indexed by Hypem

```

