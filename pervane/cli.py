from pervane import serve


def main(as_module=False):
    print('sys.argv', sys.argv)
    serve.cli_main()
