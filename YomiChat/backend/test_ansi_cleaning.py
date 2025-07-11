#!/usr/bin/env python3
"""
测试ANSI转义序列清理功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent_wrapper import clean_ansi_codes, extract_meaningful_content

def test_ansi_cleaning():
    """测试ANSI代码清理功能"""
    
    # 测试数据 - 模拟smolagents的实际输出
    test_cases = [
        {
            "input": "[38;2;212;183;2m╭─[0m[38;2;212;183;2m─────────────────────────────────────────────────────[0m[38;2;212;183;2m [0m[1;38;2;212;183;2mNew run[0m[38;2;212;183;2m [0m[38;2;212;183;2m─────────────────────────────────────────────────────[0m[38;2;212;183;2m─╮[0m",
            "expected_type": "decorated_box",
            "description": "装饰性边框开始"
        },
        {
            "input": "[38;2;212;183;2m│[0m [38;2;212;183;2m│[0m [38;2;212;183;2m│[0m [1m帮我制定一个在上海旅游三天的旅游计划[0m [38;2;212;183;2m│[0m",
            "expected_type": "content_line",
            "description": "边框内的内容行"
        },
        {
            "input": "[38;2;212;183;2m╰─[0m[38;2;212;183;2m LiteLLMModel - azure/gpt-4-32k [0m[38;2;212;183;2m───────────────────────────────────────────────────────────────────────────────────[0m[38;2;212;183;2m─╯[0m",
            "expected_type": "decorated_box",
            "description": "装饰性边框结束"
        }
    ]
    
    print("开始测试ANSI代码清理功能...\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"测试用例 {i}: {test_case['description']}")
        print(f"原始输入: {repr(test_case['input'])}")
        
        # 测试基本清理
        cleaned = clean_ansi_codes(test_case['input'])
        print(f"清理后: {repr(cleaned)}")
        
        # 测试内容提取
        meaningful = extract_meaningful_content(test_case['input'])
        print(f"提取内容: {repr(meaningful)}")
        
        print("-" * 60)
        print()

if __name__ == "__main__":
    test_ansi_cleaning()
