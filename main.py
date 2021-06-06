from collections import defaultdict
from sys import setrecursionlimit
import os

all_faces = []
node_neighbour_faces = defaultdict(set)
node_neighbour_nodes = defaultdict(set)
coordinate_list = []
directionNode = None
borderNodes = []
visitedNodes = []

input_folder = input("Enter location of input .ply file: ")
output_folder = input("Enter location of output folder for processed files: ")

def readPly():
    try:
        with open(input_folder) as f:
            lines = [line.rstrip() for line in f]
    except:
        print("Something went wrong with reading the file")
        return False
    finally:
        f.close()

    for i in range(0,len(lines) - 1):
        line = lines[i]
        truncline_vertex = line[0:14]
        truncline_face = line[0:12]

        if line == "end_header":
            header_end_iter = i
        if truncline_vertex == "element vertex":
            vertex_count = int(line[15:len(line)])
        if truncline_face == "element face":
            face_count = int(line[13:len(line)])

    vertex_end_iter = vertex_count + header_end_iter + 1
    face_end_iter = face_count + vertex_end_iter

    for i in range(header_end_iter + 1, vertex_end_iter):
        coordinate_list.append(lines[i])

    for i in range(vertex_end_iter, face_end_iter):
        line = lines[i].split()
        line.pop(0)
        all_faces.append(line)

    for i in range(0,len(all_faces)):
        all_faces[i] = list(map(int, all_faces[i]))

def createAuxstruct():
    for i in range(0, len(all_faces)-1):
        for node in all_faces[i]:
            currSet = node_neighbour_faces[int(node)]
            if currSet is None:
                currSet = {i}
            else:
                currSet.add(i)
            node_neighbour_faces[int(node)] = currSet

def promptDivisions():
    print("--------------------------------------------------------------------")
    print("Now for each sub-division of the complete figure,")
    print("enter the name and division nodes, followed by the directional node")
    print("after a space, eg. 'HEAD 5,8,9,11 4'.")
    print("")
    print("Each line represents a new sub-division.")
    print("When done enter 'DONE' or whitespace instead of a new subdivision in the prompt.")
    print("Any remaining undefined regions will be grouped under the name REST")
    print("--------------------------------------------------------------------")
    divisionprompts = []
    i = 0
    while True:
        i += 1
        prompt = input("Enter sub-division "+str(i)+": ")
        if prompt.lower() == "done" or prompt.lower() == "":
            break
        else:
            divisionprompts.append(prompt)

    temp_prompts = []
    modified_prompts = []
    complete_prompt_struct = []

    try:
        for elem in divisionprompts:
            temp_prompts = []
            stripped_elem = elem.split()
            middle_list = stripped_elem[1]
            stripped_middle_list = middle_list.split(",")
            stripped_middle_list = list(map(int, stripped_middle_list))
            for d in stripped_middle_list:
                temp_prompts.append(int(d))
            temp_prompts.append(int(stripped_elem[2]))
            modified_prompts.append(temp_prompts)

            temp_list = []
            temp_list.append(stripped_elem[0])
            temp_list.append(stripped_middle_list)
            temp_list.append(int(stripped_elem[2]))
            complete_prompt_struct.append(temp_list)

    except:
        exit("Garbage input values for sub-division: check grammar")

    for node in modified_prompts:
        for elem in node:
            if node_neighbour_faces.get(elem) is None:
                exit("Garbage input values for sub-division: entered nodes singular or non-existent")

    return(complete_prompt_struct, modified_prompts)

def adjacentNodes():
    for i in range(0, len(all_faces)-1):
        nodes = all_faces[i]
        currSet = node_neighbour_nodes[int(nodes[0])]
        currSet.add(int(nodes[1]))
        currSet.add(int(nodes[2]))

        node_neighbour_nodes[int(nodes[0])] = currSet

        currSet = node_neighbour_nodes[int(nodes[1])]
        currSet.add(int(nodes[0]))
        currSet.add(int(nodes[2]))

        node_neighbour_nodes[int(nodes[1])] = currSet

        currSet = node_neighbour_nodes[int(nodes[2])]
        currSet.add(int(nodes[0]))
        currSet.add(int(nodes[1]))

        node_neighbour_nodes[int(nodes[2])] = currSet

def recursion(nodeCurr):
    global visitedNodes
    neighbours = node_neighbour_nodes[nodeCurr]
    for neighCurr in neighbours:
        if (neighCurr not in visitedNodes) and (neighCurr not in borderNodes):
            visitedNodes.append(neighCurr)
            recursion(neighCurr)

def listToDict(faceStruct):
    correctedStruct = {}
    for i in range(0, len(faceStruct)):
        correctedStruct[i] = faceStruct[i]
    return correctedStruct

### Function contains lots of hacks, beware ###
def traverseNodes(promptsList, nodeList):
    faceDict = listToDict(all_faces)
    faceDictAll = faceDict.copy()
    region_faces_list = []
    global borderNodes
    global visitedNodes
    setrecursionlimit(5000)
    i = 0
    os.chdir(output_folder)
    visitedNodes = []
    for prompt in nodeList:
        directionNode = prompt[-1]
        borderNodes = prompt[:-1]
        visitedNodes = [directionNode]
        recursion(directionNode)

        regions_faces = set()
        for nodeCurr in visitedNodes:
            neighbours = node_neighbour_faces[nodeCurr]
            regions_faces = regions_faces.union(neighbours)
        region_faces_list.append(regions_faces)

        if i > 0:
            intersectionFace = region_faces_list[(i-1)].intersection(region_faces_list[i])
            currRegions_Faces = regions_faces.difference(intersectionFace)
        else:
            currRegions_Faces = regions_faces

        try:
            dirName = output_folder + "\\" + promptsList[i][0]
            os.mkdir(dirName)
        except FileExistsError:
            print("Directory already exists, continue on as normal")
        except:
            exit("Couldn't create directory: " + dirName + ". Restart program with admin rights and check given input and output folder locations. ")

        for faceCurr in currRegions_Faces:
            filename = output_folder + "\\" + promptsList[i][0] + "\\" + str(faceCurr) + ".ply"
            file = open(filename, 'w')
            print("Created file: " + filename)
            file.write("ply\n")
            file.write("format ascii 1.0\n")
            file.write("comment VCGLIB generated\n")
            file.write("element vertex 3\n")
            file.write("property float x\n")
            file.write("property float y\n")
            file.write("property float z\n")
            file.write("element face 1\n")
            file.write("property list uchar int vertex_indices\n")
            file.write("end_header\n")
            coord1 = coordinate_list[faceDict[faceCurr][0]]
            coord2 = coordinate_list[faceDict[faceCurr][1]]
            coord3 = coordinate_list[faceDict[faceCurr][2]]
            file.write(str(coord1) + "\n")
            file.write(str(coord2) + "\n")
            file.write(str(coord3) + "\n")
            file.write("3 0 1 2\n")
            file.close()

        for faceToRemove in currRegions_Faces:
            if faceDict[faceToRemove] != None:
                removedFace = faceDict.pop(faceToRemove)

        for key, container in node_neighbour_nodes.copy().items():
            for elem in container.copy():
                if elem in visitedNodes:
                    node_neighbour_nodes[key].remove(elem)
            if key in visitedNodes:
                node_neighbour_nodes.pop(key)

        i += 1

    setOfUsedFaces = set()

    for usedFaceSet in region_faces_list:
        setOfUsedFaces = setOfUsedFaces.union(usedFaceSet)

    for usedFace in setOfUsedFaces:
        faceDictAll.pop(usedFace)

    try:
        dirName = output_folder + "\\" + "REST"
        os.mkdir(dirName)
    except FileExistsError:
        print("Directory already exists, continue on as normal")
    except:
        exit("Couldn't create directory: " + dirName + ". Restart program with admin rights and check given input and output folder locations. ")

    for faceRestCurr in faceDictAll:
        filename = output_folder + "\\" + "REST" + "\\" + str(faceRestCurr) + ".ply"
        file = open(filename, 'w')
        print("Created file: " + filename)
        file.write("ply\n")
        file.write("format ascii 1.0\n")
        file.write("comment VCGLIB generated\n")
        file.write("element vertex 3\n")
        file.write("property float x\n")
        file.write("property float y\n")
        file.write("property float z\n")
        file.write("element face 1\n")
        file.write("property list uchar int vertex_indices\n")
        file.write("end_header\n")
        coord1 = coordinate_list[faceDict[faceRestCurr][0]]
        coord2 = coordinate_list[faceDict[faceRestCurr][1]]
        coord3 = coordinate_list[faceDict[faceRestCurr][2]]
        file.write(str(coord1) + "\n")
        file.write(str(coord2) + "\n")
        file.write(str(coord3) + "\n")
        file.write("3 0 1 2\n")
        file.close()


if __name__ == '__main__':
    readPly()
    createAuxstruct()
    promptsList, nodeList = promptDivisions()
    adjacentNodes()
    traverseNodes(promptsList, nodeList)
    print("Program finished, check directory")
