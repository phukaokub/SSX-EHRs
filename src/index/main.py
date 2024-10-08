import hashlib
import time
from concurrent.futures import ThreadPoolExecutor

def hash_data(data):
    """Hash a piece of data using SHA-256."""
    return hashlib.sha256(data.encode()).hexdigest()

class Node:
    def __init__(self, hash_value, left=None, right=None):
        self.hash_value = hash_value
        self.left = left
        self.right = right

class MerkleTree:
    def __init__(self, leaves):
        """Initialize the Merkle Tree with leaf nodes."""
        self.leaves = [hash_data(leaf) for leaf in leaves]
        self.root = self._build_tree(self.leaves)

    def _build_tree(self, leaf_hashes):
        """Build the Merkle Tree and return the root node."""
        nodes = [Node(h) for h in leaf_hashes]
        while len(nodes) > 1:
            new_nodes = []
            for i in range(0, len(nodes), 2):
                left = nodes[i]
                right = nodes[i + 1] if i + 1 < len(nodes) else left
                parent_hash = hash_data(left.hash_value + right.hash_value)
                new_nodes.append(Node(parent_hash, left, right))
            nodes = new_nodes
        return nodes[0] if nodes else None

    def get_root(self):
        """Get the root hash of the Merkle Tree."""
        return self.root.hash_value if self.root else None

    def search(self, leaf):
        """Search for a leaf in the Merkle Tree and return whether it exists."""
        leaf_hash = hash_data(leaf)
        return self._search(self.root, leaf_hash) if self.root else False

    def _search(self, node, leaf_hash):
        """Recursively search the Merkle Tree for the given leaf hash."""
        if node is None:
            return False
        if node.hash_value == leaf_hash:
            return True
        # Search in both left and right subtrees
        return self._search(node.left, leaf_hash) or self._search(node.right, leaf_hash)

def concurrent_searches(tree, num_searches):
    """Perform concurrent searches on the Merkle Tree."""
    leaf = "EncEHR500"  # Example search target
    with ThreadPoolExecutor(max_workers=500) as executor:
        futures = [executor.submit(tree.search, leaf) for _ in range(num_searches)]
        results = [f.result() for f in futures]
        return sum(results)  # Total number of successful searches

def throughput_test(num_leaves, search_requests, num_seqs=5):
    """Run the throughput test on the Merkle Tree and save results to a file."""
    print(f"Creating Merkle Tree with {num_leaves} nodes...")
    start_time = time.time()
    
    # Generate leaves
    leaves = [f"EncEHR{i}" for i in range(num_leaves)]  # List of leaf data

    # Create the Merkle Tree using the generated leaves
    tree = MerkleTree(leaves)
    creation_time = time.time() - start_time
    print(f"Tree created in {creation_time:.2f} seconds.")
    
    # Open a file to write the results
    with open("index.txt", "w") as file:
        file.write('{:7} {:18}\n'.format(
            'request', 'tps'
        ))

        for num_requests in search_requests:
            total_requests = 0
            total_duration = 0

            for _ in range(num_seqs):
                print(f"Running throughput test with {num_requests} concurrent searches...")
                start_time = time.time()
                successful_searches = concurrent_searches(tree, num_requests)
                duration = time.time() - start_time
                
                total_requests += num_requests
                total_duration += duration
                
            tps = total_requests / total_duration
            
            out1 = str(num_requests).zfill(6)
            out2 = str(format(tps, '.16f'))

            file.write(f'{out1}  {out2}\n')

            print(f"Processed {num_requests} concurrent searches ({num_seqs} sequences) in {total_duration:.2f} seconds.")
            print(f"Throughput: {tps:.2f} transactions per second (TPS)")
            print(f"Successful searches: {successful_searches}/{num_requests}\n")

if __name__ == "__main__":
    num_leaves = 1000000  # 1M nodes
    search_requests = [100, 500, 1000, 2000, 4000, 8000, 16000, 32000, 64000, 128000, 256000, 512000]  # Increasing concurrent search requests
    
    throughput_test(num_leaves, search_requests)
