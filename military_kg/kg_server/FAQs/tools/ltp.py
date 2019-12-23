import os
from pyltp import Postagger, Parser


class LTP:
    def __init__(self, ltp_dir):
        # 要加载的模型
        self.pos_model_path = os.path.join(ltp_dir, "pos.model")
        self.parser_model_path = os.path.join(ltp_dir, "parser.model")
        # 词性标注
        self.postagger = Postagger()
        # 依存句法分析
        self.parser = Parser()
        print('ltp加载成功...')

    def postag(self, words):
        res = list()
        self.postagger.load(self.pos_model_path)
        postags = self.postagger.postag(words)
        # for index in range(len(postags)):
        #     res.append((words[index], postags[index]))
        self.postagger.release()
        return postags

    # 句法依存分析
    def parse(self, words, postags):
        res = list()
        self.parser.load(self.parser_model_path)
        arcs = self.parser.parse(words, postags)  # 提取依存关系
        rely_id = [arc.head for arc in arcs]  # 提取依存父节点id
        relation = [arc.relation for arc in arcs]  # 提取依存关系
        heads = ['Root' if id == 0 else words[id - 1] for id in rely_id]  # 匹配依存父节点词语
        for i in range(len(words)):
            res.append((relation[i], words[i], heads[i]))
        self.parser.release()
        return res

    def ner(self, words, postags):
        entity_type = ['n', 'nh', 'ni', 'nl', 'ns', 'nz', 'i']
        i = 0
        n_words = []
        for j in range(len(postags)):
            if postags[j] in entity_type:
                i = i + 1
                n_words.append(words[j])
        return n_words

    def release(self):
        self.postagger.release()
        self.parser.release()
        print('ltp模型已释放...')
