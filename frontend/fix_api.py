import os
import glob

api_dir = r"e:\Downloads\Antigravity Project\ClosingSHIN\frontend\src\app\api"
files = glob.glob(os.path.join(api_dir, "**", "route.ts"), recursive=True)

for file in files:
    with open(file, "r", encoding="utf-8") as f:
        content = f.read()

    # The broken string from previous script
    broken_str_1 = "export const dynamic = \" force-dynamic\\;\n\n"
    broken_str_2 = "export const dynamic = \" force-dynamic\\;"
    
    if broken_str_1 in content:
        content = content.replace(broken_str_1, "")
    elif broken_str_2 in content:
        content = content.replace(broken_str_2, "")

    # Write the correct string
    correct_str = "export const dynamic = 'force-dynamic';\n\n"
    
    if correct_str not in content:
        with open(file, "w", encoding="utf-8") as f:
            f.write(correct_str + content.lstrip())
        print(f"Fixed {file}")
    else:
        with open(file, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Already correct {file}")
