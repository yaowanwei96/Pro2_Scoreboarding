# --*-- coding:utf8 --*--

from __future__ import print_function

flag = False

list = []
data = []
finish = False  # 标记是否结束
pc = 0  # 程序计数器

# 定义list
IF_Unit_Wait = None
IF_Unit_Excute = None
Pre_Issue_Buffer = []
Pre_ALU_Queue = []
Post_ALU_Buffer = None
Pre_ALUB_Queue = []
Post_ALUB_Buffer = None
Pre_MEM_Queue = []
Post_MEM_Buffer = None

# 标志当前周期是否可以取指令
CanFetch = True

# 上个周期结束时的各个队列的数据情况
C_ALU = 0
C_ALUB = 0
C_MEM = 0
C_ISSUE = 0

# 寄存器初始化
R = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]


class Instruct(object):
    times = 0
    name = ""

    def __init__(self):
        pass


# 读文件函数
def read_file():
    data = []
    file_name='t1.txt'
    for line in open(file_name):
        line = line.split()
        data.append(line)
    return data


# 反汇编
def disassembly(instruction,pc):
    global flag
    global list
    global data

    inst = Instruct()
    code = ""
    opcode = instruction[0][0:6]
    rs1 = instruction[0][6:11]
    rt1 = instruction[0][11:16]
    rd1 = instruction[0][16:21]
    shamt1 = instruction[0][21:26]
    func1 = instruction[0][26:32]
    offset1 = instruction[0][16:32]

    rs = str(int(instruction[0][6:11],2))
    rt = str(int(instruction[0][11:16],2))
    rd = str(int(instruction[0][16:21],2))
    shamt = str(int(instruction[0][21:26],2))
    func = str(int(instruction[0][26:32],2))
    offset = str(int((instruction[0][16:32]),2))
    inst.addr = 64 + pc * 4

    if flag:
        if instruction[0].startswith("1"):
            code = str(int(instruction[0], 2)- 2**32)
        else:
            code = str(int(instruction[0],2))
    else:
        inst.rt = rt
        inst.rs = rs
        inst.rd = rd
        inst.shamt = shamt

        if opcode == "000010":
            inst.name = "J"
            inst.imm = int(instruction[0][6:32], 2)*4
            code = "J\t#"+str(int(instruction[0][6:32], 2)*4)
        elif opcode=="000000" and func1=="001000":
            inst.name = "JR"
            code = "JR\tR"+rs
        elif opcode=="000100":
            inst.name = "BEQ"
            inst.imm = int(instruction[0][16:32], 2)*4
            code = "BEQ\tR"+rs+", R"+rt+", #"+str(int((instruction[0][16:32]),2)*4)
        elif opcode=="000001" and rt1=="00000":
            inst.name = "BLTZ"
            inst.imm = int(instruction[0][16:32], 2)*4
            code = "BLTZ\tR"+rs+", #"+str(int((instruction[0][16:32]),2)*4)
        elif opcode=="000111" and rt1=="00000":
            inst.name = "BGTZ"
            inst.imm = int(instruction[0][16:32], 2)*4
            code = "BGTZ\tR"+rs+", #"+str(int((instruction[0][16:32]),2)*4)
        elif opcode=="000000" and shamt1=="00000" and func1=="100000":
            inst.name = "ADD"
            code = "ADD\tR"+rd+", R"+rs+", R"+rt
        elif opcode=="000000" and shamt1=="00000" and func1=="100010":
            inst.name = "SUB"
            code = "SUB\tR"+rd+", R"+rs+", R"+rt
        elif opcode=="000000" and func1=="001101":
            flag = True
            code = "BREAK"
        elif opcode=="101011":
            inst.name = "SW"
            inst.imm = int(instruction[0][16:32], 2)
            code = "SW\tR"+rt+", "+offset+"(R"+rs+")"
        elif opcode=="100011":
            inst.name = "LW"
            inst.imm = int(instruction[0][16:32], 2)
            code = "LW\tR"+rt+", "+offset+"(R"+rs+")"
        elif instruction[0] == "00000000000000000000000000000000":
            code = "NOP"
        elif opcode=="000000" and func1=="000000":
            inst.name = "SLL"
            code = "SLL\tR"+rd+", R"+rt+", #"+shamt
        elif opcode=="000000" and func1=="000010" and rs1=="00000":
            inst.name = "SRL"
            code = "SRL\tR"+rd+", R"+rt+", #"+shamt
        elif opcode=="000000" and func1=="000011" and rs1=="00000":
            inst.name = "SRA"
            code = "SRA\tR"+rd+", R"+rt+", #"+shamt
        elif opcode=="011100" and func1=="000010" and shamt1=="00000":
            inst.name = "MUL"
            code = "MUL\tR"+rd+", R"+rs+", #"+rt
        elif opcode=="000000" and func1=="100100" and shamt1=="00000":
            inst.name = "AND"
            code = "AND\tR"+rd+", R"+rs+", #"+rt
        elif opcode=="000000" and func1=="100111" and shamt1=="00000":
            inst.name = "NOR"
            code = "NOR\tR"+rd+", R"+rs+", #"+rt
        elif opcode=="000000" and func1=="101010" and shamt1=="00000":
            inst.name = "SLT"
            code = "SLT\tR"+rd+", R"+rs+", #"+rt
        elif opcode=="110000":
            inst.name = "ADDI"
            inst.imm = int(instruction[0][16:32], 2)
            code = "ADD\tR"+rt+", R"+rs+", #"+offset
        elif opcode=="110001":
            inst.name = "SUBI"
            inst.imm = int(instruction[0][16:32], 2)
            code = "SUB\tR"+rt+", R"+rs+", #"+offset
        elif opcode=="100001":
            inst.name = "MULI"
            inst.imm = int(instruction[0][16:32], 2)
            code = "MUL\tR"+rt+", R"+rs+", #"+offset
        elif opcode=="110010":
            inst.name = "ANDI"
            inst.imm = int(instruction[0][16:32], 2)
            code = "AND\tR"+rt+", R"+rs+", #"+offset
        elif opcode=="110011":
            inst.name = "NORI"
            inst.imm = int(instruction[0][16:32], 2)
            code = "NOR\tR"+rt+", R"+rs+", #"+offset
        elif opcode=="110101":
            inst.name = "SLTI"
            inst.imm = int(instruction[0][16:32], 2)
            code = "SLT\tR"+rt+", R"+rs+", #"+offset

    inst.code = code
    # print(code)
    if flag and code!="BREAK":
        inst.imm = code
        data.append(inst)
    else:
        list.append(inst)
    return code


# 打印寄存器数据
def printRegister(ff):
    global R
    ff.write("Registers\n")
    ff.write("R00:\t"+str(R[0])+"\t"+str(R[1])+"\t"+str(R[2])+"\t"+str(R[3])+"\t"+str(R[4])+"\t"+str(R[5])+"\t"+str(R[6])+"\t"+str(R[7])+"\nR08:"+"\t"+str(R[8])+"\t"+str(R[9])+"\t"+str(R[10])+"\t"+str(R[11])+"\t"+str(R[12])+"\t"+str(R[13])+"\t"+str(R[14])+"\t"+str(R[15])+"\n")
    ff.write("R16:\t"+str(R[16])+"\t"+str(R[17])+"\t"+str(R[18])+"\t"+str(R[19])+"\t"+str(R[20])+"\t"+str(R[21])+"\t"+str(R[22])+"\t"+str(R[23])+"\nR24:"+"\t"+str(R[24])+"\t"+str(R[25])+"\t"+str(R[26])+"\t"+str(R[27])+"\t"+str(R[28])+"\t"+str(R[29])+"\t"+str(R[30])+"\t"+str(R[31])+"\n")
    pass


# 打印data数据
def printData(ff):
    global data
    ff.write("Data\n")
    for i in range(len(data)):
        if i % 8 == 0 :
            if i!=0 : ff.write("\n")
            ff.write(str(data[i].addr)+":\t")
        if i % 8 == 7:
            ff.write(str(data[i].imm))
        else:
            ff.write(str(data[i].imm) + "\t")
    pass


# 流水线 模拟
def pipeline():
    global pc
    global Pre_ALU_Queue
    global Pre_ALUB_Queue
    global Pre_MEM_Queue
    global Pre_Issue_Buffer
    global Post_ALU_Buffer
    global Post_ALUB_Buffer
    global Post_MEM_Buffer
    global IF_Unit_Excute
    global IF_Unit_Wait
    global CanFetch
    global C_ALU
    global C_ALUB
    global C_MEM
    global C_ISSUE
    global finish

    C_ALU = len(Pre_ALU_Queue)
    C_ALUB = len(Pre_ALUB_Queue)
    C_MEM = len(Pre_MEM_Queue)
    C_ISSUE = len(Pre_Issue_Buffer)

    if IF_Unit_Excute != None :
        # print(IF_Unit_Excute.code)
        # print(IF_Unit_Excute.name)
        simulator(IF_Unit_Excute)
        CanFetch = True
        IF_Unit_Excute = None

    if IF_Unit_Wait != None and noWAWandWAR_CUNIT(IF_Unit_Wait):
        IF_Unit_Excute = IF_Unit_Wait
        IF_Unit_Wait = None

    #issue发射指令
    issue()

    #WB
    if Post_ALU_Buffer != None:
        simulator(Post_ALU_Buffer)
        Post_ALU_Buffer = None

    if Post_ALUB_Buffer != None:
        simulator(Post_ALUB_Buffer)
        Post_ALUB_Buffer = None

    if Post_MEM_Buffer != None:
        simulator(Post_MEM_Buffer)
        Post_MEM_Buffer = None

    postbuffer()

    # 取指令
    if CanFetch :
        fetch()

    pass


# 数据准备好了 放到post_buffer
def postbuffer():
    global Pre_ALU_Queue
    global Pre_ALUB_Queue
    global Pre_MEM_Queue
    global Post_MEM_Buffer
    global Post_ALU_Buffer
    global Post_ALUB_Buffer
    if C_ALU > 0 :
        ist= Pre_ALU_Queue[0]
        Post_ALU_Buffer = Pre_ALU_Queue[0]
        Pre_ALU_Queue.remove(ist)

    elif C_ALUB > 0 :
        ist = Pre_ALUB_Queue[0]
        if ist.times == 0:
            ist.times = ist.times  + 1
            return
        Post_ALUB_Buffer = Pre_ALUB_Queue[0]
        Pre_ALUB_Queue.remove(ist)

    elif C_MEM > 0 :
        ist = Pre_MEM_Queue[0]
        if ist.name == "SW":
            simulator(ist)
            Pre_MEM_Queue.remove(ist)
        else:
            Post_MEM_Buffer = Pre_MEM_Queue[0]
            Pre_MEM_Queue.remove(ist)
    pass


# 计算
def simulator(ist):
    global list
    global data
    global R
    global pc
    # print(ist.name)
    if ist.name == "J":
        pc = int((ist.imm - 64) /4)
    elif ist.name == "JR":
        pc = R[int(ist.rs)]
    elif ist.name == "BEQ":
        if R[int(ist.rs)] == R[int(ist.rt)] :
            pc = pc + int(ist.imm/4)
    elif ist.name == "BLTZ":
        if R[int(ist.rs)] < 0:
            pc = pc + int(ist.imm / 4)
    elif ist.name == "BGTZ":
        if R[int(ist.rs)] > 0:
            pc = pc + int(ist.imm / 4)
    elif ist.name == "ADD":
        R[int(ist.rd)] = int(R[int(ist.rs)]) + int(R[int(ist.rt)])
    elif ist.name == "SUB":
        R[int(ist.rd)] = int(R[int(ist.rs)]) - int(R[int(ist.rt)])
    elif ist.name == "BREAK":
        return
    elif ist.name == "SW":
        for d in data:
            if d.addr == R[int(ist.rs)]+int(ist.imm):
                d.imm = R[int(ist.rt)]
    elif ist.name == "LW":
        for d in data:
            if d.addr == R[int(ist.rs)]+int(ist.imm):
                R[int(ist.rt)]= d.imm
    elif ist.name == "SLL":
        R[int(ist.rd)] = R[int(ist.rt)] << int(ist.shamt)
    elif ist.name == "SRL":
        R[int(ist.rd)] = R[int(ist.rt)] >> int(ist.shamt)
    elif ist.name == "SRA":
        R[int(ist.rd)] = R[int(ist.rt)] >> int(ist.shamt)
    elif ist.name == "NOP":
        return
    elif ist.name == "MUL":
        R[int(ist.rd)] = int(R[int(ist.rs)]) * int(R[int(ist.rt)])
    elif ist.name == "AND":
        R[int(ist.rd)] = R[int(ist.rs)] & R[int(ist.rt)]
    elif ist.name == "NOR":
        R[int(ist.rd)] = ~ (R[int(ist.rs)] | R[int(ist.rt)])
    elif ist.name == "SLT":
        if R[int(ist.rs)] < R[int(ist.rt)]:
            R[int(ist.rd)] = 1
        else:
            R[int(ist.rd)] = 0
    elif ist.name == "ADDI":
        R[int(ist.rt)] = R[int(ist.rs)] + int(ist.imm)
    elif ist.name == "SUBI":
        R[int(ist.rt)] = R[int(ist.rs)] - int(ist.imm)
    elif ist.name == "MULI":
        R[int(ist.rt)] = R[int(ist.rs)] * int(ist.imm)
    elif ist.name == "ANDI":
        R[int(ist.rt)] = R[int(ist.rs)] & int(ist.imm)
    elif ist.name == "NORI":
        R[int(ist.rt)] = ~(R[int(ist.rs)] | int(ist.imm))
    elif ist.name == "SLTI":
        if R[int(ist.rs)] < int(ist.imm):
            R[int(ist.rd)] = 1
        else:
            R[int(ist.rd)] = 0
    pass


def save(it,listWrite):
    if it.name == "JR":
        listWrite.append(it.rs)
    elif it.name == "ADD":
        listWrite.append(it.rd)
    elif it.name == "ADDI":
        listWrite.append(it.rt)
    elif it.name == "NOR":
        listWrite.append(it.rd)
    elif it.name == "NORI":
        listWrite.append(it.rt)
    elif it.name == "SLT":
        listWrite.append(it.rd)
    elif it.name == "SLTI":
        listWrite.append(it.rt)
    elif it.name == "SUB":
        listWrite.append(it.rd)
    elif it.name == "SUBI":
        listWrite.append(it.rt)
    elif it.name == "SLL":
        listWrite.append(it.rd)
    elif it.name == "SRL":
        listWrite.append(it.rd)
    elif it.name == "SRA":
        listWrite.append(it.rd)
    elif it.name == "MUL":
        listWrite.append(it.rd)
    elif it.name == "MULI":
        listWrite.append(it.rt)
    elif it.name == "LW":
        listWrite.append(it.rt)
    elif it.name == "AND":
        listWrite.append(it.rd)
    elif it.name == "ANDI":
        listWrite.append(it.rt)
    pass


def exist(id,listWrite):
    for i in range(len(listWrite)):
        if id == listWrite[i]:
            return True
    return False


# Pre_ISSUE WAW 和 WAR 检测
def noWAWandWAR(index):
    global Pre_MEM_Queue
    global Pre_ALU_Queue
    global Pre_ALUB_Queue
    global Post_ALUB_Buffer
    global Post_ALU_Buffer
    global Post_MEM_Buffer
    global Pre_Issue_Buffer

    listWrite = []

    for i in range(index):
        it = Pre_Issue_Buffer[i]
        save(it,listWrite)

    for i in range(len(Pre_MEM_Queue)):
        it = Pre_MEM_Queue[i]
        save(it,listWrite)

    for i in range(len(Pre_ALU_Queue)):
        it = Pre_ALU_Queue[i]
        save(it,listWrite)

    for i in range(len(Pre_ALUB_Queue)):
        it = Pre_ALUB_Queue[i]
        save(it,listWrite)

    if Post_ALUB_Buffer != None :
        save(Post_ALUB_Buffer,listWrite)

    if Post_ALU_Buffer != None :
        save(Post_ALU_Buffer,listWrite)

    if Post_MEM_Buffer != None :
        save(Post_MEM_Buffer,listWrite)

    idct = Pre_Issue_Buffer[index]

    if idct.name == "J":
        return True
    elif idct.name == "JR":
        return not exist(idct.rs,listWrite)
    elif idct.name == "ADD":
        return not exist(idct.rd,listWrite) and not exist(idct.rt,listWrite) and not exist(idct.rs,listWrite)
    elif idct.name == "ADDI":
        return not exist(idct.rt,listWrite) and not exist(idct.rs,listWrite)
    elif idct.name == "NOR":
        return not exist(idct.rd,listWrite) and not exist(idct.rt,listWrite) and not exist(idct.rs,listWrite)
    elif idct.name == "NORI":
        return not exist(idct.rt,listWrite) and not exist(idct.rs,listWrite)
    elif idct.name == "SLT":
        return not exist(idct.rd,listWrite) and not exist(idct.rt,listWrite) and not exist(idct.rs,listWrite)
    elif idct.name == "SLTI":
        return not exist(idct.rt,listWrite) and not(idct.rs,listWrite)
    elif idct.name == "SUB":
        return not exist(idct.rd,listWrite) and not exist(idct.rt,listWrite) and not exist(idct.rs,listWrite)
    elif idct.name == "SUBI":
        return not exist(idct.rt,listWrite) and not exist(idct.rs,listWrite)
    elif idct.name == "SLL":
        return not exist(idct.rt,listWrite) and not exist(idct.rd,listWrite)
    elif idct.name == "SRL":
        return not exist(idct.rt,listWrite) and not exist(idct.rd,listWrite)
    elif idct.name == "SRA":
        return not exist(idct.rt,listWrite) and not exist(idct.rd,listWrite)
    elif idct.name == "MUL":
        return not exist(idct.rd,listWrite) and not exist(idct.rt,listWrite) and not exist(idct.rs,listWrite)
    elif idct.name == "MULI":
        return not exist(idct.rt,listWrite) and not exist(idct.rs,listWrite)
    elif idct.name == "LW":
        return not exist(idct.rt,listWrite) and not exist(idct.rs,listWrite)
    elif idct.name == "SW":
        return not exist(idct.rt,listWrite) and not exist(idct.rs,listWrite)
    elif idct.name == "BGTZ":
        return not exist(idct.rs,listWrite)
    elif idct.name == "BLTZ":
        return not exist(idct.rs,listWrite)
    elif idct.name == "BEQ":
        return not exist(idct.rt,listWrite) and not exist(idct.rs,listWrite)
    elif idct.name == "AND":
        return not exist(idct.rd,listWrite) and not exist(idct.rt,listWrite) and not exist(idct.rs,listWrite)
    elif idct.name == "ANDI":
        return not exist(idct.rt,listWrite) and not exist(idct.rs,listWrite)

    return False


#  控制单元 WAW 和 WAR 检测
def noWAWandWAR_CUNIT(idct):
    global Pre_MEM_Queue
    global Pre_ALU_Queue
    global Pre_ALUB_Queue
    global Post_ALUB_Buffer
    global Post_ALU_Buffer
    global Post_MEM_Buffer
    global Pre_Issue_Buffer

    listWrite = []

    for i in range(len(Pre_Issue_Buffer)):
        it = Pre_Issue_Buffer[i]
        save(it,listWrite)

    for i in range(len(Pre_MEM_Queue)):
        it = Pre_MEM_Queue[i]
        save(it,listWrite)

    for i in range(len(Pre_ALU_Queue)):
        it = Pre_ALU_Queue[i]
        save(it,listWrite)

    for i in range(len(Pre_ALUB_Queue)):
        it = Pre_ALUB_Queue[i]
        save(it,listWrite)

    if Post_ALUB_Buffer != None :
        save(Post_ALUB_Buffer,listWrite)

    if Post_ALU_Buffer != None :
        save(Post_ALU_Buffer,listWrite)

    if Post_MEM_Buffer != None :
        save(Post_MEM_Buffer,listWrite)

    if idct.name == "J":
        return True
    elif idct.name == "JR":
        return not exist(idct.rs,listWrite)
    elif idct.name == "ADD":
        return not exist(idct.rd,listWrite) and not exist(idct.rt,listWrite) and not exist(idct.rs,listWrite)
    elif idct.name == "ADDI":
        return not exist(idct.rt,listWrite) and not exist(idct.rs,listWrite)
    elif idct.name == "NOR":
        return not exist(idct.rd,listWrite) and not exist(idct.rt,listWrite) and not exist(idct.rs,listWrite)
    elif idct.name == "NORI":
        return not exist(idct.rt,listWrite) and not exist(idct.rs,listWrite)
    elif idct.name == "SLT":
        return not exist(idct.rd,listWrite) and not exist(idct.rt,listWrite) and not exist(idct.rs,listWrite)
    elif idct.name == "SLTI":
        return not exist(idct.rt,listWrite) and not(idct.rs,listWrite)
    elif idct.name == "SUB":
        return not exist(idct.rd,listWrite) and not exist(idct.rt,listWrite) and not exist(idct.rs,listWrite)
    elif idct.name == "SUBI":
        return not exist(idct.rt,listWrite) and not exist(idct.rs,listWrite)
    elif idct.name == "SLL":
        return not exist(idct.rt,listWrite) and not exist(idct.rd,listWrite)
    elif idct.name == "SRL":
        return not exist(idct.rt,listWrite) and not exist(idct.rd,listWrite)
    elif idct.name == "SRA":
        return not exist(idct.rt,listWrite) and not exist(idct.rd,listWrite)
    elif idct.name == "MUL":
        return not exist(idct.rd,listWrite) and not exist(idct.rt,listWrite) and not exist(idct.rs,listWrite)
    elif idct.name == "MULI":
        return not exist(idct.rt,listWrite) and not exist(idct.rs,listWrite)
    elif idct.name == "LW":
        return not exist(idct.rt,listWrite) and not exist(idct.rs,listWrite)
    elif idct.name == "SW":
        return not exist(idct.rt,listWrite) and not exist(idct.rs,listWrite)
    elif idct.name == "BGTZ":
        return not exist(idct.rs,listWrite)
    elif idct.name == "BLTZ":
        return not exist(idct.rs,listWrite)
    elif idct.name == "BEQ":
        return not exist(idct.rt,listWrite) and not exist(idct.rs,listWrite)
    elif idct.name == "AND":
        return not exist(idct.rd,listWrite) and not exist(idct.rt,listWrite) and not exist(idct.rs,listWrite)
    elif idct.name == "ANDI":
        return not exist(idct.rt,listWrite) and not exist(idct.rs,listWrite)

    return False


# 发射指令
def issue():
    global C_ISSUE
    global Pre_Issue_Buffer
    n = C_ISSUE
    i = 0
    while i < n:
        it = Pre_Issue_Buffer[i]
        if noWAWandWAR(i):
            if len(Pre_ALU_Queue) < 2 and ( it.name == "ADD" or it.name == "ADDI" or it.name == "SUB" or it.name == "SUBI" or it.name == "NOR" or it.name == "NORI" or it.name == "SLT" or it.name == "SLTI" or it.name == "AND" or it.name == "ANDI" ):
                 Pre_ALU_Queue.append(it)
                 Pre_Issue_Buffer.remove(it)
                 i = i - 1
                 n = n - 1
            if len(Pre_ALUB_Queue) < 2 and ( it.name == "MUL" or it.name == "MULI" or it.name == "SLL" or it.name == "SRA" or it.name == "SRL"):
                it.times = 0
                Pre_ALUB_Queue.append(it)
                Pre_Issue_Buffer.remove(it)
                i = i - 1
                n = n - 1
            if len(Pre_MEM_Queue) < 2 and ( it.name == "LW" or it.name == "SW"):
                Pre_MEM_Queue.append(it)
                Pre_Issue_Buffer.remove(it)
                i = i - 1
                n = n - 1
        i = i + 1
    pass


# 取指令
def fetch():
    global IF_Unit_Wait
    global IF_Unit_Excute
    global pc
    global C_ISSUE
    global CanFetch
    global finish

    count = 0
    for i in range(4 - C_ISSUE):
        # print(list[pc].code)
        if list[pc].name == "J":
            IF_Unit_Excute = list[pc]
            CanFetch = False
            return
        if list[pc].code == "BREAK":
            IF_Unit_Excute = list[pc]
            CanFetch = False
            finish = True
            return
        elif list[pc].name == "JR" or list[pc].name == "BEQ" or list[pc].name == "BLTZ" or list[pc].name == "BGTZ"  :
            IF_Unit_Wait = list[pc]
            pc = pc + 1
            CanFetch = False
            break
        else:
            Pre_Issue_Buffer.append(list[pc])
            pc = pc + 1
        count = count + 1
        if count >= 2:
            break
    pass


# 输出
def printScore(ff):
    global R
    global IF_Unit_Wait
    global IF_Unit_Excute
    global Post_ALUB_Buffer
    global Post_ALU_Buffer
    global Post_MEM_Buffer
    global Pre_Issue_Buffer
    global Pre_ALU_Queue
    global Pre_ALUB_Queue
    global Pre_MEM_Queue



    ff.write("IF Unit:\n")
    if IF_Unit_Excute == None and IF_Unit_Wait == None :
        ff.write("	Waiting Instruction: \n")
        ff.write("	Executed Instruction: \n")
    elif IF_Unit_Excute == None and IF_Unit_Wait != None :
        ff.write("	Waiting Instruction: "+ IF_Unit_Wait.code + "\n")
        ff.write("	Executed Instruction: \n")
    elif IF_Unit_Excute != None and IF_Unit_Wait == None :
        ff.write("	Waiting Instruction: \n")
        ff.write("	Executed Instruction: "+ IF_Unit_Excute.code + "\n")
    elif IF_Unit_Excute != None and IF_Unit_Wait != None :
        ff.write("	Waiting Instruction: "+ IF_Unit_Wait.code + "\n")
        ff.write("	Executed Instruction: "+ IF_Unit_Excute.code + "\n")


    ff.write("Pre-Issue Buffer:\n")

    if len(Pre_Issue_Buffer) == 0:
        ff.write("	Entry 0:\n")
        ff.write("	Entry 1:\n")
        ff.write("	Entry 2:\n")
        ff.write("	Entry 3:\n")
    elif len(Pre_Issue_Buffer) == 1:
        ff.write("	Entry 0:[" + Pre_Issue_Buffer[0].code + "]\n")
        ff.write("	Entry 1:\n")
        ff.write("	Entry 2:\n")
        ff.write("	Entry 3:\n")
    elif len(Pre_Issue_Buffer) == 2:
        ff.write("	Entry 0:[" + Pre_Issue_Buffer[0].code + "]\n")
        ff.write("	Entry 1:[" + Pre_Issue_Buffer[1].code + "]\n")
        ff.write("	Entry 2:\n")
        ff.write("	Entry 3:\n")
    elif len(Pre_Issue_Buffer) == 3:
        ff.write("	Entry 0:[" + Pre_Issue_Buffer[0].code + "]\n")
        ff.write("	Entry 1:[" + Pre_Issue_Buffer[1].code + "]\n")
        ff.write("	Entry 2:[" + Pre_Issue_Buffer[2].code + "]\n")
        ff.write("	Entry 3:\n")
    elif len(Pre_Issue_Buffer) == 4:
        ff.write("	Entry 0:[" + Pre_Issue_Buffer[0].code + "]\n")
        ff.write("	Entry 1:[" + Pre_Issue_Buffer[1].code + "]\n")
        ff.write("	Entry 2:[" + Pre_Issue_Buffer[2].code + "]\n")
        ff.write("	Entry 3:[" + Pre_Issue_Buffer[3].code + "]\n")

    ff.write("Pre-ALU Queue:\n")
    if len(Pre_ALU_Queue) == 0 :
        ff.write("	Entry 0:\n")
        ff.write("	Entry 1:\n")
    elif len(Pre_ALU_Queue) == 1 :
        ff.write("	Entry 0:[" + Pre_ALU_Queue[0].code + "]\n")
        ff.write("	Entry 1:\n")
    elif len(Pre_ALU_Queue) == 2 :
        ff.write("	Entry 0:[" + Pre_ALU_Queue[0].code + "]\n")
        ff.write("	Entry 1:[" + Pre_ALU_Queue[1].code + "]\n")

    if Post_ALU_Buffer == None:
        ff.write("Post-ALU Buffer:\n")
    else:
        ff.write("Post-ALU Buffer:["+Post_ALU_Buffer.code+"]\n")

    ff.write("Pre-ALUB Queue:\n")
    if len(Pre_ALUB_Queue) == 0 :
        ff.write("	Entry 0:\n")
        ff.write("	Entry 1:\n")
    elif len(Pre_ALUB_Queue) == 1 :
        ff.write("	Entry 0:[" + Pre_ALUB_Queue[0].code + "]\n")
        ff.write("	Entry 1:\n")
    elif len(Pre_ALUB_Queue) == 2 :
        ff.write("	Entry 0:[" + Pre_ALUB_Queue[0].code + "]\n")
        ff.write("	Entry 1:[" + Pre_ALUB_Queue[1].code + "]\n")


    if Post_ALUB_Buffer == None:
        ff.write("Post-ALUB Buffer:\n")
    else:
        ff.write("Post-ALUB Buffer:["+Post_ALUB_Buffer.code+"]\n")


    ff.write("Pre-MEM Queue:\n")
    if len(Pre_MEM_Queue) == 0 :
        ff.write("	Entry 0:\n")
        ff.write("	Entry 1:\n")
    elif len(Pre_MEM_Queue) == 1 :
        ff.write("	Entry 0:[" + Pre_MEM_Queue[0].code + "]\n")
        ff.write("	Entry 1:\n")
    elif len(Pre_MEM_Queue) == 2 :
        ff.write("	Entry 0:[" + Pre_MEM_Queue[0].code + "]\n")
        ff.write("	Entry 1:[" + Pre_MEM_Queue[1].code + "]\n")

    if Post_MEM_Buffer == None:
        ff.write("Post-MEM Buffer:\n")
    else:
        ff.write("Post-MEM Buffer:["+Post_MEM_Buffer.code+"]\n")
    ff.write("\n")
    pass


if __name__ == '__main__':
    sample = read_file()
    address = 64
    pc = 0
    f = open("t1_dis.txt","w")
    for pc in range(len(sample)):
        instruction= disassembly(sample[pc],pc)
        if flag:
            f.write(sample[pc][0] + "\t" + str(address + pc * 4) + "\t" + instruction + "\n")
        else:
            f.write(sample[pc][0][0:1]+" "+sample[pc][0][1:6]+" "+sample[pc][0][6:11]+" "+sample[pc][0][11:16]+" "+sample[pc][0][16:21]+" "+sample[pc][0][21:26]+" "+sample[pc][0][26:32]+"\t"+str(address+pc*4)+"\t"+instruction+"\n")

    f.close()

    pc = int(0)
    count = 1
    ff = open("t1_sim.txt", "w")
    while not finish:
        ff.write("--------------------")
        ff.write("\nCycle:"+str(count)+"\n\n")
        pipeline()
        printScore(ff)
        printRegister(ff)
        ff.write("\n")
        printData(ff)
        ff.write("\n")
        count = count + 1
    pass
