from enum import Enum

Gravity = 9.80665

class AccelDirection(Enum):
    X = 0
    PX = 1
    NX = 2
    Y = 3
    PY = 4
    NY = 5
    Z = 6
    PZ = 7
    NZ = 8

    def zeroXoneYtwoZ(self) -> Literal[0,1,2]:
        return int(self.value / 3)

    def isNegative(self) -> bool:
        return self.value % 3 == 2
