#!/usr/bin/env python

import os

import typer

program = typer.Typer()

options = {}

def run_command(command: str):
    print ("$ " + command)
    os.system(command)

def create_generator(language: str):
    """
    Creates a function that generates one of the default languages supported by protoc
    """
    def generator(dir: str):
        run_command(' '.join([
            f'protoc',
            f'--{language}_out={dir}',
            f'sonica.proto',
        ]))
    return generator

@program.command()
def generate_grpc_python(dir: str):
    """
    Generates the python protobuf spec and grpc clients/server from the sonica service spec.
    """
    run_command(' '.join([
        f'python -m grpc_tools.protoc',
        f'-I ./',
        f'--python_out="{dir}"',
        f'--grpc_python_out="{dir}"',
        f'sonica.proto',
    ]))

@program.command()
def generate_grpc_go(dir: str):
    """
    Generates the go protobuf spec and grpc clients/server from the sonica service spec.
    """
    run_command(' '.join([
        f'protoc',

        f'--plugin=protoc-gen-go={options["protoc_gen_go"]}',
        f'--plugin=protoc-gen-go-grpc={options["protoc_gen_go_grpc"]}',

        f'--go-grpc_out={dir}',
        #f'--go_opt paths=source_relative',

        f'--go_out={dir}',
        #f'--go-grpc-opt=paths=source_relative',

        #f'--grpc-gateway_out={dir}',
        #f'--grpc-gateway_opt=logtostderr=true',
        #f'--grpc-gateway_opt=paths=source_relative',
        #f'--grpc-gateway_opt=generate_unbound_methods=true',

        f'sonica.proto',
    ]))

@program.command()
def generate_grpc_crystal(dir: str):
    """
    Generates the crystal protobuf spec and grpc clients/server from the sonica service spec.
    Uses https://github.com/jgaskins/grpc and requires the binaries.
    """
    run_command(' '.join([
        f'protoc',
        f'--grpc_out={dir}',
        f'--crystal_out={dir}',
        f'--plugin=protoc-gen-grpc={options["protoc_gen_grpc"]}',
        f'--plugin=protoc-gen-crystal={options["protoc_gen_crystal"]}',
        f'sonica.proto',
    ]))

@program.command()
def discord():
    generate_grpc_python('discord')

@program.command()
def daemon():
    generate_grpc_python('daemon')

@program.command()
def http():
    generate_grpc_crystal('http')

@program.command()
def cli():
    generate_grpc_python('cli')

def error(text: str):
    typer.secho(text, fg = typer.colors.RED, err = True)
    exit(1)

@program.callback()
def callback(
        protoc_gen_grpc: str = typer.Option("", envvar="PROTOC_GEN_GRPC"),
        protoc_gen_crystal: str = typer.Option("", envvar="PROTOC_GEN_CRYSTAL"),
        protoc_gen_go: str = typer.Option("", envvar="PROTOC_GEN_GO"),
        protoc_gen_go_grpc: str = typer.Option("", envvar="PROTOC_GEN_GO_GRPC")
    ):
    crystal_url = "Check https://github.com/jgaskins/grpc for info on how to get the binaries";

    if protoc_gen_crystal == "":
        error("PROTOC_GEN_CRYSTAL needs to be given as an option or be in the environment\n" + crystal_url)
    else:
        options["protoc_gen_crystal"] = protoc_gen_crystal

    if protoc_gen_grpc == "":
        error("PROTOC_GEN_GRPC needs to be given as an option or be in the environment\n" + crystal_url)
    else:
        options["protoc_gen_grpc"] = protoc_gen_grpc

    go_url = "Check https://github.com/grpc-ecosystem/grpc-gateway/ for info on how to set the binaries"

    if protoc_gen_go == "":
        error("PROTOC_GEN_GO needs to be given as an option or be in the environment\n" + go_url)
    else:
        options["protoc_gen_go"] = protoc_gen_go

    if protoc_gen_go_grpc == "":
        error("PROTOC_GEN_GO_GRPC needs to be given as an option or be in the environment\n" + go_url)
    else:
        options["protoc_gen_go_grpc"] = protoc_gen_go_grpc

for lang in ['cpp', 'csharp', 'java', 'js', 'objc', 'php', 'ruby']:
    name = f'generate-grpc-{lang}'
    program.command(name = name)(create_generator(lang))

program()
