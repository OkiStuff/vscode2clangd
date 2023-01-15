import typing as t
import json
import sys
from pathlib import Path

def substitute_env_var(string: str, env: t.Dict[str, t.Union[int, bool, str, t.List, None]]) -> t.Union[str, None, bool]:
    varindex: int = string.find("${")
    if (varindex == -1): return None # No substitution neede
    
    endindex: int = string.find("}", (varindex + 2))
    if (endindex == -1):
        print("- missing '}' for enviornment variable subtitution, failed...")
        return False # Substitution failed
    
    varname: str = string[(varindex + 2):endindex]
    
    varval: t.Union[int, bool, str, t.List, None] = env.get(varname)
    if (varval == None):
        print(f"- enviornment variable '{varname}' was not found, failed...")
        return False # Substitution failed
    
    return string.replace("${" + varname + "}", varval)

def main() -> None:
    # Check if -h or --help was called
    if (len(sys.argv) < 2):
        print("not enough arguments...")
        return
    
    if (sys.argv[1] == "-h" or sys.argv[1] == "--help"):
        print("vscode2clangd [[-h] | [--help]] | [c_cpp_properties.json path]")
        print("vscode2clangd version 1.0 - (c) 2023 Frankie A.")
        return
    
    # Read JSON
    if (Path(sys.argv[1]).is_file() == False):
        print(f"{sys.argv[1]} is not a file...")
        return
    
    with open(sys.argv[1], "r") as fp:
        properties: t.Dict[str, t.Union[int, bool, str, t.List, None, t.Dict]] = json.load(fp)
        print("- parsed properties file into dictionary")
    
    print(f"- {sys.argv[1]} is c_cpp_properties version {properties['version']}")
    
    # Read environment variables:
    env: t.Dict[str, t.Union[int, bool, str, t.List, None]] = {
        "workspaceFolder": "./"
    }
    
    if (properties.get('env') == None):
        print("- 'env' key not found, skipping...")
    
    else:
        for var in properties['env']:
            print(f"- found environment variable '{var}' with a value of '{properties['env'][var]}'")
            
            if (type(properties['env'][var]) == list):
                for i in range(len(properties['env'][var])):
                    if (type(properties['env'][var][i]) != str): continue
                    subitem: t.Union[str, None, bool] = substitute_env_var(properties['env'][var][i], env)
                    
                    if (type(subitem) == Exception):
                        return
                    
                    properties['env'][var][i] = subitem
            
            elif (type(properties['env'][var]) == str):
                subitem: t.Union[str, None, bool] = substitute_env_var(properties['env'][var], env)
                
                if (type(subitem) == Exception):
                    return
                    
                properties['env'][var] = subitem
                
                    
            env.update({var: properties['env'][var]})
    
    print(env)
    
    # Read Configurations
    for configuration in properties['configurations']:
        print(f"- found configuration '{configuration['name']}'")

if __name__ == "__main__":
    main()