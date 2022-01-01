"""
House all the logic for box and boxes in a single package
"""

product = lambda x, p=1: product(x[1:], p*x[0]) if x else p

binary_choose = lambda b, v1, v2: tuple(
    [v1[i] if bi == '0' else v2[i] for i, bi in enumerate(bin(b % (2**len(v1)))[2:].zfill(len(v1)))]
)


def recursive_split(boxes, points, splits=None):
    if splits is None:
        splits = Boxes()
    
    if len(points) < 1:
        splits.boxes |= boxes.boxes
    else:
        for b in boxes:
            recursive_split(b.split(points[0]), points[1:], splits)
    
    return Boxes(splits)
            


class Box:
    def __init__(self, m, M):
        mt = []
        Mt = []
        
        for x,y in zip(m,M):
            mt.append(min(x,y))
            Mt.append(max(x,y))
        
        self.m = tuple(mt)
        self.M = tuple(Mt)
    
    def __len__(self):
        return len(self.m)
    
    def __bool__(self):
        return (self.vol() > 0)
    
    def __contains__(self, point):
        return all([self.m[i] <= point[i] <= self.M[i] for i in range(len(self))])
    
    def on_boundary(self, point):
        return (point in self) and (
            any([point[i] == self.m[i] for i in range(len(self))]) 
            or 
            any([point[i] == self.M[i] for i in range(len(self))])
        )
    
    def interior(self, point):
        return all([self.m[i] < point[i] < self.M[i] for i in range(len(self))])
    
    def __eq__(self, other):
        return (self.m == other.m) and (self.M == other.M)
    
    def __lt__(self, other):
        return (self.m in other) and (self.M in other)
    
    def vol(self):
        return product([Mi-mi for mi, Mi in zip(self.m, self.M)])
    
    def intersection(self, other):
        return bool(self&other)
    
    def __and__(self, other):
        mt, Mt = [], []
        for ms, Ms, mo, Mo in zip(self.m, self.M, other.m, other.M):
            if (ms < Mo) and (mo < Ms):
                mt.append(max(ms,mo))
                Mt.append(min(Ms,Mo))
            else:
                return Box((0,0,0),(0,0,0))
        return Box(mt, Mt)
    
    def __repr__(self):
        return f"Box({self.m}, {self.M})"
    
    def __str__(self):
        return repr(self)
    
    def __hash__(self):
        return hash(self.m+self.M+("Box",))
    
    def corners(self):
        return [binary_choose(i, self.m, self.M) for i in range(2**len(self))]
    
    def split(self, point):
        bs = set()
        
        if point in self:
            for i in self.corners():
                b = Box(point, i)
                if b:
                    bs.add(b)
        else:
            bs.add(self)
        
        return Boxes(bs)
    
    def __sub__(self, other):
        i = self & other
        
        if not i:
            return Boxes({self})
        else:
            pts = i.corners()

            bs = recursive_split({self}, pts).boxes

            final = set()
            for b in bs:
                if not b.intersection(other):
                    final.add(b)

            return Boxes(boxes=final)
    
    def __or__(self, other):
        if self < other:
            return {other}
        elif other < self:
            return {self}
        elif self.intersection(other):
            pts = (self & other).corners()
            r = recursive_split({self, other}, pts)
            option1 = {self}
            option2 = {other}
            for b in r:
                if b:
                    if not (b < self):
                        option1.add(b)
                    if not (b < other):
                        option2.add(b)
            if len(option1) < len(option2):
                return option1
            else:
                return option2
        else:
            return {self, other}
                
            

class Boxes:
    def __init__(self, boxes:set=None):
        if boxes is None:
            boxes = set()
        self.boxes = boxes
        
    def __repr__(self):
        if len(self) > 10:
            bs = list(self.boxes)[:30]
            s = 'Boxes{\n'
            for b in bs:
                s += '\t' + str(b) + ',\n'
            return s + '\t...\n}'
        if len(self) > 5:
            bs = list(self.boxes)
            s = 'Boxes{\n'
            for b in bs:
                s += '\t' + str(b) + ',\n'
            return s + '}'
        if len(self) == 0:
            return "Boxes{}"
        else:
            return f"Boxes{self.boxes}"
    
    def __len__(self):
        return len(self.boxes)
    
    def copy(self):
        return Boxes(self.boxes.copy())
    
    def __str__(self):
        if len(self) == 0:
            return "Boxes{}"
        else:
            return f"Boxes{self.boxes}"
    
    def __iter__(self):
        return iter(self.boxes)
    
    def __contains__(self, other):
        if isinstance(other, Box):
            # Would be good to update to include if box - boxes is null set
            return box in self.boxes
        else:
            for box in self.boxes:
                if other in box:
                    return True
            return False
    
    def vol(self):
        s = 0
        for b in self:
            s += b.vol()
        
        return s
    
    def add(self, box):
        
        trouble = set()
        
        for b in self.boxes.copy():
            if box < b:
                return
            elif b < box:
                self.boxes.remove(b)
            elif b.intersection(box):
                trouble.add(b)
                
        finished = False
        bs = {box}
        final = set()
        while not finished:
            finished = True
            for b in bs.copy():
                intersection = False
                for c in trouble:
                    if b.intersection(c):
                        intersection = True
                        finished = False
                        bs.remove(b)
                        bs |= (b - c).boxes
                        break
                if not finished:
                    break
                if not intersection:
                    bs.remove(b)
                    final.add(b)
        self.boxes |= final
    
    def subtract(self, box):
        new = set()
        
        for b in self:
            new |= (b - box).boxes
        
        self.boxes = new
    
    def __or__(self, other):
        new = self.copy()
        
        for b in other:
            new.add(b)
        
        return new
