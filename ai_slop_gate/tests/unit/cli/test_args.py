from ai_slop_gate.cli.args import build_parser

def test_parser_has_init_and_run():
    parser = build_parser()
    args = parser.parse_args(["init"])
    assert args.command == "init"

    args = parser.parse_args(["run", "--policy", "policy.yml"])
    assert args.command == "run"

def test_run_requires_policy():
    parser = build_parser()
    try:
        parser.parse_args(["run"])
        assert False
    except SystemExit:
        pass
