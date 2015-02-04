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
workdir = str(sys.argv[1])

if workdir[-1] is not '/':
    workdir += '/'

# feb_file = workdir + 'afm.feb'


# print 'Reading file %s...' % feb_file

# tree = etree.parse(feb_file)
# root = tree.getroot()

# for child in root:
#     if child.tag == 'Geometry':
#         Geometry_xml = child

# for child in Geometry_xml:
#     if child.tag == "Nodes":
#         Nodes_xml = child
#     elif child.tag == "Elements":
#         Elements_xml = child

# load data
node_data = np.loadtxt(workdir+'nodes.dat')
elem_data_0 = np.loadtxt(workdir+'elements_0.dat', dtype=int)
elem_data_1 = np.loadtxt(workdir+'elements_1.dat', dtype=int)
# elem_data_2 = np.loadtxt(workdir+'elements_2.dat', dtype=int)

elem_data = np.vstack((elem_data_0[:, 1:], elem_data_1[:, 1:]))


# elem_data = np.vstack((np.vstack((elem_data_0[:, 1:], elem_data_1[:, 1:])),
#                       elem_data_2[:, 1:]))

nel_0 = len(elem_data_0)
nel_1 = len(elem_data_1)
# nel_2 = len(elem_data_2)

n_elems = len(elem_data)

elem_types = np.ones(n_elems, dtype=int)*10
offsets = np.array(range(4, n_elems*4+1, 4), dtype=int)
# mat_types = np.array([1]*nel_0 + [2]*nel_1 + [3]*nel_2, dtype=int)
mat_types = np.array([1]*nel_0 + [2]*nel_1, dtype=int)

# load more data
displacement = np.loadtxt(workdir+'displacement.dat')
# ff = np.loadtxt(workdir+'fluid flux.dat')
J = np.loadtxt(workdir+'relative volume.dat')
velocity = np.loadtxt(workdir+'velocity.dat')
# pressure = np.loadtxt(workdir+'effective fluid pressure.dat')
stress = np.loadtxt(workdir+'stress.dat')
fiber = np.loadtxt(workdir+'vic-fiber.dat')


# append zeros
stress = np.vstack((stress, np.zeros((n_elems-len(stress), 6))))
fiber = np.vstack((fiber, np.zeros((n_elems-len(fiber), 3))))

### OUTPUT

print "Outputting to the .vtu file..."

# header
root = etree.Element("VTKFile", type="UnstructuredGrid")

UnstructuredGrid_xml = etree.SubElement(root, "UnstructuredGrid")

Piece_xml = etree.SubElement(UnstructuredGrid_xml, "Piece",
                             NumberOfPoints=str(len(node_data)),
                             NumberOfCells=str(len(elem_data)))

PointData_xml = etree.SubElement(Piece_xml, "PointData",
                                 Vectors="displacement")

DataArray_xml = etree.SubElement(PointData_xml, "DataArray",
                                 type="Float32",
                                 NumberOfComponents="3",
                                 Name="displacement")
DataArray_xml.text = '\n'+' '.join([`a` for a in displacement.flatten()])+'\n'

CellData_xml = etree.SubElement(Piece_xml, "CellData",
                                Scalars='material_type',
                                Vectors='fiber')

DataArray_xml = etree.SubElement(CellData_xml, "DataArray",
                                 type="Int32",
                                 Name="material_type")
DataArray_xml.text = '\n'+' '.join([`a` for a in mat_types])+'\n'

DataArray_xml = etree.SubElement(CellData_xml, "DataArray",
                                 type="Float32",
                                 NumberOfComponents="3",
                                 Name="fiber")
DataArray_xml.text = '\n'+' '.join([`a` for a in fiber.flatten()])+'\n'


DataArray_xml = etree.SubElement(CellData_xml, "DataArray",
                                 type="Float32",
                                 NumberOfComponents="3",
                                 Name="stress")
DataArray_xml.text = '\n'+' '.join([`a` for a in stress[:,0:3].flatten()])+'\n'
# DataArray_xml.text = ' '.join(map((lambda x: np.array_str(x)[1:-1]),
                                  # stress))



Points_xml = etree.SubElement(Piece_xml, "Points")
DataArray_xml = etree.SubElement(Points_xml, "DataArray",
                                 NumberOfComponents="3",
                                 type="Float32")
DataArray_xml.text = '\n'+' '.join([`a` for a in node_data.flatten()])+'\n'

Cells_xml = etree.SubElement(Piece_xml, "Cells")
DataArray_xml = etree.SubElement(Cells_xml, "DataArray",
                                 type="Int32",
                                 Name="connectivity")
DataArray_xml.text = ' '.join(map((lambda x: np.array_str(x)[1:-1]),
                                  elem_data))

DataArray_xml = etree.SubElement(Cells_xml, "DataArray",
                                 type="Int32",
                                 Name="offsets")
DataArray_xml.text = '\n'+' '.join([`a` for a in offsets])+'\n'

DataArray_xml = etree.SubElement(Cells_xml, "DataArray",
                                 type="UInt8",
                                 Name="types")
DataArray_xml.text = '\n'+' '.join([`a` for a in elem_types])+'\n'



# xml_str = etree.tostring(root, encoding='ISO-8859-1',
                         # pretty_print="true")
xml_str = prettify(root)


# output
output_file = workdir+'test.vtu'
f_out = open(output_file, 'w')
f_out.write(xml_str)
f_out.close()


# dom = xml.dom.minidom.parseString(xml_str)
