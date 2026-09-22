import argparse
import os

# import torch
import pdb
import yaml
from typing import Dict


def get_args():
    parser = argparse.ArgumentParser(description='LLM-based Heterogeneous Multi-Robot System Setting')

    parser.add_argument('--env', type=str, required=True, choices=['env0', 'env1', 'env2', 'env3', 'env4'],
                    help='Select a simulation environment')
    parser.add_argument('--task', type=int, required=True, nargs='+', 
                    help='Specifies the ID of the task to run. Enter at least one parameter.')
    parser.add_argument('--source', default='deepseek', choices=['deepseek', 'openai'],
                    help='Model API provider (local inference is not implemented)')
    parser.add_argument('--lm_id', default=None,
                    help='Model ID; defaults to deepseek-v4-pro for DeepSeek')
    parser.add_argument('--log_dir', default='./log', help='Experiment log directory')
    parser.add_argument('--debug', action='store_true', default=False,
                    help='debugging mode')
    parser.add_argument('--oracle_prompt_path', default="./prompt/oracle_prompt.txt" ,
                    help='path of oracle_prompt')
    parser.add_argument('--quadrotor_prompt_path', default="./prompt/quadrotor_prompt.txt",
                    help='path of quadrotor_prompt')
    parser.add_argument('--robot_dog_prompt_path', default="./prompt/robot_dog_prompt.txt",
                    help='path of robot_dog_prompt')
    parser.add_argument('--robot_arm_prompt_path', default="./prompt/robot_arm_prompt.txt",
                    help='path of robot_arm_prompt')
    parser.add_argument('--judge_prompt_path', default="./prompt/judge_prompt.txt",
                    help='path of judge_prompt')
    parser.add_argument('--base_url', default=None, help='Override the API endpoint')
    parser.add_argument('--api_key', default='',
                    help='API key; prefer DEEPSEEK_API_KEY or OPENAI_API_KEY environment variable')
    parser.add_argument('--organization', default='', 
                    help='please enter your openai organization')
    parser.add_argument("--t", default=0, type=float)

    parser.add_argument("--top_p", default=1.0, type=float)

    parser.add_argument("--max_tokens", default=512, type=int)

    parser.add_argument("--n", default=1, type=int)

    args = parser.parse_args()
    if args.source == 'deepseek':
        args.api_key = args.api_key or os.environ.get('DEEPSEEK_API_KEY', '')
        args.base_url = args.base_url or 'https://api.deepseek.com'
        args.lm_id = args.lm_id or 'deepseek-v4-pro'
        if args.n != 1:
            parser.error('DeepSeek integration requires --n 1')
    else:
        args.api_key = args.api_key or os.environ.get('OPENAI_API_KEY', '')
        args.base_url = args.base_url or 'https://api.openai.com/v1'
        args.lm_id = args.lm_id or 'gpt-4-0125-preview'
    return args

if __name__ == '__main__':
    args = get_args()
