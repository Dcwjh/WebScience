import pkuseg


class PKU:
    def __init__(self, customized_dict=None):
        self.pku = pkuseg.pkuseg(user_dict=customized_dict)
        print('pku加载成功...')

    def cut(self, sentence):
        return self.pku.cut(sentence)
