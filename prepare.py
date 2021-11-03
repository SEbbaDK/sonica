#!/usr/bin/env python

import os

import typer
import yaml

class Options:
    filename: str = 'sonica.yml'
    verbose: bool = False
    version: str = None

program = typer.Typer()

def echo(s : str):
    if o.verbose:
        print(s)

def ensure_generated_folder():
    try:
        os.mkdir('generated')
        echo('Created ./generated folder')
    except:
        echo('Skipped creating ./generated folder')
        pass

def run(c: str):
    echo('$ ' + c)
    os.system(c)

@program.command()
def validate():
    run(f'openapi-generator-cli validate -i {o.filename}')

@program.command()
def crystal_client():
    ensure_generated_folder()
    run(' '.join([
        'openapi-generator-cli generate',
        f'-i {o.filename}',
        '-o ./generated/crystal-client',
        '-g crystal',
        '-p shardName=sonica',
        '-p shardAuthor=sonica-team',
        f'-p shardVersion={o.version}',
    ]))

@program.command()
def python_server():
    ensure_generated_folder()
    run(' '.join([
		'openapi-generator-cli generate',
		f'-i {o.filename}',
		'-o ./generated/python',
		'-g python',
    ]))

@program.command()
def all():
	crystal()

@program.callback()
def callback(verbose : bool = False, filename : str = None):
    global o
    o = Options()
    o.verbose = verbose
    if filename:
        o.filename = filename
    with open('sonica.yml', 'r') as f:
        yml = yaml.safe_load(f)
        o.version = yml['info']['version']


program()

