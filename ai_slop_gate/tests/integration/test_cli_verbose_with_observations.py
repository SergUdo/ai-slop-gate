# import subprocess
# import sys
# from pathlib import Path


# def test_cli_verbose_with_observations(tmp_path: Path):
#     policy = tmp_path / "policy.yml"
#     policy.write_text("""
# version: "v1"
# compliance:
#   enabled: true
#   forbid_licenses: ["GPL-3.0"]
# rules:
#   - id: forbid_gpl
#     when:
#       category: COMPLIANCE
#       signal: FORBIDDEN_LICENSE
#     then:
#       action: blocking
#       message: "Forbidden license detected"
# """)

#     req = tmp_path / "requirements.txt"
#     req.write_text("somepkg==1.0  # GPL-3.0\n")

#     result = subprocess.run(
#         [
#             sys.executable,
#             "-m",
#             "ai_slop_gate.cli.main",
#             "run",
#             "--provider",
#             "static",
#             "--policy",
#             str(policy),
#             "--input-file",
#             str(tmp_path),
#             "--compliance",
#             "--verbose",
#         ],
#         capture_output=True,
#         text=True,
#     )

#     out = result.stdout
#     assert "Forbidden licenses: ['GPL-3.0']" in out
#     assert "Decision: BLOCKING" in out

