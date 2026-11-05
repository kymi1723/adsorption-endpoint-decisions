"""Original function bodies extracted without numerical changes; see provenance/source_manifest.json."""
from collections import defaultdict
import numpy as np

def hierarchy_weights(rows,levels):
    w=np.zeros(len(rows))
    def split(indices,depth,mass):
        if depth==len(levels):w[indices]=mass/len(indices);return
        groups=defaultdict(list)
        for i in indices:groups[rows[i][levels[depth]]].append(i)
        for group in groups.values():split(group,depth+1,mass/len(groups))
    split(list(range(len(rows))),0,1.)
    assert abs(w.sum()-1)<1e-12 and np.all(w>0)
    return w
