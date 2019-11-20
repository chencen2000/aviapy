import os
import re
import json

def put_fd_grade():
    data = {}
    for root, dirs, files in os.walk('.'):
        if len(files) > 0:
            for fn in files:
                m = re.match('classify_(?P<imei>\d+).txt', fn)
                if m is not None:
                    with open(os.path.join(root, fn)) as f:
                        s = f.read()
                        m1 = re.search('Grade = (?P<grade>\S+)', s)
                        if m1 is not None:                        
                            if m.group('imei') in data:
                                print('{}: {}'.format(m.group('imei'), m1.group('grade')))
                            else:
                                data[m.group('imei').zfill(4)] = m1.group('grade')
    #print(json.dumps(data, indent=4))
    with open('fdgrading.json', 'w') as f:
        json.dump(data, f, indent=4)
    with open('verizon_data.json') as f:
        vzw=json.load(f)
    for vd in vzw:
        s = vd['imei'][-4:]
        if s in data:
            vd['fd'] = data[s]
        else:
            s = vd['imei'][-5:]
            if s in data:
                vd['fd'] = data[s]
    #print(json.dumps(vzw))        
    with open('temp.json', 'w') as f:
        json.dump(vzw,f, indent=4)

def check_match():
    with open('temp.json') as f:
        data = json.load(f)
    total=len(data)
    match=0
    for d in data:
        try:
            if d['vzw'] == d['fd']:
                match += 1
        except:
            pass
    print('total: {}, match: {}, rate={:.2%}'.format(total, match, match/total))

put_fd_grade()
with open('temp.json') as f:
    data = json.load(f)
for d in data:
    if 'fd' not in d:
        print(d['imei'])
