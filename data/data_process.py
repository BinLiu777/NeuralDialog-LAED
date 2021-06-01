# import re
import regex as re
import json
from tqdm import tqdm

intents = ['返学费规则', '随单礼品问题', '绘本售前咨询', '金额查询', '返学费进度', '修改级别问题', '其他绘本问题', '倒计时查询', '返学费申请', 'VIP/退款申请']

def clear_text(text):
    text = text.replace('\\n', '')
    patten = re.compile(r'[\u4e00-\u9fa5a-zA-Z0-9\p{P}]')
    res = re.findall(patten, text)
    res = ''.join(res)
    res = res.replace('*', '')
    return res

def get_name(text):
    text = text.replace('~', '')
    patten = re.compile(r'\\n[\u4e00-\u9fa5]+：')
    res = re.findall(patten, text)
    res = [x.strip('\\n').strip('：') for x in res]
    res = set(res)
    res -= {'顾客'}
    # if len(res) != 1:
    #     print(res)
    #     print(text)
    return res.pop()


def process_data(lines):
    data = []
    for i in tqdm(range(len(lines))):
        sess = {}
        sess['dialogue'] = []
        sess['scenario'] = {}

        saller_id, intent, text = lines[i].split('\t')
        text = clear_text(text)
        patten = re.compile(r'(顾客：|{}：)'.format(saller_id))
        texts = re.split(patten, text)
        text_merge = []
        cur = ''
        for turn in texts:
            if turn:
                if turn == '顾客：' or turn == saller_id + '：':
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


