#!/usr/bin/env python3
"""Extract original embedded Fall 2025 figures as dashboard covers, without redrawing content."""
from pathlib import Path
import hashlib,json,shutil,subprocess,tempfile
from PIL import Image
APP=Path(__file__).resolve().parents[1]
course_path=APP/'data/extracted/fall2025.json'  # Fall 2025 covers; Fall 2026 uses slide images
course=json.loads(course_path.read_text())
# Values identify the PDF page and image number reported by `pdfimages -list`.
selection={
 'introduction':(8,4), 'chemistry':(26,0), 'macromolecules':(31,0),
 'molecular-biology':(6,0), 'cells':(32,0), 'energy':(23,2),
 'homeostasis':(4,0), 'circulation':(4,0), 'digestion':(5,2),
 'respiration-excretion':(8,0), 'nutrition':(3,0), 'diabetes-lipids':(8,1),
}
(APP/'public/covers').mkdir(exist_ok=True)
manifest={}
for module in course['modules']:
 mid=module['id']; original=APP/'public/sources'/module['source']['file']
 pdf=original.with_suffix('.pdf') if original.suffix=='.pptx' else original
 with tempfile.TemporaryDirectory() as tmp:
  prefix=Path(tmp)/'figure'
  if mid in ('cell-division','molecular-biology'):
   page=22 if mid=='cell-division' else 6
   x,y,w,h=(70,260,1650,1015) if mid=='cell-division' else (510,190,780,980)
   # Extract a page region around the original multi-part diagram, using the PDF renderer.
   subprocess.run(['pdftoppm','-f',str(page),'-l',str(page),'-singlefile','-scale-to','1800','-r','150','-x',str(x),'-y',str(y),'-W',str(w),'-H',str(h),'-png',str(pdf),str(prefix)],check=True,capture_output=True)
   image=prefix.with_suffix('.png')
   provenance={'page':page,'extractionMethod':'PDF diagram region rendered with pdftoppm','regionPixels':{'x':x,'y':y,'width':w,'height':h},'renderScaleTo':1800}
  else:
   page,index=selection[mid]
   subprocess.run(['pdfimages','-f',str(page),'-l',str(page),'-png','-j',str(pdf),str(prefix)],check=True,capture_output=True)
   image=next(Path(tmp).glob(f'figure-{index:03d}.*'))
   provenance={'page':page,'embeddedImageIndex':index,'extractionMethod':'Original embedded image extracted by pdfimages'}
   if mid=='cells':
    # Reattach the PDF image's original soft mask to restore source transparency.
    mask=next(Path(tmp).glob(f'figure-{index+1:03d}.*'))
    frame=Image.open(image).convert('RGBA');frame.putalpha(Image.open(mask).convert('L'))
    image=Path(tmp)/'with-original-softmask.png';frame.save(image)
    provenance['softMaskImageIndex']=index+1
  output=APP/'public/covers'/(mid+image.suffix)
  shutil.copyfile(image,output)
  with Image.open(output) as frame: width,height=frame.size
  provenance.update({'file':module['source']['file'],'sourceSha256':module['source']['sha256'],'imageSha256':hashlib.sha256(output.read_bytes()).hexdigest(),'width':width,'height':height})
  module['cover']='/covers/'+output.name
  module['coverSource']=provenance
  manifest[mid]={'cover':module['cover'],'coverSource':provenance}
(APP/'data/covers.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
course_path.write_text(json.dumps(course,ensure_ascii=False,indent=2))
print('Extracted 13 original figure covers.')
