def neighboring_node_faces(nodes, faces, node_face):
    # node contain nodes' face definitions and also can store relative position of the nodes in faces
    nodes[node_face] = []

    for face in faces:
        # check if node is in face
        if nodes[face[0]] or nodes[face[1]]:
            nodes[node_face].append(face)
    return nodes
