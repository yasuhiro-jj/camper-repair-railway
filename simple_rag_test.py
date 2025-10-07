from streamlit_app_simple import get_relevant_blog_links

def test_rag():
    print("RAG Test Start")
    
    # Test 1: Battery query
    result1 = get_relevant_blog_links("battery")
    print(f"Battery query result: {len(result1)} blogs found")
    
    # Test 2: Water pump query
    result2 = get_relevant_blog_links("water pump")
    print(f"Water pump query result: {len(result2)} blogs found")
    
    # Test 3: Gas query
    result3 = get_relevant_blog_links("gas")
    print(f"Gas query result: {len(result3)} blogs found")
    
    print("RAG Test Complete")

if __name__ == "__main__":
    test_rag()
