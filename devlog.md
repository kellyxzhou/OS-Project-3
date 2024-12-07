### Devlog Entry - [2024-12-02, 11:41 AM]

The goal is to create an interactive program that manages index files using a B-tree structure. The project will involve handling file creation, insertion of key-value pairs, searching for keys, and printing/extracting data. There are specific file and node structures, detailed in the project description.

The B-tree itself will need to be managed through blocks in the file, with each block being 512 bytes. I’m thinking of implementing the project in Python because it’s relatively easy to handle file I/O, and I’m familiar with it. I will need to ensure the program can handle various user commands like creating a new index file, opening an existing one, inserting data, and so on. The index file will need to store a magic number, root node id, and next block id in the header, and I will also need to manage node splitting and child pointers in the B-tree.

I'm starting by setting up the basic file handling logic to create an index file. The focus is on implementing the create function that writes the initial header structure. I've also added a check to handle file overwriting, allowing the user to confirm before overwriting an existing file.

### Devlog Entry - [2024-12-03, 10:00 AM]

**Thoughts so far:**
So far, I’ve successfully set up the basic file structure for the B-tree index file, allowing for the creation of a new file and handling the overwrite scenario gracefully. I’ve also added a simple menu system to allow the user to choose between creating a new index file or quitting the program. At this point, the program can create and open a file but doesn’t yet handle inserting or searching for data, as those will be implemented in future commits.

I’m starting to think about how to handle the actual B-tree operations, like inserting keys and splitting nodes. Once the B-tree is functioning, the file will need to store key-value pairs and manage nodes efficiently, so I’ll need to focus on how to implement that next.

**Plan for this session:**
- Start thinking through and planning the logic for inserting key-value pairs into the B-tree. I need to understand how the node structure works, how to split nodes when they exceed the max number of keys, and how to manage child pointers.
- Implement the insert operation for adding key-value pairs into the index file.
- Ensure the structure allows for handling multiple nodes, as the B-tree will need to balance itself when a node overflows.
- Consider how the search operation will work, especially in terms of traversing through nodes based on key comparisons.
- Once the insert operation is in place, I will be able to test the functionality by inserting a few keys and verifying their storage in the index file.

The immediate goal is to implement the `insert` method and lay the foundation for handling the B-tree structure. Once the insert operation works, I will start implementing the `search` functionality.

### Devlog Entry - [2024-12-04, 2:00 AM]

**Thoughts so far:**
I started implementing the logic for inserting key-value pairs into the B-tree. I added functionality to create the root node when the first key-value pair is inserted. The split_node function is a placeholder for when a node exceeds its capacity, which will be implemented in future commits. For now, the program creates the root node when inserting the first pair and prints a message confirming the action.

The insert method checks if the root exists and creates it if necessary. The logic for handling node splitting will come later once the tree grows and nodes fill up.

**Plan for this session:**
- Implement logic to insert key-value pairs into the root node and handle node splitting.
- Define the structure of nodes more clearly, including key/value pairs and child pointers.
- Prepare for testing by inserting multiple key-value pairs and verifying the root creation and data insertion.
- Expand search functionality later, as the tree structure grows.

### Devlog Entry - [2024-12-04, 3:00 PM]

**Thoughts so far:**
I began implementing the logic for inserting key-value pairs into the B-tree. I introduced methods for inserting into nodes, handling node splits when the node is full, and searching for keys. Although the node splitting and searching are not fully implemented, I have laid the groundwork for handling node splits when the node is full and handling a basic search for the root node.

I also updated the insert method to insert key-value pairs into the root node and added the method to insert into non-full nodes.

**Plan for this session:**
Implement the actual logic for node splitting, handling when a node exceeds its capacity.
Expand the search functionality to handle a multi-level B-tree traversal.
Add more functionality to test and validate the node insertion and search operations.

### Devlog Entry - [2024-12-04, 7:08 PM]

**Thoughts so far:**
Worked on improving the user interaction by addressing an issue where valid commands were being rejected as "invalid" due to extra spaces or incorrect handling of input. I updated the menu method to handle user inputs more effectively by stripping spaces and converting input to lowercase. I also allowed the user to input either the full command name (e.g., create, insert, search, quit) or the numeric option associated with each command (e.g., 1, 2, 3, 4), which adds flexibility to the interface.

The program now correctly handles all commands and performs the appropriate actions when the user selects them. There is still some work to do to handle more complex operations like node splitting and multi-level B-tree traversal, but the basic structure is in place.

**Plan for this session:**
Refine the input handling for the menu commands to ensure correct processing.
Test the create, insert, and search operations to make sure they work as expected.

### Devlog Entry - [2024-12-05, 2:28 PM]

**Thoughts so far:**
Focused on implementing the foundation for the B-tree structure, particularly addressing the insertion of key-value pairs and handling node creation. I added the functionality for creating the root node if the index file is empty. When a node becomes full, the logic to split the node is added as a placeholder for future development. The search function now checks for keys within the root node and displays the corresponding values if found. The B-tree structure is now capable of handling the basic insertion and search operations.

I also updated the menu to allow users to interact with the program and perform the main operations (create, insert, search, and quit). The `split_node` function was introduced as a placeholder for when nodes need to be split, but the actual logic for splitting nodes will be developed later.

**Plan for this session:**
- Continue refining the insertion process and node splitting logic.
- Implement the actual splitting logic for nodes when they exceed their capacity.
- Expand the search functionality to handle multi-level B-tree traversal.
- Test the insertion and search functionality with different sets of key-value pairs.

### Devlog Entry - [2024-12-05, 4:03 PM]

**Thoughts so far:**
Implemented the logic for splitting a B-tree node when it exceeds its maximum capacity. The node is split into two parts, with the middle key moved up to the parent node. If the parent doesn't exist (i.e., the split happens at the root), a new root node is created. The splitting logic is now in place, though it still needs to handle updating child pointers and managing nodes beyond the root. The program now allows for basic insertions, splits, and searches within the root node.

Additionally, the search functionality was enhanced to search for keys in the root node and return the associated value. The menu system was improved to allow the user to interact with the program by choosing from options like creating a new index file, inserting key-value pairs, searching for keys, and quitting the program.

**Plan for this session:**
- Refine the logic for splitting nodes to handle child pointers and ensure that nodes are correctly linked after a split.
- Expand the search functionality to traverse the tree and handle multi-level B-trees.
- Implement more commands such as printing and extracting data, as well as error handling for invalid inputs and edge cases.

### Devlog - [2024-12-07, 1:40 PM]

**What I did today:**
- Today, I worked on fixing the issue where the value was incorrectly displayed as `0` when searching for a key after inserting a key-value pair into the B-tree index file.
- I identified that the problem was due to misalignment of key-value pairs within the node structure and improper offsets used when writing and reading from the file. Specifically, the values were not being written to the correct offsets in the file, causing them to not be correctly read during the search.
- I implemented a thorough fix by updating the logic in the following areas:
  - **Inserting key-value pairs**: I ensured that the values were written to the correct offsets (starting at byte 176 for the values section in each node).
  - **Searching for keys**: I corrected the logic to ensure values were correctly unpacked from the proper positions when searching for a key.
  - **Node layout**: I ensured the node structure strictly adhered to the 512-byte layout with proper padding for unused space.

**What I learned:**
- The B-tree node layout was crucial to ensure that keys and values were written and read correctly from the file. Understanding the exact positions in the file where keys, values, and child pointers are stored allowed me to correct the offsets and avoid misreading data.
- It became clear that managing file offsets in a binary file for a data structure like a B-tree requires precise control over the layout, especially when dealing with multiple elements (keys, values, child pointers) in each node.

**What I plan to do next:**
- Continue testing the B-tree implementation, especially for larger sets of data, to ensure the insert, search, and split functionalities are all operating as expected.
- Look into potential improvements for node splitting logic to handle cases when nodes exceed the maximum number of keys and need to be split efficiently.

**Challenges faced:**
- A significant challenge was aligning the data structures in memory with the actual file format. It was critical to ensure that the key-value pairs and child pointers were placed at the correct offsets in the node structure.
- Debugging the issue took some time because the misalignment only became apparent during searches, making it tricky to pinpoint the exact cause. Once I identified the node layout problem, the fix was straightforward.

