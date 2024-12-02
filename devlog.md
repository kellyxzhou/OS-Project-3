### Devlog Entry - [2024-12-02, 11:41 AM]

The goal is to create an interactive program that manages index files using a B-tree structure. The project will involve handling file creation, insertion of key-value pairs, searching for keys, and printing/extracting data. There are specific file and node structures, detailed in the project description.

The B-tree itself will need to be managed through blocks in the file, with each block being 512 bytes. I’m thinking of implementing the project in Python because it’s relatively easy to handle file I/O, and I’m familiar with it. I will need to ensure the program can handle various user commands like creating a new index file, opening an existing one, inserting data, and so on. The index file will need to store a magic number, root node id, and next block id in the header, and I will also need to manage node splitting and child pointers in the B-tree.

I'm starting by setting up the basic file handling logic to create an index file. The focus is on implementing the create function that writes the initial header structure. I've also added a check to handle file overwriting, allowing the user to confirm before overwriting an existing file.
