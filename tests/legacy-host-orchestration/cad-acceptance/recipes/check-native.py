"""Independent authored-source checks on the actual synchronized native saves."""
import argparse,hashlib,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--output-dir',type=Path,required=True);p.add_argument('--receipt',type=Path,required=True);a=p.parse_args()
circle=json.loads((a.output_dir/'Agent-circle.jsketcher.json').read_bytes());enclosure=json.loads((a.output_dir/'Agent-enclosure.jsketcher.json').read_bytes())
for d in (circle,enclosure):assert (d['format'],d['version'],d['unit'])==('codi-jsketcher-project',2,'millimeter')
assert len(circle['project']['model']['history'])==1 and circle['project']['model']['history'][0]['type']=='PLANE'
sketches=circle['project']['sketches'];assert len(sketches)==1;objects=sketches[0]['data']['objects'];assert len(objects)==1
entity=objects[0];assert entity['type']=='Circle' and entity['stage']==0 and entity['role'] is None and entity['data']=={'c':{'x':3,'y':4},'r':5}
history=enclosure['project']['model']['history'];assert len(history)==1 and history[0]['type']=='WORKER_ENCLOSURE_V2'
for field,value in {'width':100,'length':70,'height':30,'wall':2,'clearance':.3,'lidThickness':2,'lipDepth':3,'labelWidth':40,'labelLength':20,'labelDepth':1}.items():assert float(history[0]['params'][field])==value
m=enclosure['manufacturing'];assert m['unit']=='millimeter' and len(m['objects'])==2 and len(m['bindings'])==3
assert sorted((x['id'],x['name']) for x in m['materials'])==[('pla','PLA'),('tpu','TPU')]
assert sorted((x['id'],x['color'].lower()) for x in m['appearances'])==[('body-blue','#3366cc'),('label-white','#ffffff'),('lid-blue','#3366cc')]
actual={}
for binding in m['bindings']:
 region=next(r for o in m['objects'] for r in o['regions'] if r['bodyId']==binding['id']);actual[binding['outputRole']]=[region['materialId'],region['appearanceId']]
assert actual=={'BODY':['pla','body-blue'],'LID':['pla','lid-blue'],'LABEL':['tpu','label-white']}
result={'status':'PASS','scope':'Independent synchronized native authored-source inspection, not another solve','circle':{'x':3,'y':4,'r':5,'entities':1,'history':['PLANE']},'enclosure':{'history':['WORKER_ENCLOSURE_V2'],'printObjects':2,'regions':3,'roles':actual},'files':{s:hashlib.sha256((a.output_dir/s).read_bytes()).hexdigest() for s in ['Agent-circle.jsketcher.json','Agent-enclosure.jsketcher.json']}}
a.receipt.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
