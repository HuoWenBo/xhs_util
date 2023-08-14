from loguru import logger

from top2vec import Top2Vec


class Model:
    def __init__(self, path="models/models3") -> None:
        self.model = Top2Vec.load(path)
        self.classes = {
            0: "外出（生活）",
            1: "美术（笔|文化）",
            2: "美食",
            3: "生活（日常）",
            4: "财经（其他）",
            5: "音乐（其他）",
            6: "旅行",
            7: "母婴",
            8: "文化",
            9: "居家（装修）",
            10: "生活（日常）",
            11: "其他",
            12: "穿搭",
            13: "健身",
            14: "夫妻",
            15: "美妆",
            16: "其他",
            17: "护发",
            18: "科技（数码）",
            19: "车",
            20: "萌宠",
            21: "医疗",
            22: "萌宠",
            23: "日常（其他）",
            24: "旅游（地名）",
            25: "影视（其他）",
            26: "设计（其他）",
            27: "游戏",
            28: "日常（其他）",
            29: "运动",
            30: "科技（好物）",
            31: "美食",
            32: "旅游（地名）",
            33: "萌宠",
            34: "婚姻",
            35: "美食",
        }
        logger.info("模型加载完成")

    def get_topic(self, d: str) -> list:
        """
        d: 文本(需要判断的一段文字)
        return: list
        """
        topic_words, word_scores, topic_scores, topic_nums = self.model.query_topics(
            d, num_topics=5
        )
        result = []
        for i in range(5):
            logger.info(
                f"Topic ID({topic_nums[i]}), Topic Name({self.classes[topic_nums[i]]}): {topic_scores[i] * 100:.2f}%"
            )
            if i == 0:
                result.append(self.classes[topic_nums[i]])
            elif topic_scores[i] > 0.7:
                result.append(self.classes[topic_nums[i]])
            elif topic_scores[i] > 0.6:
                result.append(self.classes[topic_nums[i]])
            elif topic_scores[i] > 0.55 and len(result) < 3:
                if len(result) < 2:
                    result.append(self.classes[topic_nums[i]])
            elif topic_scores[i] > 0.5 and len(result) < 2:
                if len(result) <= 0:
                    result.append(self.classes[topic_nums[i]])
            # else: return ['其它'] if len(result) == 0 else result.append(self.classes[topic_nums[0]])
        # if len(result) == 1: result.append('其他')
        # if len(result) <=1 : tags = jieba.analyse.extract_tags(d, topK=3)
        return result

    def judge(self, d: str, ncls: str) -> bool:
        """
        d: 文本(需要判断的一段文字)
        ncls: 需要匹配的类别
        return: bool
        """
        topic_words, word_scores, topic_scores, topic_nums = self.model.query_topics(
            d, num_topics=3)
        for i in range(3):
            if ncls in self.classes[topic_nums[i]] and topic_scores[i] > 0.5:
                return True
        return False

    def get_all_tags(self, d: str, desc: str) -> tuple[list, str]:
        tag_main = self.get_topic(d)
        dict_labels = [
            '美食', '好物', '测评', '旅行', '宠物', '探店', '校园', '文化', '健身', '音乐', '影视', '设计',
            '运动', '护发', '穿搭', '医疗', '日常', '婚姻', '母婴', '夫妻', '居家', '车', '美妆', '游戏',
            '旅游'
        ]
        works: list[str] = ['育婴师', '育儿师', '营养师', '设计师', '幼师', '舞蹈师']
        profession = [work for work in works if work in desc]
        # for i in works:
        #     if i in desc:
        #         profession.append(i)
        dict_labels = ['好物', '测评', '时尚', '美妆', '护肤']
        d_d = d.replace(desc, '')
        for i in dict_labels:
            if i in d_d:
                tag_main.append(i)
        # tag_main.extend(jieba.analyse.extract_tags(d, topK=3, allowPOS=('n')))
        return tag_main, ','.join(profession)
