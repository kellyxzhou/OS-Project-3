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
        if not os.path.exists(filename):
            print(f"File {filename} does not exist.")
            return

        with open(filename, 'rb') as f:
            magic_number = f.read(len(MAGIC_NUMBER))
            if magic_number != MAGIC_NUMBER:
                print(f"Invalid file format.")
                return

            f.seek(8)
            self.root_id = struct.unpack(">Q", f.read(8))[0]
            self.next_block_id = struct.unpack(">Q", f.read(8))[0]

        self.index_file = filename
        print(f"Opened index file {filename}")

    def insert(self, key, value):
        if self.index_file is None:
            print("No index file is open.")
            return

        if self.root_id == 0:
            self.create_root_node(key, value)
        else:
            self.insert_into_node(self.root_id, key, value)

    def create_root_node(self, key, value):
        node_id = self.next_block_id
        self.next_block_id += 1

        with open(self.index_file, 'r+b') as f:
            f.seek(HEADER_SIZE + (node_id * NODE_SIZE))

            # Block ID, Parent ID, Number of Keys
            node_data = struct.pack(">Q", node_id)  # Block ID
            node_data += struct.pack(">Q", 0)  # Parent ID (0 for root)
            node_data += struct.pack(">Q", 1)  # Number of keys

            # Initialize Keys (19 keys)
            keys = [key] + [0] * (KEYS_PER_NODE - 1)
            for k in keys:
                node_data += struct.pack(">Q", k)

            # Initialize Values (19 values)
            values = [value] + [0] * (VALUES_PER_NODE - 1)
            for v in values:
                node_data += struct.pack(">Q", v)

            # Initialize Child Pointers (20 pointers)
            child_pointers = [0] * CHILDREN_PER_NODE
            for c in child_pointers:
                node_data += struct.pack(">Q", c)

            # Pad remaining space to NODE_SIZE
            node_data += b'\x00' * (NODE_SIZE - len(node_data))

            f.write(node_data)

        self.root_id = node_id
        print(f"Root node created with key: {key}, value: {value}")

    def insert_into_node(self, node_id, key, value):
        with open(self.index_file, 'r+b') as f:
            # Locate the node in the file
            f.seek(HEADER_SIZE + (node_id * NODE_SIZE))
            node_data = f.read(NODE_SIZE)

            # If the node data is too short, return an error
            if len(node_data) < NODE_SIZE:
                print(f"Error: Node data is too short.")
                return

            # Read the number of keys, keys, and values
            num_keys = struct.unpack(">Q", node_data[16:24])[0]
            keys = [struct.unpack(">Q", node_data[24 + (i * 8):32 + (i * 8)])[0]
                    for i in range(num_keys)]
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
            keys = [struct.unpack(
                ">Q", node_data[24 + (i * 8):32 + (i * 8)])[0] for i in range(num_keys)]
            values = [struct.unpack(
                ">Q", node_data[176 + (i * 8):184 + (i * 8)])[0] for i in range(num_keys)]

            keys.append(key)
            values.append(value)
            combined = list(zip(keys, values))
            combined.sort(key=lambda x: x[0])

            mid = len(combined) // 2
            left_keys = [k for k, v in combined[:mid]]
            left_values = [v for k, v in combined[:mid]]
            right_keys = [k for k, v in combined[mid:]]
            right_values = [v for k, v in combined[mid:]]

            left_node_id = self.next_block_id
            self.next_block_id += 1
            with open(self.index_file, 'r+b') as f:
                f.seek(HEADER_SIZE + (left_node_id * NODE_SIZE))
                new_node_data = struct.pack(">Q", left_node_id)
                # Parent ID (to be updated later)
                new_node_data += struct.pack(">Q", 0)
                new_node_data += struct.pack(">Q", len(left_keys))
                for i in range(len(left_keys)):
                    new_node_data += struct.pack(">Q", left_keys[i])
                    new_node_data += struct.pack(">Q", left_values[i])
                # Child pointers (to be updated later)
                new_node_data += b'\x00' * 160
                new_node_data += b'\x00' * \
                    (NODE_SIZE - len(new_node_data))  # Fill remaining bytes
                f.write(new_node_data)

            right_node_id = self.next_block_id
            self.next_block_id += 1
            with open(self.index_file, 'r+b') as f:
                f.seek(HEADER_SIZE + (right_node_id * NODE_SIZE))
                new_node_data = struct.pack(">Q", right_node_id)
                # Parent ID (to be updated later)
                new_node_data += struct.pack(">Q", 0)
                new_node_data += struct.pack(">Q", len(right_keys))
                for i in range(len(right_keys)):
                    new_node_data += struct.pack(">Q", right_keys[i])
                    new_node_data += struct.pack(">Q", right_values[i])
                # Child pointers (to be updated later)
                new_node_data += b'\x00' * 160
                new_node_data += b'\x00' * \
                    (NODE_SIZE - len(new_node_data))  # Fill remaining bytes
                f.write(new_node_data)

            middle_key = combined[mid][0]
            self.create_root_node(middle_key, 0)

    def search(self, key):
        if self.index_file is None:
            print("No index file is open.")
            return

        current_node_id = self.root_id

        while current_node_id != 0:
            with open(self.index_file, 'r+b') as f:
                f.seek(HEADER_SIZE + (current_node_id * NODE_SIZE))
                node_data = f.read(NODE_SIZE)

                # Read number of keys, keys, and values
                num_keys = struct.unpack(">Q", node_data[16:24])[0]
                keys = [struct.unpack(
                    ">Q", node_data[24 + (i * 8):32 + (i * 8)])[0] for i in range(num_keys)]
                values = [struct.unpack(
                    ">Q", node_data[176 + (i * 8):184 + (i * 8)])[0] for i in range(num_keys)]

                # Check if the key exists in this node
                for i in range(num_keys):
                    if keys[i] == key:
                        print(f"Found key: {key}, value: {values[i]}")
                        return

                # Determine the next child node to search
                for i in range(num_keys):
                    if key < keys[i]:
                        current_node_id = struct.unpack(
                            ">Q", node_data[344 + (i * 8):352 + (i * 8)])[0]
                        break
                else:
                    current_node_id = struct.unpack(
                        ">Q", node_data[344 + (num_keys * 8):352 + (num_keys * 8)])[0]

        print(f"Key {key} not found")

    def quit(self):
        print("Exiting the program.")
        exit()

    def load(self, filename):
        if self.index_file is None:
            print("No index file is open.")
            return

        if not os.path.exists(filename):
            print(f"File {filename} does not exist.")
            return

        with open(filename, 'r') as f:
            for line in f:
                try:
                    key, value = map(int, line.strip().split(','))
                    self.insert(key, value)
                except ValueError:
                    print(f"Invalid line in file: {line.strip()}")
                    continue
        print(f"Loaded key-value pairs from {filename}")

    def print_index(self):
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

            print("Key-Value Pairs in the Index:")
            for key, value in zip(keys, values):
                print(f"Key: {key}, Value: {value}")

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
