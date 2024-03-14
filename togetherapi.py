import os
import requests
from typing import List, Dict

class BaseApi:
    def __init__(self, model: str, api_key_envvar: str = 'TOGETHER_KEY'):
        assert isinstance(model, str), "The model argument must be a string."
        self._model = model
        self._settings = vars().copy()  # Copy all initial variables into _settings dict
        del self._settings['_settings']  # Remove '_settings' itself from _settings dict

        self._api_key = lambda : os.getenv(api_key_envvar)

    @property
    def headers(self):
        return {'Authorization': f'Bearer {self._api_key()}'}

    def payload(self, **kwargs):
        data = {}
        for attr, val in self._settings.items():
            if val!= getattr(self, '_' + attr):
                data[attr] = val
        data.update(**kwargs)  # Add additional arguments passed during function call
        return data 

    def __call__(self, *args, **kwargs):
        raise NotImplementedError("Subclasses need to implement '__call__'")

    def __getitem__(self, item):
        return self._settings[item]

    def __setitem__(self, key, value):
        setattr(self, '_' + key, value)
        self._settings[key] = value

class TogetherCompletion(BaseApi):
    ENDPOINT = 'https://api.together.xyz/v1/completions'
    MAX_TOKENS = 1536
    TEMPERATURE = 0.5
    TOP_P = 0.85
    TOP_K = 42
    REPETITION_PENALTY = 1

    def __init__(self, model: str, stop_sequences: List[str] = None, **kwargs):
        super().__init__(model, **kwargs)
        self._stop_sequences = stop_sequences
        self._endpoint = kwargs.get('endpoint', self.ENDPOINT)
        self._max_tokens = kwargs.get('max_tokens', self.MAX_TOKENS)
        self._temperature = kwargs.get('temperature', self.TEMPERATURE)
        self._top_p = kwargs.get('top_p', self.TOP_P)
        self._top_k = kwargs.get('top_k', self.TOP_K)
        self._repetition_penalty = kwargs.get('repetition_penalty', self.REPETITION_PENALTY)

    def __call__(self, prompt: str) -> dict:
        r = requests.post(self._endpoint, headers=self.headers, json=self.payload(prompt=prompt))
        r.raise_for_status()
        return r.json()

class TogetherChat(BaseApi):
    ENDPOINT = 'https://api.together.xyz/v1/chat/completions'
    MAX_TOKENS = 1024

    def __init__(self, model: str, messages: List[Dict[str, str]], **kwargs):
        super().__init__(model, **kwargs)
        self._messages = messages
        self._endpoint = kwargs.get('endpoint', self.ENDPOINT)
        self._max_tokens = kwargs.get('max_tokens', self.MAX_TOKENS)

    def __call__(self) -> dict:
        r = requests.post(self._endpoint, headers=self.headers, json=self.payload(messages=self._messages))
        r.raise_for_status()
        return r.json()
