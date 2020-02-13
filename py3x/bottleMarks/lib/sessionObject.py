class SessionObject(object):

    def __init__(self,sessionID=None,userID=None,userName=None,sessionData=None,rowCount=None,sort=None):
        self.SESSIONID = sessionID
        self.USERID = userID
        self.USERNAME = userName 
        self.SESSIONDATA = sessionData 
        self.ROWCOUNT = rowCount
        self.SORT = sort
