import os
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from flask import Flask, request, render_template
app = Flask(__name__)

import BZ_avia
import getGrade_270
import getGrade

#GRRmodel = open('GRRmodel', 'rb') 

@app.route('/')
def hello_world():
    # return 'post data to http://10.1.1.154:5000/sga'
    return render_template('home.html')


@app.route('/test270', methods=['POST'])
def test_270():
    x = request.stream.read()
    ret = {'error': 0, 'message': 'success'}
    content_type = request.headers['Content-Type']
    if content_type=='application/json':
        data = json.loads(x)
        dt = datetime.now().strftime('%Y%m%d-%H%M%S')
        imei = data['imei']
        fn = os.path.join('/home/qa/incoming/defect_json', '{}-{}.json'.format(imei,dt))
        with open(fn, 'w') as f:
            json.dump(data, f, indent=4)
        g, posibi = getGrade_270.runTesting(fn, 'GRRmodel')
        ret['grade']=g
        ret['score']=posibi.tolist()
    else:
        ret['error']=1
        ret['message']='Error: content_type: {} not accept, please use application/json'.format(content_type)
    return json.dumps(ret)


@app.route('/grr', methods=['POST'])
def secondary_gradeing():        
    # print(request.headers)
    data = request.stream.read()
    ret = {'error': 0, 'message': 'success'}
    content_type = request.headers['Content-Type']
    if content_type=='text/xml' or content_type=='application/xml':
        xml=ET.fromstring(data.decode())
        subfolder = datetime.now().strftime('%Y%m%d')
        try:
            os.mkdir(os.path.join('/home/qa/incoming/defect_xml/', subfolder))
            os.mkdir(os.path.join('/home/qa/incoming/defect_json/', subfolder))
        except:
            pass
        dt = datetime.now().strftime('%Y%m%d-%H%M%S')
        imei = xml.find('imei')
        if imei is not None:
            imei = imei.text
        else:
            imei = 'imei'
        if xml.tag == 'defect_record':
            fn = os.path.join('/home/qa/incoming/defect_xml/{}'.format(subfolder), '{}-{}.xml'.format(imei,dt))
            with open(fn, 'w') as f:
                f.write(ET.tostring(xml).decode())
            data = BZ_avia.defect_xml_to_json(fn)
            fn = os.path.join('/home/qa/incoming/defect_json/{}'.format(subfolder), '{}-{}.json'.format(imei,dt))
            with open(fn, 'w') as f:
                json.dump(data, f, indent=4)
            # predict
            # GRRmodel.seek(0,0)
            g, posibi = getGrade.runTesting_v2(fn)
            ret['grade']=g
            try:
                ret['score']=posibi.tolist()
            except:
                pass
        else:
            ret['error']=2
            ret['message']='Error: xml root is {} not accept, please use try with defect xml'.format(xml.tag)
    else:
        ret['error']=1
        ret['message']='Error: content_type: {} not accept, please use text/xml or application/xml'.format(content_type)
    return json.dumps(ret)

if __name__ == '__main__':
    #GRRmodel = open('GRRmodel', 'rb')    
    app.run(host='0.0.0.0')