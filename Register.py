class IFID:
    def __init__(self):
        self.regRs = 0
        self.regRt = 0
        self.regRd = 0
        self.inst = ""
    
    def reset(self):
        self.regRs = 0
        self.regRt = 0
        self.regRd = 0
    
    def instReset(self):
        self.inst = ""

class IDEX:
    def __init__(self):
        self.regRs = 0
        self.regRt = 0
        self.regRd = 0
        self.regWrite = 0
        self.memRead = 0
        self.regDst = 0
        self.inst = ""

    def reset(self):
        self.regRs = 0
        self.regRt = 0
        self.regRd = 0
        self.regWrite = 0
        self.memRead = 0
        self.regDst = 0
    
    def instReset(self):
        self.inst = ""

class EXMEM:
    def __init__(self):
        self.regRd = 0
        self.regWrite = 0
        self.inst = ""

    def reset(self):
        self.regRd = 0
        self.regWrite = 0
    
    def instReset(self):
        self.inst = ""

class MEMWB:
    def __init__(self):
        self.regRd = 0
        self.regWrite = 0
        self.inst = ""
        
    def reset(self):
        self.regRd = 0
        self.regWrite = 0     

    def instReset(self):
        self.inst = ""