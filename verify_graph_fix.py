
import asyncio
from pathlib import Path
from coding_agent.swarm.graph_store import GraphStore

async def test_update():
    workspace = Path(r"c:\Users\HP\coding agent")
    graph = GraphStore(workspace)
    
    # Test Node Creation
    graph.create_node("SystemComponent", "test_comp", {"status": "initial"})
    print("Node created.")
    
    # Test Property Update
    try:
        graph.update_node_properties("SystemComponent", "test_comp", {"status": "updated"})
        print("update_node_properties successful.")
    except AttributeError as e:
        print(f"FAILED: {e}")
    except Exception as e:
        print(f"Other error: {e}")
        
    graph.close()

if __name__ == "__main__":
    asyncio.run(test_update())
