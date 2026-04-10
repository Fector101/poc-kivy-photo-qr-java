# -*- coding: utf-8 -*-
import os
import json
import tempfile
from pathlib import Path

from kivy.app import App
from kivy.lang import Builder
from kivy.utils import platform

def load_kv(file_name, file_path="gui_kv"):
    with open(os.path.join(file_path, file_name), encoding="utf-8") as kv:
        return Builder.load_string(kv.read())

def is_android():
    return platform == 'android'

def is_ios():
    return platform == 'ios'

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

def save_settings(data: dict):
    app = App.get_running_app()
    path = os.path.join(app.user_data_dir, "settings.json")
    data = data.to_dict()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_settings() -> dict:
    app = App.get_running_app()
    path = os.path.join(app.user_data_dir, "settings.json")
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.decoder.JSONDecodeError:
            return {}

def get_datadir() -> Path:
    if is_android() or is_ios():
        app = App.get_running_app()
        data_dir = Path(app.user_data_dir) / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir    
    else:
        return Path(tempfile.gettempdir())
