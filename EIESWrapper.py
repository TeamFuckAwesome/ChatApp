#!/usr/bin/env python3

#
#  Eric McCann 2016
#

from Common import *
printerer.Instance().setPrefixer() #singleton for prefixing prints with file and number

success = False
try:
    import requests,json,time,datetime
    success = True
except:
    print("It seems like your python3 doesn't include requests!\nRun:\n\nsudo apt-get install python3-requests\n\n\n")

debug = False #True

def typeRighter(val):
    try:
        return float(val)
    except:
        pass
    try:
        return int(val)
    except:
        pass
    return val

def typeRightArr(arr):
    return [typeRighter(x) for x in arr]

urlprefix = "https://eies.herokuapp.com"
    
class EIESWrapper:
    def __init__(self, url=None):
        global urlprefix
        if url != None:
            urlprefix = url
        self.baseUrl='%s/api/v1/' % urlprefix
        if debug:
            print("Using %s as base URL for API calls" % self.baseUrl)
        self.user_id = None
        self.session_id = None
        self.session = requests.Session()
        self.logged_in_callback = None

    def __exec(self, operation, page, args):
        global debug
        url = "%s%s" % (self.baseUrl, page)
        if debug:
            import urllib
            enc = None
            try:
                enc = urllib.urlencode
                enc({'test': 0})
            except:
                import urllib.parse
                enc = urllib.parse.urlencode
                enc({'test': 0})
            print("%s %s?%s" % (operation.__name__.upper(), url, enc(args)))
        res = operation(url, data=json.dumps(args), headers={'content-type': 'application/json'})
        if debug:
            jsonmaybe = None
            try:
                jsonmaybe = str(res.json())
            except:
                jsonmaybe = "NOT JSON?"
            print("%s\t%s" % (str(res), jsonmaybe))
        return res

    def SetLoginCallback(self, func):
        self.logged_in_callback = func

    ### BEGIN SESSION
    def Login(self, email, password):
        res = self.__exec(self.session.post, 'login', {'email': email, 'password': password})
        if int(res.status_code) != 200:
            res.close()
            return False
        self.user_id = res.json()['user_id']
        self.session_id = res.json()['session_id']
        if self.logged_in_callback != None:
            self.logged_in_callback(self.user_id)
        return True

    def Logout(self):
        res = self.session.delete("%s%s" % (self.baseUrl, 'login'))
        if int(res.status_code) != 204:
            print(res)
            return False
        self.session.close()
        EIESWrapper.__init__(self) #reset all the things
        return True
        
    ### END SESSION

    ### BEGIN USER INFO STUFF
    def GetUserInfo(self, user_id=None):
        if user_id == None:
            user_id = self.user_id
        return self.__exec(self.session.get, 'users/%d.json' % user_id, {'session_id': self.session_id}).json()
    ### BEGIN USER INFO STUFF

    ### BEGIN KEY STUFF
    def LookupPubKey(self, domain, port):
        return self.__exec(self.session.get, 'public_keys', {'domain': domain, 'port': port}).json()

    def NewKey(self, name, body):
        return self.__exec(self.session.post, 'keys', {'session_id': self.session_id, 'name': name, 'body': body}).json()
        
    def RetrieveKey(self, key_id):
        return self.__exec(self.session.get, 'keys/%d' % key_id, {'session_id': self.session_id}).json()
    
    def UpdateKey(self, key_id, name, body):
        return self.__exec(self.session.put, 'keys/%d' % key_id, {'session_id': self.session_id, 'name': name, 'body': body}).json()
        
    def DestroyKey(self, key_id):
        return self.__exec(self.session.delete, 'keys/%d' % key_id, {'session_id': self.session_id}).json()
    ### END KEY STUFF
    
    
    ### BEGIN ENTITY STUFF
    def NewEntity(self, name, domain, port):
        return self.__exec(self.session.post, 'entities', {'session_id': self.session_id, 'name': name, 'domain': domain, 'port': port}).json()
        
    def RetrieveEntity(self, entity_id):
        return self.__exec(self.session.get, 'entities/%d' % entity_id, {'session_id': self.session_id}).json()
    
    def UpdateEntity(self, entity_id, name, domain, port):
        return self.__exec(self.session.put, 'entities/%d' % entity_id, {'session_id': self.session_id, 'name': name, 'domain': domain, 'port': port}).json()
        
    def DestroyEntity(self, entity_id):
        return self.__exec(self.session.delete, 'entities/%d' % entity_id, {'session_id': self.session_id}).json()
    ### END ENTITY STUFF
    

    ### BEGIN ENTITY TOKEN STUFF
    def CreateEntityToken(self, entity_id, key_id):
        return self.__exec(self.session.post, 'entity_tokens', {'session_id': self.session_id, 'entity_id': entity_id, 'key_id': key_id}).json()
        
    def RetrieveEntityToken(self, token_id, session_id):
        return self.__exec(self.session.get, 'entity_tokens/%d' % token_id, {'session_id': self.session_id}).json()
    
    def DestroyEntityToken(self, token_id, session_id):
        return self.__exec(self.session.delete, 'entities_tokens/%d', {'session_id': self.session_id}).json()
    ### END ENTITY TOKEN STUFF

if __name__ == "__main__":
    import sys,code
    if not success:
        sys.exit(-1)
    eies = None
    if len(sys.argv) > 1:
       eies = EIESWrapper(url=sys.argv[1])
    else:
       eies = EIESWrapper()
    def inp(fn):
        return (fn('email: '), fn('password: '))
    try:
        email, password = inp(raw_input) #only defined for python2, because python3's equivalent of python2's input isn't input
    except:
        email, password = inp(input) #python 3 equivalent of raw_input
    if email != None and len(email) > 0 and password != None and len(password) > 0:
        eies.Login(email, password)
        code.interact(banner="Object \"eies\" initialized. Now calling eies.Login with your username and password. Good luck!",local=locals())
    else:
        code.interact(banner="Object \"eies\" initialized. Please call eies.Login with your username and password to fool around with the wrapper!",local=locals())
