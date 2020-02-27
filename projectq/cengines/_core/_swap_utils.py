def return_swap_depth(swaps):
    """
    Returns the circuit depth to execute these swaps.

    Args:
        swaps(list of tuples): Each tuple contains two integers representing
                               the two IDs of the qubits involved in the
                               Swap operation
    Returns:
        Circuit depth to execute these swaps.
    """
    depth_of_qubits = dict()
    for qb0_id, qb1_id in swaps:
        if qb0_id not in depth_of_qubits:
            depth_of_qubits[qb0_id] = 0
        if qb1_id not in depth_of_qubits:
            depth_of_qubits[qb1_id] = 0
        max_depth = max(depth_of_qubits[qb0_id], depth_of_qubits[qb1_id])
        depth_of_qubits[qb0_id] = max_depth + 1
        depth_of_qubits[qb1_id] = max_depth + 1
    return max(list(depth_of_qubits.values()) + [0])
