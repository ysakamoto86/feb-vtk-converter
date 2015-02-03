import sys
from subprocess import call
import xml.etree.ElementTree as etree
import numpy as np
# from lxml import etree
import pdb
import xml.dom.minidom as minidom


def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """

    rough_string = etree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)

    return reparsed.toprettyxml(indent="\t")


### INPUT
feb_file = 'cell_001.feb'


print 'Reading file %s...' % feb_file

tree = etree.parse(feb_file)
root = tree.getroot()

for child in root:
    if child.tag == 'Geometry':
        Geometry_xml = child

for child in Geometry_xml:
    if child.tag == "Nodes":
        Nodes_xml = child
    elif child.tag == "Elements":
        Elements_xml = child

node_data = []
for node in Nodes_xml:
    node_data.append(node.text.replace(',', ''))

elem_conns = []
elem_types = []
offsets = []
mat_types = []
nd = 0
for elem in Elements_xml:
    conn = np.array(elem.text.split(','), dtype=int)-1
    elem_conns.append(conn)
    if elem.tag=='tet4':
        elem_types.append(10)

    mat_types.append(int(elem.attrib['mat']))
        
    nd += len(conn)
    offsets.append(nd)
    
for logfile_xml in root.iter('logfile'):
    nd_file = logfile_xml[1].attrib['file']
    el_file = logfile_xml[2].attrib['file']

print 'Reading data files:\n%s \n%s...' %(nd_file, el_file)

def read_nd_file(ndf, t):
    '''Read the node output file and return the displacements at a given
    time.

    '''
    
    f = open(ndf, 'r')

    lines = f.readlines()

    ln = 0
    for line in lines:
        if line.startswith('*Time'):
            t_cur = float(line.split('=')[1])
            if abs(t_cur-t)<0.000001:
                break
    ln += 1

    d = []
    for line in lines[ln+3:]:
        if line.startswith('*'):
            break

        d.append(np.array(line.split(' ')[1:], dtype=float))

    return d


def read_el_file(elf, t):
    '''Read the element output file and return the stress at a
    given time.

    '''
    
    f = open(elf, 'r')

    lines = f.readlines()

    ln = 0
    for line in lines:
        if line.startswith('*Time'):
            t_cur = float(line.split('=')[1])
            if abs(t_cur-t)<0.000001:
                break
    ln += 1

    sig = []
    for line in lines[ln+3:]:
        if line.startswith('*'):
            break

        sig.append(np.array(line.split(' ')[1:], dtype=float))

    return sig


disp = read_nd_file(nd_file, 1.0)
defgrad = read_el_file(el_file, 1.0)

### OUTPUT

print "Outputting to the .vtu file..."

# header
root = etree.Element("VTKFile", type="UnstructuredGrid")

UnstructuredGrid_xml = etree.SubElement(root, "UnstructuredGrid")

Piece_xml = etree.SubElement(UnstructuredGrid_xml, "Piece",
                             NumberOfPoints=str(len(node_data)),
                             NumberOfCells=str(len(elem_conns)))

PointData_xml = etree.SubElement(Piece_xml, "PointData",
                                 Vectors="displacement")

DataArray_xml = etree.SubElement(PointData_xml, "DataArray",
                                 type="Float32",
                                 NumberOfComponents="3",
                                 Name="displacement")
DataArray_xml.text = ' '.join(map((lambda x: np.array_str(x)[1:-1]),
                                  disp))

CellData_xml = etree.SubElement(Piece_xml, "CellData",
                                Scalars='material_type',
                                Tensors='deformation_gradient')

DataArray_xml = etree.SubElement(CellData_xml, "DataArray",
                                 type="Int32",
                                 Name="material_type")
DataArray_xml.text = str(mat_types)[1:-1].replace(',', '')


DataArray_xml = etree.SubElement(CellData_xml, "DataArray",
                                 type="Float32",
                                 NumberOfComponents="9",
                                 Name="deformation_gradient")
DataArray_xml.text = ' '.join(map((lambda x: np.array_str(x)[1:-1]),
                                  defgrad))



Points_xml = etree.SubElement(Piece_xml, "Points")
DataArray_xml = etree.SubElement(Points_xml, "DataArray",
                                 NumberOfComponents="3",
                                 type="Float32")
DataArray_xml.text = '\n'+'\n'.join(node_data)+'\n'


Cells_xml = etree.SubElement(Piece_xml, "Cells")
DataArray_xml = etree.SubElement(Cells_xml, "DataArray",
                                 type="Int32",
                                 Name="connectivity")
DataArray_xml.text = ' '.join(map((lambda x: np.array_str(x)[1:-1]),
                                  elem_conns))

DataArray_xml = etree.SubElement(Cells_xml, "DataArray",
                                 type="Int32",
                                 Name="offsets")
DataArray_xml.text = str(offsets)[1:-1].replace(',', '')

DataArray_xml = etree.SubElement(Cells_xml, "DataArray",
                                 type="UInt8",
                                 Name="types")
DataArray_xml.text = str(elem_types)[1:-1].replace(',', '')



# xml_str = etree.tostring(root, encoding='ISO-8859-1',
                         # pretty_print="true")
xml_str = prettify(root)


# output
output_file = 'test.vtu'
f_out = open(output_file, 'w')
f_out.write(xml_str)
f_out.close()


# dom = xml.dom.minidom.parseString(xml_str)
