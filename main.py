import os
import struct

MAGIC_NUMBER = b'4337PRJ3'
HEADER_SIZE = 512
NODE_SIZE = 512
KEYS_PER_NODE = 19
VALUES_PER_NODE = 19
CHILDREN_PER_NODE = 20


class BTree:
    def __init__(self):
        self.index_file = None
        self.root_id = 0
        self.next_block_id = 1
        self.nodes_in_memory = {}

    def create(self, filename):
        if os.path.exists(filename):
            overwrite = input(
                f"File {filename} already exists. Overwrite? (y/n): ").strip().lower()
            if overwrite != 'y':
                print(f"Command aborted. {filename} was not overwritten.")
                return

        with open(filename, 'wb') as f:
            f.write(MAGIC_NUMBER)
            f.write(struct.pack(">Q", 0))  # Root ID (0 if empty)
            f.write(struct.pack(">Q", self.next_block_id))  # Next Block ID
            # Fill remaining space
            f.write(b'\x00' * (HEADER_SIZE - len(MAGIC_NUMBER) - 2 * 8))

        self.index_file = filename
        print(f"Created index file {filename}")
        # Automatically open the file after creating it
        self.open(filename)

    def open(self, filename):
        try:
            if not os.path.exists(filename):
                print(f"Error: File {filename} does not exist.")
                return

            with open(filename, 'rb') as f:
                magic_number = f.read(len(MAGIC_NUMBER))
                if magic_number != MAGIC_NUMBER:
                    print(f"Error: Invalid file format.")
                    return

                f.seek(8)
                self.root_id = struct.unpack(">Q", f.read(8))[0]
                self.next_block_id = struct.unpack(">Q", f.read(8))[0]

            self.index_file = filename
            print(f"Opened index file {filename}")
        except Exception as e:
            print(f"Error opening file {filename}: {e}")

    def insert(self, key, value):
        if self.index_file is None:
            print("No index file is open.")
            return

        if self.root_id == 0:
            self.create_root_node(key, value)
        else:
            self.insert_into_node(self.root_id, key, value)

    def create_root_node(self, key, value, left_node_id=None, right_node_id=None):
        node_id = self.next_block_id
        self.next_block_id += 1

        with open(self.index_file, 'r+b') as f:
            f.seek(HEADER_SIZE + (node_id * NODE_SIZE))

            # Node ID and Parent ID (0 for the root)
            node_data = struct.pack(">Q", node_id)
            node_data += struct.pack(">Q", 0)  # Root node has no parent
            node_data += struct.pack(">Q", 1)  # One key in the root

            # Adding the middle key
            node_data += struct.pack(">Q", key)
            node_data += b'\x00' * ((KEYS_PER_NODE - 1)
                                    * 8)  # Pad remaining keys

            # Values
            node_data += struct.pack(">Q", value)
            # Pad remaining values
            node_data += b'\x00' * ((VALUES_PER_NODE - 1) * 8)

            # Add child pointers: the left and right nodes created during the split
            node_data += struct.pack(">Q", left_node_id if left_node_id else 0)
            node_data += struct.pack(">Q",
                                     right_node_id if right_node_id else 0)
            # Remaining child pointers
            node_data += b'\x00' * ((CHILDREN_PER_NODE - 2) * 8)

            # Ensure the node data is padded to NODE_SIZE
            node_data += b'\x00' * (NODE_SIZE - len(node_data))

            # Write the node to the file
            f.write(node_data)

        self.root_id = node_id
        print(f"Root node created with key: {key}, value: {value}")

    def insert_into_node(self, node_id, key, value):
        with open(self.index_file, 'r+b') as f:
            # Locate the node in the file
            f.seek(HEADER_SIZE + (node_id * NODE_SIZE))
            node_data = f.read(NODE_SIZE)

            if len(node_data) < NODE_SIZE:
                print(f"Error: Node data is too short.")
                return

            # Read the number of keys, keys, and values
            num_keys = struct.unpack(">Q", node_data[16:24])[0]
            keys = [struct.unpack(
                ">Q", node_data[24 + (i * 8):32 + (i * 8)])[0] for i in range(num_keys)]
            values = [struct.unpack(
                ">Q", node_data[176 + (i * 8):184 + (i * 8)])[0] for i in range(num_keys)]

            # Insert the new key-value pair in sorted order
            for i in range(num_keys):
                if key < keys[i]:
                    keys.insert(i, key)
                    values.insert(i, value)
                    break
            else:
                keys.append(key)
                values.append(value)

            num_keys += 1

            # Rebuild the node data
            new_node_data = struct.pack(">Q", node_id)  # Block ID
            new_node_data += struct.pack(">Q", 0)  # Parent ID
            # Updated number of keys
            new_node_data += struct.pack(">Q", num_keys)

            # Write updated keys
            for k in keys:
                new_node_data += struct.pack(">Q", k)
            new_node_data += b'\x00' * \
                ((KEYS_PER_NODE - num_keys) * 8)  # Pad remaining keys

            # Write updated values
            for v in values:
                new_node_data += struct.pack(">Q", v)
            new_node_data += b'\x00' * \
                ((VALUES_PER_NODE - num_keys) * 8)  # Pad remaining values

            # Preserve child pointers
            new_node_data += node_data[344:504]

            # Pad the node to NODE_SIZE
            new_node_data += b'\x00' * (NODE_SIZE - len(new_node_data))

            # Write back the updated node to the file
            f.seek(HEADER_SIZE + (node_id * NODE_SIZE))
            f.write(new_node_data)

    def split_node(self, node_id, key, value):
        print(f"Splitting node with ID: {node_id}")

        with open(self.index_file, 'r+b') as f:
            f.seek(HEADER_SIZE + (node_id * NODE_SIZE))
            node_data = f.read(NODE_SIZE)

        num_keys = struct.unpack(">Q", node_data[16:24])[0]
        keys = [struct.unpack(">Q", node_data[24 + (i * 8):32 + (i * 8)])[0]
                for i in range(num_keys)]
        values = [struct.unpack(
            ">Q", node_data[176 + (i * 8):184 + (i * 8)])[0] for i in range(num_keys)]

        # Insert new key-value pair
        keys.append(key)
        values.append(value)

        # Sort the keys and values
        combined = list(zip(keys, values))
        combined.sort(key=lambda x: x[0])

        mid = len(combined) // 2
        left_keys = [k for k, v in combined[:mid]]
        left_values = [v for k, v in combined[:mid]]
        right_keys = [k for k, v in combined[mid+1:]]
        right_values = [v for k, v in combined[mid+1:]]
        middle_key = combined[mid][0]

        left_node_id = self.next_block_id
        self.next_block_id += 1
        right_node_id = self.next_block_id
        self.next_block_id += 1

        # Write the left and right nodes
        self.write_node(left_node_id, left_keys, left_values, node_id)
        self.write_node(right_node_id, right_keys, right_values, node_id)

        # Create a new root node with the middle key
        self.create_root_node(middle_key, 0)

    def _write_node(self, node_id, keys, values, parent_id):
        with open(self.index_file, 'r+b') as f:
            f.seek(HEADER_SIZE + (node_id * NODE_SIZE))
            node_data = struct.pack(">Q", node_id)  # Block ID
            node_data += struct.pack(">Q", parent_id)  # Parent ID
            node_data += struct.pack(">Q", len(keys))  # Number of keys

            for k, v in zip(keys, values):
                node_data += struct.pack(">Q", k)
                node_data += struct.pack(">Q", v)

            # Initialize child pointers
            node_data += b'\x00' * 160

            # Pad the remaining space
            node_data += b'\x00' * (NODE_SIZE - len(node_data))
            f.write(node_data)

    def quit(self):
        print("Exiting the program.")
        exit()

    def load(self, filename):
        if self.index_file is None:
            print("No index file is open.")
            return

        try:
            print(f"Loading key-value pairs from {filename}...")
            with open(filename, 'r') as f:
                for line in f:
                    key, value = map(int, line.strip().split(","))
                    self.insert(key, value)
                    print(f"  Loaded Key: {key}, Value: {value}")
            print(f"Finished loading from {filename}.")
        except FileNotFoundError:
            print(f"File {filename} does not exist.")
        except Exception as e:
            print(f"Error loading file: {e}")

    def print_index(self):
        if self.index_file is None:
            print("No index file is open.")
            return

        if self.root_id == 0:
            print("The B-tree is empty.")
            return

        print("Key-Value Pairs in the Index:")

        def traverse_and_print(node_id, level=0):
            with open(self.index_file, 'r+b') as f:
                f.seek(HEADER_SIZE + (node_id * NODE_SIZE))
                node_data = f.read(NODE_SIZE)

                if len(node_data) < NODE_SIZE:
                    print(f"Error: Node {node_id} data is too short ({
                        len(node_data)} bytes). Skipping.")
                    return

                num_keys = struct.unpack(">Q", node_data[16:24])[0]
                keys = [struct.unpack(
                    ">Q", node_data[24 + (i * 8):32 + (i * 8)])[0] for i in range(num_keys)]
                values = [struct.unpack(
                    ">Q", node_data[176 + (i * 8):184 + (i * 8)])[0] for i in range(num_keys)]

                # Initialize an empty list for child pointers
                child_pointers = []
                for i in range(num_keys + 1):
                    child_pointer_offset = 344 + (i * 8)
                    # Ensure there is enough data before unpacking
                    if child_pointer_offset + 8 <= len(node_data):
                        child_pointer = struct.unpack(
                            ">Q", node_data[child_pointer_offset:child_pointer_offset + 8])[0]
                        child_pointers.append(child_pointer)
                    else:
                        print(f"Warning: Invalid child pointer offset for Node {
                            node_id}, skipping.")
                        break

                indent = "  " * level
                print(f"{indent}Node {node_id}:")
                for key, value in zip(keys, values):
                    print(f"{indent}  Key: {key}, Value: {value}")

                # Recursively print child nodes
                for child_id in child_pointers:
                    if child_id != 0:
                        traverse_and_print(child_id, level + 1)

        traverse_and_print(self.root_id)

    def extract(self, filename):
        if self.index_file is None:
            print("No index file is open.")
            return

        with open(self.index_file, 'r+b') as f:
            f.seek(HEADER_SIZE)
            node_data = f.read(NODE_SIZE)

            num_keys = struct.unpack(">Q", node_data[16:24])[0]
            keys = [struct.unpack(
                ">Q", node_data[24 + (i * 8):32 + (i * 8)])[0] for i in range(num_keys)]
            values = [struct.unpack(
                ">Q", node_data[176 + (i * 8):184 + (i * 8)])[0] for i in range(num_keys)]

            with open(filename, 'w') as out_file:
                for key, value in zip(keys, values):
                    out_file.write(f"{key},{value}\n")
            print(f"Extracted key-value pairs to {filename}")

    def menu(self):
        while True:
            print("\nMenu:")
            print("1. Create a new index file (create)")
            print("2. Insert a key/value pair (insert)")
            print("3. Search for a key (search)")
            print("4. Load key/value pairs from a file (load)")
            print("5. Print all key/value pairs (print)")
            print("6. Extract key/value pairs to a file (extract)")
            print("7. Quit (quit)")

            command = input("Enter command: ").strip().lower()

            if command == "create" or command == "1":
                filename = input("Enter the index file name: ").strip()
                self.create(filename)
            elif command == "insert" or command == "2":
                if self.index_file is None:
                    print("No index file is open.")
                    continue
                key = int(input("Enter key (unsigned integer): "))
                value = int(input("Enter value (unsigned integer): "))
                self.insert(key, value)
            elif command == "search" or command == "3":
                if self.index_file is None:
                    print("No index file is open.")
                    continue
                key = int(input("Enter key (unsigned integer): "))
                self.search(key)
            elif command == "load" or command == "4":
                filename = input("Enter the filename to load: ").strip()
                self.load(filename)
            elif command == "print" or command == "5":
                self.print_index()
            elif command == "extract" or command == "6":
                filename = input("Enter the filename to extract: ").strip()
                self.extract(filename)
            elif command == "quit" or command == "7":
                self.quit()
            else:
                print("Invalid command.")


if __name__ == "__main__":
    btree = BTree()
    btree.menu()
