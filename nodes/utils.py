def get_link(socket):
    """
    Returns the link if this socket is linked, None otherwise.
    All reroute nodes between this socket and the next non-reroute node are skipped.
    Muted nodes are ignored.
    """

    if not socket.is_linked:
        return None

    link = socket.links[0]

    while link.from_node.bl_idname == "NodeReroute" or link.from_node.mute:
        node = link.from_node

        if node.mute:
            if node.internal_links:
                # Only nodes defined in C can have internal_links in Blender
                links = node.internal_links[0].from_socket.links
                if links:
                    link = links[0]
                else:
                    return None
            else:
                if not link.from_socket.bl_idname.startswith("LuxCoreSocket") or not node.inputs:
                    return None

                # We can't define internal_links, so try to make up a link that makes sense.
                found_internal_link = False

                for input_socket in node.inputs:
                    if input_socket.links and link.from_socket.is_allowed_input(input_socket):
                        link = input_socket.links[0]
                        found_internal_link = True
                        break

                if not found_internal_link:
                    return None
        else:
            # Reroute node
            if node.inputs[0].is_linked:
                link = node.inputs[0].links[0]
            else:
                # If the left-most reroute has no input, it is like self.is_linked == False
                return None

    return link