import xml.etree.ElementTree as ET
import json
import os
import re
from pathlib import Path

def defect_xml_to_json(filename = 'BZ_defect.xml'):
    xml = ET.parse(filename)
    data = {}
    defects = []
    for c in list(xml.getroot()):
        if c.tag != 'station':
            data[c.tag] = c.text
        else:
            pass
    # for each defect
    for sta in xml.getroot().findall('station'):
        for alg in list(sta):
            for suf in list(alg):
                defect_data = {'station': sta.get('name'), 'alg': alg.get('name'), 'surface': suf.get('name')}
                x = suf.find('ROIregion')
                temp = x.text.split(',')
                defect_data['ROIregion.x'] = temp[0]
                defect_data['ROIregion.y'] = temp[1]
                defect_data['ROIregion.width'] = temp[2]
                defect_data['ROIregion.height'] = temp[3]
                x = suf.find('defect/item')
                for c in list(x):
                    if c.tag != 'location':
                        defect_data[c.tag] = c.text
                    else:
                        loc = 0
                        for pt in list(c):
                            temp = pt.text.split(',')
                            defect_data['location_{}.x'.format(loc)] = temp[0]
                            defect_data['location_{}.y'.format(loc)] = temp[1]
                            loc += 1
                defects.append(defect_data)
    data['defects'] = defects
    return data

def find_vzw_data_by_imei(vzw, imei):
    ret = None
    for data in vzw:
        l=len(imei)
        x=str(data['IMEI'])[-l:]
        if x == imei:
            ret=data
            break
    return ret


def find_vzw_data_by_xml(vzw, filename):
    ret = None
    xml = ET.parse(filename)
    imeiNode = xml.getroot().find('imei')
    if imeiNode is not None:
        imei = imeiNode.text
        for data in vzw:
            l=len(imei)
            x=str(data['IMEI'])[-l:]
            if x == imei:
                ret=data
                break
    return ret

def get_FD_grade(path):
    ret = ''
    files = os.listdir(path)
    for fn in files:
        if Path(fn).suffix.lower() == '.json':
            with open(os.path.join(path, fn)) as f:
                data = json.load(f)
                ret = data['Grade']
                break
    return ret

# json_str = defect_xml_to_json('D:\\Projects\\repo\\aviapy\\data_117\\source\\Iphone X silver\\143210-iPhone-iPhoneX-Silver-0.xml')
# print(json_str)
# # save to file
# with open('test.json', 'w') as f:
#     f.write(json_str)

def parse_data_117():
    data117_dir='data_117'
    input_dir='defect_117'
    output_dir='data117_json'

    with open('vzw_grr_117.json') as f:
        vzw_data=json.load(f)

    for root, dirs, files in os.walk(os.path.join(data117_dir,input_dir)):
        for fn in files:
            print(os.path.join(root,fn))
            if fn == 'defect.xml':
                record = find_vzw_data_by_xml(vzw_data, os.path.join(root,fn))
                if record is not None:
                    fd = get_FD_grade(root)
                    json_data = defect_xml_to_json(os.path.join(root,fn))
                    json_data['imei']=str(record['IMEI'])
                    json_data['vzw']=record['VZW Grade']
                    json_data['chris']=record['Chris\'s Grade']
                    json_data['fd']=fd
                    with open(os.path.join(data117_dir,output_dir,'{}.json'.format(str(record['IMEI']))), 'w') as f:
                        json.dump(json_data, f, indent=4)

def parse_data_150():
    data150_dir="data_150"
    input_dir="defect_150"
    output_dir="data150_json"
    with open('vzw_grr_150.json') as f:
        vzw_data=json.load(f)
    for root, dirs, files in os.walk(os.path.join(data150_dir,input_dir)):
        for fn in files:
            print(os.path.join(root,fn))
            if fn == 'defect.xml':
                record = find_vzw_data_by_xml(vzw_data, os.path.join(root,fn))
                if record is not None:
                    fd = get_FD_grade(root)
                    json_data = defect_xml_to_json(os.path.join(root,fn))
                    json_data['imei']=str(record['IMEI'])
                    json_data['vzw']=record['VZW Grade']
                    json_data['chris']=record['Chris\'s Grade']
                    json_data['fd']=fd
                    with open(os.path.join(data150_dir,output_dir,'{}.json'.format(str(json_data['imei']))), 'w') as f:
                        json.dump(json_data, f, indent=4)


if __name__ == '__main__':
    parse_data_117()
    parse_data_150()