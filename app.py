#!/usr/bin/env python3
import os

import aws_cdk as cdk

from encryption_best_practices.stacks import register_stacks as register_encbp_stacks


app = cdk.App()

register_encbp_stacks(app)

app.synth()
