import Register as Reg

class Datapath:
    def __init__(self, instList):
        self.opType = {
            "R":["ADD","OR"],
            "I":["ADDI","ORI","LW","SW"]
        }  
        self.PCWrite = 1
        self.IFIDWrite = 1
        self.IDEXFlush = 0
        self.ForwardA = "00"
        self.ForwardB = "00"
        self.instList = instList
        self.ifid = Reg.IFID()
        self.idex = Reg.IDEX()
        self.exmem = Reg.EXMEM()
        self.memwb = Reg.MEMWB()
        # To check instruction set is finished
        self.cnt = len(instList)

    def fetch_inst(self):

        if self.IFIDWrite == 0:
            return 
        self.ifid.reset()

        # check inst
        if len(self.instList) != 0 :
            inst = self.instList.pop(0)

            # parsing inst
            splitInst = inst.replace(",", "").split(" ")

            # change reg value
            if splitInst[0] != "SW" and splitInst[0] != "LW":
                if splitInst[0].endswith("I"):
                    self.ifid.regRs = int(splitInst[2].replace("$", ""))
                    self.ifid.regRt = int(splitInst[1].replace("$", ""))
                    self.ifid.regRd = 0
                else :
                    self.ifid.regRs = int(splitInst[2].replace("$", ""))
                    self.ifid.regRt = int(splitInst[3].replace("$", ""))
                    self.ifid.regRd = int(splitInst[1].replace("$", ""))
            else :
                self.ifid.regRs = int(splitInst[2][-2:-1])
                self.ifid.regRt = int(splitInst[1].replace("$", ""))
                self.ifid.regRd = 0

            self.ifid.inst = splitInst[0]
        
    def decode_inst(self):
        self.idex.reset() # ID/EXFlush가 일어나던 말던 reset은 무조건 발생함
        if self.IDEXFlush == 1:
            self.idex.inst = ""
            return 
        inst = self.ifid.inst
       
        if self.ifid.regRs is 0:
            return
        else :
            self.idex.regRs = self.ifid.regRs
            self.idex.regRt = self.ifid.regRt
            self.idex.regRd = self.ifid.regRd
            if inst != "SW":
                self.idex.regWrite = 1
                if inst == "LW":
                    self.idex.memRead = 1
                elif not inst.endswith("I"):
                    self.idex.regDst = 1
        
        self.idex.inst = inst
        self.ifid.instReset()

    def execute_oper(self):
        self.exmem.reset()

        if self.idex.inst == "":
            return
        else : 
            self.exmem.regRd = self.idex.regRt if self.idex.regRd is 0 else self.idex.regRd
            self.exmem.regWrite = self.idex.regWrite

        self.exmem.inst = self.idex.inst
        self.idex.instReset()
        return

    def access_data_in_memory(self):
        self.memwb.reset()
        if self.exmem.inst == "":
            return
        self.memwb.regRd = self.exmem.regRd
        self.memwb.regWrite = self.exmem.regWrite

        self.memwb.inst = self.exmem.inst
        self.exmem.inst = ""
        return

    def write_back(self):
        if self.memwb.inst == "":
            return
        print(self.memwb.inst)
        self.cnt -= 1
        self.memwb.instReset()

    def forwarding(self):
        self.ForwardA = "00"
        self.ForwardB = "00"
        if self.exmem.regWrite == 1:
            if self.exmem.regRd != 0:
                if self.exmem.regRd == self.idex.regRs :
                    self.ForwardA = "10"
                if self.exmem.regRd == self.idex.regRt :
                    self.ForwardB = "10"
        if self.memwb.regWrite == 1:
            if self.memwb.regRd != 0:
                if self.memwb.regRd == self.idex.regRs:
                    if not (self.exmem.regWrite == 1 and self.exmem.regRd != 0 and self.exmem.regRd == self.idex.regRs):
                        self.ForwardA = "01"
                    else :
                        self.ForwardA = "01"
                if self.memwb.regRd == self.idex.regRt:
                    if not (self.exmem.regWrite == 1 and self.exmem.regRd != 0 and self.exmem.regRd == self.idex.regRt):
                        self.ForwardB = "01"
                    else :
                        self.ForwardB = "01"
    
    def detect_hazard(self):
        if self.idex.regRt == self.ifid.regRs and self.idex.memRead == 1:
            self.PCWrite = 0
            self.IFIDWrite = 0
            self.IDEXFlush = 1
        else :
            self.PCWrite = 1
            self.IFIDWrite = 1
            self.IDEXFlush = 0

def get_all_inst():
    excuteInst = ["ADD $1, $2, $3",
                "ADD $4, $1, $1",
                "OR $5, $4, $2",
                "OR $3, $1, $5",
                "LW $2, 20($1)",
                "ADD $2, $2, $5",
                "OR $3, $6, $2"
                ]             
    return excuteInst

def print_reg(idx, datapath, printDict):
    printDict["Clock Cycle"].append("CC{}".format(idx))

    printDict["IF/ID.registerRs"].append(datapath.ifid.regRs)
    printDict["IF/ID.registerRt"].append(datapath.ifid.regRt)
    printDict["IF/ID.registerRd"].append(datapath.ifid.regRd)

    printDict["ID/EX.registerRs"].append(datapath.idex.regRs)
    printDict["ID/EX.registerRt"].append(datapath.idex.regRt)
    printDict["ID/EX.registerRd"].append(datapath.idex.regRd)
    printDict["ID/EX.regWrite"].append(datapath.idex.regWrite)
    printDict["ID/EX.memRead"].append(datapath.idex.memRead)
    printDict["ID/EX.regDst"].append(datapath.idex.regDst)

    printDict["EX/MEM.registerRd"].append(datapath.exmem.regRd)
    printDict["EX/MEM.regWrite"].append(datapath.exmem.regWrite)


    printDict["MEM/WB.registerRd"].append(datapath.memwb.regRd)
    printDict["MEM/WB.regWrite"].append(datapath.memwb.regWrite)

    printDict["ForwardA"].append(datapath.ForwardA)
    printDict["ForwardB"].append(datapath.ForwardB)
    
    printDict["PCWrite"].append(datapath.PCWrite)

    printDict["IF/IDWrite"].append(datapath.IFIDWrite)
    printDict["ID/EXFlush"].append(datapath.IDEXFlush)

def main():
    printDict = {
        "Clock Cycle": [],
        "IF/ID.registerRs": [],
        "IF/ID.registerRt": [],
        "IF/ID.registerRd": [],
        "ID/EX.registerRs": [],
        "ID/EX.registerRt": [],
        "ID/EX.registerRd": [],
        "ID/EX.regWrite": [],
        'ID/EX.memRead': [],
        "ID/EX.regDst": [],
        "EX/MEM.registerRd": [],
        "EX/MEM.regWrite": [],
        "MEM/WB.registerRd": [],
        "MEM/WB.regWrite": [],
        "ForwardA":[] ,
        "ForwardB": [],
        "PCWrite": [],
        "IF/IDWrite": [],
        "ID/EXFlush": [],
    }

    datapath = Datapath(get_all_inst())

    idx = 1

    while datapath.cnt != 0:
        print_reg(idx, datapath, printDict)
        
        datapath.write_back()
        datapath.access_data_in_memory()
        datapath.execute_oper()
        datapath.decode_inst()
        datapath.fetch_inst()
        datapath.detect_hazard()
        datapath.forwarding()
        
        idx += 1

    for key in printDict.keys():
        print("{:<20}".format(key), end ="")
        for value in printDict[key]:
            print("{:^4}".format(value), end = "  ")
        print()
        

main()
