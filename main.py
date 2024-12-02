import os
import struct

MAGIC_NUMBER = b'4337PRJ3'
HEADER_SIZE = 512


class BTree:
    def __init__(self):
        self.index_file = None
        self.root_id = 0
        self.next_block_id = 1

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

        print(f"Created index file {filename}")

    def quit(self):
        print("Exiting the program.")
        exit()


if __name__ == "__main__":
    btree = BTree()
    filename = input("Enter the index file name: ").strip()
    btree.create(filename)
