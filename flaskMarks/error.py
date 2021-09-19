class Error(object):


    err_codes = { 
            101 : "Failed Login",
            102 : "Database Failure",
            103 : "Session Exists",
            104 : "No Session Exists for ID",
            105 : "No Object exists for Session",
            106 : "User Name is must be at least 6 characters",
            107 : "User Name or Password cannot be blank",
            108 : None,
            109 : None,
            110 : None,
            111 : "Password must be at least 6 characters",
            112 : "Incorrect User Name / Password",
            113 : "Passwords do not match",
            119 : "Invalid Email Address",
            120 : "User Name already taken",
            150 : "Duplicate Web Mark entry",
            151 : "Invalid Web Mark Submission",
            2000 : "Search Criteria Failure",
            1 : "Testing",
            'ERRCOND' : None
    }



    def __init__(self,code):
        self.code  = code 
        self.err_codes = Error.err_codes
        self.ERRCOND = code


    def errText(self):
        return self.err_codes[self.ERRCOND]

