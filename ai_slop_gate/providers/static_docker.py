# ai_slop_gate/providers/static_docker.py
import re
from pathlib import Path
from typing import List
from ai_slop_gate.providers.base import BaseProvider, ProviderObservation
from ai_slop_gate.domain.observation_factory import make_observation

class StaticDockerProvider(BaseProvider):
    SUSPICIOUS_PKGS = {"cowsay", "fortune", "nmap", "tcpdump", "netcat", "tmux", "systemd"}
    CHMOD_777_RE = re.compile(r"chmod\s+-R\s+777\s+/", re.IGNORECASE)
    SUDOERS_RE = re.compile(r"NOPASSWD:\s*ALL", re.IGNORECASE)
    MULTIPLE_ENTRYPOINT_RE = re.compile(r"^ENTRYPOINT", re.MULTILINE)
    COPY_SYSTEM_DIRS_RE = re.compile(r"COPY\s+/(etc|var|bin|usr|root)", re.IGNORECASE)
    EXPOSE_DANGEROUS_RE = re.compile(r"EXPOSE\s+(22|3306|5432|27017|65535|31337)", re.IGNORECASE)

    def __init__(self, model: str = "docker-slop-v1"):
        self.name = "static-docker"
        self.kind = "infra"
        self.model = model

    def analyze(self, input_data: str = "") -> ProviderObservation:
        observations = []
        files = self._collect_docker_files()

        for file_path in files:
            text = file_path.read_text(errors="ignore")
            lines = text.splitlines()

            entrypoints = self.MULTIPLE_ENTRYPOINT_RE.findall(text)
            if len(entrypoints) > 1:
                observations.append(make_observation(
                    self.name, "quality", "redundant_entrypoint", 1.0, "high",
                    "Multiple ENTRYPOINT instructions detected. Only the last one will take effect.",
                    {"file": str(file_path)}
                ))

            for i, line in enumerate(lines, start=1):
                if self.CHMOD_777_RE.search(line):
                    observations.append(make_observation(
                        self.name, "security", "extreme_privilege", 1.0, "critical",
                        "Recursive chmod 777 on root or app detected. High security risk.",
                        {"file": str(file_path), "line": i}
                    ))

                found_pkgs = [p for p in self.SUSPICIOUS_PKGS if p in line.lower()]
                if "apt-get install" in line and found_pkgs:
                    observations.append(make_observation(
                        self.name, "quality", "package_bloat", 0.8, "medium",
                        f"Suspicious or redundant packages found: {', '.join(found_pkgs)}.",
                        {"file": str(file_path), "line": i}
                    ))

                if self.COPY_SYSTEM_DIRS_RE.search(line):
                    observations.append(make_observation(
                        self.name, "quality", "system_dir_copy", 0.9, "high",
                        "Copying system directories (/etc, /usr, /bin) into the image is a bad practice.",
                        {"file": str(file_path), "line": i}
                    ))

                if self.EXPOSE_DANGEROUS_RE.search(line):
                    observations.append(make_observation(
                        self.name, "security", "dangerous_port_exposed", 0.9, "high",
                        f"Potentially dangerous or sensitive port exposed: {line.strip()}",
                        {"file": str(file_path), "line": i}
                    ))

                if self.SUDOERS_RE.search(line):
                    observations.append(make_observation(
                        self.name, "security", "sudoers_exploit", 1.0, "high",
                        "Insecure sudoers configuration (NOPASSWD:ALL) detected.",
                        {"file": str(file_path), "line": i}
                    ))

        return ProviderObservation(
            self.name, self.model, observations, f"Analyzed {len(files)} Docker files."
        )

    def _collect_docker_files(self) -> List[Path]:
        return [p for p in Path(".").rglob("*") if p.is_file() and (p.name == "Dockerfile" or p.suffix == ".dockerfile")]

    def collect(self) -> ProviderObservation:
        return self.analyze()
