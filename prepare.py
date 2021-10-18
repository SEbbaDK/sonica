#!/usr/bin/env python

import os

import typer

cli = typer.Typer()

options = {}

@cli.command()
def generate_grpc_python(dir: str):
    """
    Generates the python protobuf spec and grpc clients/server from the sonica service spec.
    """
    command = ' '.join([
        f'python -m grpc_tools.protoc',
        f'-I ./',
        f'--python_out="{dir}"',
        f'--grpc_python_out="{dir}"',
        f'sonica.proto',
    ])
    print ("$ " + command)
    os.system(command)

@cli.command()
def generate_grpc_crystal(dir: str):
    """
    Generates the crystal protobuf spec and grpc clients/server from the sonica service spec.
    Uses https://github.com/jgaskins/grpc and requires the binaries.
    """
    command = ' '.join([
        f'protoc',
        f'--grpc_out={dir}',
        f'--crystal_out={dir}',
        f'--plugin=protoc-gen-grpc={options["protoc_gen_grpc"]}',
        f'--plugin=protoc-gen-crystal={options["protoc_gen_crystal"]}',
        f'sonica.proto',
    ])
    print ("$ " + command)
    os.system(command)

@cli.command()
def discord():
    generate_grpc_python('discord')

@cli.command()
def daemon():
    generate_grpc_python('daemon')

@cli.command()
def http():
    generate_grpc_crystal('http')

def error(text: str):
    typer.secho(text, fg = typer.colors.RED, err = True)
    exit(1)

@cli.callback()
def callback(
        protoc_gen_grpc: str = typer.Option("", envvar="PROTOC_GEN_GRPC"),
        protoc_gen_crystal: str = typer.Option("", envvar="PROTOC_GEN_CRYSTAL")
    ):
    crystal_url = "Check https://github.com/jgaskins/grpc for info on how to get the binaries";
    if protoc_gen_crystal == "":
        error("PROTOC_GEN_CRYSTAL needs to be given as an option or be in the environment\n" + crystal_url)
    if protoc_gen_grpc == "":
        op
        error("PROTOC_GEN_GRPC needs to be given as an option or be in the environment\n" + crystal_url)

    options["protoc_gen_crystal"] = protoc_gen_crystal
    options["protoc_gen_grpc"] = protoc_gen_grpc

cli()
