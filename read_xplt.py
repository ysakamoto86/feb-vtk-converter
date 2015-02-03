import struct
from numpy import *
import sys
import pdb

TAGS = {
    'FEBIO': '0x00464542',
    'ROOT': '0x01000000',
    'HEADER': '0x01010000',
    'VERSION': '0x01010001',
    'CURRENT_VERSION': '0x0003', # verion 3
    'NODES': '0x01010002',
    'DICTIONARY': '0x01020000',
    'MATERIAL': '0x01030000',
    'GEOMETRY': '0x01040000',
    'STATE_SECTION': '0x02000000',
    'STATE_HEADER': '0x02010000',
    'TIME': '0x02010002',
    'STATE_DATA': '0x02020000',
    'NODE_DATA': '0x02020300',
    'DOMAIN_DATA': '0x02020400',
    'SURFACE_DATA': '0x02020500',
    'STATE_VAR': '0x02020001',
    'VARIABLE_ID': '0x02020002',
    'VARIABLE_DATA': '0x02020003',
    'UNKNOWN': '0x01010003'
}

filename = str(sys.argv[1])
nstate = int(sys.argv[2])  # read this state

f = open(filename, 'rb')


def search_block(f, TAGS, BLOCK_TAG):
    '''Search some block in the current level.'''

    cur_tag = struct.unpack('I', f.read(4))[0]

    if(int(TAGS[BLOCK_TAG], base=16) == cur_tag):
        print('%s' %BLOCK_TAG)
    a = struct.unpack('I', f.read(4))  # size of the root section

    return a[0]

    


def seek_block(TAGS, BLOCK_TAG):
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
    a = struct.unpack('I', f.read(4))[0]  # size of the root section
    f.seek(a, 1)

    print hex(block_id) + '(size %d)' %a + ' skipped.'
    
    return a
    

if(int(TAGS['FEBIO'], base=16) == struct.unpack('I', f.read(4))[0]):
    print('Correct FEBio format')
# struct.unpack('I',f.read(4)) #size of the whole file


# if(int(TAGS['ROOT'], base=16) == struct.unpack('I', f.read(4))[0]):
#     print('Root section')
# a = struct.unpack('I', f.read(4))  # size of the root section
# # f.seek(a[0],1) #skip the root section

seek_block(TAGS, 'ROOT')
seek_block(TAGS, 'HEADER')

seek_block(TAGS, 'VERSION')
if(int(TAGS['CURRENT_VERSION'], base=16) == struct.unpack('I', f.read(4))[0]):
    print('Current version is: %d' % int(TAGS['CURRENT_VERSION'], base=16))

a = seek_block(TAGS, 'NODES')
nNodes = struct.unpack('I', f.read(4))[0]
print 'Number of nodes: %d' % (nNodes)


f.seek(a-4, 1)  # skip to the next section

a = skip_block(f)


# if(int(TAGS['UNKNOWN'], base=16) == struct.unpack('I', f.read(4))[0]):
#     print('Unknown section')
# struct.unpack('I', f.read(4))  # size of an unknown section
# struct.unpack('I', f.read(4))[0]  # some value, what does it mean?

# f.read(12)

a = seek_block(TAGS, 'DICTIONARY')
f.seek(a, 1)

# if(int(HEADER, base=16) == struct.unpack('I', f.read(4))[0]):
#     print('Header section')
# struct.unpack('I', f.read(4))  # size of the header section

# if(int(TAGS['VERSION'], base=16) == struct.unpack('I', f.read(4))[0]):
#     print('Version section')
# struct.unpack('I', f.read(4))  # size of the version section

# if(int(TAGS['CURRENT_VERSION'], base=16) == struct.unpack('I', f.read(4))[0]):
#     print('Current version is: %d' % int(TAGS['CURRENT_VERSION'], base=16))

# if(int(TAGS['NODES'], base=16) == struct.unpack('I', f.read(4))[0]):
#     print('Nodes section')
# struct.unpack('I', f.read(4))  # size of the nodes section
# nNodes = struct.unpack('I', f.read(4))[0]
# print 'Numver of nodes: %d' % (nNodes)

# if(int(TAGS['UNKNOWN'], base=16) == struct.unpack('I', f.read(4))[0]):
#     print('Unknown section')
# struct.unpack('I', f.read(4))  # size of an unknown section
# struct.unpack('I', f.read(4))[0]  # some value, what does it mean?

# if(int(TAGS['DICTIONARY'], base=16) == struct.unpack('I', f.read(4))[0]):
#     print('Dictionary section')
# a = struct.unpack('I', f.read(4))  # size of the dictionary section
# f.seek(a[0], 1)  # skip the dictionary section

'''
a=struct.unpack('I',f.read(4))[0];
if( int('0x01021000',base=16) == a ):
	print('Dictionary global_data section');
	a = struct.unpack('I',f.read(4)) #size of the dictionary global data section

if( int('0x01022000',base=16) == a ):
	print('Dictionary material_data section');
	a = struct.unpack('I',f.read(4)) #size of the dictionary material data section

if( int('0x01023000',base=16) == a ):
	print('Dictionary nodeset_data section');
	b = struct.unpack('I',f.read(4)) #size of the dictionary nodeset data section

	if( int('0x01020001',base=16) == struct.unpack('I',f.read(4))[0] ):
		print('Dictionary nodeset data dictionary item section');
	b = struct.unpack('I',f.read(4)) #size of the dictionary nodeset data dictionary item section

	if( int('0x01020002',base=16) == struct.unpack('I',f.read(4))[0] ):
		print('Dictionary nodeset data dictionary item item_type section');
	b = struct.unpack('I',f.read(4)) #size of the dictionary nodeset data dictionary item item_type section
	item_type = struct.unpack('I',f.read(4))[0] #size of the dictionary nodeset data dictionary item item_type section
	if(item_type==0):
		print('item_type::float');
	elif(item_type==1):
		print('item_type::vector');
	elif(item_type==2):
		print('item_type::natrix');

	if( int('0x01020003',base=16) == struct.unpack('I',f.read(4))[0] ):
		print('Dictionary nodeset data dictionary item item_format section');
	b = struct.unpack('I',f.read(4)) #size of the dictionary nodeset data dictionary item item_format section
	item_format = struct.unpack('I',f.read(4))[0] #size of the dictionary nodeset data dictionary item item_type section
	if(item_format==0):
		print('item_format::node');
	elif(item_format==1):
		print('item_format::item');
	elif(item_format==2):
		print('item_format::multiple');

	if( int('0x01020004',base=16) == struct.unpack('I',f.read(4))[0] ):
		print('Dictionary nodeset data dictionary item item_name section');
	b = struct.unpack('I',f.read(4)) #size of the dictionary nodeset data dictionary item item_name section
	item_name = f.read(64) #size of the dictionary nodeset data dictionary item item_name section
	print(item_name)

if( int('0x01024000',base=16) == a ):
	print('Dictionary domain_data section');
	a = struct.unpack('I',f.read(4)) #size of the dictionary domain data section

if( int('0x01025000',base=16) == a ):
	print('Dictionary surface_data section');
	a = struct.unpack('I',f.read(4)) #size of the dictionary surface data section
'''

if(int(MATERIAL, base=16) == struct.unpack('I', f.read(4))[0]):
    print('Material section')
a = struct.unpack('I', f.read(4))  # size of the Material section
f.seek(a[0], 1)  # skip the material section

if(int(GEOMETRY, base=16) == struct.unpack('I', f.read(4))[0]):
    print('Geometry section')
a = struct.unpack('I', f.read(4))  # size of the Geometry section
f.seek(a[0], 1)  # skip the geometry section

# skip the first nstate-1 states
for ns in range(0, nstate):
    if(int(STATE_SECTION, base=16) == struct.unpack('I', f.read(4))[0]):
        print('State section %d' %ns)
    a = struct.unpack('I', f.read(4))[0]  # size of the state section
    print('skipping this state')
    f.seek(a, 1)  # skip this section

if(int(STATE_SECTION, base=16) == struct.unpack('I', f.read(4))[0]):
    print('State section %d' %nstate)
struct.unpack('I', f.read(4))  # size of the state section

if(int(STATE_HEADER, base=16) == struct.unpack('I', f.read(4))[0]):
    print('State section %d header' %nstate)
struct.unpack('I', f.read(4))  # size of the state header section

if(int(TIME, base=16) == struct.unpack('I', f.read(4))[0]):
    print('State section %d time' %nstate)
struct.unpack('I', f.read(4))  # size of the state time section
time = struct.unpack('f', f.read(4))
print 'This state is at %f time' % (time)

if(int(STATE_DATA, base=16) == struct.unpack('I', f.read(4))[0]):
    print('State section %d data' %nstate)
struct.unpack('I', f.read(4))  # size of the state data section

if(int(NODE_DATA, base=16) == struct.unpack('I', f.read(4))[0]):
    print('State section %d node data' %nstate)
struct.unpack('I', f.read(4))  # size of the state node_data section

if(int(STATE_VAR, base=16) == struct.unpack('I', f.read(4))[0]):
    print('State section %d node data state data 1' %nstate)
struct.unpack('I', f.read(4))  # size of the state node_data section

if(int(VARIABLE_ID, base=16) == struct.unpack('I', f.read(4))[0]):
    print('State section 1 node data state data 1 region ID')
struct.unpack('I', f.read(4))  # size of the state node_data section
ID = struct.unpack('I', f.read(4))
print 'Region ID is %d' % (ID)

if(int(VARIABLE_DATA, base=16) == struct.unpack('I', f.read(4))[0]):
    print('State section 1 node data state data 1 data')
a = struct.unpack('I', f.read(4))  # size of the state node_data section
print(a[0])
a = struct.unpack('I', f.read(4))
print(a[0])
a = struct.unpack('I', f.read(4))
print(a[0])
# f.read(8)
disp = zeros([nNodes, 3])
for i in range(0, nNodes):
    for j in range(0, 3):
        disp[i, j] = struct.unpack('f', f.read(4))[0]
savetxt('try.dat', disp)

f.close()
