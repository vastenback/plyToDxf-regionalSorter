import os
import glob
import numpy

input_base_path = input("Enter location of sub-division parent directory, eg. 'REST' or 'right-ear': ")

def plyify():
    globStr = input_base_path + "\\" + "PLY" + "\\" + "*.ply"
    fileList = glob.glob(globStr)
    all_lines = []
    all_nodes = []
    headerList  = ["ply\n", "format ascii 1.0\n", "comment VCGLIB generated\n", "element vertex 3\n", "property float x\n", "property float y\n", "property float z\n", "element face 1\n", "property list uchar int vertex_indices\n", "end_header\n"]

    for file in fileList:
        with open(file) as f:
            lines = [line.rstrip() for line in f]
            all_lines.append(lines)
        f.close()

    total_faces = len(fileList)
    headerList_np = numpy.array(headerList)
    headerList_np[7] = "element face " + str(total_faces) + "\n"

    def addToNodeList(node_str):
        if node_str not in all_nodes:
            all_nodes.append(node_str)

    for file in all_lines:
        node_one = file[10]
        node_two = file[11]
        node_three = file[12]
        addToNodeList(node_one)
        addToNodeList(node_two)
        addToNodeList(node_three)

    total_nodes = len(all_nodes)
    headerList_np[3] = "element vertex " + str(total_nodes) + "\n"

    dirName = input_base_path + "\\" + "collection"
    try:
        os.mkdir(dirName)
    except FileExistsError:
        print("Directory already exists, continuing as normal. ")

    file_open = open(dirName + "\\" + "collection_all.ply", 'w')
    for header_part in headerList_np:
        file_open.write(header_part)

    for coord in all_nodes:
        file_open.write(coord + "\n")

    for file in all_lines:
        node_one = file[10]
        node_two = file[11]
        node_three = file[12]
        output_one = all_nodes.index(node_one)
        output_two = all_nodes.index(node_two)
        output_three = all_nodes.index(node_three)
        file_open.write("3" + " " + str(output_one) + " " + str(output_two) + " " + str(output_three) + "\n")

    file_open.close()
    print("Individual faces collected and organized under folder 'collect'. ")

plyify()
