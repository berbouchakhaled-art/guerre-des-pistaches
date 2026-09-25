import math, json
from PIL import Image
import numpy as np

CW, CH = 48, 64
OUT = (28,18,24)
P = {
 # hair
 'O':OUT,'d':(26,18,17),'h':(50,37,32),'H':(78,58,46),'L':(114,84,62),
 # skin
 's':(248,200,166),'S':(224,160,124),'k':(186,120,90),'K':(142,86,64),
 # face
 'w':(242,238,230),'e':(92,52,30),'b':(44,28,24),'m':(222,128,128),'M':(172,84,90),'r':(236,150,134),
 # shirt
 'A':(255,253,248),'B':(232,228,222),'C':(190,186,194),'D':(140,134,152),
 # jeans
 'j':(104,146,204),'J':(70,106,166),'q':(46,70,120),'Q':(30,44,82),
 # shoes
 'R':(210,64,56),'X':(146,38,44),'Y':(246,242,234),'y':(178,170,172),
 # blaster
 'G':(168,212,88),'g':(116,170,62),'E':(72,118,44),'T':(236,214,160),'t':(192,160,108),'n':(128,200,80),'Z':(70,64,80),'z':(40,36,48),
 'F':(255,240,140),'f':(255,190,70),
}
SEL = {'skin':(150,90,66),'shirt':(150,144,160),'jeans':(34,50,92),'shoe':(110,30,36),'hair':OUT,'gun':(44,74,30)}

def grid(txt):
    rows=[r for r in txt.strip('\n').split('\n')]
    return rows

HEAD = grid(open('head_v4.txt').read())
def head_variant(kind):
    g=[list(r.ljust(23,'.')) for r in HEAD]
    def put(x,y,c): g[y][x]=c
    if kind=='blink':
        for x in (10,11,12): put(x,12,'S'); put(x,13,'O')
        for x in (16,17,18): put(x,12,'S'); put(x,13,'O')
        put(10,13,'k');put(16,13,'S')
    if kind=='hurt':
        # squeezed eyes > <
        for x,y,c in [(10,12,'O'),(11,12,'S'),(12,12,'S'),(11,13,'O'),(12,13,'O'),(10,13,'S'),
                      (16,12,'S'),(17,12,'S'),(18,12,'O'),(16,13,'O'),(17,13,'O'),(18,13,'S')]:
            put(x,y,c)
        # open mouth
        for x,y,c in [(14,17,'O'),(15,17,'O'),(16,17,'O'),(14,18,'O'),(15,18,'m'),(16,18,'S')]:
            put(x,y,c)
    return [''.join(r) for r in g]

TORSO = grid('''
.....KkkK....
.....KkkkK...
...BBCKkkCBA.
..BBBBCCCBAAB
.CBBBBBBBBAAB
.CBBBBBBBBBAB
.CCBBBBBBBBAB
.CCBBBBBBBBAB
.CCBBBBBBBBBB
.CCBBBBBBBBBB
.CCBBBBBBBBBB
CCCBBBBBBBBBB
CCDCCBBBBBBBC
''')
PELVIS = grid('''
.qJJJJJJJjJ.
qqJJJJJJJJjJ
qqJJJJJJJJJJ
''')
SHOE = grid('''
.RRR....
RRRRRR..
XRRRRRRR
yYYYYYYY
''')
BLASTER = grid('''
....tTTTt....
...tTnGnTt...
.EEEgGGGGgZz.
EgGGGGGGGgZYz
EggGGGGGGgZZz
.EEEgEEEEEEz.
..EzzE.......
..Ezz........
''')
FLASH = grid('''
.F.
FfF
.F.
''')

class Layer:
    def __init__(s): s.px={}  # (x,y)->(color, part)
def blit(layer, rows, ox, oy, part, flip=False):
    for y,r in enumerate(rows):
        for x,c in enumerate(r):
            if c=='.' or c==' ': continue
            xx = ox + ((len(r)-1-x) if flip else x)
            layer.append(((xx,oy+y),P[c],part,c))

def capsule(p0,p1,w):
    (x0,y0),(x1,y1)=p0,p1
    r=w/2.0
    pts=[]
    minx=int(math.floor(min(x0,x1)-r-1)); maxx=int(math.ceil(max(x0,x1)+r+1))
    miny=int(math.floor(min(y0,y1)-r-1)); maxy=int(math.ceil(max(y0,y1)+r+1))
    dx,dy=x1-x0,y1-y0; L2=dx*dx+dy*dy or 1e-9
    L=math.sqrt(L2)
    nx,ny=dy/L,-dx/L   # "front" normal for downward limbs
    for yy in range(miny,maxy+1):
        for xx in range(minx,maxx+1):
            cx,cy=xx+0.5,yy+0.5
            t=max(0,min(1,((cx-x0)*dx+(cy-y0)*dy)/L2))
            px,py=x0+t*dx,y0+t*dy
            if (cx-px)**2+(cy-py)**2 <= r*r:
                sd=((cx-x0)*nx+(cy-y0)*ny)/r
                pts.append((xx,yy,sd,t))
    return pts

def limb_pts(pts, cols, part, out, key):
    light,base,shade=cols
    for xx,yy,sd,t in pts:
        c = light if sd>0.5 else (shade if sd<-0.3 else base)
        out.append(((xx,yy),P[c],part,c))

def polar(p,ang,l):
    a=math.radians(ang)
    return (p[0]+math.sin(a)*l, p[1]+math.cos(a)*l)

def leg(out, hip, thigh, bend, part, back=False):
    knee=polar(hip,thigh,6.5)
    ankle=polar(knee,thigh-bend,6.5)
    cols=('J','q','Q') if back else ('j','J','q')
    limb_pts(capsule(hip,knee,4.6),cols,part,out,'jeans')
    limb_pts(capsule(knee,ankle,4.2),cols,part,out,'jeans')
    ax,ay=int(round(ankle[0])),int(round(ankle[1]))
    shoe=SHOE
    if back:
        shoe=[r.replace('R','X') for r in SHOE]
    blit(out, shoe, ax-2, ay-1, part+'_shoe')
    return ankle

def arm(out, sh, up, bend, part, back=False, hand=True):
    elbow=polar(sh,up,5.0)
    wrist=polar(elbow,up+bend,4.5)
    skin=('k','k','K') if back else ('S','S','k')
    shirt=('C','C','D') if back else ('A','B','C')
    limb_pts(capsule(elbow,wrist,3.0),skin,part,out,'skin')
    # upper arm skin then sleeve over first part
    limb_pts(capsule(sh,elbow,3.2),skin,part,out,'skin')
    slv_end=polar(sh,up,3.0)
    limb_pts(capsule((sh[0],sh[1]-0.5),slv_end,5.0),shirt,part,out,'shirt')
    if hand:
        hx,hy=polar(wrist,up+bend,1.2)
        for xx,yy,sd,t in capsule((hx,hy),(hx,hy),3.3):
            c = skin[2] if sd<-0.5 else skin[0]
            out.append(((xx,yy),P[c],part,c))
    return wrist

def render(pose):
    """pose: dict with keys"""
    parts=[]  # list of lists of pixel records in draw order
    bx=pose.get('bx',0); by=pose.get('by',0)
    ly=pose.get('lean',0)
    FL=pose['fleg']; BL=pose['bleg']
    # compute leg extents to auto-ground
    def ext(th,bd):
        k=polar((0,0),th,6.5); a=polar(k,th-bd,6.5); return a[1]
    hipY = pose.get('hipY')
    if hipY is None:
        hipY = 59 - max(ext(*FL),ext(*BL))
    hipY = int(round(hipY)) + by
    br=pose.get('br',0)
    tx = 17+bx; ty = hipY-13+br   # torso top
    hx = tx-6+ly; hy = ty-20
    L_bleg=[]; leg(L_bleg,(tx+6.0+0,hipY+1.0),BL[0],BL[1],'bleg',back=True)
    L_barm=[]; arm(L_barm,(tx+5.5,ty+4.0),pose['barm'][0],pose['barm'][1],'barm',back=True)
    L_torso=[]; blit(L_torso,PELVIS,tx+1,hipY-1,'pelvis'); blit(L_torso,TORSO,tx,ty,'torso')
    L_fleg=[]; leg(L_fleg,(tx+7.5,hipY+1.0),FL[0],FL[1],'fleg')
    L_head=[]; blit(L_head,head_variant(pose.get('face','normal')),hx,hy,'head')
    sw=pose.get('sway',0)
    if sw:
        L_head=[((x+sw,y),c,p,ch) if (y-hy>=15 and x-hx<=9) else ((x,y),c,p,ch) for ((x,y),c,p,ch) in L_head]
        # fill gaps created at the seam with hair
        have={pos for pos,_,_,_ in L_head}
        for ((x,y),c,p,ch) in list(L_head):
            if y-hy>=15 and x-hx==9+sw and (x+1,y) not in have: pass
    L_farm=[]
    wrist=arm(L_farm,(tx+pose.get('fsx',8.5)+ly*0.5,ty+4.0),pose['farm'][0],pose['farm'][1],'farm')
    L_gun=[]
    if pose.get('gun'):
        gx,gy=int(round(wrist[0]))-3, int(round(wrist[1]))-4
        blit(L_gun,BLASTER,gx,gy,'gun')
        if pose.get('flash'):
            blit(L_gun,FLASH,gx+13,gy+2,'flash')
        # re-draw the fist over grip
        hxx,hyy=int(round(wrist[0])),int(round(wrist[1]))
        for (dx,dy,c) in [(-1,0,'s'),(0,0,'s'),(1,0,'S'),(-1,1,'S'),(0,1,'S'),(1,1,'k')]:
            L_gun.append(((hxx+dx,hyy+dy),P[c],'fist',c))
    order=[L_bleg,L_barm,L_torso,L_fleg,L_head,L_farm,L_gun]
    if pose.get('arm_behind_gun'):
        order=[L_bleg,L_barm,L_torso,L_fleg,L_head,L_gun,L_farm]
    img={}  # (x,y)->(color,part,char)
    GRP={'bleg':'jeans','fleg':'jeans','barm':'skin','farm':'skin','torso':'shirt','pelvis':'jeans','gun':'gun'}
    for layer in order:
        mask={}
        for (pos,col,part,ch) in layer: mask[pos]=(col,part,ch)
        grps=set(p.split('_')[0] for _,(c,p,ch) in mask.items())
        # ring outline drawn onto underlying pixels of *other* groups
        ring={}
        for pos,(col,part,ch) in mask.items():
            grp=part.split('_')[0]
            if grp in ('head','flash','fist'): continue
            x,y=pos
            for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
                q=(x+dx,y+dy)
                if q in mask or q not in img: continue
                under=img[q][1].split('_')[0]
                if under==grp: continue
                if img[q][2] in 'O': continue
                sel=GRP.get(grp,'skin')
                if part.endswith('shoe'): sel='shoe'
                elif ch in 'ABCD': sel='shirt'
                ring[q]=(SEL[sel],img[q][1],'#')
        img.update(ring)
        for pos,v in mask.items(): img[pos]=v
    # global outline
    arr=np.zeros((CH,CW,4),np.uint8)
    for (x,y),(col,part,ch) in img.items():
        if 0<=x<CW and 0<=y<CH: arr[y,x,:3]=col; arr[y,x,3]=255
    a=arr[:,:,3]>0
    notout=a & ~((arr[:,:,0]==OUT[0])&(arr[:,:,1]==OUT[1])&(arr[:,:,2]==OUT[2]))
    nb=np.zeros_like(a)
    nb[1:,:]|=notout[:-1,:]; nb[:-1,:]|=notout[1:,:]; nb[:,1:]|=notout[:,:-1]; nb[:,:-1]|=notout[:,1:]
    ol = nb & ~a
    arr[ol,:3]=OUT; arr[ol,3]=255
    # remove orphan outline pixels (outline with no neighbors besides outline? keep)
    return Image.fromarray(arr,'RGBA')

# ---- poses ----
FR = []
def add(name, **pose): FR.append((name,pose))
# idle: breathing
add('idle_0', fleg=(8,4),  bleg=(-6,4), farm=(4,4), fsx=9.5, barm=(-6,-6))
add('idle_1', fleg=(8,4),  bleg=(-6,4), farm=(4,2), fsx=9.5, barm=(-6,-6), br=1)
add('idle_2', fleg=(8,4),  bleg=(-6,4), farm=(3,2), fsx=9.5, barm=(-7,-8), br=1)
add('idle_3', fleg=(8,4),  bleg=(-6,4), farm=(4,2), fsx=9.5, barm=(-6,-6))
cyc=[(42,12),(18,22),(-12,10),(-38,40),(-12,95),(28,70)]
for i in range(6):
    f=cyc[i]; b=cyc[(i+3)%6]
    add(f'run_{i}', fleg=f, bleg=b, farm=(-f[0]*1.0, 80), barm=(-b[0]*1.0, 80), lean=1, sway=(0 if i in (1,4) else -1))
add('jump', fleg=(60,95), bleg=(-15,25), farm=(80,40), barm=(-60,-20))
add('fall', fleg=(15,25), bleg=(-20,35), farm=(105,30), barm=(-120,10))
add('shoot_0', fleg=(14,8), bleg=(-10,6), farm=(90,0), barm=(60,40), gun=True)
add('shoot_1', fleg=(14,8), bleg=(-10,6), farm=(88,0), barm=(60,40), gun=True, flash=True, bx=-1)
add('blink', fleg=(8,4),  bleg=(-6,4), farm=(4,4), fsx=9.5, barm=(-6,-6), face='blink')
add('hurt', fleg=(35,30), bleg=(-10,10), farm=(60,50), barm=(-60,20), face='hurt', lean=-2, bx=-1)

if __name__=='__main__':
    frames=[(n,render(p)) for n,p in FR]
    cols=6; rows=math.ceil(len(frames)/cols)
    sheet=Image.new('RGBA',(cols*CW,rows*CH),(0,0,0,0))
    meta={'image':'sousou_sprite.png','cell':{'w':CW,'h':CH},'anchor':{'x':22,'y':64,'note':'Facing right. Feet rest on the bottom edge of the cell (lowest opaque row y=63 incl. outline). Body centre x~22. Air frames (jump/fall) are also bottom-aligned; move them via game physics.'},'frames':{},'animations':{}}
    for i,(n,im) in enumerate(frames):
        x=(i%cols)*CW; y=(i//cols)*CH
        sheet.alpha_composite(im,(x,y))
        meta['frames'][n]={'x':x,'y':y,'w':CW,'h':CH}
    anims={}
    for n,_ in frames:
        k=n.rsplit('_',1)[0] if n[-1].isdigit() else n
        anims.setdefault(k,[]).append(n)
    fps={'blink':1,'idle':4,'run':12,'jump':1,'fall':1,'shoot':12,'hurt':1}
    for k,v in anims.items(): meta['animations'][k]={'frames':v,'fps':fps[k],'loop':k in('idle','run')}
    sheet.save('sousou_sprite.png')
    json.dump(meta,open('sousou_sprite.json','w'),indent=2)
    bg=Image.new('RGBA',sheet.size,(0,0,0,0))
    # preview: checker bg + grid
    pv=Image.new('RGBA',sheet.size,(150,190,215,255))
    for i in range(len(frames)):
        x=(i%cols)*CW; y=(i//cols)*CH
        if (i%cols+i//cols)%2: pv.paste((140,180,205,255),(x,y,x+CW,y+CH))
    pv.alpha_composite(sheet)
    pv.resize((sheet.width*6,sheet.height*6),Image.NEAREST).save('sousou_sprite_preview_6x.png')
    print('ok',len(frames),sheet.size)
