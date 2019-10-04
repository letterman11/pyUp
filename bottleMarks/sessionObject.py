class SessionObject:

    def __init__(self,sessionID=None,userID=None,userName=None,sessionData=None,rowCount=None,sort=None):

        self.wmSESSIONID = sessionID
        self.wmUSERID = userID
        self.wmUSERNAME = userName 
        self.SESSIONDATA = sessionData 
        self.ROWCOUNT = rowCount
        self.SORT = sort
