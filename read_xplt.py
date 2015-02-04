import struct
from numpy import *
import sys
import pdb


'''
// file tags
enum { 
        PLT_ROOT				  = 0x01000000,
        PLT_HEADER				  = 0x01010000,
                PLT_HDR_VERSION			  = 0x01010001,
                PLT_HDR_NODES			  = 0x01010002,
                PLT_HDR_MAX_FACET_NODES		  = 0x01010003,
                PLT_HDR_COMPRESSION		  = 0x01010004,	// added in version 0x03
        PLT_DICTIONARY				  = 0x01020000,
                PLT_DIC_ITEM			  = 0x01020001,
                PLT_DIC_ITEM_TYPE		  = 0x01020002,
                PLT_DIC_ITEM_FMT		  = 0x01020003,
                PLT_DIC_ITEM_NAME		  = 0x01020004,
                PLT_DIC_GLOBAL			  = 0x01021000,
                PLT_DIC_MATERIAL		  = 0x01022000,
                PLT_DIC_NODAL			  = 0x01023000,
                PLT_DIC_DOMAIN			  = 0x01024000,
                PLT_DIC_SURFACE			  = 0x01025000,
        PLT_MATERIALS				  = 0x01030000,
                PLT_MATERIAL			  = 0x01030001,
                PLT_MAT_ID			  = 0x01030002,
                PLT_MAT_NAME			  = 0x01030003,
        PLT_GEOMETRY				  = 0x01040000,
                PLT_NODE_SECTION		  = 0x01041000,
                        PLT_NODE_COORDS		  = 0x01041001,
                PLT_DOMAIN_SECTION		  = 0x01042000,
                        PLT_DOMAIN		  = 0x01042100,
                        PLT_DOMAIN_HDR		  = 0x01042101,
                                PLT_DOM_ELEM_TYPE = 0x01042102,
                                PLT_DOM_MAT_ID	  = 0x01042103,
                                PLT_DOM_ELEMS	  = 0x01032104,
                                PLT_DOM_NAME	  = 0x01032105,	// added in version 0x03
                        PLT_DOM_ELEM_LIST	  = 0x01042200,
                                PLT_ELEMENT	  = 0x01042201,
                PLT_SURFACE_SECTION		  = 0x01043000,
                        PLT_SURFACE		  = 0x01043100,
                        PLT_SURFACE_HDR		  = 0x01043101,
                                PLT_SURFACE_ID	  = 0x01043102,
                                PLT_SURFACE_FACES = 0x01043103,
                                PLT_SURFACE_NAME  = 0x01043104,	// added in version 0x03
                        PLT_FACE_LIST		  = 0x01043200,
                                PLT_FACE	  = 0x01043201, 
                PLT_NODESET_SECTION		  = 0x01044000,	// added in version 0x03
                        PLT_NODESET		  = 0x01044100,	// added in version 0x03
                        PLT_NODESET_HDR		  = 0x01044101,	// added in version 0x03
                                PLT_NODESET_ID	  = 0x01044102,	// added in version 0x03
                                PLT_NODESET_NAME  = 0x01044103,	// added in version 0x03
                                PLT_NODESET_SIZE  = 0x01044104,	// added in version 0x03
                        PLT_NODESET_LIST	  = 0x01044200,	// added in version 0x03
        PLT_STATE				  = 0x02000000,
                PLT_STATE_HEADER		  = 0x02010000,
                        PLT_STATE_HDR_ID	  = 0x02010001,
                        PLT_STATE_HDR_TIME	  = 0x02010002,
                PLT_STATE_DATA			  = 0x02020000,
                        PLT_STATE_VARIABLE	  = 0x02020001,
                        PLT_STATE_VAR_ID	  = 0x02020002,
                        PLT_STATE_VAR_DATA	  = 0x02020003,
                        PLT_GLOBAL_DATA		  = 0x02020100,
                        PLT_MATERIAL_DATA	  = 0x02020200,
                        PLT_NODE_DATA		  = 0x02020300,
                        PLT_ELEMENT_DATA	  = 0x02020400,
                        PLT_FACE_DATA		  = 0x02020500
};
'''

TAGS = {
    'FEBIO': '0x00464542',
    'VERSION': '0x0003',
    'ROOT': '0x01000000',
    'HEADER': '0x01010000',
    'HDR_VERSION': '0x01010001',
    'HDR_NODES': '0x01010002',
    'HDR_MAX_FACET_NODES': '0x01010003',
    'HDR_COMPRESSION': '0x01010004',  #addedinversion0x03
    'DICTIONARY': '0x01020000',
    'DIC_ITEM': '0x01020001',
    'DIC_ITEM_TYPE': '0x01020002',
    'DIC_ITEM_FMT': '0x01020003',
    'DIC_ITEM_NAME': '0x01020004',
    'DIC_GLOBAL': '0x01021000',
    'DIC_MATERIAL': '0x01022000',
    'DIC_NODAL': '0x01023000',
    'DIC_DOMAIN': '0x01024000',
    'DIC_SURFACE': '0x01025000',
    'MATERIALS': '0x01030000',
    'MATERIAL': '0x01030001',
    'MAT_ID': '0x01030002',
    'MAT_NAME': '0x01030003',
    'GEOMETRY': '0x01040000',
    'NODE_SECTION': '0x01041000',
    'NODE_COORDS': '0x01041001',
    'DOMAIN_SECTION': '0x01042000',
    'DOMAIN': '0x01042100',
    'DOMAIN_HDR': '0x01042101',
    'DOM_ELEM_TYPE': '0x01042102',
    'DOM_MAT_ID': '0x01042103',
    'DOM_ELEMS': '0x01032104',
    'DOM_NAME': '0x01032105',  #addedinversion0x03
    'DOM_ELEM_LIST': '0x01042200',
    'ELEMENT': '0x01042201',
    'SURFACE_SECTION': '0x01043000',
    'SURFACE': '0x01043100',
    'SURFACE_HDR': '0x01043101',
    'SURFACE_ID': '0x01043102',
    'SURFACE_FACES': '0x01043103',
    'SURFACE_NAME': '0x01043104',  #addedinversion0x03
    'FACE_LIST': '0x01043200',
    'FACE': '0x01043201',
    'NODESET_SECTION': '0x01044000',  #addedinversion0x03
    'NODESET': '0x01044100',  #addedinversion0x03
    'NODESET_HDR': '0x01044101',  #addedinversion0x03
    'NODESET_ID': '0x01044102',  #addedinversion0x03
    'NODESET_NAME': '0x01044103',  #addedinversion0x03
    'NODESET_SIZE': '0x01044104',  #addedinversion0x03
    'NODESET_LIST': '0x01044200',  #addedinversion0x03
    'STATE': '0x02000000',
    'STATE_HEADER': '0x02010000',
    'STATE_HDR_ID': '0x02010001',
    'STATE_HDR_TIME': '0x02010002',
    'STATE_DATA': '0x02020000',
    'STATE_VARIABLE': '0x02020001',
    'STATE_VAR_ID': '0x02020002',
    'STATE_VAR_DATA': '0x02020003',
    'GLOBAL_DATA': '0x02020100',
    'MATERIAL_DATA': '0x02020200',
    'NODE_DATA': '0x02020300',
    'ELEMENT_DATA': '0x02020400',
    'FACE_DATA': '0x02020500'
}

inv_TAGS = {v: k for k, v in TAGS.items()}

filename = str(sys.argv[1])
nstate = int(sys.argv[2])  # read this state

f = open(filename, 'rb')

f.seek(0,2)
filesize = f.tell()
f.seek(0,0)


def search_block(f, TAGS, BLOCK_TAG, max_rec=5, cur_rec=0,
                 verbose=0, inv_TAGS=0):
    '''Search some block in the current level.'''

    if cur_rec>max_rec:
        print 'Max iteration reached: Cannot find %s' % BLOCK_TAG
        return -1

    buf = f.read(4)

    if buf == '':
        print 'EOF: Cannot find %s' % BLOCK_TAG
        return -1
    else:
        cur_id = struct.unpack('I', buf)[0]
    a = struct.unpack('I', f.read(4))[0]  # size of the block

    if verbose == 1:
        cur_id_str = '0x'+'{0:08x}'.format(cur_id)
        # print 'cur_ID: ' + cur_id_str
        print 'cur_tag:', inv_TAGS[cur_id_str]
        print 'size:', a
    
    if(int(TAGS[BLOCK_TAG], base=16) == cur_id):
        print('%s' %BLOCK_TAG)
        
        return a
    else:
        f.seek(a, 1)
        d = search_block(f, TAGS, BLOCK_TAG, cur_rec=cur_rec+1,
                         verbose=verbose,
                         inv_TAGS=inv_TAGS)
        if d == -1:
            f.seek(-a, 1)
            return -1
        else:
            return d



def check_block(f, TAGS, BLOCK_TAG):
    '''Check if the BLOCK TAG exists immediately after the file cursor.'''

    buf = struct.unpack('I', f.read(4))[0]
    f.seek(-4, 1)
    
    if(int(TAGS[BLOCK_TAG], base=16) == buf):
        return 1
    
    return 0

        
def seek_block(f, TAGS, BLOCK_TAG):
    if(int(TAGS[BLOCK_TAG], base=16) == struct.unpack('I', f.read(4))[0]):
        print('%s' %BLOCK_TAG)
    a = struct.unpack('I', f.read(4))  # size of the root section

    return a[0]

def skip_block(f):
    '''skip some block 

    WARNING: the file cursor needs to be at the begining of the
    section!

    '''
    
    block_id = struct.unpack('I', f.read(4))[0]
    a = struct.unpack('I', f.read(4))[0]
    f.seek(a, 1)

    print hex(block_id) + '(size %d)' %a + ' skipped.'
    
    return a
    

if(int(TAGS['FEBIO'], base=16) == struct.unpack('I', f.read(4))[0]):
    print('Correct FEBio format')

seek_block(f, TAGS, 'ROOT')

search_block(f, TAGS, 'HEADER')

search_block(f, TAGS, 'HDR_VERSION')
version = struct.unpack('I', f.read(4))[0]
if(int(TAGS['VERSION'], base=16) == version):
    print('Current version is: %d' % version)

a = search_block(f, TAGS, 'HDR_NODES')
nNodes = struct.unpack('I', f.read(4))[0]
print 'Number of nodes: %d' % (nNodes)

search_block(f, TAGS, 'DICTIONARY')

a = search_block(f, TAGS, 'DIC_NODAL')
print a

item_types = []
item_formats = []
item_names = []

while check_block(f, TAGS, 'DIC_ITEM'):

    a = search_block(f, TAGS, 'DIC_ITEM')
    a = search_block(f, TAGS, 'DIC_ITEM_TYPE')
    item_types.append(int(struct.unpack('I', f.read(4))[0]))

    a = search_block(f, TAGS, 'DIC_ITEM_FMT')
    item_formats.append(int(struct.unpack('I', f.read(4))[0]))

    a = search_block(f, TAGS, 'DIC_ITEM_NAME')
    item_names.append(f.read(64).split('\x00')[0])

a = search_block(f, TAGS, 'DIC_DOMAIN')
while check_block(f, TAGS, 'DIC_ITEM'):

    a = search_block(f, TAGS, 'DIC_ITEM')
    a = search_block(f, TAGS, 'DIC_ITEM_TYPE')
    item_types.append(int(struct.unpack('I', f.read(4))[0]))

    a = search_block(f, TAGS, 'DIC_ITEM_FMT')
    item_formats.append(int(struct.unpack('I', f.read(4))[0]))
    
    a = search_block(f, TAGS, 'DIC_ITEM_NAME')
    item_names.append(f.read(64).split('\x00')[0])

a = search_block(f, TAGS, 'MATERIALS')
f.seek(a, 1)  # skip the material section

a = search_block(f, TAGS, 'GEOMETRY')
f.seek(a, 1)  # skip the material section

# skip the first nstate-1 states
for ns in range(0, nstate):
    a = search_block(f, TAGS, 'STATE')
    f.seek(a, 1)

    
    # if(int(STATE_SECTION, base=16) == struct.unpack('I', f.read(4))[0]):
    #     print('State section %d' %ns)
    # a = struct.unpack('I', f.read(4))[0]  # size of the state section
    # print('skipping this state')
    # f.seek(a, 1)  # skip this section

a = search_block(f, TAGS, 'STATE')
a = search_block(f, TAGS, 'STATE_HEADER')

# a = search_block(f, TAGS, 'STATE_HDR_ID', verbose=1, inv_TAGS=inv_TAGS)
# state_id = struct.unpack('f', f.read(4))
# print 'The state ID: %d' % state_id


a = search_block(f, TAGS, 'STATE_HDR_TIME')
time = struct.unpack('f', f.read(4))
print 'This state is at %f time' % (time)

a = search_block(f, TAGS, 'STATE_DATA')
print a


a = search_block(f, TAGS, 'NODE_DATA')
print a

n_node_data = 0
while check_block(f, TAGS, 'STATE_VARIABLE'):
    n_node_data += 1
    
    a = search_block(f, TAGS, 'STATE_VARIABLE')
    print a

    a = search_block(f, TAGS, 'STATE_VAR_ID')
    var_id = struct.unpack('I', f.read(4))[0]
    print 'variable id:', var_id
    print 'variable_name:', item_names[var_id-1]
    
    a = search_block(f, TAGS, 'STATE_VAR_DATA')
    print a

    #### ????? ####
    f.read(8)

    # VEC3F
    if item_types[var_id-1] == 1:

        disp = zeros([nNodes, 3])
        for i in range(0, nNodes):
            for j in range(0, 3):
                disp[i, j] = struct.unpack('f', f.read(4))[0]
        savetxt('%s.dat' %item_names[var_id-1], disp)


a = search_block(f, TAGS, 'ELEMENT_DATA')
print a

while check_block(f, TAGS, 'STATE_VARIABLE'):

    a = search_block(f, TAGS, 'STATE_VARIABLE')
    print a

    a = search_block(f, TAGS, 'STATE_VAR_ID')
    var_id = struct.unpack('I', f.read(4))[0] + n_node_data
    print 'variable id:', var_id
    print 'variable_name:', item_names[var_id-1]
    
    a = search_block(f, TAGS, 'STATE_VAR_DATA')
    print 'state var data size', a
    
    # VEC3F
    if item_types[var_id-1] == 1:
        n_data = int((a-8)/3/4)
        print 'number of data points', n_data

        if n_data > 0:
            f.read(8)
            disp = zeros([n_data, 3])
            for i in range(0, n_data):
                for j in range(0, 3):
                    disp[i, j] = struct.unpack('f', f.read(4))[0]
            savetxt('%s.dat' %item_names[var_id-1], disp)
        else:
            f.seek(a,1)
    else:
        f.seek(a,1)

print 'done'


cur_state = nstate
while check_block(f, TAGS, 'STATE'):
    cur_state += 1
    a_state = search_block(f, TAGS, 'STATE')
    
    cur_cur = f.tell()
    a = search_block(f, TAGS, 'STATE_HEADER')
    a = search_block(f, TAGS, 'STATE_HDR_TIME')
    time = struct.unpack('f', f.read(4))
    print 'This state is at %f time' % (time)
    f.seek(cur_cur, 0)
    
    f.seek(a_state, 1)
    if f.tell() == filesize:
        break

    
print 'EOF?'
print f.read(4)
# a = search_block(f, TAGS, 'ROOT', verbose=1, inv_TAGS=inv_TAGS)


f.close()
