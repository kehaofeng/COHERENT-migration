"""Shared API configuration for the planner and robot agents."""

import warnings

from openai import OpenAI, DefaultHttpxClient


def create_client(args):
    if not args.api_key:
        variable = 'DEEPSEEK_API_KEY' if args.source == 'deepseek' else 'OPENAI_API_KEY'
        raise ValueError(f'Missing API key: set {variable} before running a task')
    options = dict(api_key=args.api_key, base_url=args.base_url,
                   timeout=60.0, max_retries=0)
    if args.source == 'openai' and args.organization:
        options['organization'] = args.organization
    if args.source == 'deepseek':
        # Ignore shell proxy settings for both planner and robot API calls.
        options['http_client'] = DefaultHttpxClient(trust_env=False)
        warnings.warn('DeepSeek cost is not calculated; legacy cost=0 does not mean free.',
                      stacklevel=2)
    return OpenAI(**options)


def request_params(source, sampling_params):
    params = dict(sampling_params)
    if source == 'deepseek':
        # Existing callers consume one text answer, not reasoning history.
        params.pop('n', None)
        params['extra_body'] = {'thinking': {'type': 'disabled'}}
    return params
