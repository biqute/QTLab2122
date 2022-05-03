from random import randrange


class Fridge_handler():
    def __init__(self):
        print('inizializzo il frigo')

    def get_sens(self, s):
        print('get il sens: ', s)
        return randrange(101)

    def execute(self, a):
        print('execute: ', a)
        if a == 'X':
            ret = 'X'+str(randrange(2))
            ret += 'A'+str(randrange(2))
            ret += 'C'+str(randrange(4))
            ret += 'P'+str('040F0000')
            ret += 'S'+'0'
            ret += 'O'+str(randrange(6))
            ret += 'E'+str(randrange(6))
            return ret

        return randrange(10)
