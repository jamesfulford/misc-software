SELECT
    ntm.node_map,
    d.native_id,
    d.name
FROM
    network_tree nt
    INNER JOIN network_tree_map ntm ON ntm.node_id = nt.id
    LEFT JOIN device d ON nt.device_id = d.id
    LEFT JOIN device_type dt ON dt.id = d.type_id
WHERE
    ntm.node_map LIKE '%.:NODE_ID.%';
