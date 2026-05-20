from node import Node
from blockchain import Block, Blockchain

def main():
    bc = Blockchain()
    
    konsti = Node(node_name="k", port=3000)
    enrico = Node(node_name="e", port=4000)
    marvin = Node(node_name="m", port=5000)
    konsti.run()
    print(konsti.private_key)




if __name__ == "__main__":
    main()
