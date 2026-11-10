# Contrôle bloquant de Ligne IA (l1) : python3 check_l1.py [--maj-dettes]. Code retour 1 si une erreur n'est pas inscrite dans dettes.json.
import json,re,sys
s=open('app.html',encoding='utf8').read()
a=s.index('/*CONTENT*/\nconst CONTENT = ')+len('/*CONTENT*/\nconst CONTENT = '); b=s.index(';\n/*/CONTENT*/')
C=json.loads(s[a:b].replace('<\\/','</'))
ORDER=[k for k in ['m1','m2','m3','m4','m5','m6','m7','term'] if k in C]
SIG=json.load(open('sigles.json',encoding='utf8'))
err=[]
pos={}; firstdef={}
n=0
for m in ORDER:
    for l in C[m]['lessons']:
        pos[f'{m}.{l["id"]}']=n; n+=1
        for blk in l['blocks']:
            if blk[0]=='def' and len(blk)>4 and blk[4] and not (len(blk)>5 and blk[5]=='rappel'):
                firstdef.setdefault(blk[4],f'{m}.{l["id"]}')
NEED={'processus':{'trajet'},'decision':{'aiguillage','signals','table'},'classement':{'table','signals'},'comparaison':{'table'},'quantites':{'table'},'structure':{'table','trajet'},'aspect':{'carte'}}
txt=lambda blk:json.dumps(blk[1:4] if blk[0]=='def' else blk[1:],ensure_ascii=False)
for m in ORDER:
    for l in C[m]['lessons']:
        lid=f'{m}.{l["id"]}'; types={blk[0] for blk in l['blocks']}
        formes=l.get('formes') or []
        if not formes: err.append((lid,'forme non déclarée'))
        for f in formes:
            f2=f.replace('é','e').replace('è','e')
            if f2=='texte':
                if not l.get('justif_texte'): err.append((lid,'texte sans justification'))
            elif f2 in NEED and not (NEED[f2]&types): err.append((lid,f'forme {f} sans visuel adapté ({"/".join(sorted(NEED[f2]))})'))
        if 'ol' in types: err.append((lid,'liste d\'étapes non convertie en trajet'))
        for i,blk in enumerate(l['blocks']):
            if blk[0]=='p' and len(re.findall(r'\d+[,.]?\d*\s?(%|€|\$|min|h\b|jours?|mois|ans?|Mo|Go|km|dB)',blk[1]))>=3: err.append((lid,f'chiffres en série dans un paragraphe (bloc {i})'))
        defs=[blk for blk in l['blocks'] if blk[0]=='def' and not (len(blk)>5 and blk[5]=='rappel')]
        if len(defs)>7: err.append((lid,f'{len(defs)} notions nouvelles (max 7)'))
        if l.get('min',0)>20: err.append((lid,f'{l["min"]} min (max 20)'))
        flat=' '.join(txt(blk) for blk in l['blocks'] if blk[0] not in('src','code'))
        for sg in SIG:
            mm=re.search(r'(?<![\w-])'+re.escape(sg)+r'(?![\w-])',flat)
            if mm and not re.match(r'\s*\(',flat[mm.end():]) and not re.search(re.escape(sg)+r'\s*\(',flat) and not re.search(r'\(\s*'+re.escape(sg)+r'\s*[)\s]',flat): err.append((lid,f'sigle {sg} non développé'))
    for e in C[m]['exercises']:
        eid=f'{m}.{e["id"]}'; here=max([pos[f'{m}.{l["id"]}'] for l in C[m]['lessons']] or [0])
        if 'notions' not in e: err.append((eid,'notions non déclarées')); continue
        ap=set(e.get('apercus',[]))
        for nt in e['notions']:
            if nt.startswith('def:'):
                fd=firstdef.get(nt)
                if fd is None and nt not in ap: err.append((eid,f'notion {nt} jamais définie'))
                elif fd and pos[fd]>here and not (ap & {k for k,v in firstdef.items() if pos.get(v,99)<=here}): err.append((eid,f'notion {nt} définie après l\'exercice ({fd})'))
        if e.get('type')=='methode' and not e.get('exemple_resolu'): err.append((eid,'exercice de méthode sans exemple résolu'))
keys=sorted({f'{x}|{y}' for x,y in err})
try: dettes=set(json.load(open('dettes.json',encoding='utf8'))['dettes'])
except FileNotFoundError: dettes=set()
if '--maj-dettes' in sys.argv:
    json.dump({'note':'Écarts connus au 10/11/2026, tolérés jusqu\'à correction (option B). Toute nouvelle erreur bloque la publication.','dettes':keys},open('dettes.json','w',encoding='utf8'),ensure_ascii=False,indent=1); print('dettes.json :',len(keys)); sys.exit(0)
new=[k for k in keys if k not in dettes]; fixed=[k for k in dettes if k not in keys]
print(f'{len(keys)} écarts ({len(keys)-len(new)} connus, {len(new)} nouveaux) ; {len(fixed)} dettes résolues')
for k in new: print('  NOUVEAU',k)
sys.exit(1 if new else 0)
