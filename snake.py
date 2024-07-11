from collections import deque as d; import tkinter as tk; from random import randint as ri
G, TS, BX, BY = 100, 20, 40, 40
r = tk.Tk()
cvs = tk.Canvas(r, width=BX*TS, height=BY*TS)
cvs.pack()
db = lambda x, y, c='black': cvs.create_rectangle(x*TS, y*TS, (x+1)*TS, (y+1)*TS, fill=c)
pa = lambda: next((x, y) for x, y in iter(lambda: (ri(0, BX-1), ri(0, BY-1)), None) if (x, y) not in s)
s, sids = d([(0, 0), (0, 1), (0, 2)]), d([db(0, 0), db(0, 1), db(0, 2)])
a = pa(); aid = db(a[0], a[1], 'red')
ds, dinvs, cd, ed = ((1, 0), (-1, 0), (0, -1), (0, 1)), (1, 0, 3, 2), 0, False
ud = lambda dir: globals().update(cd=dir) if dinvs[cd] != dir and ed else None
def us():
    global ed, a, aid
    hx, hy = s[-1]
    h = (hx+ds[cd][0], hy+ds[cd][1])
    if h in s or h[0] < 0 or h[0] >= BX or h[1] < 0 or h[1] >= BY: print('Game Over'); r.quit()
    else:
        s.append(h); sids.append(db(*h))
        if h == a: a = pa(); cvs.delete(aid); aid = db(a[0], a[1], 'red')
        else: cvs.delete(sids.popleft()); s.popleft()
        ed = True
ru = lambda: (us(), r.after(G, ru))
r.bind('<Left>', lambda e: ud(1)); r.bind('<Right>', lambda e: ud(0)); r.bind('<Up>', lambda e: ud(2)); r.bind('<Down>', lambda e: ud(3))
r.after(G, ru); r.mainloop()