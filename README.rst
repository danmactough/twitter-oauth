======
README
======

These are four contents.

- License_
- Required_
- Installation_
- Tutorial_
- `Sample Code`_

What is changed from version 0.1.0 to 0.2.0
===========================================

-   Using json data in version 0.2.0
-   You can use more methods in version 0.2.0 than 0.1.0
-   Especially, you can use search methods in version 0.2.0 

License
=======

**Copyright (c) 2010 Kenko Abe**

The MIT License. See the LICENSE.rst for the complete license.


Required
========

Twitter_oauth requires Python 2.x superior to 2.5.


These modules are required.

- oauth2

If you use python 2.5, you also need

- simplejson


Installation
============

On Linux.

install simplejson
-------------------

If you use Python 2.x superior to Python 2.6, skip `install simplejson`_ and go to `install twitter_oauth`_


If you use python2.5, you should install simplejson first.

Download simplejson from `http://pypi.python.org/pypi/simplejson/`_

.. _`http://pypi.python.org/pypi/simplejson/`: http://pypi.python.org/pypi/simplejson/

Then, change the directory which contains simplejson file, and 


::

   $ tar vxzf simplejson-2.1.1.tar.gz
   $ cd simplejson-2.1.1
   $ sudo python setup.py install


install twitter_oauth
---------------------

From PyPI:

::

    $ sudo easy_install twitter_oauth


Tutorial
========

OAuth
------

First, you shold have two keys, 
'consumer key', 'consumer secret'.

If you don't have 'consumer key' and 'consumer secret', 
you cat get these keys to register your application to Twitter.
You cat register your application at next URL.

`http://twitter.com/apps`_

.. _`http://twitter.com/apps`: http://twitter.com/apps




Then, you shold get two keys, 'oauth_token', and 'oauth_token_secret'

To get these keys, you use GetOauth class in this module.

::

    >>> import twitter_oauth

    >>> # write your key and secret
    >>> consumer_key = '***'
    >>> consumer_secret = '***'
    
    >>> get_oauth_obj = twitter_oauth.GetOauth(consumer_key, consumer_secret)


Then, you get 'oauth_token' and 'oauth_token_secret' by using get_oauth method.
This method returns a dictionary that contain 'consumer key', 'consumer secret',
'oauth_token' and 'oauth_token_secret'

::

    >>> get_oauth_obj.get_oauth()
      Request Token:
      - oauth_token        = ***
      - oauth_token_secret = ***
      Go to the following link in your browser
      http://twitter.com/oauth/authorize?oauth_token=***
              
      What is the PIN? ***
      Access Token:
      - oauth_token        = ***
      - oauth_token_secret = ***
              
      You may now access protected resources using the access token above
       
      
Api class
----------
  
Now, you can use twitter_oauth.Api class.
To use this class, you can post update, or get friends timeline, etc...
    
Next example is how to use twitter_oauth.Api class

::

    >>> # import twitter_oauth module
    >>> import twitter_oauth
    
    >>> # write yoru consumer_key, consumer_secret,
    >>> # oauth_token, oauth_token_secret
    >>> consumer_key = '***'
    >>> consumer_secret = '***'
    >>> oauth_token        = '***'
    >>> oauth_token_secret = '***'

    >>> # Then, create Api instance

    >>> api = twitter_oauth.Api(consumer_key, consumer_secret,
    >>>                         oauth_token, oauth_token_secret)

Use get_friends_timeline method.
You can get friends timeline to use this method.

::

    >>> friends_timeline = api.get_friends_timeline()
    >>> print [stauts.text for status in friends_timeline]
    
    Use get_user_timeline method.
    You can get user timeline to use this method.
    
    >>> user_timeline = api.get_user_timeline()
    >>> print [stauts.text for status in user_timeline]
    
    Use get_replies method.
    You can get replies to use this method.
    
    >>> replies = api.get_replies()
    >>> print [stauts.text for status in replies]


Use post_update method 
You can post message to Twitter.

CAUTION : post_update method shold take a unicode.
Especially, you can post a Japanese text.

::

    >>> api.post_update(tweet=u'Hello, Twitter')

Use get_list_status method.

::
    >>> # write username and list name 
    >>> api.get_list_status(user='username', list_id='listname')


Use search method

If you want to show tweets including 'keyword', 

::

    >>> api.search(q='keyword')


If you want to show tweets including 'keyword' and 'anotherkeyword', 

::

    >>> api.search(q='keyword anotherkeyword')


If you want to show tweets including 'keyword' or 'anotherkeyword', 

::

    >>> api.search(q='keyword OR anotherkeyword')

If you want to show  timeline from 'user', 

::

    >>> api.search(q='from:user')

If you want to show tweets to 'user', then

::

    >>> api.search(q='to:user')

If you want to show tweets from 'user' to 'another', then

::

    >>> api.search(q='from:user to:another')

If you want to search tag, 

::

    >>> api.search(q='#twitter')


To know more information about a search method, see the next link.

`http://dev.twitter.com/doc/get/search`_

.. _`http://dev.twitter.com/doc/get/search`: http://dev.twitter.com/doc/get/search

Methods
-------


You can use next methods

-   status
    
    -   post_update()
    -   show_status()
    -   destroy_status()

-   timeline

    -   get_user_timeline()
    -   get_friends_timeline()
    -   get_replies()

-   list

    -   get_list_status()

-   friendship

    -   create_friendship()
    -   destroy_friendship()

-   user

    -   search_user()
    -   show_user()

-   search

    -   search()



Sample Code
===========

::

    #! /usr/bin/env python
    # coding:utf-8
    
    import twitter_oauth
    
    # write your oauth token and oauth token secret
    consumer_key = '***'
    consumer_secret = '***'
    
    # create GetOauth instance
    get_oauth_obj = twitter_oauth.GetOauth(consumer_key, consumer_secret)
    
    # get oauth_token and oauth token secret
    key_dict = get_oauth_obj.get_oauth()
    
    # create Api instance
    api = twitter_oauth.Api(consumer_key, consumer_secret, key_dict['oauth_token'], key_dict['oauth_token_secret'])

    
    ## timeline method
    
    # get friends timeline
    print [status.text for status in api.get_friends_timeline()]
    
    # get user timeline
    print [status.text for status in api.get_user_timeline()]
    
    # get replies
    print [status.text for status in api.get_replies()]


    ## status method
    
    # post update
    api.post_update(tweet=u'Hello, Twitter')

    # show status and destroy status
    status = api.get_user_timeline()[0]

    print api.show_status(id=status.id).text
    api.destroy_status(id=status.id)


    ## friendship method

    api.create_friendship(id='twitter')
    api.destroy_friendship(id='twitter')
    
    
    ## user method 
    print api.show_user(id='twitter').screen_name
    print [user.screen_name for user in api.search_user(q='twitter')]


    ## search method
    
    print [tweet_info.text for tweet_info in api.search(q='#twitter').results]
