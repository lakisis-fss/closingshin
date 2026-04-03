import pb_utils
import json

client = pb_utils.get_pb_client()
res = client.collection('market_status').get_list(1, 1, {"sort": "-date"})

if not res.items:
    print("NO RECORDS FOUND")
else:
    item = res.items[0]
    print(f"ID: {item.id}")
    print(f"Collection: {item.collection_id}/{item.collection_name}")
    print(f"Date: {getattr(item, 'date', 'N/A')}")
    
    # Check custom attributes (how SDK 0.15.0 provides them)
    # Usually it is item.field_name or item.__dict__['extra_model_attrs']
    
    print("--- Available methods/attrs ---")
    print(dir(item))
    
    print("--- Data field content ---")
    if hasattr(item, 'data'):
        print(json.dumps(item.data, indent=2, ensure_ascii=False))
    else:
        print("NO 'data' ATTRIBUTE FOUND DIRECTLY")
        
    print("--- Full __dict__ ---")
    # For debugging the Record object structure
    print(item.__dict__)
