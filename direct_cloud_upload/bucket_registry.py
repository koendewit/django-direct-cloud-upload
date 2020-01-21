#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Dict
from google.cloud.storage import Bucket

_bucket_registry: Dict[str, Bucket] = dict()

def register_gcs_bucket(bucket):
    id = "gs://" + bucket.name
    _bucket_registry[id] = bucket
    return id