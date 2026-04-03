try:
    with open('debug_output.txt', 'r', encoding='utf-16') as f:
        content = f.read()
        
    idx = content.find("Traceback")
    if idx != -1:
        print("--- FOUND TRACEBACK ---\n")
        print(content[idx:idx+1500])
    else:
        print("Traceback not found. First 500 chars:")
        print(content[:500])
except Exception as e:
    print(f"Error reading file: {e}")
