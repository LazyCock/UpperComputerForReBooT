import numpy as np
from collections import deque


RoboHand_flag = False
Myo_flag = False
Emotiv_flag = False


# 手势代码-GestureCode
FIST = 0
PINCH = 1
DELIVER = 2
RELAX = 3
SPREAD = 4
TWIST = 5
POINT = 6
HOLD = 7


DataLen = 50
MyoInputs = 100
GestureCode = 0


# MyoDataFlow = [deque(maxlen=DataLen), deque(maxlen=DataLen), deque(maxlen=DataLen), deque(maxlen=DataLen),
#                deque(maxlen=DataLen), deque(maxlen=DataLen), deque(maxlen=DataLen), deque(maxlen=DataLen)]
MyoDataFlow = np.zeros(shape=(8, DataLen), dtype=int)


MyoDataFlowForModel = [deque(maxlen=MyoInputs), deque(maxlen=MyoInputs), deque(maxlen=MyoInputs), deque(maxlen=MyoInputs),
                       deque(maxlen=MyoInputs), deque(maxlen=MyoInputs), deque(maxlen=MyoInputs), deque(maxlen=MyoInputs)]


def GetMyoInputs():
    for i in range(8):
        MyoDataFlowForModel[i].extend(MyoDataFlow[i])
