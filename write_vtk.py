import sys
import os
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


def load_geom(workdir, ndfiles, elfiles):

    nodes = []
    elems = []

    # load data
    for ndf in ndfiles:
        nodes.append(np.loadtxt(workdir + ndf + '.dat'))
    for elf in elfiles:
        elems.append(np.loadtxt(workdir + elf + '.dat', dtype=int)[:, 1:])

    if len(ndfiles) < 2:
        node_coords = nodes[0]
    else:
        for i in range(len(ndfiles) - 1):
            node_coords = np.vstack((nodes[i], nodes[i + 1]))

    dom_n_elems = [len(elems[0])]
    elem_conns = elems[0]
    if len(elfiles) > 1:
        for i in range(len(elfiles) - 1):
            elem_conns = np.vstack((elem_conns, elems[i + 1]))
            dom_n_elems.append(len(elems[i + 1]))

    return node_coords, elem_conns, dom_n_elems


def load_data(workdir, nstate, ndd_names, eld_names):

    # load node data
    node_data = []
    # assumption: node data is define on all the nodes
    for nf in ndd_names:
        filename = workdir + '%s_%d.dat' % (nf, nstate)
        node_data.append(np.loadtxt(filename))

    # get element data files
    elem_files = []
    elem_data = []
    data_dims = [0] * len(eld_names)
    k = 0
    for eldn in eld_names:
        elf = []
        eld = []
        for i in range(len(dom_n_elems)):
            filename = workdir + '%s_%d_%d.dat' % (eldn, nstate, i)
            if os.path.isfile(filename):
                elf.append(filename)
                eld.append(np.loadtxt(filename))

                if eld[i].ndim == 1:
                    data_dims[k] = 1
                    eld[i] = np.array([eld[i]]).T
                else:
                    data_dims[k] = len(eld[i][0])

            else:
                elf.append('')
                eld.append([])

        elem_files.append(elf)
        elem_data.append(eld)
        k += 1

    # fill zeros to the empty data
    for i in range(len(elem_data)):
        for j in range(len(elem_data[i])):

            if len(elem_data[i][j]) == 0:
                elem_data[i][j] = np.zeros([dom_n_elems[j], data_dims[i]])

    # merge the element data together
    elem_data_merge = [0] * len(elem_data)
    for i in range(len(elem_data)):

        elem_data_merge[i] = elem_data[i][0]

        for j in range(1, len(elem_data[i])):
            elem_data_merge[i] = np.vstack(
                (elem_data_merge[i], elem_data[i][j]))

    return node_data, elem_data_merge


def write_vtk(workdir, nodes, elems, dom_n_elems, node_data, elem_data,
              ndd_names, eld_names, vtkfile):

    output_file = workdir + vtkfile

    n_elems = len(elems)

    # element types (tet4, hex6, etc)
    elem_types = np.ones(n_elems, dtype=int) * 10
    offsets = np.array(range(4, n_elems * 4 + 1, 4), dtype=int)

    # material type (subdomain number)
    mat_types = []
    for i in range(len(dom_n_elems)):
        mat_types += [i] * dom_n_elems[i]
    mat_types = np.array(mat_types, dtype=int)

    # OUTPUT
    print "Outputting to %s..." % output_file

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
        data_dim = len(node_data[i][0])

        DataArray_xml = etree.SubElement(PointData_xml, "DataArray",
                                         type="Float32",
                                         NumberOfComponents=str(data_dim),
                                         Name=ndd_names[i])
        DataArray_xml.text = '\n' + ' '.join([repr(a) for a in
                                              node_data[i].flatten()]) + '\n'

    CellData_xml = etree.SubElement(Piece_xml, "CellData")

    DataArray_xml = etree.SubElement(CellData_xml, "DataArray",
                                     type="Int32",
                                     NumberOfComponents="1",
                                     Name="mat_types")
    DataArray_xml.text = '\n' + ' '.join([`a` for a in mat_types]) + '\n'

    # elem_data[1] = mat_types
    for i in range(len(elem_data)):
        if elem_data[i].ndim == 1:
            data_dim = 1
            # febio bug? number of dimension does not match
            # elem_data[i] = elem_data[i][:n_elems]
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
                                         Name=eld_names[i])
        DataArray_xml.text = '\n' + ' '.join([repr(a) for a in
                                              elem_data[i].flatten()]) + '\n'

    Points_xml = etree.SubElement(Piece_xml, "Points")
    DataArray_xml = etree.SubElement(Points_xml, "DataArray",
                                     NumberOfComponents="3",
                                     type="Float32")
    DataArray_xml.text = '\n' + ' '.join([`a` for a in nodes.flatten()]) + '\n'

    Cells_xml = etree.SubElement(Piece_xml, "Cells")
    DataArray_xml = etree.SubElement(Cells_xml, "DataArray",
                                     type="Int32",
                                     Name="connectivity")
    DataArray_xml.text = '\n' + ' '.join([`a` for a in elems.flatten()]) + '\n'

    DataArray_xml = etree.SubElement(Cells_xml, "DataArray",
                                     type="Int32",
                                     Name="offsets")
    DataArray_xml.text = '\n' + ' '.join([`a` for a in offsets]) + '\n'

    DataArray_xml = etree.SubElement(Cells_xml, "DataArray",
                                     type="UInt8",
                                     Name="types")
    DataArray_xml.text = '\n' + ' '.join([`a` for a in elem_types]) + '\n'

    # xml_str = etree.tostring(root, encoding='ISO-8859-1',
    # pretty_print="true")
    xml_str = prettify(root)

    # output
    f_out = open(output_file, 'w')
    f_out.write(xml_str)
    f_out.close()


if __name__ == '__main__':
    # INPUT
    if int(len(sys.argv) < 3):
        print "Provide the work directory!"
        sys.exit(1)

    workdir = str(sys.argv[1])
    nstate = int(sys.argv[2])

    for nstate in [10]:  # range(101):

        if workdir[-1] is not '/':
            workdir += '/'

        # ndfiles = ['nodes_%d.dat' % nstate]

        # AFM
        # elfiles = ['elements_%d_0.dat' % nstate, 'elements_%d_1.dat' % nstate,
        # 'elements_%d_2.dat' % nstate]
        # eldfiles = ['vic-fiber_%d.dat' % nstate, 'relative volume_%d.dat'
        # % nstate, 'stress_%d.dat' % nstate]

        # # MA
        # ndfiles = ['nodes_%d' % nstate]
        # elfiles = ['elements_%d_0' % nstate, 'elements_%d_1' % nstate]
        # ndd_names = ['displacement', 'velocity']
        # eld_names = ['relative volume', 'stress']

        # ECM-comp
        ndfiles = ['nodes_%d' % nstate]
        elfiles = ['elements_%d_0' % nstate, 'elements_%d_1' % nstate]
        ndd_names = ['displacement', 'velocity']
        eld_names = ['effective fluid pressure', 'fluid flux',
                     'stress', 'relative volume']

        vtkfile = 'res_%d.vtu' % nstate

        nodes, elems, dom_n_elems = load_geom(workdir, ndfiles, elfiles)
        node_data, elem_data = load_data(workdir, nstate, ndd_names, eld_names)

        write_vtk(workdir, nodes, elems, dom_n_elems, node_data,
                  elem_data, ndd_names, eld_names, vtkfile)
