import numpy as np
import xml.etree.ElementTree as ET
import json
import os
import pandas
import re
import functools
from sklearn.feature_extraction import DictVectorizer
from sklearn import cluster
import csv


def num(s):
    try:
        return int(s)
    except ValueError:
        try:
            return float(s)
        except ValueError:
            return s


def etree_to_dict(t):
    d = {}
    for c in list(t):
        if c.text and not c.text.isspace():
            d[c.tag] = num(c.text)
        else:
            if len(c) > 0:
                a = []
                for ch in c.getchildren():
                    a.append(ch.text)
                d[c.tag] = a
    d.update(t.attrib)
    return d


def parse_defect_xml(filename):
    defects = []
    myxml = ET.parse(filename)
    surfaces = myxml.findall('.//surface')
    for surface in surfaces:
        defect_items = surface.findall('./sensor/defect/item')
        for item in defect_items:
            d = etree_to_dict(item)
            d['surface'] = surface.attrib['name']
            # ignore class='defect' and type='discoloration'
            if d['class'] == 'defect' and d['type'] == 'Discoloration' \
                    or d['type'] == 'OK' or d['type'] == 'OK' or d['class'] == 'fail':
                pass
            else:
                defects.append(d)
    return defects


def parse_avia_log(root='data270_xml', output='output'):
    # root = '117_Testing Set'
    # output = 'output'
    rg = re.compile(r'^defect_(\d*).xml$')
    vdb = None
    with open('verizon_data.json') as f:
        vdb = json.load(f)
    for r, d, f in os.walk(root):
        for fn in f:
            m = rg.match(fn)
            if m:
                print("parse: {}".format(fn))
                defects = parse_defect_xml(os.path.join(r, fn))
                vd = find_by_imei_last(m.group(1), vdb)
                dict = {}
                dict.update(vd)
                dict['defects'] = defects
                with open(os.path.join(output, '{}.json'.format(vd['imei'])), 'w') as f:
                    json.dump(dict, f, indent=4)


def find_by_imei_last(imei, vdb):
    ret = None
    for v in vdb:
        if v['imei'].endswith('{:0>4}'.format(imei)):
            ret = v
            break
    return ret


def load_device_json(folder='data270_json'):
    ret = []
    for fn in os.listdir(folder):
        data = None
        fullname = os.path.join(folder, fn)
        if os.path.isfile(fullname):
            with open(fullname) as f:
                try:
                    data = json.load(f)
                except:
                    pass
        if data:
            ret.append(data)
    return ret


def get_features(data):
    d1 = []
    d2 = []
    if data is not None:
        model = data['model']
        color = data['color']
        defects = data['defects']
        for i in defects:
            # print(i)
            if i['class'] == 'defect':
                n = {}
                n['model'] = model
                n['color'] = color
                n.update(i)
                n.pop('class', None)
                n.pop('defect_item', None)
                n.pop('location', None)
                d1.append(n)
            elif i['class'] == 'measurement':
                n = {}
                n['model'] = model
                n['color'] = color
                n.update(i)
                n.pop('class', None)
                n.pop('type', None)
                n.pop('surface', None)
                d2.append(n)
    return {
        'defects': d1,
        'measurement': d2
    }


def get_feature_score(data):
    features = {}
    if data:
        for d in data['defects']:
            if d['class'] == 'defect':
                k = '{}_{}'.format(d['surface'], d['type'])
                v = d['length'] * d['area_mm'] * d['contrast'] / d['width']
                if k not in features:
                    features[k] = 0
                features[k] += v
                pass
            elif d['class'] == 'measurement':
                features[d['region']] = d['value']
                pass
            else:
                pass
        data['features'] = features
    return data


def put_together(root):
    all_data = {
        'defects': [],
        'measurement': []
    }
    for fn in os.listdir(root):
        data = None
        fullname = os.path.join(root, fn)
        if os.path.isfile(fullname):
            with open(fullname) as f:
                try:
                    data = json.load(f)
                except:
                    pass
        if data:
            fe = get_features(data)
            all_data['defects'].extend(fe['defects'])
            all_data['measurement'].extend(fe['measurement'])
    return all_data


def csv_record(nc_d):
    ret = {
        'vzw': 'D',
        'Discoloration_Mic': 0,
        'Discoloration_Logo': 0,
        'Discoloration_Rear_Cam': 0,
        'Discoloration_Switch': 0
    }
    for i in range(0, nc_d):
        ret['D_{:03d}'.format(i+1)] = 0
    return ret


def csv_recode_score():
    return {
        'vzw': 'D',
        'AA_Scratch': 0,
        'AA_Nick': 0,
        'A_Scratch': 0,
        'A_Nick': 0,
        'A_PinDotGroup': 0,
        'B_Scratch': 0,
        'B_Nick': 0,
        'B_PinDotGroup': 0,
        'Logo': 0,
        'Switch': 0,
        'Rear_Cam': 0,
        'Mic': 0,
    }


def separate_defects_by_surface(defects):
    ret = {}
    df = pandas.DataFrame.from_dict(defects)
    surfaces = df.surface.unique()
    for s in surfaces:
        x = df[df.surface == s]
        # d = {s: x.to_dict(orient='records')}
        ret[s] = x.to_dict(orient='records')
    return ret


def prepare_data_1(folder, nc_d=25):
    db = put_together(folder)
    surfaces = separate_defects_by_surface(db['defects'])
    for s in surfaces:
        dv = DictVectorizer()
        vec = dv.fit_transform(surfaces[s])
        km = cluster.KMeans(n_clusters=nc_d)
        km.fit(vec)
        surfaces[s] = (dv, km)
    # dv_defects = DictVectorizer()
    # vec_defects = dv_defects.fit_transform(db['defects'])
    # km_defects = cluster.KMeans(n_clusters=nc_d)
    # km_defects.fit(vec_defects)
    ready = []
    for fn in os.listdir(folder):
        data = None
        fullname = os.path.join(folder, fn)
        if os.path.isfile(fullname):
            with open(fullname) as f:
                try:
                    data = json.load(f)
                except:
                    pass
        if data:
            fe = get_features(data)
            r = {}
            r['vzw'] = data['vzw']
            r['measurement'] = fe['measurement']
            if len(fe['defects']) > 0:
                ss = separate_defects_by_surface(fe['defects'])
                for s in ss:
                    dv, km = surfaces[s]
                    vec = dv.transform(ss[s])
                    p = km.transform(ss[s])
                    r[s] = p.tolist()
            ready.append(r)
    # save data into json
    # with open('test.json', 'w') as f:
    #     json.dump(ready, f, indent=4)
    ready_csv = []
    for r in ready:
        csv = csv_record(nc_d)
        csv['vzw'] = r['vzw']
        for i in r['defects']:
            k = 'D_{:03d}'.format(i+1)
            if k in csv:
                csv[k] += 1
        for i in r['measurement']:
            k = 'Discoloration_{}'.format(i['region'])
            if k in csv:
                csv[k] = i['value']
        ready_csv.append(csv)
    # with open('test.json', 'w') as f:
    #     json.dump(ready_csv, f, indent=4)
    return ready_csv


def prepare_data(folder, nc_d=25):
    db = put_together(folder)
    dv_defects = DictVectorizer()
    vec_defects = dv_defects.fit_transform(db['defects'])
    km_defects = cluster.KMeans(n_clusters=nc_d)
    km_defects.fit(vec_defects)
    ready = []
    for fn in os.listdir(folder):
        data = None
        fullname = os.path.join(folder, fn)
        if os.path.isfile(fullname):
            with open(fullname) as f:
                try:
                    data = json.load(f)
                except:
                    pass
        if data:
            fe = get_features(data)
            if len(fe['defects']) > 0:
                vec = dv_defects.transform(fe['defects'])
                p = km_defects.predict(vec)
                data['vd'] = p.tolist()
                r = {}
                r['vzw'] = data['vzw']
                r['defects'] = p.tolist()
                r['measurement'] = fe['measurement']
            ready.append(r)
    # save data into json
    # with open('test.json', 'w') as f:
    #     json.dump(ready, f, indent=4)
    ready_csv = []
    for r in ready:
        csv = csv_record(nc_d)
        csv['vzw'] = r['vzw']
        for i in r['defects']:
            k = 'D_{:03d}'.format(i+1)
            if k in csv:
                csv[k] += 1
        for i in r['measurement']:
            k = 'Discoloration_{}'.format(i['region'])
            if k in csv:
                csv[k] = i['value']
        ready_csv.append(csv)
    # with open('test.json', 'w') as f:
    #     json.dump(ready_csv, f, indent=4)
    return ready_csv


def prepare_data_score(folder):
    db = []
    for fn in os.listdir(folder):
        data = None
        fullname = os.path.join(folder, fn)
        if os.path.isfile(fullname):
            with open(fullname) as f:
                try:
                    data = json.load(f)
                except:
                    pass
        if data:
            fe = get_feature_score(data)
            r = csv_recode_score()
            r['vzw'] = fe['vzw']
            r['model'] = fe['model']
            r['color'] = fe['color']
            for f in fe['features']:
                if f in r:
                    r[f] = fe['features'][f]
            db.append(r)
    with open('test.json', 'w') as f:
        json.dump(db, f, indent=4)
    df = pandas.DataFrame.from_dict(db)
    df['model'] = df['model'].astype('category').cat.codes
    df['color'] = df['color'].astype('category').cat.codes
    df['label'] = df['vzw'].astype('category').cat.codes
    df.drop('vzw', axis=1).to_csv('test.csv', index=False)


def count_defects(defects, stype, surface, min_l, max_l, min_w, max_w, logic_and=True):
    count = 0
    for d in defects:
        if d['class'] == 'defect' and d['type'] == stype and d['surface'] == surface:
            if logic_and:
                if min_l<=d['length']<=max_l and min_w<=d['width']<=max_w:
                    count += 1
            else:
                if min_l <= d['length'] <= max_l or min_w <= d['width'] <= max_w:
                    count += 1
    return count


def count_defects_by_spec(data=None, spec=None):
    ret = {}
    if not data:
        with open('data270_json/359487085405625.json') as f:
            data = json.load(f)
    if not spec:
        spec = ET.parse('classify.xml')
    defects = data['defects']
    nodes = spec.findall('.//category/item')
    for n in nodes:
        stype = n.find('sort').text
        surface = n.find('surface').text
        # for f in n.find('flaw').getchildren():
        for f in list(n.find('flaw')):
            name = f.find('name').text
            max_l = 1000
            min_l = 0
            max_w = 1000
            min_w = 0
            logic_and = True
            if f.find('length_max') is not None:
                max_l = float(f.find('length_max').text)
            if f.find('width_max') is not None:
                max_w = float(f.find('width_max').text)
            if f.find('length_min') is not None:
                min_l = float(f.find('length_min').text)
            if f.find('width_min') is not None:
                min_w = float(f.find('width_min').text)
            if f.find('logic') is not None:
                if f.find('logic').text == 'or':
                    logic_and = False
            cnt = count_defects(defects, stype, surface, min_l, max_l, min_w, max_w, logic_and)
            ret[name] = cnt
    # 'All-All-All': 0,
    # 'All-A-All': 0,
    # 'All-A-Major': 0,
    # 'All-AA-All': 0,
    # 'All-AA-Major': 0,
    # 'All-B-All': 0,
    # 'All-B-Major': 0,
    ret['All-All-All'] = len(defects)
    ret['All-AA-All'] = 0
    ret['All-AA-Major'] = 0
    ret['All-A-All'] = 0
    ret['All-A-Major'] = 0
    ret['All-B-All'] = 0
    ret['All-B-Major'] = 0
    for d in defects:
        if d['class'] == 'defect':
            k = 'All-{}-All'.format(d['surface'])
            if k in ret:
                ret[k] += 1
            k = 'All-{}-Major'.format(d['surface'])
            if d['length'] >= 15 or d['width'] >= 0.2:
                if k in ret:
                    ret[k] += 1
    return ret


def csv_read_counts():
    return {
        'All-All-All': 0,
        'All-A-All': 0,
        'All-A-Major': 0,
        'All-AA-All': 0,
        'All-AA-Major': 0,
        'All-B-All': 0,
        'All-B-Major': 0,
        'Discoloration-Logo': 0,
        'Discoloration-Mic': 0,
        'Discoloration-Rear_Cam': 0,
        'Discoloration-Switch': 0,
        'Nick-A-Major': 0,
        'Nick-A-Minor': 0,
        'Nick-A-Other1': 0,
        'Nick-A-Other2': 0,
        'Nick-A-S': 0,
        'Nick-AA-Major': 0,
        'Nick-AA-Minor': 0,
        'Nick-AA-Other1': 0,
        'Nick-AA-Other2': 0,
        'Nick-AA-S': 0,
        'Nick-B-Major': 0,
        'Nick-B-Minor': 0,
        'Nick-B-Other1': 0,
        'Nick-B-Other2': 0,
        'Nick-B-S': 0,
        'PinDotGroup-A-10x10': 0,
        'PinDotGroup-A-10x40': 0,
        'PinDotGroup-A-Other': 0,
        'PinDotGroup-B-10x10': 0,
        'PinDotGroup-B-10x40': 0,
        'PinDotGroup-B-Other': 0,
        'Scratch-A-Major': 0,
        'Scratch-A-Minor': 0,
        'Scratch-A-Other1': 0,
        'Scratch-A-Other2': 0,
        'Scratch-A-Other3': 0,
        'Scratch-A-S1': 0,
        'Scratch-A-S2': 0,
        'Scratch-AA-Major': 0,
        'Scratch-AA-Minor': 0,
        'Scratch-AA-Other1': 0,
        'Scratch-AA-Other2': 0,
        'Scratch-AA-S': 0,
        'Scratch-B-Major': 0,
        'Scratch-B-Minor': 0,
        'Scratch-B-Other1': 0,
        'Scratch-B-Other2': 0,
        'Scratch-B-Other3': 0,
        'Scratch-B-S1': 0,
        'Scratch-B-S2': 0,
    }


def prepare_data_by_spec(folder='data270_json', specfn='classify.xml', output='test.csv'):
    # folder = 'data270_json'
    spec = ET.parse(specfn)
    db = []
    for fn in os.listdir(folder):
        with open(os.path.join(folder, fn)) as f:
            data = json.load(f)
        counts = {}
        counts['vzw'] = data['vzw']
        counts['model'] = data['model']
        counts['color'] = data['color']
        counts.update(count_defects_by_spec(data, spec))
        for d in data['defects']:
            if d['class'] == 'measurement' and d['type'] == 'Discoloration':
                counts['Discoloration-{}'.format(d['region'])] = d['value']
        db.append(counts)
    with open('test.json', 'w') as f:
        json.dump(db, f, indent=4)
    grades = ['A+', 'A', 'B', 'C', 'D+']
    # db = json.load(open('test.json'))
    db1 = []
    for record in db:
        n = csv_read_counts()
        for key in n:
            if key in record:
                n[key] = record[key]
        n['vzw'] = grades.index(record['vzw'])
        db1.append(n)
    df = pandas.DataFrame.from_dict(db1)
    df.to_csv(output, index=False)


def combinate(l):
    return functools.reduce(lambda x, y: [np.append(i, j) for i in x for j in y], l)


def generate_grade_ap(output='grade_ap.csv'):
    spec = [
        ('Scratch-AA-S', 1, 'AA', False),
        ('Scratch-A-S1', 3, 'A', False),
        ('Scratch-B-S1', 3, 'B', False),
    ]
    l = None
    f = None
    if os.path.exists('tempdata/grade_ap_raw_data.csv'):
        f = open('tempdata/grade_ap_raw_data.csv')
        r = csv.reader(f)
        h = next(r)
        l = r
    else:
        l = []
        for s in spec:
            a = list(range(0, s[1]+1))
            l.append(a)
        l = combinate(l)
    db = []
    for ii in l:
        i = [int(x) for x in ii]
        r = csv_read_counts()
        r['All-All-All'] = int(sum(i))
        for j in range(len(i)):
            k = 'All-{}-All'.format(spec[j][2])
            if k in r:
                r[k] += int(i[j])
            k = spec[j][0]
            if k in r:
                r[k] = int(i[j])
        if r['All-All-All'] <= 3:
            db.append(r)
    if f is not None:
        f.close()
    if os.path.splitext(output)[1].lower() == '.json':
        with open(output, 'w') as f:
            json.dump(db, f, indent=4)
    elif os.path.splitext(output)[1].lower() == '.csv':
        df = pandas.DataFrame.from_dict(db)
        df.to_csv(output, index=False)


def generate_grade_ap_0(output='grade_ap.json'):
    spec = [
        ('Scratch-AA-S', 1, 'AA', False),
        ('Scratch-A-S1', 3, 'A', False),
        ('Scratch-B-S1', 3, 'B', False),
    ]
    l = []
    for s in spec:
        a = list(range(0, s[1]+1))
        l.append(a)
    l = combinate(l)
    db = []
    for i in l:
        r = csv_read_counts()
        r['All-All-All'] = int(sum(i))
        for j in range(len(i)):
            k = 'All-{}-All'.format(spec[j][2])
            if k in r:
                r[k] += int(i[j])
            k = spec[j][0]
            if k in r:
                r[k] = int(i[j])
        if r['All-All-All'] <= 3:
            db.append(r)
    with open(output, 'w') as f:
        json.dump(db, f, indent=4)


def generate_grade_a(output='grade_a.csv'):
    spec = [
        ('Scratch-AA-S', range(0, 1+1), 'AA', False),
        ('Scratch-A-S2', range(0, 4+1), 'A', False),
        ('Nick-A-S', range(0, 4+1), 'A', False),
        ('Scratch-B-S2', range(3, 12+1), 'B', False),
        ('Nick-B-S', range(3, 12+1), 'B', False),
        ('PinDotGroup-B-10x10', range(0, 2+1), 'B', False),
        ('PinDotGroup-B-10x40', range(0, 1+1), 'B', False),
    ]
    l = None
    f = None
    if os.path.exists('tempdata/grade_a_raw_data.csv'):
        f = open('tempdata/grade_a_raw_data.csv')
        r = csv.reader(f)
        h = next(r)
        l = r
    else:
        l = []
        for s in spec:
            # a = list(range(0, s[1]+1))
            l.append(list(s[1]))
        l = combinate(l)
    db = []
    for ii in l:
        i = [int(x) for x in ii]
        r = csv_read_counts()
        r['All-All-All'] = int(sum(i))
        for j in range(len(i)):
            k = 'All-{}-All'.format(spec[j][2])
            if k in r:
                r[k] += int(i[j])
            k = spec[j][0]
            if k in r:
                r[k] = int(i[j])
        if 3<r['All-All-All'] <= 12 and r['All-A-All']<=4 and r['All-B-All']<=12:
            db.append(r)
    if f is not None:
        f.close()
    df = pandas.DataFrame.from_dict(db)
    df.to_csv(output, index=False)


def generate_grade_a_0(output='grade_a.json'):
    spec = [
        ('Scratch-AA-S', range(0, 1+1), 'AA', False),
        ('Scratch-A-S2', range(0, 4+1), 'A', False),
        ('Nick-A-S', range(0, 4+1), 'A', False),
        ('Scratch-B-S2', range(3, 12+1), 'B', False),
        ('Nick-B-S', range(3, 12+1), 'B', False),
        ('PinDotGroup-B-10x10', range(0, 2+1), 'B', False),
        ('PinDotGroup-B-10x40', range(0, 1+1), 'B', False),
    ]
    l = []
    for s in spec:
        # a = list(range(0, s[1]+1))
        l.append(list(s[1]))
    l = combinate(l)
    db = []
    for i in l:
        r = csv_read_counts()
        r['All-All-All'] = int(sum(i))
        for j in range(len(i)):
            k = 'All-{}-All'.format(spec[j][2])
            if k in r:
                r[k] += int(i[j])
            k = spec[j][0]
            if k in r:
                r[k] = int(i[j])
        if 3<r['All-All-All'] <= 12 and r['All-A-All']<=4 and r['All-B-All']<=12:
            db.append(r)
    with open(output, 'w') as f:
        json.dump(db, f, indent=4)


def generate_grade_b(output='grade_b.csv'):
    spec = [
        ('Scratch-AA-Minor', range(3, 6+1), 'AA', False),
        ('Scratch-AA-Major', range(0, 1+1), 'AA', True),
        ('Nick-AA-Minor', range(3, 6+1), 'AA', False),
        ('Nick-AA-Major', range(0, 1+1), 'AA', True),
        ('Scratch-A-Minor', range(3, 6+1), 'A', False),
        ('Scratch-A-Major', range(0, 1+1), 'A', True),
        ('Nick-A-Minor', range(3, 6+1), 'A', False),
        ('Nick-A-Major', range(0, 1+1), 'A', True),
        ('Scratch-B-Minor', range(8, 16+1), 'B', False),
        ('Scratch-B-Major', range(0, 2+1), 'B', True),
        ('Nick-B-Minor', range(8, 16+1), 'B', False),
        ('Nick-B-Major', range(0, 2+1), 'B', True),
        ('PinDotGroup-B-10x10', range(0, 4+1), 'B', False),
        ('PinDotGroup-B-10x40', range(0, 1+1), 'B', False),
    ]
    l = None
    f = None
    if os.path.exists('tempdata/grade_b_raw_data.csv'):
        f = open('tempdata/grade_b_raw_data.csv')
        r = csv.reader(f)
        h = next(r)
        l = r
    else:
        l = []
        for s in spec:
            # a = list(range(0, s[1]+1))
            l.append(list(s[1]))
        l = combinate(l)
    # print(len(l))
    db = []
    for ii in l:
        i = [int(x) for x in ii]
        if 12 < sum(i) <= 18:
            r = csv_read_counts()
            r['All-All-All'] = int(sum(i))
            for j in range(len(i)):
                k = 'All-{}-All'.format(spec[j][2])
                if k in r:
                    r[k] += int(i[j])
                k = spec[j][0]
                if k in r:
                    r[k] = int(i[j])
                if spec[j][3]:
                    k = 'All-{}-Major'.format(spec[j][2])
                    if k in r:
                        r[k] += int(i[j])
            if 12<r['All-All-All'] <= 18 and r['All-AA-All']<=6 and r['All-AA-Major']<=1 and r['All-A-All']<=6 and r['All-A-Major']<=6 and r['All-B-All']<=16 and r['All-B-Major']<=2:
                db.append(r)
    df = pandas.DataFrame.from_dict(db)
    df.to_csv(output, index=False)


def generate_grade_b_0(output='grade_b.json'):
    spec = [
        ('Scratch-AA-Minor', range(3, 6+1), 'AA', False),
        ('Scratch-AA-Major', range(0, 1+1), 'AA', True),
        ('Nick-AA-Minor', range(3, 6+1), 'AA', False),
        ('Nick-AA-Major', range(0, 1+1), 'AA', True),
        ('Scratch-A-Minor', range(3, 6+1), 'A', False),
        ('Scratch-A-Major', range(0, 1+1), 'A', True),
        ('Nick-A-Minor', range(3, 6+1), 'A', False),
        ('Nick-A-Major', range(0, 1+1), 'A', True),
        ('Scratch-B-Minor', range(8, 16+1), 'B', False),
        ('Scratch-B-Major', range(0, 2+1), 'B', True),
        ('Nick-B-Minor', range(8, 16+1), 'B', False),
        ('Nick-B-Major', range(0, 2+1), 'B', True),
        ('PinDotGroup-B-10x10', range(0, 4+1), 'B', False),
        ('PinDotGroup-B-10x40', range(0, 1+1), 'B', False),
    ]
    l = []
    for s in spec:
        # a = list(range(0, s[1]+1))
        l.append(list(s[1]))
    l = combinate(l)
    print(len(l))
    db = []
    for i in l:
        r = csv_read_counts()
        r['All-All-All'] = int(sum(i))
        for j in range(len(i)):
            k = 'All-{}-All'.format(spec[j][2])
            if k in r:
                r[k] += int(i[j])
            k = spec[j][0]
            if k in r:
                r[k] = int(i[j])
            if spec[j][3]:
                k = 'All-{}-Major'.format(spec[j][2])
                if k in r:
                    r[k] += int(i[j])
        if 12<r['All-All-All'] <= 18 and r['All-AA-All']<=6 and r['All-AA-Major']<=1 and r['All-A-All']<=6 and r['All-A-Major']<=6 and r['All-B-All']<=16 and r['All-B-Major']<=2:
            db.append(r)
    with open(output, 'w') as f:
        json.dump(db, f, indent=4)


def generate_grade_b_raw_data(output='grade_b_rawdata.csv'):
    spec = [
        ('Scratch-AA-Minor', range(1, 6 + 1), 'AA', False),
        ('Scratch-AA-Major', range(0, 1 + 1), 'AA', True),
        ('Nick-AA-Minor', range(1, 6 + 1), 'AA', False),
        ('Nick-AA-Major', range(0, 1 + 1), 'AA', True),
        ('Scratch-A-Minor', range(2, 6 + 1), 'A', False),
        ('Scratch-A-Major', range(0, 1 + 1), 'A', True),
        ('Nick-A-Minor', range(2, 6 + 1), 'A', False),
        ('Nick-A-Major', range(0, 1 + 1), 'A', True),
        ('Scratch-B-Minor', range(3, 16 + 1), 'B', False),
        ('Scratch-B-Major', range(0, 2 + 1), 'B', True),
        ('Nick-B-Minor', range(3, 16 + 1), 'B', False),
        ('Nick-B-Major', range(0, 2 + 1), 'B', True),
        ('PinDotGroup-B-10x10', range(0, 4 + 1), 'B', False),
        ('PinDotGroup-B-10x40', range(0, 1 + 1), 'B', False),
    ]
    headers = []
    csv_file = open(output, 'w')
    wr = csv.writer(csv_file)
    # wr.writerow(['Scratch-AA-Minor','Scratch-AA-Major'])
    for s in spec:
        headers.append(s[0])
    wr.writerow(headers)
    for i0 in spec[0][1]:
        for i1 in spec[1][1]:
            for i2 in spec[2][1]:
                for i3 in spec[3][1]:
                    for i4 in spec[4][1]:
                        for i5 in spec[5][1]:
                            for i6 in spec[6][1]:
                                for i7 in spec[7][1]:
                                    for i8 in spec[8][1]:
                                        for i9 in spec[9][1]:
                                            for i10 in spec[10][1]:
                                                for i11 in spec[11][1]:
                                                    for i12 in spec[12][1]:
                                                        for i13 in spec[13][1]:
                                                            i = [i0, i1, i2, i3, i4, i5, i6, i7, i8, i9, i10, i11, i12,
                                                                 i13]
                                                            if 12 < sum(i) <= 18:
                                                                wr.writerow(i)
    csv_file.close()


def generate_grade_c(output='grade_c.csv'):
    spec = [
        ('Scratch-AA-Minor', range(2, 8+1), 'AA', False),
        ('Scratch-AA-Major', range(0, 1+1), 'AA', True),
        ('Nick-AA-Minor', range(2, 8+1), 'AA', False),
        ('Nick-AA-Major', range(0, 1+1), 'AA', True),
        ('Scratch-A-Minor', range(2, 8+1), 'A', False),
        ('Scratch-A-Major', range(0, 1+1), 'A', True),
        ('Nick-A-Minor', range(2, 8+1), 'A', False),
        ('Nick-A-Major', range(0, 1+1), 'A', True),
        ('Scratch-B-Minor', range(4, 18+1), 'B', False),
        ('Scratch-B-Major', range(0, 3+1), 'B', True),
        ('Nick-B-Minor', range(4, 18+1), 'B', False),
        ('Nick-B-Major', range(0, 3+1), 'B', True),
        ('PinDotGroup-B-10x10', range(0, 4+1), 'B', False),
        ('PinDotGroup-B-10x40', range(0, 1+1), 'B', False),
    ]
    l = None
    f = None
    if os.path.exists('tempdata/grade_c_raw_data.csv'):
        f = open('tempdata/grade_c_raw_data.csv')
        r = csv.reader(f)
        h = next(r)
        l = r
    else:
        l = []
        for s in spec:
            # a = list(range(0, s[1]+1))
            l.append(list(s[1]))
        l = combinate(l)
    db = []
    for ii in l:
        i = [int(x) for x in ii]
        if 18 < sum(i) <= 26:
            r = csv_read_counts()
            r['All-All-All'] = int(sum(i))
            for j in range(len(i)):
                k = 'All-{}-All'.format(spec[j][2])
                if k in r:
                    r[k] += int(i[j])
                k = spec[j][0]
                if k in r:
                    r[k] = int(i[j])
                if spec[j][3]:
                    k = 'All-{}-Major'.format(spec[j][2])
                    if k in r:
                        r[k] += int(i[j])
            if 18<r['All-All-All'] <= 26 and r['All-AA-All']<=8 and r['All-AA-Major']<=1 and r['All-A-All']<=8 and r['All-A-Major']<=6 and r['All-B-All']<=18 and r['All-B-Major']<=2:
                db.append(r)
    df = pandas.DataFrame.from_dict(db)
    df.to_csv(output, index=False)


def generate_grade_c_0(output='grade_c.json'):
    spec = [
        ('Scratch-AA-Minor', range(2, 8+1), 'AA', False),
        ('Scratch-AA-Major', range(0, 1+1), 'AA', True),
        ('Nick-AA-Minor', range(2, 8+1), 'AA', False),
        ('Nick-AA-Major', range(0, 1+1), 'AA', True),
        ('Scratch-A-Minor', range(2, 8+1), 'A', False),
        ('Scratch-A-Major', range(0, 1+1), 'A', True),
        ('Nick-A-Minor', range(2, 8+1), 'A', False),
        ('Nick-A-Major', range(0, 1+1), 'A', True),
        ('Scratch-B-Minor', range(4, 18+1), 'B', False),
        ('Scratch-B-Major', range(0, 3+1), 'B', True),
        ('Nick-B-Minor', range(4, 18+1), 'B', False),
        ('Nick-B-Major', range(0, 3+1), 'B', True),
        ('PinDotGroup-B-10x10', range(0, 4+1), 'B', False),
        ('PinDotGroup-B-10x40', range(0, 1+1), 'B', False),
    ]
    l = []
    for s in spec:
        # a = list(range(0, s[1]+1))
        l.append(list(s[1]))
    l = combinate(l)
    db = []
    for i in l:
        r = csv_read_counts()
        r['All-All-All'] = int(sum(i))
        for j in range(len(i)):
            k = 'All-{}-All'.format(spec[j][2])
            if k in r:
                r[k] += int(i[j])
            k = spec[j][0]
            if k in r:
                r[k] = int(i[j])
            if spec[j][3]:
                k = 'All-{}-Major'.format(spec[j][2])
                if k in r:
                    r[k] += int(i[j])
        if 18<r['All-All-All'] <= 26 and r['All-AA-All']<=8 and r['All-AA-Major']<=1 and r['All-A-All']<=8 and r['All-A-Major']<=6 and r['All-B-All']<=18 and r['All-B-Major']<=2:
            db.append(r)
    with open(output, 'w') as f:
        json.dump(db, f, indent=4)


def generate_grade_ap_1(output='grade_ap.json'):
    spec = [
        ('Scratch-AA-S', 1),
        ("Scratch-A-S1", 3),
        ("Scratch-B-S1", 3)
    ]
    db = []
    for i0 in range(0, spec[0][1]+1):
        for i1 in range(0, spec[1][1] + 1):
            for i2 in range(0, spec[2][1] + 1):
                all_all = i0+i1+i2
                if all_all <= 3:
                    r = csv_read_counts()
                    r['All-All-All'] = all_all
                    r['All-AA-All'] = i0
                    r['All-A-All'] = i1
                    r['All-B-All'] = i2
                    r[spec[0][0]] = i0
                    r[spec[1][0]] = i1
                    r[spec[2][0]] = i2
                    db.append(r)
    with open(output, 'w') as f:
        json.dump(db, f, indent=4)


def generate_grade_a_1(output='grade_a.json'):
    spec = [
        ('Scratch-AA-S', 1),
        ("Scratch-A-S2", 4),
        ("Nick-A-S", 4),
        ("Scratch-B-S2", 12),
        ("Nick-B-S", 12),
        ("PinDotGroup-B-10x10", 3),
        ("PinDotGroup-B-10x40", 1),
    ]
    db = []
    for i0 in range(0, spec[0][1]+1):
        for i1 in range(0, spec[1][1] + 1):
            for i2 in range(0, spec[2][1] + 1):
                for i3 in range(0, spec[3][1] + 1):
                    for i4 in range(0, spec[4][1] + 1):
                        for i5 in range(0, spec[5][1] + 1):
                            for i6 in range(0, spec[6][1] + 1):
                                all_all = i0+i1+i2+i3+i4+i5+i6
                                all_aa = i0
                                all_a = i1+i2
                                all_b = i3+i4+i5+i6
                                if 3<all_all<=12 and all_a<=4 and all_b<=12:
                                    r = csv_read_counts()
                                    r['All-All-All'] = all_all
                                    r['All-AA-All'] = all_aa
                                    r['All-A-All'] = all_a
                                    r['All-B-All'] = all_b
                                    r[spec[0][0]] = i0
                                    r[spec[1][0]] = i1
                                    r[spec[2][0]] = i2
                                    r[spec[3][0]] = i3
                                    r[spec[4][0]] = i4
                                    r[spec[5][0]] = i5
                                    r[spec[6][0]] = i6
                                    db.append(r)
    with open(output, 'w') as f:
        json.dump(db, f, indent=4)


def generate_grade_b_1(output='grade_b.json'):
    spec = [
        ('Scratch-AA-Minor', 6),
        ('Scratch-AA-Major', 1),
        ('Nick-AA-Minor', 6),
        ('Nick-AA-Major', 1),
        ('Scratch-A-Minor', 6),
        ('Scratch-A-Major', 1),
        ('Nick-A-Minor', 6),
        ('Nick-A-Major', 1),
        ('Scratch-B-Minor', 16),
        ('Scratch-B-Major', 2),
        ('Nick-B-Minor', 16),
        ('Nick-B-Major', 2),
        ('PinDotGroup-B-10x10', 4),
        ('PinDotGroup-B-10x40', 1),
    ]
    db = []
    for i0 in range(2, spec[0][1]+1):
        for i1 in range(0, spec[1][1] + 1):
            for i2 in range(2, spec[2][1] + 1):
                for i3 in range(0, spec[3][1] + 1):
                    for i4 in range(2, spec[4][1] + 1):
                        for i5 in range(0, spec[5][1] + 1):
                            for i6 in range(2, spec[6][1] + 1):
                                for i7 in range(0, spec[7][1] + 1):
                                    for i8 in range(2, spec[8][1] + 1):
                                        for i9 in range(0, spec[9][1] + 1):
                                            for i10 in range(2, spec[10][1] + 1):
                                                for i11 in range(0, spec[11][1] + 1):
                                                    for i12 in range(0, spec[12][1] + 1):
                                                        for i13 in range(0, spec[13][1] + 1):
                                                            all_all = i0+i1+i2+i3+i4+i5+i6+i7+i8+i9+i10+i11+i12+i13
                                                            all_aa = i0+i1+i2+i3
                                                            all_a = i4 + i5+i6+i7
                                                            all_b = i8+i9+i10+i11+i12+i13
                                                            all_aa_major=i1+i3
                                                            all_a_major = i5 + i7
                                                            all_b_major = i9 + i11
                                                            if 12<all_all<=18 and all_aa<=6 and all_aa_major<=1 and all_a<=6 and all_a_major<=1 and all_b<=16 and all_b_major<=2:
                                                                r = csv_read_counts()
                                                                r['All-All-All'] = all_all
                                                                r['All-AA-All'] = all_aa
                                                                r['All-AA-Major'] = all_aa_major
                                                                r['All-A-All'] = all_a
                                                                r['All-A-Major'] = all_a_major
                                                                r['All-B-All'] = all_b
                                                                r['All-B-Major'] = all_b_major
                                                                r[spec[0][0]] = i0
                                                                r[spec[1][0]] = i1
                                                                r[spec[2][0]] = i2
                                                                r[spec[3][0]] = i3
                                                                r[spec[4][0]] = i4
                                                                r[spec[5][0]] = i5
                                                                r[spec[6][0]] = i6
                                                                r[spec[7][0]] = i7
                                                                r[spec[8][0]] = i8
                                                                r[spec[9][0]] = i9
                                                                r[spec[10][0]] = i10
                                                                r[spec[11][0]] = i11
                                                                r[spec[12][0]] = i12
                                                                r[spec[13][0]] = i13
                                                                db.append(r)
    with open(output, 'w') as f:
        json.dump(db, f, indent=4)


def generate_grade_c_1(output='grade_c.json'):
    spec = [
        ('Scratch-AA-Minor', 18),
        ('Scratch-AA-Major', 1),
        ('Nick-AA-Minor', 18),
        ('Nick-AA-Major', 1),
        ('Scratch-A-Minor', 8),
        ('Scratch-A-Major', 1),
        ('Nick-A-Minor', 8),
        ('Nick-A-Major', 1),
        ('Scratch-B-Minor', 18),
        ('Scratch-B-Major', 3),
        ('Nick-B-Minor', 18),
        ('Nick-B-Major', 3),
    ]
    db = []
    for i0 in range(2, spec[0][1]+1):
        for i1 in range(0, spec[1][1] + 1):
            for i2 in range(2, spec[2][1] + 1):
                for i3 in range(0, spec[3][1] + 1):
                    for i4 in range(2, spec[4][1] + 1):
                        for i5 in range(0, spec[5][1] + 1):
                            for i6 in range(2, spec[6][1] + 1):
                                for i7 in range(0, spec[7][1] + 1):
                                    for i8 in range(2, spec[8][1] + 1):
                                        for i9 in range(0, spec[9][1] + 1):
                                            for i10 in range(2, spec[10][1] + 1):
                                                for i11 in range(0, spec[11][1] + 1):
                                                    all_all = i0+i1+i2+i3+i4+i5+i6+i7+i8+i9+i10+i11
                                                    all_aa = i0+i1+i2+i3
                                                    all_a = i4 + i5+i6+i7
                                                    all_b = i8+i9+i10+i11
                                                    all_aa_major=i1+i3
                                                    all_a_major = i5 + i7
                                                    all_b_major = i9 + i11
                                                    if 18<all_all<=26 and all_aa<=8 and all_aa_major<=1 and all_a<=8 and all_a_major<=1 and all_b<=18 and all_b_major<=3:
                                                        r = csv_read_counts()
                                                        r['All-All-All'] = all_all
                                                        r['All-AA-All'] = all_aa
                                                        r['All-AA-Major'] = all_aa_major
                                                        r['All-A-All'] = all_a
                                                        r['All-A-Major'] = all_a_major
                                                        r['All-B-All'] = all_b
                                                        r['All-B-Major'] = all_b_major
                                                        r[spec[0][0]] = i0
                                                        r[spec[1][0]] = i1
                                                        r[spec[2][0]] = i2
                                                        r[spec[3][0]] = i3
                                                        r[spec[4][0]] = i4
                                                        r[spec[5][0]] = i5
                                                        r[spec[6][0]] = i6
                                                        r[spec[7][0]] = i7
                                                        r[spec[8][0]] = i8
                                                        r[spec[9][0]] = i9
                                                        r[spec[10][0]] = i10
                                                        r[spec[11][0]] = i11
                                                        db.append(r)
    with open(output, 'w') as f:
        json.dump(db, f, indent=4)


def generate_grade_c_raw_data(output='grade_c_raw_data.csv'):
    spec = [
        ('Scratch-AA-Minor', range(1, 8 + 1), 'AA', False),
        ('Scratch-AA-Major', range(0, 1 + 1), 'AA', True),
        ('Nick-AA-Minor', range(1, 8 + 1), 'AA', False),
        ('Nick-AA-Major', range(0, 1 + 1), 'AA', True),
        ('Scratch-A-Minor', range(2, 8 + 1), 'A', False),
        ('Scratch-A-Major', range(0, 1 + 1), 'A', True),
        ('Nick-A-Minor', range(2, 8 + 1), 'A', False),
        ('Nick-A-Major', range(0, 1 + 1), 'A', True),
        ('Scratch-B-Minor', range(3, 18 + 1), 'B', False),
        ('Scratch-B-Major', range(0, 3 + 1), 'B', True),
        ('Nick-B-Minor', range(3, 18 + 1), 'B', False),
        ('Nick-B-Major', range(0, 3 + 1), 'B', True),
        ('PinDotGroup-B-10x10', range(0, 4 + 1), 'B', False),
        ('PinDotGroup-B-10x40', range(0, 1 + 1), 'B', False),
    ]
    headers = []
    csv_file = open('tmp/output.csv', 'w')
    wr = csv.writer(csv_file)
    # wr.writerow(['Scratch-AA-Minor','Scratch-AA-Major'])
    for s in spec:
        headers.append(s[0])
    wr.writerow(headers)
    for i0 in spec[0][1]:
        for i1 in spec[1][1]:
            for i2 in spec[2][1]:
                for i3 in spec[3][1]:
                    for i4 in spec[4][1]:
                        for i5 in spec[5][1]:
                            for i6 in spec[6][1]:
                                for i7 in spec[7][1]:
                                    for i8 in spec[8][1]:
                                        for i9 in spec[9][1]:
                                            for i10 in spec[10][1]:
                                                for i11 in spec[11][1]:
                                                    for i12 in spec[12][1]:
                                                        for i13 in spec[13][1]:
                                                            # all_data.append([i0,i1,i2,i3,i4,i5,i6,i7,i8,i9,i10,i11,i12,i13])
                                                            i = [i0, i1, i2, i3, i4, i5, i6, i7, i8, i9, i10, i11, i12,
                                                                 i13]
                                                            if 18 < sum(i) <= 26:
                                                                wr.writerow(i)
    # csv_file = open('tmp/output.csv', 'w')
    # wr = csv.writer(csv_file)
    # wr.writerow(['Scratch-AA-Minor','Scratch-AA-Major'])
    # for i0 in spec[0][1]:
    #     for i1 in spec[1][1]:
    #         # all_data.append([i0,i1])
    #         wr.writerow([i0,i1])
    # with open('tmp/output.csv', 'w') as f:
    #     wr = csv.writer(f)
    #     wr.writerow(['Scratch-AA-Minor','Scratch-AA-Major'])
    #     wr.writerows(all_data)
    csv_file.close()


def gen_csv_train_data(output='ready_1.csv'):
    df = pandas.DataFrame()
    d = pandas.read_csv('ready_270.csv')
    df = df.append(d, ignore_index=True)
    d = pandas.read_csv('grade_ap.csv')
    d['vzw'] = 0
    df = df.append(d, ignore_index=True)
    d = pandas.read_csv('grade_a.csv')
    d['vzw'] = 1
    df = df.append(d, ignore_index=True)
    d = pandas.read_csv('grade_b.csv')
    d['vzw'] = 2
    df = df.append(d.sample(3000), ignore_index=True)
    d = pandas.read_csv('grade_c.csv')
    d['vzw'] = 3
    df = df.append(d.sample(3000), ignore_index=True)
    df.to_csv(output, index=False)


def gen_csv_binary_classify(src='ready_270.csv', output='temp.csv', train=False):
    df = pandas.DataFrame()
    d = pandas.read_csv(src)
    df = df.append(d, ignore_index=True)
    for index, row in df.iterrows():
        if row['vzw'] == 1:
            df.at[index, 'vzw'] = 1
            # df.set_value(index, 'vzw', 1)
        else:
            df.at[index, 'vzw'] = -1
            # df.set_value(index, 'vzw', -1)
    if train:
        d = pandas.read_csv('grade_a.csv')
        d['vzw'] = 1
        df = df.append(d, ignore_index=True)
        d = pandas.read_csv('grade_ap.csv')
        d['vzw'] = -1
        df = df.append(d, ignore_index=True)
        d = pandas.read_csv('grade_b.csv')
        d['vzw'] = -1
        df = df.append(d.sample(1000), ignore_index=True)
        d = pandas.read_csv('grade_c.csv')
        d['vzw'] = -1
        df = df.append(d.sample(1000), ignore_index=True)
    df.to_csv(output, index=False)


# parse_avia_log('117_Testing Set/75_overlapped with 270 models')
# db = prepare_data('iPhone6s Gray')
# prepare_data_score('data270_json')
# cnt = count_defects_by_spec()
# print(json.dumps(cnt))
# prepare_data_by_spec('data270_json', output='ready_270.csv')
# prepare_data_by_spec('data_75_of_117', output='test.csv')
# generate_grade_ap('sample_ap.json')
# generate_grade_a('sample_a.json')
# generate_grade_b('sample_b.json')
# generate_grade_c('sample_c.json')
# generate_grade_b()
# generate_grade_b_raw_data()
# generate_grade_c_raw_data()
# generate_grade_c()
# gen_csv_train_data()
gen_csv_binary_classify(src='ready_270.csv', output='ready_train.csv', train=True)
gen_csv_binary_classify(src='test.csv', output='ready_test.csv')