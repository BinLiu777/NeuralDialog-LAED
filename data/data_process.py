# import re
import regex as re
import json
from tqdm import tqdm

intents = ['返学费规则', '随单礼品问题', '绘本售前咨询', '金额查询', '返学费进度', '修改级别问题', '其他绘本问题', '倒计时查询', '返学费申请', 'VIP/退款申请']


def get_name(text):
    text = text.replace('~', '')
    patten = re.compile(r'\\n[\u4e00-\u9fa5]+：')
    res = re.findall(patten, text)
    res = [x.strip('\\n').strip('：') for x in res]
    res = set(res)
    res -= {'顾客'}
    return res.pop()


def clear_symbol(text):
    text = text.replace('\\n', '')
    text = re.sub(r':[a-zA-Z]+:', '', text)  # 表情
    patten = re.compile(r'[\u4e00-\u9fa5a-zA-Z0-9\p{P}~]')
    res = re.findall(patten, text)
    res = ''.join(res)
    res = res.replace('*', '')
    res = res.replace('()', '')
    res = res.replace('(｡)', '')
    return res


def clear_spec_sent(text):
    text = re.sub(r'[xw|您好][\s\S]*有什么可以帮您[。|~|！|？|呢、|呢？|的吗？]*', '', text)
    text = re.sub(r'嗨~[\s\S]*非常高兴为您服务！', '', text)
    text = re.sub(r'[您好|Hi]，我是[\s\S]*很高兴再次遇到您[！]*', '', text)
    text = re.sub(r'[非常]*抱歉[哦]*，由于现在咨询人数较多，[\s\S]*正在逐一解答。', '', text)
    text = re.sub(r'请您不要着急，耐心等待下吧。小鱼仔很快就来！', '', text)
    text = re.sub(r'请您耐心等待下，不要着急。小鱼仔很快就来！', '', text)
    text = re.sub(r'非常抱歉，咨询的人有些多，不能及时回复您，请您耐心等待下，[\s\S]*马上赶来~', '', text)
    text = re.sub(r'请问还有其他[的问题]*可以帮您的吗[？|~|亲亲~]*', '', text)
    text = re.sub(r'[如果没有，]*麻烦您给个好评哦[~]*', '', text)
    text = re.sub(r'如果没有请您稍后为我的服务作出评价，谢谢！', '', text)
    text = re.sub(r'为了保证服务质量，[\s\S]*结束了本次服务。', '', text)
    text = re.sub(r'如果您还有其他问题，请随时联系我哦！', '', text)
    text = re.sub(r'遇见您是我最大的幸运。祝您学习愉快，再见！', '', text)
    text = re.sub(r'[不客气，您好，|嗨~]*如果我的服务有帮助到您，麻烦您给我一个好评哦~感谢您的[支持]*[！]*', '', text)
    return text


def clear_address(text):
    text = re.sub(r'image[\s\S]*.[png|jpg|jpeg]', '', text)
    return text


def process_data(lines):
    data = []
    for i in tqdm(range(len(lines))):
        sess = {}
        sess['dialogue'] = []
        sess['scenario'] = {}

        saller_id, intent, text = lines[i].split('\t')

        text = clear_symbol(text)
        text = clear_address(text)
        text = clear_spec_sent(text)

        patten = re.compile(r'(顾客：|{}：)'.format(saller_id))
        texts = re.split(patten, text)
        text_merge = []
        cur = ''
        for j in range(len(texts)):
            turn = texts[j]
            if turn:
                if turn == '顾客：' or turn == saller_id + '：':
                    try:
                        if texts[j+1] == '顾客：' or texts[j+1] == saller_id + '：':
                            continue
                    except:
                        continue
                    if cur != turn:
                        text_merge.append(turn)
                        cur = turn
                    else:
                        continue
                else:
                    try:
                        text_merge[-1] += turn
                    except:
                        continue

        for j in range(len(text_merge)):
            dialogue = {}
            turn = text_merge[j]
            name, utterance = turn.split('：', 1)
            dialogue['turn'] = name if name == '顾客' else '小鱼仔'
            dialogue['data'] = {}
            dialogue['data']['end_dialogue'] = True if j == len(text_merge) - 1 else False
            dialogue['data']['utterance'] = utterance
            dialogue['data']['requested'] = {}
            dialogue['data']['slots'] = {}
            sess['dialogue'].append(dialogue)

        sess['scenario']['kb'] = {}
        sess['scenario']['task'] = {}
        sess['scenario']['uuid'] = {}
        sess['scenario']['task']['intent'] = intent

        if intent in intents:
            data.append(sess)

    train_data = []
    dev_data = []
    test_data = []
    for i in range(len(data)):
        if i % 10 == 8:
            dev_data.append(data[i])
        elif i % 10 == 9:
            test_data.append(data[i])
        else:
            train_data.append(data[i])
    print(len(train_data))
    print(len(dev_data))
    print(len(test_data))

    json_train = json.dumps(train_data, indent=4, ensure_ascii=False)
    with open('customer_service/customer_train.json', 'w') as json_file:
        json_file.write(json_train)

    json_dev = json.dumps(dev_data, indent=4, ensure_ascii=False)
    with open('customer_service/customer_dev.json', 'w') as json_file:
        json_file.write(json_dev)

    json_test = json.dumps(test_data, indent=4, ensure_ascii=False)
    with open('customer_service/customer_test.json', 'w') as json_file:
        json_file.write(json_test)


if __name__ == '__main__':

    with open('customer_service/intent_other_big.txt', 'r') as f:
        lines_ = f.readlines()
    lines1 = []
    for line in lines_:
        line = line.strip().split('\t')
        text = line[1]
        try:
            name = get_name(text)
        except:
            continue
        lines1.append('\t'.join([name, line[-1].strip('\n'), line[1]]))
    # process_data(lines1, 'customer_service/customer_service_2.json')

    with open('customer_service/dialog.txt', 'r') as f:
        lines2 = f.readlines()
    # process_data(lines2, 'customer_service/customer_service1.json')

    lines = lines1 + lines2
    process_data(lines)


