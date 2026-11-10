# Construit la PWA Ligne IA (l1) depuis app.html : index.html, contenu.json, sw.js. Usage : python3 build_pwa.py <dossier_cible> <numero_cache>
import re,sys,json,subprocess
dst,ver=sys.argv[1],sys.argv[2]
body=open('app.html',encoding='utf8').read()
head=re.match(r'(<title>.*?</title>\s*<meta[^>]*>\s*<link[^>]*>\s*<link[^>]*>)',body,re.S).group(1)
rest=body[len(head):]
open(f'{dst}/index.html','w',encoding='utf8').write(f'''<!doctype html>
<html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#15212C">
<link rel="manifest" href="manifest.json">
<link rel="icon" href="icon-192.png">
<link rel="apple-touch-icon" href="icon-192.png">
{head}
</head><body>
{rest}
<script>if("serviceWorker" in navigator)navigator.serviceWorker.register("sw.js").catch(()=>{{}});</script>
</body></html>''')
js=re.findall(r'<script>(.*?)</script>',body,re.S)[0]
code=js[:js.index('/* ===================== ÉTAT')]
import tempfile,os
tf=tempfile.NamedTemporaryFile('w',suffix='.js',delete=False,encoding='utf8'); tf.write(code+';process.stdout.write(JSON.stringify({app:"l1",schemaVersion:1,modules:MODULES}))'); tf.close()
out=subprocess.run(['node',tf.name],capture_output=True,text=True,check=True).stdout; os.unlink(tf.name)
open(f'{dst}/contenu.json','w',encoding='utf8').write(out)
open(f'{dst}/sw.js','w').write('const PREFIXE="ligne-ia-v",C=PREFIXE+"'+ver+'";const CORE=["./","index.html","manifest.json","contenu.json","icon-192.png","icon-512.png"];\n'
 'self.addEventListener("install",e=>{e.waitUntil(caches.open(C).then(c=>c.addAll(CORE)));self.skipWaiting();});\n'
 'self.addEventListener("activate",e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k.startsWith(PREFIXE)&&k!==C).map(k=>caches.delete(k)))));self.clients.claim();});\n'
 'self.addEventListener("fetch",e=>{if(e.request.method!=="GET")return;\n e.respondWith(caches.match(e.request).then(hit=>{const net=fetch(e.request).then(r=>{if(r&&(r.ok||r.type==="opaque")){const cp=r.clone();caches.open(C).then(c=>c.put(e.request,cp));}return r;}).catch(()=>hit);return hit||net;}));});\n')
print("ok",dst,"cache",ver,"contenu.json",len(out),"octets")
