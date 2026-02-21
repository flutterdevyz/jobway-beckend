import sys

def check_strings(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    in_string = None # None, ', ", or `
    escape = False
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        row = i + 1
        for col, char in enumerate(line):
            if escape:
                escape = False
                continue
            
            if char == '\\':
                escape = True
                continue
            
            if in_string == '`':
                if char == '`':
                    in_string = None
                elif char == '$' and col + 1 < len(line) and line[col+1] == '{':
                    # This starts a nested expression, but for string tracking we just care about the `
                    pass
            elif in_string:
                if char == in_string:
                    in_string = None
            else:
                if char in ("'", '"', '`'):
                    in_string = char
        
        # Strings with ' and " cannot span lines unless escaped
        if in_string in ("'", '"'):
             print(f"Unclosed string {in_string} at end of line {row}")
             in_string = None # Reset for next line
    
    if in_string == '`':
        print(f"Unclosed template literal ` at end of file")

if __name__ == "__main__":
    check_strings(sys.argv[1])
