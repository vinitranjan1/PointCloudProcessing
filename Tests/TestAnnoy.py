from annoy import AnnoyIndex
import random

f = 40
t = AnnoyIndex(f, metric='euclidean')  # Length of item vector that will be indexed
for i in range(1000):
    v = [random.gauss(0, 1) for z in range(f)]
    t.add_item(i, v)

t.build(10) # 10 trees
t.save('test.tree')

# ...

u = AnnoyIndex(f, metric='euclidean')
u.load('test.tree') # super fast, will just mmap the file
print(u.get_nns_by_item(0, 1000)) # will find the 1000 nearest neighbors