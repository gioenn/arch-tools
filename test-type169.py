import TRNSYSpy as TRNSYS


def test():
    inp1 = TRNSYS.getInputValue(1)
    TRNSYS.setOutputValue(1, inp1+1)
    return