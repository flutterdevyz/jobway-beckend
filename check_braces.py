import sys

def check_braces(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    stack = []
    lines = content.split('\n')
    for i, line in enumerate(lines):
        row = i + 1
        for col, char in enumerate(line):
            if char == '{':
                stack.append(('{', row, col + 1))
            elif char == '(':
                stack.append(('(', row, col + 1))
            elif char == '[':
                stack.append(('[', row, col + 1))
            elif char == '}':
                if not stack:
                    print(f"Unbalanced }} at {row}:{col+1}")
                elif stack[-1][0] == '{':
                    stack.pop()
                else:
                    print(f"Mismatched }} (expected {stack[-1][0]} from {stack[-1][1]}:{stack[-1][2]}) at {row}:{col+1}")
            elif char == ')':
                if not stack:
                    print(f"Unbalanced ) at {row}:{col+1}")
                elif stack[-1][0] == '(':
                    stack.pop()
                else:
                    print(f"Mismatched ) (expected {stack[-1][0]} from {stack[-1][1]}:{stack[-1][2]}) at {row}:{col+1}")
            elif char == ']':
                if not stack:
                    print(f"Unbalanced ] at {row}:{col+1}")
                elif stack[-1][0] == '[':
                    stack.pop()
                else:
                    print(f"Mismatched ] (expected {stack[-1][0]} from {stack[-1][1]}:{stack[-1][2]}) at {row}:{col+1}")
    
    if stack:
        print("Unclosed delimiters at end:")
        for b in stack:
            print(f"  {b[0]} at {b[1]}:{b[2]}")
    else:
        print("All delimiters balanced.")

if __name__ == "__main__":
    check_braces(sys.argv[1])
