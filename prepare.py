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
def crystal():
    ensure_generated_folder()
    run(' '.join([
        'openapi-generator-cli generate',
        f'-i {o.filename}',
        '-o ./generated/crystal',
        '-g crystal',
        '-p moduleName=Sonica',
        '-p shardName=sonica-client',
        '-p shardAuthor=sonica-team',
        f'-p shardVersion={o.version}',
    ]))

    # We also replace some old pre 1.0 crystal syntax
    conffile = './generated/crystal/src/sonica-client/configuration.cr'
    with open(conffile, 'r') as f:
        lines = f.readlines()
    with open(conffile, 'w') as f:
        f.writelines([
            l.replace('Hash{       }', '{} of String => String')
            for l in lines
        ])

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

