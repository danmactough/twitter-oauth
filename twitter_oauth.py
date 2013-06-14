#! /usr/bin/env python
# coding:utf-8

'''
A module that provide a Python interface to the Twitter API
'''

# to use OAuth
import oauth2 as oauth

# import urllib for using urllib.urlencode when using 'POST' method 
import urllib

# to parse json
try:
    import json
except:
    # for python 2.5
    import simplejson as json 

# to use datetime.datetime, datetime.timedelta class
import datetime

# next modules are used in GetOauth class
import webbrowser
import urlparse



# Tiwtter Api URL
_UPDATE_URL = 'http://api.twitter.com/1/statuses/update.json'
_FRIENDS_TIMELINE_URL = 'http://api.twitter.com/1/statuses/friends_timeline.json'
_USER_TIMELINE_URL = 'http://api.twitter.com/1/statuses/user_timeline.json'
_REPLIES_URL = 'http://api.twitter.com/1/statuses/replies.json'
_SHOW_STATUS_URL = 'http://api.twitter.com/1/statuses/show/%s.json'
_DESTROY_URL = 'http://api.twitter.com/1/statuses/destroy/%s.json'
_LIST_STATUS_URL = 'http://api.twitter.com/1/%s/lists/%s/statuses.json'
_CREATE_FRIENDSHIP_URL = 'http://api.twitter.com/1/friendships/create/%s.json'
_DESTROY_FRIENDSHIP_URL = 'http://api.twitter.com/1/friendships/destroy/%s.json'
_SEARCH_USER_URL = 'http://api.twitter.com/1/users/search.json'
_SHOW_USER_URL = 'http://api.twitter.com/1/users/show/%s.json'
_SEARCH_URL = 'http://search.twitter.com/search.json'


# these constants are used in the GetOuath class.
_REQUEST_TOKEN_URL = 'http://twitter.com/oauth/request_token'
_ACCESS_TOKEN_URL = 'http://twitter.com/oauth/access_token'
_AUTHORIZE_URL = 'http://twitter.com/oauth/authorize'




class GetOauth:
    '''
    A class for getting consumer_key and consumer_secret.
    '''

    def __init__(self, consumer_key, consumer_secret):
        '''
        GetOauth initializer.
        '''
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret

    # for python2.5
    def _parse_qsl(self, url):
        '''
        Parse_qsl method.

        for python 2.5
        '''
        param = {}
        for i in url.split('&'):
            p = i.split('=')
            param.update({p[0]:p[1]})
        return param
    
    def get_oauth(self):
        '''
        Get consumer_key and consumer_secret.

        How to use:
        
        >>> import twitter_oauth
        >>> consumer_key = '***'
        >>> consumer_secret = '***'
        >>> get_oauth_obj = twitter_oauth.GetOauht(consumer_key, consumer_secret)
        >>> get_oauth_obj.get_oauth()
        '''

        consumer = oauth.Consumer(self.consumer_key, self.consumer_secret)
        client = oauth.Client(consumer)
        
        #Step1: Get a request token.
        resp, content = client.request(_REQUEST_TOKEN_URL, "GET")
        if resp['status'] != '200':
            raise Exception('Invalid response %s' % resp['status'])
    
        request_token = dict(self._parse_qsl(content))
        
        print "Request Token:"
        print "  - oauth_token        = %s" % request_token['oauth_token']
        print "  - oauth_token_secret = %s" % request_token['oauth_token_secret']
    
    
        #step2 Redirect to the provider
    
        print "Go to the following link in your browser"
        print '%s?oauth_token=%s' % (_AUTHORIZE_URL, request_token['oauth_token'])
        print 
    
        webbrowser.open('%s?oauth_token=%s' % (_AUTHORIZE_URL, request_token['oauth_token']))
    
        # accepted = 'n'
        # while accepted != 'y':
        #     accepted = raw_input('Have you authorized me? (y/n) ')
    
        oauth_verifier = raw_input('What is the PIN? ')
    
        #step3
        token = oauth.Token(request_token['oauth_token'], 
                            request_token['oauth_token_secret'])
        token.set_verifier(oauth_verifier)
        client = oauth.Client(consumer, token)
    
        resp, content = client.request(_ACCESS_TOKEN_URL, "POST")
        access_token = dict(self._parse_qsl(content))

        oauth_token = access_token['oauth_token']
        oauth_token_secret = access_token['oauth_token_secret']
        
        print "Access Token:"
        print "  - oauth_token        = %s" % oauth_token
        print "  - oauth_token_secret = %s" % oauth_token_secret
        print
        print "You may now access protected resources using the access token above"
        print
     
        return {'consumer_key':self.consumer_key, 
                'consumer_secret':self.consumer_secret, 
                'oauth_token':oauth_token, 
                'oauth_token_secret':oauth_token_secret}




class JsonParser:
    def __init__(self):
        pass

    def set_value(self, res, value):
            if res.has_key(value):
                try:
                    return res[value].decode('utf-8')
                except:
                    return res[value]
            else:
                return None


    def create_search_info(self, search_dict):
        '''
        search_dict is a json dictionary got from twitter
        >>> create_search_info(json.loads(json_str))
        '''
        return SearchInfo(self.create_tweet_info(search_dict['results']),
                          self.set_value(search_dict,'max_id'), self.set_value(search_dict,'since_id'),
                          self.set_value(search_dict,'refresh_url'), self.set_value(search_dict, 'next_page'), self.set_value(search_dict,'results_per_page'),
                          self.set_value(search_dict,'page'), self.set_value(search_dict,'completed_in'), self.set_value(search_dict,'query'))

    def create_tweet_info(self, results):
        '''
        results = json.loads(search_json)['results']

        to_userキーを持つ時と持たない時がある...
        '''
        return [TweetInfo(self.set_value(res, 'created_at'),self.set_value(res,'id'),self.set_value(res,'text'),
                          self.set_value(res,'from_user'),self.set_value(res,'from_user_id'),
                          self.set_value(res,'to_user'),self.set_value(res,'to_user_id'),self.set_value(res,'profile_image_url'),
                          self.set_value(res,'geo'), self.set_value(res,'iso_language_code'), self.set_value(res,'source')) for res in results]


    def create_status_object(self,status_dict):
        '''
        >>> create_status_object(json.loads(json_str))
        '''

        status_obj = Status(created_at=self.set_value(status_dict, 'created_at'), 
                            id=self.set_value(status_dict, 'id'), 
                            text=self.set_value(status_dict, 'text'),
                            source=self.set_value(status_dict, 'source'),
                            truncated=self.set_value(status_dict, 'truncated'), 
                            in_reply_to_status_id=self.set_value(status_dict, 'in_reply_to_status_id'),
                            in_reply_to_user_id=self.set_value(status_dict, 'in_reply_to_user_id'),
                            favorited=self.set_value(status_dict, 'favorited'), 
                            user=self.create_user_object(status_dict['user']),
                            geo=self.set_value(status_dict, 'geo'),
                            contributors=self.set_value(status_dict, 'contributors'))

        return status_obj




    def create_user_object(self, user_dict):
        '''
        >>> create_user_object(json.loads(json_str))
        '''
    
        user_obj = User(id=self.set_value(user_dict, 'id'), name=self.set_value(user_dict, 'name'),
                        screen_name=self.set_value(user_dict, 'screen_name'), 
                        created_at=self.set_value(user_dict, 'created_at'),
                        location=self.set_value(user_dict, 'location'),
                        description=self.set_value(user_dict, 'description'),
                        url=self.set_value(user_dict, 'url'),
                        protected=self.set_value(user_dict, 'protected'), 
                        followers_count=self.set_value(user_dict, 'followers_count'),
                        friends_count=self.set_value(user_dict, 'friends_count'), 
                        favourites_count=self.set_value(user_dict, 'favourites_count'),
                        statuses_count=self.set_value(user_dict, 'statuses_count'),
                        profile_image_url=self.set_value(user_dict, 'profile_image_url'),
                        profile_background_color=self.set_value(user_dict, 'profile_background_color'),
                        profile_text_color=self.set_value(user_dict, 'profile_text_color'),
                        profile_link_color=self.set_value(user_dict, 'profile_link_color'),
                        profile_sidebar_fill_color=self.set_value(user_dict, 'profile_sidebar_fill_color'),
                        profile_sidebar_border_color=self.set_value(user_dict, 'profile_sidebar_border_color'),
                        profile_background_image_url=self.set_value(user_dict, 'profile_background_image_url'),
                        profile_background_tile=self.set_value(user_dict, 'profile_background_tile'),
                        utc_offset=self.set_value(user_dict, 'utc_offset'),
                        time_zone=self.set_value(user_dict, 'time_zone'),
                        lang=self.set_value(user_dict, 'lang'),
                        geo_enabled=self.set_value(user_dict, 'geo_enabled'),
                        verified=self.set_value(user_dict, 'verified'),
                        notifications=self.set_value(user_dict, 'notifications'),
                        following=self.set_value(user_dict, 'following'), 
                        contributors_enabled=self.set_value(user_dict, 'contributors_enabled'))

        return user_obj


    def create_user_object_list(self, user_list):
        '''
        Create a User object list from xml.getElementsByTagName('user')
        '''
        return [self.create_user_object(i) for i in user_list]

    def create_status_object_list(self, status_list):
        return [self.create_status_object(i) for i in status_list]

    
class SearchInfo:
    def __init__(self, results, max_id, since_id,
                 refresh_url, next_page, results_per_page,
                 page, completed_in, query):
    
        self.results = results
        self.max_id = max_id
        self.since_id = since_id
        self.refresh_url = refresh_url
        self.next_page = next_page
        self.results_per_page = results_per_page
        self.page = page
        self.completed_in = completed_in
        self.query = query


class TweetInfo:
    def __init__(self, created_at, id, text,
                 from_user, from_user_id, to_user,
                 to_user_id, profile_image_url, geo,
                 iso_language_code, source):
        
        self.created_at = created_at
        self.id = id
        self.text = text
        self.from_user = from_user
        self.from_user_id = from_user_id
        self.to_user = to_user
        self.to_user_id = to_user_id
        self.profile_image_url = profile_image_url
        self.geo = geo
        self.iso_language_code = iso_language_code
        self.source = source



    def _create_datetime_obj(self, utc_datetime):
        '''
        Create datetime object
        
        
        Thu, 14 Oct 2010 08:35:44 +0000 <type 'str'>
            
        input : utc_datetime = u'Sun Jul 25 14:12:06 +0000 2010'
        return : str(datetime.datetime(2010,07,26,23,12)
        '''
        month_str = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 
                     'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}
        
        


        sub = utc_datetime.split()
        utc_datetime_list = [sub[0][:-1], sub[2], sub[1], sub[4], sub[5], sub[3]]
        utc_time = utc_datetime_list[3].split(':')

        utc_now = datetime.datetime(int(utc_datetime_list[5]), 
                                    int(month_str[utc_datetime_list[1]]),
                                    int(utc_datetime_list[2]),
                                    int(utc_time[0]),
                                    int(utc_time[1]))

                                              
        return utc_now


    def get_created_at_from_now(self):
        '''
        When created from now
        '''

        t = datetime.datetime.utcnow() - self._create_datetime_obj(self.created_at)
        
        day = t.days
        sec = t.seconds
        min = sec / 60
        hour = min / 60
        
        
        if t.days >= 1:
            return u'%s days ago' % str(day)
        elif hour >= 1:
            return u'%s hours ago' % str(hour)
        elif min >= 1:
            return u'%s minutes ago' % (str(min))
        else:
            return u'%s seconds ago' % (str(sec))
        

        



    def get_created_at_in_utc(self):
        '''
        return datetime.datetime object in UTC
        '''

        return self._create_datetime_obj(self.created_at)
    
    def get_created_at_in_jsp(self):
        '''
        return datetime.datetime object in JSP
        '''

        return self._create_datetime_obj(self.created_at) + datetime.timedelta(hours=9)

    



class Status:
    '''
    A class representing a status.

    The Status class have next attributes:

        stauts.created_at
        stauts.id
        stauts.text
        stauts.source
        stauts.truncated
        stauts.in_reply_to_status_id
        stauts.in_reply_to_user_id
        stauts.favorited
        stauts.user
        stauts.geo
        stauts.contributors

    The Status class have next methods:

        status.get_created_at_from_now()
        status.get_created_at_in_utc()
        status.get_created_at_in_jsp()

    '''

    def __init__(self, 
                 created_at=None, id=None, text=None,
                 source=None, truncated=None, in_reply_to_status_id=None,
                 in_reply_to_user_id=None,
                 favorited=None, user=None,
                 geo=None, contributors=None):
        '''
        Status class initializer.
        '''
        
        self.created_at = created_at
        self.id = id
        self.text = text
        self.source = source
        self.truncated = truncated
        self.in_reply_to_status_id = in_reply_to_status_id
        self.in_reply_to_user_id = in_reply_to_user_id
        self.favorited = favorited
        self.user = user
        self.geo = geo
        self.contributors = contributors

    def _create_datetime_obj(self, utc_datetime):
        '''
        Create datetime object
        
        
        input : utc_datetime = u'Sun Jul 25 14:12:06 +0000 2010'
        return : str(datetime.datetime(2010,07,26,23,12)
        '''
        month_str = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 
                     'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}
        
        
        utc_datetime_list = utc_datetime.split()
        utc_time = utc_datetime_list[3].split(':')

        utc_now = datetime.datetime(int(utc_datetime_list[5]), 
                                    int(month_str[utc_datetime_list[1]]),
                                    int(utc_datetime_list[2]),
                                    int(utc_time[0]),
                                    int(utc_time[1]))

                                              
        return utc_now


    def get_created_at_from_now(self):
        '''
        When created from now
        '''

        t = datetime.datetime.utcnow() - self._create_datetime_obj(self.created_at)
        
        day = t.days
        sec = t.seconds
        min = sec / 60
        hour = min / 60
        
        
        if t.days >= 1:
            return u'%s days ago' % str(day)
        elif hour >= 1:
            return u'%s hours ago' % str(hour)
        elif min >= 1:
            return u'%s minutes ago' % (str(min))
        else:
            return u'%s seconds ago' % (str(sec))
        

        



    def get_created_at_in_utc(self):
        '''
        return datetime.datetime object in UTC
        '''

        return self._create_datetime_obj(self.created_at)
    
    def get_created_at_in_jsp(self):
        '''
        return datetime.datetime object in JSP
        '''

        return self._create_datetime_obj(self.created_at) + datetime.timedelta(hours=9)

class User:
    '''
    A class representing User.

    The User class have next attributes:

        user.id
        user.name
        user.screen_name
        user.created_at
        user.location
        user.description
        user.url
        user.protected
        user.followers_count
        user.friends_count
        user.favourites_count
        user.statuses_count
        user.profile_image_url
        user.profile_background_color
        user.profile_text_color
        user.profile_link_color
        user.profile_sidebar_fill_color
        user.profile_sidebar_border_color
        user.profile_background_image_url
        user.profile_background_tile
        user.utc_offset
        user.time_zone
        user.lang
        user.geo_enabled
        user.verified
        user.notifications
        user.following
        user.contributors_enabled


    The Status class have next methods:

        status.get_created_at_in_utc()
        status.get_created_at_in_jsp()

    '''
    def __init__(self, 
                 id=None, name=None, screen_name=None, 
                 created_at=None, location=None, description=None,
                 url=None, protected=None, followers_count=None, friends_count=None, 
                 favourites_count=None, statuses_count=None, profile_image_url=None,
                 profile_background_color=None, profile_text_color=None,
                 profile_link_color=None, profile_sidebar_fill_color=None,
                 profile_sidebar_border_color=None,
                 profile_background_image_url=None,
                 profile_background_tile=None,
                 utc_offset=None, time_zone=None, lang=None, geo_enabled=None,
                 verified=None, notifications=None, following=None, 
                 contributors_enabled=None):

        self.id = id
        self.name = name
        self.screen_name = screen_name
        self.created_at = created_at
        self.location = location
        self.description = description
        self.url = url
        self.protected = protected
        self.followers_count = followers_count
        self.friends_count = friends_count
        self.favourites_count = favourites_count
        self.statuses_count = statuses_count
        self.profile_image_url = profile_image_url
        self.profile_background_color = profile_background_color
        self.profile_text_color = profile_text_color
        self.profile_link_color = profile_link_color
        self.profile_sidebar_fill_color = profile_sidebar_fill_color
        self.profile_sidebar_border_color = profile_sidebar_border_color
        self.profile_background_image_url = profile_background_image_url
        self.profile_background_tile = profile_background_tile
        self.utc_offset = utc_offset
        self.time_zone = time_zone
        self.lang = lang
        self.geo_enabled = geo_enabled
        self.verified = verified
        self.notifications = notifications
        self.following = following
        self.contributors_enabled = contributors_enabled

    def _create_datetime_obj(self, utc_datetime):
        '''
        Create a datetime object.
        
        
        input : utc_datetime = u'Sun Jul 25 14:12:06 +0000 2010'
        return : str(datetime.datetime(2010,07,26,23,12)
        '''
        month_str = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 
                     'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}
        
        
        utc_datetime_list = utc_datetime.split()
        utc_time = utc_datetime_list[3].split(':')

        utc_now = datetime.datetime(int(utc_datetime_list[5]), 
                                    int(month_str[utc_datetime_list[1]]),
                                    int(utc_datetime_list[2]),
                                    int(utc_time[0]),
                                    int(utc_time[1]))

                                              
        return utc_now


    # def get_created_at_from_now(self):
    #     '''
    #     return datetime.timedelta object
        
    #     使用例
    #     t = get_created_at_from_now()
    #     [t.days, t.seconds]
    #     '''
    #     t = datetime.datetime.utcnow() - self._create_datetime_obj(self.created_at)
    #     #return [t.days, t.seconds]
    #     return t
    

    def get_created_at_in_utc(self):
        '''
        return datetime.datetime object in UTC
        '''
        return self._create_datetime_obj(self.created_at)
    
    def get_created_at_in_jsp(self):
        '''
        return datetime.datetime object in JSP
        '''
        return self._create_datetime_obj(self.created_at) + datetime.timedelta(hours=9)

    
class TwitterError(Exception):
    '''
    A class representing twitter error.

    A TwitterError is raised when a status code is not 200 returned from Twitter.
    '''
    
    def __init__(self, status=None, content=None):
        '''
        res : status code
        content : XML
        '''
        Exception.__init__(self)
        
        self.status = status
        self.content = content

    def get_response(self):
        '''
        Return status code
        '''

        return self.status
		
    def get_content(self):
        '''
        Return XML.
        '''

    def __str__(self):
        return 'status_code:%s' % self.status
        



class Api:
    '''
    A Python interface to the Twitter API

    How To Use:

    First, you shold have two keys, 
    'consumer key', 'consumer secret'.

    If you don't have 'consumer key' and 'consumer secret', 
    you cat get these keys to register your application to Twitter.
    You cat register your application at next URL.

    http://twitter.com/apps



    Second, you shold get two keys,
    'oauth_token', and 'oauth_token_secret'

    To get these keys, you use GetOauth class in this module.

    >>> import twitter_oauth

    >>> # write your key and secret
    >>> consumer_key = '***'
    >>> consumer_secret = '***'

    >>> get_oauth_obj = twitter_oauth.GetOauth(consumer_key, consumer_secret)


    Then, you get 'oauth_token' and 'oauth_token_secret' by using get_oauth method.
    This method returns a dictionary that contain 'consumer key', 'consumer secret',
    'oauth_token' and 'oauth_token_secret'


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
     


    Now, you can use twitter_oauth.Api class.
    To use this class, you can post update, or get friends timeline, etc...
    
    Next example is how to use twitter_oauth.Api class


    >>> # import twitter_oauth module
    >>> import twitter_oauth

    write yoru consumer_key, consumer_secret,
    oauth_token, oauth_token_secret

    >>> consumer_key = '***'
    >>> consumer_secret = '***'
    >>> oauth_token        = '***'
    >>> oauth_token_secret = '***'

    Then, create Api instance

    >>> api = twitter_oauth.Api(consumer_key, consumer_secret,
    >>>                         oauth_token, oauth_token_secret)

    Use get_friends_timeline method.
    You can get friends timeline to use this method.

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

    >>> post_update(u'Hello, Twitter')


    Methods:
        You can use next methods

        status
        ------
        post_update()
        show_status()
        destroy_status()

        timeline
        --------
        get_user_timeline()
        get_friends_timeline()
        get_replies()
        
        list
        ----
        get_list_status()

        friendship
        ----------
        create_friendship()
        destroy_friendship()

        user
        ----
        search_user()
        show_user()

        search
        ------
        search()

        

    '''



    def __init__(self,
                 consumer_key, consumer_secret,
                 oauth_token, oauth_token_secret):
        '''
        The Api class initializer.
        '''

        self.json_parser = JsonParser()

        self.client = oauth.Client(oauth.Consumer(consumer_key, consumer_secret),
                              oauth.Token(oauth_token, oauth_token_secret))

    def post_update(self, tweet, in_reply_to_status_id=None, lat=None, long=None,
                    place_id=None, display_doordinates=None, source=None):
        '''
        Post your tweet.
        '''



        arg_dict = {'in_reply_to_status_id':in_reply_to_status_id,
                    'lat':lat,
                    'long':long,
                    'place_id':place_id,
                    'display_doordinates':display_doordinates,
                    'source':source}
       
        url_param_dict = {}

        for (key, item) in arg_dict.iteritems():
            if item != None:
                url_param_dict.update({key: item})
    

        param = urllib.urlencode(url_param_dict)
        if param:
            url = _UPDATE_URL + '?' + param
        else:
            url = _UPDATE_URL

        res, content = self.client.request(url, 'POST', 
                                      urllib.urlencode({'status' : tweet.encode('utf-8')}))

        if res['status'] != '200':
            raise TwitterError(res['status'], content)
        else:
            # parse XML
            return self.json_parser.create_status_object(json.loads(content))
        
   
        

    def get_user_timeline(self, id=None, since_id=None, max_id=None,
                             count=None, page=None):
        
        # parse args
        arg_dict = {'id':id , 'since_id':since_id, 'max_id':max_id,
                    'count':count, 'page':page}

        url_param_list = []

        for (key, item) in arg_dict.iteritems():
            if item != None:
                url_param_list.append(key + '=' + str(item))

        # create URL. append querry to a URL
        param = '&'.join(url_param_list)
        if param:
            url = _USER_TIMELINE_URL + '?' + param
        else:
            url = _USER_TIMELINE_URL


        # GET request to Twitter
        res, content = self.client.request(url, 'GET')


        if res['status'] != '200':
            raise TwitterError(res['status'], content)
        else:
            # parse XML
            return self.json_parser.create_status_object_list(json.loads(content))
         
        

    def get_friends_timeline(self, id=None, since_id=None, max_id=None,
                             count=None, page=None):
        
        # parse args
        arg_dict = {'id':id , 'since_id':since_id, 'max_id':max_id,
                    'count':count, 'page':page}

        url_param_list = []

        for (key, item) in arg_dict.iteritems():
            if item != None:
                url_param_list.append(key + '=' + str(item))

        # create URL. append querry to a URL
        param = '&'.join(url_param_list)
        if param:
            url = _FRIENDS_TIMELINE_URL + '?' + param
        else:
            url = _FRIENDS_TIMELINE_URL


        # GET request to Twtter
        res, content = self.client.request(url, 'GET')


        if res['status'] != '200':
            raise TwitterError(res['status'], content)
        else:
            # parse XML
            return self.json_parser.create_status_object_list(json.loads(content))




    def get_replies(self, id=None, since_id=None, max_id=None,
                    count=None, page=None):

        # parse args
        arg_dict = {'id':id , 'since_id':since_id, 'max_id':max_id,
                    'count':count, 'page':page}

        url_param_list = []

        for (key, item) in arg_dict.iteritems():
            if item != None:
                url_param_list.append(key + '=' + str(item))

        # create URL. append querry to a URL
         
        param = '&'.join(url_param_list)
        if param:
            url = _REPLIES_URL + '?' + param
        else:
            url = _REPLIES_URL 


        # GET request to Twitter
        res, content = self.client.request(url, 'GET')


        if res['status'] != '200':
            raise TwitterError(res['status'], content)
        else:
            # parse XML
            return self.json_parser.create_status_object_list(json.loads(content))

    def show_status(self, id):
        '''
        get status which has a id
        '''

        # create url
        url = _SHOW_STATUS_URL % id

        res, content = self.client.request(url, 'GET')

        if res['status'] != '200':
            raise TwitterError(res['status'], content)
        else:
            # parse XML
            return self.json_parser.create_status_object(json.loads(content))
   

    def destroy_status(self, id):
        
        # create URL. Append querry to a URL
        url = _DESTROY_URL % id

        # POST request to Twitter
        res, content = self.client.request(url, 'POST')



        if res['status'] != '200':
            raise TwitterError(res['status'], content)
        else:
            # parse XML
            return self.json_parser.create_status_object(json.loads(content))

        



    def get_list_status(self, user, list_id, since_id=None, max_id=None, per_page=None):
        
        # parse args
        arg_dict = {'list_id':list_id , 'since_id':since_id, 'max_id':max_id,
                    'per_page':per_page}

        url_param_list = []

        for (key, item) in arg_dict.iteritems():
            if item != None:
                url_param_list.append(key + '=' + str(item))

        # create URL. append querry to a URL
        #
        # _LIST_STATUS_URL = 'http://api.twitter.com/1/%s/lists/%s/statuses.xml'
        param = '&'.join(url_param_list)
        if param:
            url = (_LIST_STATUS_URL % (user, list_id)) + '?' + param
        else:
            url = _LIST_STATUS_URL % (user, list_id)


        # GET request to Twtter
        res, content = self.client.request(url, 'GET')


        if res['status'] != '200':
            raise TwitterError(res['status'], content)
        else:
            # parse XML
            return self.json_parser.create_status_object_list(json.loads(content))
            


    def create_friendship(self, id, follow=None):
                            #user_id=None, screen_name=None  

        arg_dict = {'follow':follow}

        url_param_list = []

        for (key, item) in arg_dict.iteritems():
            if item != None:
                url_param_list.append(key + '=' + str(item))

        # create URL. append querry to a URL
        #
        # _LIST_STATUS_URL = 'http://api.twitter.com/1/%s/lists/%s/statuses.xml'
        param = '&'.join(url_param_list)
        if param:
            url = (_CREATE_FRIENDSHIP_URL % id) + '?' + param
        else:
            url = _CREATE_FRIENDSHIP_URL % id


        # GET request to Twtter
        res, content = self.client.request(url, 'POST')


        if res['status'] != '200':
            raise TwitterError(res['status'], content)
        else:
            # parse XML
            return self.json_parser.create_user_object(json.loads(content))


    def destroy_friendship(self, id):
                            #user_id=None, screen_name=None  

        arg_dict = {}

        url_param_list = []

        for (key, item) in arg_dict.iteritems():
            if item != None:
                url_param_list.append(key + '=' + str(item))

        # create URL. append querry to a URL
        #
        # _LIST_STATUS_URL = 'http://api.twitter.com/1/%s/lists/%s/statuses.xml'
        param = '&'.join(url_param_list)
        if param:
            url = (_DESTROY_FRIENDSHIP_URL % id) + '?' + param
        else:
            url = _DESTROY_FRIENDSHIP_URL % id


        # GET request to Twtter
        res, content = self.client.request(url, 'POST')


        if res['status'] != '200':
            raise TwitterError(res['status'], content)
        else:
            # parse XML
            return self.json_parser.create_user_object(json.loads(content))

  
    def search_user(self, q, per_page=None, page=None):
                            #user_id=None, screen_name=None  
        '''
        q:unicode
        '''

        arg_dict = {'q':q.encode('utf-8'), 'per_page':per_page, 'page':page}

        url_param_dict = {}

        for (key, item) in arg_dict.iteritems():
            if item != None:
                url_param_dict.update({key: item})

        # create URL. append querry to a URL
        #
        # _LIST_STATUS_URL = 'http://api.twitter.com/1/%s/lists/%s/statuses.xml'
        param = urllib.urlencode(url_param_dict)
        if param:
            url = _SEARCH_USER_URL + '?' + param
        else:
            url = _SEARCH_USER_URL

   

        # GET request to Twtter
        res, content = self.client.request(url, 'GET')


        if res['status'] != '200':
            raise TwitterError(res['status'], content)
        else:
            # parse XML
            return self.json_parser.create_user_object_list(json.loads(content))

    def show_user(self, id):
                 #user_id=None, screen_name=None  

        arg_dict = {}

        url_param_list = []

        for (key, item) in arg_dict.iteritems():
            if item != None:
                url_param_list.append(key + '=' + str(item))

        # create URL. append querry to a URL
        #
        # _LIST_STATUS_URL = 'http://api.twitter.com/1/%s/lists/%s/statuses.xml'
        param = '&'.join(url_param_list)
        if param:
            url = (_SHOW_USER_URL % id) + '?' + param
        else:
            url = _SHOW_USER_URL % id


        # GET request to Twtter
        res, content = self.client.request(url, 'GET')



        if res['status'] != '200':
            raise TwitterError(res['status'], content)
        else:
            # parse XML
            return self.json_parser.create_user_object(json.loads(content))





 
    def search(self, q, callback=None, lang=None, locale=None, 
                rpp=None, page=None, max_id=None, since_id=None,
                since=None, until=None, geocode=None, show_user=None):
        '''
        q:unicode
        '''

        arg_dict = {'q':q.encode('utf-8'), 'callback':callback, 'lang':lang,
                    'locale':locale, 'rpp':rpp, 'page':page, 'max_id':max_id,
                    'since_id':since_id, 'since':since, 'until':until, 
                    'geocode':geocode, 'show_user':show_user}

        url_param_dict = {}

        for (key, item) in arg_dict.iteritems():
            if item != None:
                url_param_dict.update({key: item})

        # create URL. append querry to a URL
        #
        # _LIST_STATUS_URL = 'http://api.twitter.com/1/%s/lists/%s/statuses.xml'
        param = urllib.urlencode(url_param_dict)
        if param:
            url = _SEARCH_URL + '?' + param
        else:
            url = _SEARCH_URL

   

        # GET request to Twtter
        res, content = self.client.request(url, 'GET')


        if res['status'] != '200':
            raise TwitterError(res['status'], content)
        else:
            # parse XML
            return self.json_parser.create_search_info(json.loads(content))
