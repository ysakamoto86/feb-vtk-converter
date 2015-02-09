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


def load_data(workdir, ndfiles, elfiles):

    nodes = []
    elems = []

    # load data
    for ndf in ndfiles:
        nodes.append(np.loadtxt(workdir+ndf))
    for elf in elfiles:
        elems.append(np.loadtxt(workdir+elf, dtype=int)[:, 1:])

    if len(ndfiles) < 2:
        node_data = nodes[0]
    else:
        for i in range(len(ndfiles)-1):
            node_data = np.vstack((nodes[i], nodes[i+1]))

    n_elem_sub = [len(elems[0])]
    elem_data = elems[0]
    if len(elfiles) > 1:
        for i in range(len(elfiles)-1):
            elem_data = np.vstack((elem_data, elems[i+1]))
            n_elem_sub.append(len(elems[i+1]))

    return node_data, elem_data, n_elem_sub


def write_vtk(workdir, nodes, elems, n_elem_sub, ndfiles,
              elfiles, opfile):

    n_elems = len(elems)

    # element types (tet4, hex6, etc)
    elem_types = np.ones(n_elems, dtype=int)*10
    offsets = np.array(range(4, n_elems*4+1, 4), dtype=int)

    # material type (subdomain number)
    mat_types = []
    for i in range(len(n_elem_sub)):
        mat_types += [i]*n_elem_sub[i]
    mat_types = np.array(mat_types, dtype=int)

    # load point data
    node_data = []
    for nf in ndfiles:
        node_data.append(np.loadtxt(workdir+nf))

    # load element data
    elem_data = []
    for ef in elfiles:
        elem_data.append(np.loadtxt(workdir+ef))

    # append zeros to the element data
    # NOTE: we assume that the data is defined in the first whatever elements
    for i in range(len(elem_data)):
        if len(elem_data[i]) < n_elems:
            if elem_data[i].ndim == 1:
                data_dim = 1
            else:
                data_dim = len(elem_data[i][0])
            elem_data[i] = np.vstack((elem_data[i],
                                      np.zeros((n_elems-len(elem_data[i]),
                                                data_dim))))

    ### OUTPUT

    print "Outputting to the .vtu file..."

    # header
    root = etree.Element("VTKFile", type="UnstructuredGrid")

    UnstructuredGrid_xml = etree.SubElement(root, "UnstructuredGrid")

    Piece_xml = etree.SubElement(UnstructuredGrid_xml, "Piece",
                                 NumberOfPoints=str(len(nodes)),
                                 NumberOfCells=str(len(elems)))

    # PointData_xml = etree.SubElement(Piece_xml, "PointData",
                                     # Vectors="displacement")

    PointData_xml = etree.SubElement(Piece_xml, "PointData")

    for i in range(len(ndfiles)):
        if node_data[i].ndim == 1:
            data_dim = 1
        else:
            data_dim = len(node_data[i][0])
        
        DataArray_xml = etree.SubElement(PointData_xml, "DataArray",
                                         type="Float32",
                                         NumberOfComponents=str(data_dim),
                                         Name=ndfiles[i].split('_')[0])
        DataArray_xml.text = '\n'+' '.join([repr(a) for a in
                                            node_data[i].flatten()])+'\n'

    CellData_xml = etree.SubElement(Piece_xml, "CellData")

    DataArray_xml = etree.SubElement(CellData_xml, "DataArray",
                                     type="Int32",
                                     NumberOfComponents="1",
                                     Name="mat_types")
    DataArray_xml.text = '\n'+' '.join([`a` for a in mat_types])+'\n'

    # elem_data[1] = mat_types
    for i in range(len(elem_data)):
        if elem_data[i].ndim == 1:
            data_dim = 1
            # febio bug? number of dimension does not match
            elem_data[i] = elem_data[i][:n_elems]
        else:
            data_dim = len(elem_data[i][0])

        data_type = str(elem_data[i].dtype)
        if 'int' in data_type:
            data_type = "Int64"
        elif 'float' in data_type:
            data_type = "Float64"
        else:
            data_type = "Float64"
        
        DataArray_xml = etree.SubElement(CellData_xml, "DataArray",
                                         type=data_type,
                                         NumberOfComponents=str(data_dim),
                                         Name=elfiles[i].split('_')[0])
        DataArray_xml.text = '\n'+' '.join([repr(a) for a in
                                            elem_data[i].flatten()])+'\n'

    Points_xml = etree.SubElement(Piece_xml, "Points")
    DataArray_xml = etree.SubElement(Points_xml, "DataArray",
                                     NumberOfComponents="3",
                                     type="Float32")
    DataArray_xml.text = '\n'+' '.join([`a` for a in nodes.flatten()])+'\n'

    Cells_xml = etree.SubElement(Piece_xml, "Cells")
    DataArray_xml = etree.SubElement(Cells_xml, "DataArray",
                                     type="Int32",
                                     Name="connectivity")
    DataArray_xml.text = '\n'+' '.join([`a` for a in elems.flatten()])+'\n'
    

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
    output_file = workdir+opfile
    f_out = open(output_file, 'w')
    f_out.write(xml_str)
    f_out.close()




### INPUT
if int(len(sys.argv) < 3):
    print "Provide the work directory!"
    sys.exit(1)

workdir = str(sys.argv[1])
nstate = int(sys.argv[2])


if workdir[-1] is not '/':
    workdir += '/'


ndfiles = ['nodes_%d.dat' %nstate]
elfiles = ['elements_%d_0.dat' %nstate, 'elements_%d_1.dat' %nstate,
           'elements_%d_2.dat' %nstate]
opfile = 'res_%d.vtu' %nstate

nddfiles = ['displacement_%d.dat' %nstate, 'velocity_%d.dat' %nstate]
eldfiles = ['vic-fiber_%d.dat' %nstate, 'relative volume_%d.dat'
            %nstate, 'stress_%d.dat' %nstate]

nodes, elems, n_elem_sub = load_data(workdir, ndfiles, elfiles)


write_vtk(workdir, nodes, elems, n_elem_sub, nddfiles,
          eldfiles, opfile)
