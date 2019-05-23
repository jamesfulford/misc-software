import os
from difflib import unified_diff

from lxml import etree

from css.release import constants as c
from css.release import utilities as u
from css.release.current import post


SQL = open(os.path.join(
    c.TREE_QUERY_PATH,
    "tree_dump.sql"
)).read()


def dump_tree(main_device_node_id, dump_path):
    # Query and get etree
    try:
        root = get_etree(main_device_node_id)
    except Exception as e:
        post.log.exception(e)
        return False

    # Make a string
    tree = etree.tostring(
        root,
        pretty_print=True,
        xml_declaration=True
    )

    # Write to file
    with open(dump_path, "w") as phile:
        phile.write(tree)

    # Return etree
    return root


def make_diff(before_path, after_path, output_path):
    before_text = open(before_path).readlines()
    after_text = open(after_path).readlines()
    output_text = unified_diff(
        before_text,
        after_text,
        os.path.basename(before_path),
        os.path.basename(after_path)
    )
    open(output_path, "w").writelines(output_text)


def add_rebuild(main_device_node_id):
    """
    If file does not already exist, dump the network tree
    from SitePortal database.
    """
    from css.release.process.alarm_clue.scrubbers import node_detail
    rebuild_folder = os.path.join(
        post.paths["TREE_CACHE_PATH"],
        str(main_device_node_id)
    )
    before_xml = os.path.join(rebuild_folder, "before.xml")
    after_rebuild_xml = os.path.join(rebuild_folder, "after_rebuild.xml")
    after_rebuild_diff = os.path.join(rebuild_folder, "after_rebuild.diff")
    after_fresh_build_xml = os.path.join(
        rebuild_folder, "after_fresh_build.xml"
    )
    after_fresh_build_diff = os.path.join(
        rebuild_folder, "after_fresh_build.diff"
    )
    control_json = os.path.join(rebuild_folder, "control.json")
    details_json = os.path.join(rebuild_folder, "details.json")

    # Folder does not exist, first time around
    if not os.path.exists(rebuild_folder):
        os.makedirs(rebuild_folder)

    # Before xml
    if not os.path.exists(before_xml):
        dump_tree(main_device_node_id, before_xml)

    # Control json
    if not os.path.exists(control_json):
        u.cache_results(
            {
                "after_rebuild_node_id": None,
                "after_fresh_build_node_id": None,
            },
            control_json
        )

    # Details json
    if not os.path.exists(details_json):

        details = node_detail(main_device_node_id),
        details = details[0],
        u.cache_results(
            details,
            details_json
        )

    # Rebuild
    control = u.load_cached_data(control_json)
    if control["after_rebuild_node_id"] and not os.path.exists(
        after_rebuild_xml
    ):
        dump_tree(
            control["after_rebuild_node_id"], after_rebuild_xml
        )
        make_diff(before_xml, after_rebuild_xml, after_rebuild_diff)

    # Fresh Build
    if control["after_fresh_build_node_id"] and not os.path.exists(
        after_fresh_build_xml
    ):
        dump_tree(
            control["after_fresh_build_node_id"], after_fresh_build_xml
        )
        make_diff(before_xml, after_fresh_build_xml, after_fresh_build_diff)

    return True


def sort_subelements(e):
    e[:] = sorted(e, key=lambda x: x.attrib["native_id"])
    map(sort_subelements, e)
    return e


def get_etree(node_id, **kwargs):

    # @u.memoize
    def make_element(tree_node):
        """
        When memoized, this function must remain inside get_etree so that
            the memoization cache does not carry over between successive
            runs
        """
        tree_node["node_map"] = "|".join(map(
            lambda x: x.rjust(12),
            tree_node["node_map"].strip(".").split(".")
        ))
        tree_node["native_id"] = tree_node["native_id"] if \
            tree_node["native_id"] else ""
        tree_node["name"] = tree_node["name"] if \
            tree_node["name"] else ""
        node = etree.Element('node', **tree_node)
        return node

    tree_nodes = u.run_query(SQL, NODE_ID=node_id, **kwargs)
    tree_nodes = map(make_element, tree_nodes)

    tree_nodes.sort(key=lambda x: len(x.attrib["node_map"]))
    root = tree_nodes[0]

    node_map_to_node = dict(((x.attrib["node_map"], x) for x in tree_nodes))

    def add_to_tree(tuple_node_map):
        if tuple_node_map == root.attrib["node_map"]:
            return root
        parent_node_map = "|".join(tuple_node_map.split("|")[:-1])
        node_map_to_node[parent_node_map].append(
            node_map_to_node[tuple_node_map]
        )
        return add_to_tree(parent_node_map)

    map(add_to_tree, map(lambda x: x.attrib["node_map"], tree_nodes))

    for tm in tree_nodes:
        del tm.attrib["node_map"]
        for k, v in tm.attrib.items():
            tm.attrib[k] = unicode(v).encode("ascii", errors="ignore")

    return sort_subelements(root)
