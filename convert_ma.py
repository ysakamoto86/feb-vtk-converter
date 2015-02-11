import sys

import read_xplt as rx
import write_vtk as wv


# INPUT
if int(len(sys.argv) < 3):
    print "Number of arguments wrong!"
    sys.exit(1)

workdir = str(sys.argv[1])
filename = str(sys.argv[2])
num_states = 24


for nstate in range(num_states):

    rx.read_xplt(workdir, filename, nstate, rx.TAGS)

    if workdir[-1] is not '/':
        workdir += '/'

    ndfiles = ['nodes_%d.dat' % nstate]
    elfiles = ['elements_%d_0.dat' % nstate, 'elements_%d_1.dat' % nstate]
    eldfiles = ['stress_%d.dat' % nstate]
    opfile = 'res_%d.vtu' % nstate

    nddfiles = ['displacement_%d.dat' % nstate, 'velocity_%d.dat' % nstate]

    nodes, elems, n_elem_sub = wv.load_data(workdir, ndfiles, elfiles)

    wv.write_vtk(workdir, nodes, elems, n_elem_sub, nddfiles,
                 eldfiles, opfile)
