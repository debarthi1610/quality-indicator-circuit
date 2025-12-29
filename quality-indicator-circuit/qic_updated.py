from qiskit import QuantumCircuit
from typing import List, Optional
from collections import defaultdict
from math import ceil


class QIC():

    def __init__(self,
                 circuits: List[QuantumCircuit],
                 reduce_by_ratio: Optional[bool]=True,
                 gate_2q: Optional[str]='cz',
                 insert_barriers: Optional[bool]=False
                ):
        self.circuits = circuits
        self.reduce_by_ratio = reduce_by_ratio
        self.gate_2q = gate_2q
        self.insert_barriers = insert_barriers


    def _construct_qic(self, circ: QuantumCircuit) -> QuantumCircuit:
        """
            This function constructs the QIC for an individual circuit
        """

        # first get the original circuit structure
        cnot_count_per_pair = defaultdict(int)
        for idx, (instr, qargs, cargs) in enumerate(circ.data):
            if instr.num_qubits == 2:
                control_qubit = circ.find_bit(qargs[0]).index
                target_qubit = circ.find_bit(qargs[1]).index
                qubit_pair = tuple(sorted([control_qubit, target_qubit]))
                print("qubit pair is",qubit_pair)
                cnot_count_per_pair[qubit_pair] += 1

        print("cnot_count_per_pair is",cnot_count_per_pair)

        # reduce the circuit by ratio
        if self.reduce_by_ratio:
            min_2q_count = min(cnot_count_per_pair.values())
            print("min_2q_count is",min_2q_count)
            for pair in cnot_count_per_pair.keys():
                cnot_count_per_pair[pair] = ceil(cnot_count_per_pair[pair]/min_2q_count)

        # create QIC
        qic = QuantumCircuit(circ.num_qubits)
        qic.h(range(circ.num_qubits))

        for pair in cnot_count_per_pair.keys():
            if self.gate_2q == 'cx':
                for _ in range(cnot_count_per_pair[pair]):
                    qic.cx(pair[0], pair[1])
                    if len(cnot_count_per_pair) > 1 and self.insert_barriers:
                        qic.barrier(pair[0], pair[1])
            elif self.gate_2q == 'ecr':
                for _ in range(cnot_count_per_pair[pair]):
                    qic.ecr(pair[0], pair[1])
            elif self.gate_2q == 'cz':
                for _ in range(cnot_count_per_pair[pair]):
                    qic.cz(pair[0], pair[1])
            else:
                raise ValueError(f'2-qubit gate {self.gate_2q} not recognized')

        qic.h(range(circ.num_qubits))

        # insert measurement if the original circuit has it
        if circ.num_clbits != 0:
            qic.measure_all()
        
        return qic


    def construct_qic(self):
        qic_circuits = [self._construct_qic(circ) for circ in self.circuits]
        return qic_circuits

