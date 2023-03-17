import argparse


from paddlespeech.cli.log import logger
from paddlespeech.server.bin.paddlespeech_server import ServerExecutor
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='paddlespeech_server.start', add_help=True)
    parser.add_argument(
        "--config_file",
        action="store",
        help="yaml file of the app",
        default=None,
        required=True)

    parser.add_argument(
        "--log_file",
        action="store",
        help="log file",
        default="./log/paddlespeech.log")
    logger.info("start to parse the args")
    args = parser.parse_args()

    logger.info("start to launch the streaming asr server")
    streaming_asr_server = ServerExecutor()
    streaming_asr_server(config_file=args.config_file, log_file=args.log_file)