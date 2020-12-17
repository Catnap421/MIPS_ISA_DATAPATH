import Register as Reg
import sys
import csv

class Datapath:
    def __init__(self, instList):
        self.opType = {
            "R":["ADD","OR"],
            "I":["ADDI","ORI","LW","SW"]
        }  
        # Set register instance
        self.hazardDetectionUnit = Reg.HazardDetectionUnit()
        self.forwardUnit = Reg.ForwardUnit()
        self.instList = instList
        self.ifid = Reg.IFID()
        self.idex = Reg.IDEX()
        self.exmem = Reg.EXMEM()
        self.memwb = Reg.MEMWB()

        # To check instruction set is finished
        self.cnt = len(instList)

    def fetch_inst(self):
        # Check IFID.Write value
        if self.hazardDetectionUnit.IFIDWrite == 0:
            return 

        # Reset IFID value
        self.ifid.reset()

        # Check instruction 
        if len(self.instList) == 0 :
            return

        inst = self.instList.pop(0)

        # Parsing inst
        splitInst = inst.replace(",", "").split(" ")

        # Set register value
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

        # Set IFID register's instruction value
        self.ifid.inst = splitInst[0]
        
    def decode_inst(self):
        # Reset IDEX value
        self.idex.reset() 

        # Check IDEX.Flush value
        if self.hazardDetectionUnit.IDEXFlush == 1:
            return 

        # Check IFID register's instruction value
        if self.ifid.inst == "":
            return

        # Set IDEX register 
        self.idex.regRs = self.ifid.regRs
        self.idex.regRt = self.ifid.regRt
        self.idex.regRd = self.ifid.regRd
        if self.ifid.inst != "SW":
            self.idex.regWrite = 1
            if self.ifid.inst == "LW":
                self.idex.memRead = 1
            elif not self.ifid.inst.endswith("I"):
                self.idex.regDst = 1
        
        # Set IDEX instruction value
        self.idex.inst = self.ifid.inst

        # Reset IFID instruction value
        self.ifid.instReset()

    def execute_oper(self):
        # Reset EXMEM value
        self.exmem.reset()
        
        # Check IDEX register's instruction value
        if self.idex.inst == "":
            return

        # Set EXMEM value
        self.exmem.regRd = self.idex.regRt if self.idex.regRd is 0 else self.idex.regRd
        self.exmem.regWrite = self.idex.regWrite

        # Set EXMEM intruction value
        self.exmem.inst = self.idex.inst

        # Reset IDEX instrution value
        self.idex.instReset()

    def access_data_in_memory(self):
        # Reset MEMWB value
        self.memwb.reset()

        # Check EXMEM instruction value
        if self.exmem.inst == "":
            return

        # Set MEMWB value
        self.memwb.regRd = self.exmem.regRd
        self.memwb.regWrite = self.exmem.regWrite

        # Set MEMWB instruction value
        self.memwb.inst = self.exmem.inst

        # Reset EXMEM instruction value
        self.exmem.instReset()

    def write_back(self):
        # Check MEMWB instruction value
        if self.memwb.inst == "":
            return
        
        # If instruction is finished, Subtract cnt
        self.cnt -= 1

        # Reset MEMWB instruction value
        self.memwb.instReset()

    def forwarding(self):
        # Reset Forward Unit 
        self.forwardUnit.reset()
        
        # ForwardA
        if self.exmem.regWrite == 1 and self.exmem.regRd != 0 and self.exmem.regRd == self.idex.regRs:
            self.forwardUnit.ForwardA = "10"
        elif self.memwb.regWrite == 1 and self.memwb.regRd != 0 and self.memwb.regRd == self.idex.regRs:
            self.forwardUnit.ForwardA = "01"

        # ForwardB
        if self.exmem.regWrite == 1 and self.exmem.regRd != 0 and self.exmem.regRd == self.idex.regRt:
            self.forwardUnit.ForwardB = "10"
        elif self.memwb.regWrite == 1 and self.memwb.regRd != 0 and self.memwb.regRd == self.idex.regRt:
            self.forwardUnit.ForwardB = "01"

    def detect_hazard(self):
        # Set Hazard Detection Unit
        if self.idex.regRt == self.ifid.regRs and self.idex.memRead == 1:
            self.hazardDetectionUnit.PCWrite = 0
            self.hazardDetectionUnit.IFIDWrite = 0
            self.hazardDetectionUnit.IDEXFlush = 1
        else :
            self.hazardDetectionUnit.PCWrite = 1
            self.hazardDetectionUnit.IFIDWrite = 1
            self.hazardDetectionUnit.IDEXFlush = 0

# Read instructions from input file
def get_all_inst(filePath):
    f = open(filePath, "r")
    executeInst = f.readlines() 
    f.close()

    return executeInst

# Append register value for printing
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

    printDict["ForwardA"].append(datapath.forwardUnit.ForwardA)
    printDict["ForwardB"].append(datapath.forwardUnit.ForwardB)
    
    printDict["PCWrite"].append(datapath.hazardDetectionUnit.PCWrite)

    printDict["IF/IDWrite"].append(datapath.hazardDetectionUnit.IFIDWrite)
    printDict["ID/EXFlush"].append(datapath.hazardDetectionUnit.IDEXFlush)

# Main function
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

    # Set file path
    filePath = sys.argv[1]

    if len(sys.argv) != 2:
        print("Insufficient Arguments")
        sys.exit()

    # Set DataPath instance
    datapath = Datapath(get_all_inst(filePath))

    idx = 1

    # Cycle the DataPath
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

    # Save csv file and print
    fileName = filePath.split(".")[0]
    f = open('{}_result.csv'.format(fileName), "w")

    wr = csv.writer(f, quotechar = '|', quoting=csv.QUOTE_ALL)

    for key in printDict.keys():   
        wr.writerow([key, *list(map(lambda x: " {} ".format(x), printDict[key]))])
        print("{:<20}".format(key), end ="")
        for value in printDict[key]:
            print("{:<4}".format(value), end = "")
        print()

    f.close()    

if __name__ == "__main__":
    main()
