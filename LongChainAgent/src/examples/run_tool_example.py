from src.model.openai_model import get_openai_model

def run_tools_with_simple_decorator():
    from src.tools.simple.math import multiply, add

    tool_map = {"add": add, "multiply": multiply}

    llm = get_openai_model()
    llm_with_tools = llm.bind_tools([add, multiply])

    query = "What is 3 * 12?"

    '''
    get the response object as following format:
    {
    ...
      "tool_calls": [
        {
          "name": "multiply",      # tool name
          "args": {
            "a": 3,
            "b": 12
          }
        }
      ],
      "output": None,             
      "content": None             
    }
    '''
    call_tool_res = llm_with_tools.invoke(query)
    tool_calls = call_tool_res.tool_calls

    for call in tool_calls:
        tool_name = call["name"]
        args = call["args"]
        tool_func = tool_map[tool_name]
        tool_result = tool_func.invoke(args)
        print(f"call tool {tool_name}({args}) = {tool_result}")

def run_tools_with_subclass():
    from src.tools.subclass.math import MultiplyCalculatorTool, AddCalculatorTool
    multiply_tool = MultiplyCalculatorTool()
    add_tool = AddCalculatorTool()

    tool_map = {multiply_tool.name: multiply_tool, add_tool.name: add_tool}

    llm = get_openai_model()
    llm_with_tools = llm.bind_tools([multiply_tool, add_tool])

    query = "What is 100 + 321 ?"
    call_tool_res = llm_with_tools.invoke(query)
    tool_calls = call_tool_res.tool_calls

    for call in tool_calls:
        tool_name = call["name"]
        args = call["args"]
        tool = tool_map[tool_name]
        tool_result = tool.invoke(args)
        print(f"call tool {tool_name}({args}) = {tool_result}")

# run_tools_with_simple_decorator()
run_tools_with_subclass()