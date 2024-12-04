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
                return

        with open(filename, 'wb') as f:
            f.write(MAGIC_NUMBER)
            f.write(struct.pack(">Q", 0))
            f.write(struct.pack(">Q", self.next_block_id))
            f.write(b'\x00' * (HEADER_SIZE - len(MAGIC_NUMBER) - 2 * 8))

        self.index_file = filename
        print(f"Created index file {filename}")

    def insert(self, key, value):
        print(f"Inserting key: {key}, value: {value}")

    def search(self, key):
        print(f"Searching for key: {key}")

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

            if command == "create":
                filename = input("Enter the index file name: ").strip()
                self.create(filename)
            elif command == "insert":
                if self.index_file is None:
                    print("No index file is open.")
                    continue
                key = int(input("Enter key (unsigned integer): "))
                value = int(input("Enter value (unsigned integer): "))
                self.insert(key, value)
            elif command == "search":
                if self.index_file is None:
                    print("No index file is open.")
                    continue
                key = int(input("Enter key (unsigned integer): "))
                self.search(key)
            elif command == "quit":
                self.quit()
            else:
                print("Invalid command.")


if __name__ == "__main__":
    btree = BTree()
    btree.menu()
