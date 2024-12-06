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
                f.write(struct.pack(">Q", 0))
                f.write(struct.pack(">Q", self.next_block_id))
                f.write(b'\x00' * (HEADER_SIZE - len(MAGIC_NUMBER) - 2 * 8))

            self.index_file = filename
            print(f"Created index file {filename}")

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
            f.seek(HEADER_SIZE)
            node_data = struct.pack(">Q", node_id)
            node_data += struct.pack(">Q", 0)
            node_data += struct.pack(">Q", 1)
            node_data += struct.pack(">Q", key)
            node_data += struct.pack(">Q", value)
            node_data += b'\x00' * 160
            node_data += b'\x00' * (NODE_SIZE - len(node_data))

            f.write(node_data)

        self.root_id = node_id
        print(f"Root node created with key: {key}, value: {value}")

    def insert_into_node(self, node_id, key, value):
        with open(self.index_file, 'r+b') as f:
            f.seek(HEADER_SIZE + node_id * NODE_SIZE)
            node_data = f.read(NODE_SIZE)

            num_keys = struct.unpack(">Q", node_data[16:24])[0]

            if num_keys < KEYS_PER_NODE:
                self.insert_into_non_full_node(node_id, key, value, node_data)
            else:
                self.split_node(node_id, key, value)

    def insert_into_non_full_node(self, node_id, key, value, node_data):
        num_keys = struct.unpack(">Q", node_data[16:24])[0]
        keys = [struct.unpack(">Q", node_data[24 + i * 8:32 + i * 8])[0]
                for i in range(num_keys)]
        values = [struct.unpack(
            ">Q", node_data[152 + i * 8:160 + i * 8])[0] for i in range(num_keys)]

        for i in range(num_keys):
            if key < keys[i]:
                keys.insert(i, key)
                values.insert(i, value)
                break
        else:
            keys.append(key)
            values.append(value)

        new_node_data = struct.pack(">Q", node_id)
        new_node_data += struct.pack(">Q", 0)
        new_node_data += struct.pack(">Q", len(keys))
        for i in range(len(keys)):
            new_node_data += struct.pack(">Q", keys[i])
            new_node_data += struct.pack(">Q", values[i])
        new_node_data += b'\x00' * 160
        new_node_data += b'\x00' * (NODE_SIZE - len(new_node_data))

        with open(self.index_file, 'r+b') as f:
            f.seek(HEADER_SIZE + node_id * NODE_SIZE)
            f.write(new_node_data)

    def split_node(self, node_id, key, value):
        print(f"Splitting node with ID: {node_id}")
        with open(self.index_file, 'r+b') as f:
            f.seek(HEADER_SIZE + node_id * NODE_SIZE)
            node_data = f.read(NODE_SIZE)

            num_keys = struct.unpack(">Q", node_data[16:24])[0]
            keys = [struct.unpack(">Q", node_data[24 + i * 8:32 + i * 8])[0]
                    for i in range(num_keys)]
            values = [struct.unpack(
                ">Q", node_data[152 + i * 8:160 + i * 8])[0] for i in range(num_keys)]

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
                f.seek(HEADER_SIZE + left_node_id * NODE_SIZE)
                new_node_data = struct.pack(">Q", left_node_id)
                new_node_data += struct.pack(">Q", 0)
                new_node_data += struct.pack(">Q", len(left_keys))
                for i in range(len(left_keys)):
                    new_node_data += struct.pack(">Q", left_keys[i])
                    new_node_data += struct.pack(">Q", left_values[i])
                new_node_data += b'\x00' * 160
                new_node_data += b'\x00' * (NODE_SIZE - len(new_node_data))
                f.write(new_node_data)

            right_node_id = self.next_block_id
            self.next_block_id += 1
            with open(self.index_file, 'r+b') as f:
                f.seek(HEADER_SIZE + right_node_id * NODE_SIZE)
                new_node_data = struct.pack(">Q", right_node_id)
                new_node_data += struct.pack(">Q", 0)
                new_node_data += struct.pack(">Q", len(right_keys))
                for i in range(len(right_keys)):
                    new_node_data += struct.pack(">Q", right_keys[i])
                    new_node_data += struct.pack(">Q", right_values[i])
                new_node_data += b'\x00' * 160
                new_node_data += b'\x00' * (NODE_SIZE - len(new_node_data))
                f.write(new_node_data)

            middle_key = combined[mid][0]
            self.create_root_node(middle_key, 0)

    def search(self, key):
        if self.index_file is None:
            print("No index file is open.")
            return

        with open(self.index_file, 'r+b') as f:
            f.seek(HEADER_SIZE)
            node_data = f.read(NODE_SIZE)
            num_keys = struct.unpack(">Q", node_data[16:24])[0]

            keys = [struct.unpack(">Q", node_data[24 + i * 8:32 + i * 8])[0]
                    for i in range(num_keys)]
            if key in keys:
                index = keys.index(key)
                print(f"Found key: {key}, value: {
                      node_data[152 + index * 8:160 + index * 8]}")
            else:
                print(f"Key {key} not found")

    def quit(self):
        print("Exiting the program.")
        exit()

    def menu(self):
        while True:
            print("\nMenu:")
            print("1. Create a new index file (create)")
            print("2. Insert a key/value pair (insert)")
            print("3. Search for a key (search)")
            print("4. Quit (quit)")

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
            elif command == "quit" or command == "4":
                self.quit()
            else:
                print("Invalid command.")


if __name__ == "__main__":
    btree = BTree()
    btree.menu()
