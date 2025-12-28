import os,json,glob

all_results = glob.glob(os.path.join(os.path.dirname(__file__),'result', 'all_result*'))
all_results = [i for i in all_results if len(fn:=(os.path.basename(i).replace('.json','').replace('all_result','')))>0 and int(fn)>=20251228205659]
all_results.sort(key=lambda x: int(os.path.basename(x).replace('.json','').replace('all_result','')))

all_result = {}
n = [2,5,10,20,30,40,50,60,70,80,90,100]
for i,path in enumerate(all_results):
    with open(path,'r') as f:
        all_result[n[i]] = {}

        data = json.load(f)

        for k,v in data.items():
            all_result[n[i]][k] = [
                {
                    'lap_time' : value[0],
                    'IP' : value[1]/1000000,
                    'UDP' : value[2]/1000000,
                    'success' : value[3]
                    } for value in v
            ]

with open(os.path.join(os.path.dirname(__file__),'result', 'all_result.json'),'w') as f:
    json.dump(all_result,f,indent=4)
